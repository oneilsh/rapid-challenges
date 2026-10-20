"""Review Mondo's SNOMED CT cross-references for rare diseases (runs locally; no AoU data).

For every rare-tagged Mondo disease with a `MONDO:equivalentTo` SNOMED xref, look up the
SNOMED concept's display name on a public FHIR terminology server (tx.fhir.org; cached)
and score how well it matches the Mondo label or any synonym. Low scores are candidates
for manual review: most are legitimate synonyms, some are wrong mappings. Also records
whether a parent Mondo term has its own SNOMED xref, to spot generic codes placed on a
genetic subtype.

Usage:
    uv run python scripts/mondo_snomed_review.py --out results/mondo-snomed-review/<tsv>
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from rapidaudit.aou import download_cached

RARE = {"rare", "orphanet_rare", "gard_rare", "nord_rare", "inferred_rare", "mondo_rare"}
_LOOKUP = ("https://tx.fhir.org/r4/CodeSystem/$lookup?system=http://snomed.info/sct"
           "&code={code}&_format=json")


def parse_obo(path: Path) -> pd.DataFrame:
    """One row per non-obsolete MONDO term: id, name, subsets, synonyms, is_a parents and
    SNOMED xrefs as (code, annotation) pairs."""
    recs, cur = [], None
    for line in path.open():
        line = line.rstrip("\n")
        if line == "[Term]":
            cur = {"sct": [], "isa": [], "subsets": [], "syn": [], "obsolete": False}
            recs.append(cur)
        elif line.startswith("["):
            cur = None
        elif cur is None:
            continue
        elif line.startswith("id: "):
            cur["id"] = line[4:]
        elif line.startswith("name: "):
            cur["name"] = line[6:]
        elif line.startswith("subset: "):
            cur["subsets"].append(line[8:].split()[0])
        elif line.startswith("is_a: "):
            cur["isa"].append(line[6:].split()[0])
        elif line.startswith("is_obsolete: true"):
            cur["obsolete"] = True
        elif line.startswith("synonym: "):
            m = re.match(r'synonym: "(.*?)"', line)
            if m:
                cur["syn"].append(m.group(1))
        elif line.startswith("xref: SCTID:"):
            m = re.match(r"xref: SCTID:(\d+)(?: \{(.*)\})?", line)
            cur["sct"].append((m.group(1), m.group(2) or ""))
    t = pd.DataFrame(recs)
    return t[t["id"].str.startswith("MONDO:", na=False) & ~t["obsolete"]].reset_index(drop=True)


def lookup_labels(codes, cache_path: Path, workers: int = 4) -> dict:
    """SNOMED code -> {"display", "inactive"} from tx.fhir.org, cached as JSON."""
    try:
        cache = json.loads(cache_path.read_text())
    except FileNotFoundError:
        cache = {}

    def one(code):
        for _ in range(3):
            try:
                d = json.load(urllib.request.urlopen(_LOOKUP.format(code=code), timeout=30))
                params = d.get("parameter", [])
                disp = next((x["valueString"] for x in params if x["name"] == "display"), None)
                inactive = None
                for x in params:
                    if x["name"] == "property":
                        q = {y["name"]: y for y in x["part"]}
                        if q.get("code", {}).get("valueCode") == "inactive":
                            inactive = q.get("value", {}).get("valueBoolean")
                return code, {"display": disp, "inactive": inactive}
            except Exception:  # noqa: BLE001 (public server hiccups; retry)
                time.sleep(2)
        return code, {"display": None}

    todo = [c for c in codes if cache.get(c, {}).get("display") is None]
    with ThreadPoolExecutor(workers) as pool:
        for code, r in pool.map(one, todo):
            cache[code] = r
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache))
    return cache


def _norm(s) -> str:
    s = (s or "").lower()
    s = re.sub(r"\((disorder|finding|disease|clinical)\)", "", s)
    s = re.sub(r"'s\b", "", s)
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


_STOP = {"of", "the", "and", "with", "due", "to", "disease", "disorder", "syndrome", "type"}


def match_score(names, display) -> float:
    """Best of string similarity and content-token Jaccard over the Mondo label/synonyms."""
    best, b = 0.0, _norm(display)
    tb = set(b.split()) - _STOP
    for n in names:
        a = _norm(n)
        ta = set(a.split()) - _STOP
        best = max(best, difflib.SequenceMatcher(None, a, b).ratio(),
                   len(ta & tb) / max(len(ta | tb), 1))
    return round(best, 2)


def review_table(terms: pd.DataFrame, labels: dict) -> pd.DataFrame:
    by_id = terms.set_index("id")
    rare = terms[terms["subsets"].apply(lambda s: bool(RARE & set(s)))]
    rows = []
    for _, r in rare.iterrows():
        for code, ann in r["sct"]:
            if "MONDO:equivalentTo" not in ann:
                continue
            lab = labels.get(code, {})
            parents = [p for p in r["isa"] if p in by_id.index]
            rows.append({
                "mondo_id": r["id"], "name": r["name"], "sctid": code,
                "snomed": lab.get("display"), "snomed_inactive": lab.get("inactive"),
                "score": match_score([r["name"], *r["syn"]], lab.get("display")),
                "rare_subsets": "|".join(sorted(RARE & set(r["subsets"]))),
                "parents": "; ".join(f"{p} {by_id.loc[p, 'name']}" for p in parents),
                "parent_sctids": "; ".join(c for p in parents for c, a in by_id.loc[p, "sct"]
                                           if "MONDO:equivalentTo" in a)})
    return pd.DataFrame(rows).sort_values("score").reset_index(drop=True)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out", required=True, help="output TSV")
    p.add_argument("--mondo-version", default="2026-06-02")
    p.add_argument("--cache-dir", default="data/mondo")
    args = p.parse_args(argv)
    cache = Path(args.cache_dir)
    terms = parse_obo(download_cached(args.mondo_version, "mondo.obo", cache))
    rare = terms[terms["subsets"].apply(lambda s: bool(RARE & set(s)))]
    codes = sorted({c for s in rare["sct"] for c, a in s if "MONDO:equivalentTo" in a})
    labels = lookup_labels(codes, cache / "sct_labels.json")
    df = review_table(terms, labels)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, sep="\t", index=False)
    print(f"{len(df):,} rare Mondo-SNOMED equivalences; {(df['score'] < 0.5).sum():,} "
          f"score < 0.5 (review these) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
