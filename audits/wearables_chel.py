"""CHEL HEXAGONS for the Fitbit cohort (RAPID TA1 wearables tab).

"How many persons with Fitbit data and a rare autoimmune diagnosis can be placed in an H3
hexagon, and so linked to the CHEL environmental / social indicators?"

V9 adds CHEL data; how it is laid out was not known when this was written. The CHEL
indicators come on an H3 hexagon grid (the AMIA 2026 workshop, rwdcollaborative/
amia-2026-rwd-workshop, used resolution 3 with one hexagon per county). The audit finds
the layout:

  DATASETS  --chel-dataset a.b[,c.d], else datasets in `wb resource list` and in the CDR's
            project whose name matches chel / h3 / hex / environ / exposure / geo /
            climate, plus the CDR's own person and location tables and any CDR table
            with a hexagon-like column (h3 / hex).
  LINKS     how a person reaches a hexagon: DIRECT, a table with a person column and a
            hexagon column; or LOCATION, a table with a person column and location_id,
            joined to a table holding location_id and a hexagon column (the CDR's
            person -> location is one). Every link found is reported on its own.
  INDICATOR tables: a hexagon column, no person column and no location_id.

Report, per link (no hexagon id is ever printed):
  all participants: persons with a hexagon, hexagons, persons with > 1 hexagon, persons
    by H3 resolution (the 2nd hex digit of the index)
  the cohort (same disease selection as wearables_events): persons with the dx / with
    Fitbit / with Fitbit and a hexagon, pooled and by disease; how spread out the
    Fitbit-and-hexagon persons are (hexagons, hexagons with >= 20 of them, persons in
    those); per indicator table, persons whose hexagon appears in it
  covered ED / inpatient episodes after the first dx (wearables_events rules) with and
    without a hexagon (--min-cov Fitbit days in the --lookback days before)

EGRESS: every participant count goes through `cell`, and nested cells are suppressed
together (`nested_cells`): persons with Fitbit (published in the events reports) split
into with and without a hexagon, so where one part is 1..19 the other shows "—".
Hexagon counts are counts of places, but hexagons are only described in aggregate.

OUTPUT: `<out-dir>/<CDR dataset>/<run>_chel-report.md`, `_chel-schema.tsv`,
`_chel-run.json`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

from audits.wearables_events import (CLASSES, EVENTS_SELECT, event_class_mask,
                                     events_ctes)
from audits.wearables_healthkit import (SUPPRESSED, USD_PER_TB, _project_datasets, _t,
                                        _wb_datasets, nested_cells)
from audits.wearables_rare import _SOURCE_FLAGS, build_rare_map
from audits.wearables_timing import (ALL, run_name, timing_ctes, typed_wear_sql,
                                     _TIMING_TABLES)
from rapidaudit.aou import bq_client, dry_run_bytes, query, workspace_env
from rapidaudit.egress import EGRESS_FLOOR, cell

DATASET_NAME = re.compile(r"chel|h3|hex|environ|exposure|geo|climate", re.I)
HEX_COL = re.compile(r"(^|_)(h3|hex)", re.I)
PERSON_COL = re.compile(r"^person_id$|participant", re.I)
SHOW = SUPPRESSED  # re-exported for tests


# ---------------------------------------------------------------- discovery (pure)

def chel_candidates(datasets: list[str], cdr: str) -> list[str]:
    seen, out = set(), []
    for d in datasets:
        if d != cdr and d not in seen and DATASET_NAME.search(d.split(".")[-1]):
            seen.add(d)
            out.append(d)
    return out


def _person_col(cols: dict) -> str | None:
    return "person_id" if "person_id" in cols else next(
        (c for c in cols if PERSON_COL.search(c)), None)


def _hex_col(cols: dict) -> str | None:
    hx = [c for c, t in cols.items() if HEX_COL.search(c) and t in ("STRING", "INT64")]
    return (next((c for c in hx if c.lower() in ("h3_id", "h3", "h3_index", "hex_id")), None)
            or (hx[0] if hx else None))


def find_links(schema: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    """(links, indicator tables) from a schema with dataset, table_name, column_name,
    data_type. A link: kind, table, person_col, hex_col (+ loc_table for kind
    'location'). Tables are '<dataset>.<table>'."""
    tabs = {}
    for (ds, t), g in schema.groupby(["dataset", "table_name"], sort=True):
        tabs[f"{ds}.{t}"] = dict(zip(g["column_name"], g["data_type"].str.upper()))
    hex_locs = [(t, _hex_col(c)) for t, c in tabs.items()
                if "location_id" in c and _hex_col(c) and not _person_col(c)]
    links, indicators = [], []
    for t, c in tabs.items():
        pc, hc = _person_col(c), _hex_col(c)
        if pc and hc:
            links.append({"kind": "direct", "table": t, "person_col": pc, "hex_col": hc,
                          "hex_type": c[hc]})
        elif pc and "location_id" in c:
            for lt, lh in hex_locs:
                links.append({"kind": "location", "table": t, "person_col": pc,
                              "loc_table": lt, "hex_col": lh, "hex_type": tabs[lt][lh]})
        elif hc and not pc and "location_id" not in c:
            indicators.append({"table": t, "hex_col": hc, "hex_type": c[hc],
                               "n_cols": len(c)})
    return links, indicators


def _hex_expr(alias: str, col: str, typ: str) -> str:
    return (f"LOWER(FORMAT('%x', {alias}.{col}))" if str(typ).upper() == "INT64"
            else f"LOWER(TRIM({alias}.{col}))")


def link_sql(link: dict) -> str:
    """(person_id, h) rows for a link, h = lowercase hex H3 index, NULLs dropped."""
    h = _hex_expr("l" if link["kind"] == "location" else "t", link["hex_col"],
                  link["hex_type"])
    src = (f"`{link['table']}` t JOIN `{link['loc_table']}` l "
           "ON l.location_id = t.location_id" if link["kind"] == "location"
           else f"`{link['table']}` t")
    return (f"SELECT DISTINCT SAFE_CAST(t.{link['person_col']} AS INT64) AS person_id, "
            f"{h} AS h FROM {src} WHERE {h} IS NOT NULL AND {h} != ''")


def link_name(link: dict) -> str:
    return (f"{link['table']} → {link['loc_table']}.{link['hex_col']}"
            if link["kind"] == "location" else f"{link['table']}.{link['hex_col']}")


# ---------------------------------------------------------------- queries

# All participants for one link; format with link (the ph rows).
LINK_ALL_SELECT = """
WITH ph AS ({link})
SELECT COUNT(DISTINCT person_id) AS n_persons, COUNT(DISTINCT h) AS n_hex,
       (SELECT COUNT(*) FROM (SELECT person_id FROM ph GROUP BY person_id
                              HAVING COUNT(DISTINCT h) > 1)) AS n_multi
FROM ph
"""

LINK_RES_SELECT = """
WITH ph AS ({link})
SELECT SUBSTR(h, 2, 1) AS res_digit, COUNT(DISTINCT person_id) AS n_persons,
       COUNT(DISTINCT h) AS n_hex
FROM ph WHERE LENGTH(h) = 15 GROUP BY 1
UNION ALL
SELECT 'not a 15-digit H3 index', COUNT(DISTINCT person_id), COUNT(DISTINCT h)
FROM ph WHERE LENGTH(h) != 15
"""

# Cohort per disease; ctes end with `ph` (appended by cohort_ctes).
COHORT_HEX_SELECT = """
SELECT x.mondo_id, COUNT(*) AS n_dx,
       COUNTIF(w.person_id IS NOT NULL) AS n_wear,
       COUNTIF(w.person_id IS NOT NULL AND hx.person_id IS NOT NULL) AS n_wear_hex,
       COUNTIF(hx.person_id IS NOT NULL) AS n_dx_hex
FROM dx_all x
LEFT JOIN wp w ON w.person_id = x.person_id
LEFT JOIN (SELECT DISTINCT person_id FROM ph) hx ON hx.person_id = x.person_id
GROUP BY x.mondo_id
"""

# Spread of the pooled Fitbit-and-hexagon cohort over hexagons. Param @floor INT64.
SPREAD_SELECT = """
SELECT COUNT(*) AS n_hex, COUNTIF(n >= @floor) AS n_hex_floor,
       IFNULL(SUM(IF(n >= @floor, n, 0)), 0) AS n_in_floor_hex,
       (SELECT COUNT(*) FROM (SELECT ph.person_id FROM ph JOIN wp USING (person_id)
         JOIN (SELECT DISTINCT person_id FROM dx_all) d USING (person_id)
         GROUP BY ph.person_id HAVING COUNT(DISTINCT ph.h) > 1)) AS n_multi
FROM (SELECT ph.h, COUNT(DISTINCT ph.person_id) AS n FROM ph
      JOIN wp USING (person_id) JOIN (SELECT DISTINCT person_id FROM dx_all) d
      USING (person_id) GROUP BY ph.h)
"""

# Pooled Fitbit-and-hexagon cohort persons whose hexagon is in an indicator table;
# format with table, hex expression.
INDICATOR_SELECT = """
SELECT COUNT(DISTINCT ph.person_id) AS n_persons
FROM ph JOIN wp USING (person_id) JOIN (SELECT DISTINCT person_id FROM dx_all) d
  USING (person_id)
JOIN (SELECT DISTINCT {hexpr} AS h FROM `{table}` i) ind ON ind.h = ph.h
"""

# EVENTS_SELECT plus whether the person has a hexagon.
HEX_EVENTS_SELECT = EVENTS_SELECT.replace(
    "e.site, COUNT(w.d) AS cov_days",
    "e.site, COUNT(w.d) AS cov_days, hx.person_id IS NOT NULL AS has_hex", 1).replace(
    "JOIN pids p ON p.person_id = e.person_id",
    "JOIN pids p ON p.person_id = e.person_id\n"
    "LEFT JOIN (SELECT DISTINCT person_id FROM ph) hx ON hx.person_id = e.person_id", 1
).replace("e.is_ed, e.is_ip, e.site\n", "e.is_ed, e.is_ip, e.site, hx.person_id\n", 1)


def cohort_ctes(base: str, link: dict) -> str:
    return base + f",\nph AS ({link_sql(link)})\n"


# ---------------------------------------------------------------- summaries

COHORT_KEYS = ("n_dx", "n_wear", "n_wear_hex", "n_dx_hex", "x_wear_nohex", "x_dx_nohex")
COHORT_GROUPS = (("n_wear", ("n_wear_hex", "x_wear_nohex")),
                 ("n_dx", ("n_dx_hex", "x_dx_nohex")))
EV_KEYS = ("cov", "cov_p", "cov_hex", "cov_hex_p", "x_cov_nohex", "x_cov_nohex_p")
EV_GROUPS = (("cov", ("cov_hex", "x_cov_nohex")), ("cov_p", ("cov_hex_p", "x_cov_nohex_p")))


def cohort_rows(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["x_wear_nohex"] = d["n_wear"] - d["n_wear_hex"]
    d["x_dx_nohex"] = d["n_dx"] - d["n_dx_hex"]
    order = [ALL] + sorted((m for m in d["mondo_id"] if m != ALL),
                           key=lambda m: -int(d.loc[d["mondo_id"] == m, "n_wear"].iloc[0]))
    return d.set_index("mondo_id").loc[order].reset_index()


def events_hex(ev: pd.DataFrame, *, min_cov: int) -> pd.DataFrame:
    """Covered episodes after the first dx, pooled (ALL) by class, with / without a
    hexagon (persons too)."""
    rows = []
    for cls in CLASSES:
        e = ev[(ev["mondo_id"] == ALL) & (ev["rel_day"] > 0) & (ev["cov_days"] >= min_cov)]
        e = e[event_class_mask(e, cls)]
        hx = e["has_hex"].astype(bool)
        rows.append({"event_class": cls, "cov": len(e), "cov_p": e["pid"].nunique(),
                     "cov_hex": int(hx.sum()), "cov_hex_p": e.loc[hx, "pid"].nunique(),
                     "x_cov_nohex": int((~hx).sum()),
                     "x_cov_nohex_p": len(set(e["pid"]) - set(e.loc[hx, "pid"]))})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- report

def format_report(meta, schema, links, indicators, per_link, names,
                  floor: int = EGRESS_FLOOR) -> str:
    c = lambda n: cell(n, floor)  # noqa: E731
    L = [f"# CHEL hexagons for the Fitbit cohort — {meta['run']}", "",
         f"CDR `{meta['cdr']}` · datasets searched: "
         + (", ".join(f"`{d}`" for d in meta["datasets"]) or "none besides the CDR")
         + f" · BigQuery estimate {meta['est_tb']:.3f} TB", "",
         "Counts are participants unless they say hexagons; 1-19 show as <20, and — hides "
         "a cell whose nested partner is <20. No hexagon id is printed.", "",
         "## 1. Links and indicator tables", ""]
    L += _t(["link", "kind"], [(link_name(k), k["kind"]) for k in links]) if links else \
        ["No table links a person to a hexagon."]
    L += [""]
    L += (_t(["indicator table", "hexagon column", "columns"],
             [(i["table"], i["hex_col"], i["n_cols"]) for i in indicators])
          if indicators else ["No hexagon-keyed indicator table found."])
    L += ["", "<details><summary>Columns searched</summary>", ""]
    L += _t(["dataset", "table", "column", "type"],
            [(r.dataset, r.table_name, r.column_name, r.data_type)
             for r in schema.itertuples()])
    L += ["", "</details>"]
    for k, res in zip(links, per_link):
        a = res["all"].iloc[0]
        L += ["", f"## 2. {link_name(k)}", "",
              f"All participants: {c(a.n_persons)} with a hexagon, in {int(a.n_hex):,} "
              f"hexagons; {c(a.n_multi)} with more than one.", "",
              "By H3 resolution (2nd digit of the index):", ""]
        L += _t(["resolution", "persons", "hexagons"],
                [(f"{int(r.res_digit, 16)}" if re.fullmatch(r"[0-9a-f]", str(r.res_digit))
                  else r.res_digit, c(r.n_persons), f"{int(r.n_hex):,}")
                 for r in res["res"].itertuples() if int(r.n_persons) or int(r.n_hex)])
        co = res["cohort"]
        a = co.iloc[0]
        x = nested_cells({kk: int(a[kk]) for kk in COHORT_KEYS}, COHORT_GROUPS, floor)
        s = res["spread"].iloc[0]
        L += ["", f"Cohort ({meta['scope']}): {x['n_dx']} with a selected diagnosis "
              f"({x['n_dx_hex']} with a hexagon) · {x['n_wear']} with Fitbit · "
              f"**{x['n_wear_hex']} with Fitbit and a hexagon**", "",
              f"Those Fitbit-and-hexagon persons sit in {int(s.n_hex):,} hexagons; "
              f"{int(s.n_hex_floor):,} hexagons hold >= {floor} of them "
              f"({c(s.n_in_floor_hex)} persons); {c(s.n_multi)} have more than one "
              "hexagon.", ""]
        if res["indicators"]:
            L += _t(["indicator table", "Fitbit-and-hexagon persons whose hexagon is in it"],
                    [(t, c(n)) for t, n in res["indicators"].items()])
            L += [""]
        L += [f"By disease (persons with Fitbit >= {floor}):", ""]
        drows = []
        for r in co[(co["mondo_id"] != ALL) & (co["n_wear"] >= floor)].itertuples():
            y = nested_cells({kk: int(getattr(r, kk)) for kk in COHORT_KEYS},
                             COHORT_GROUPS, floor)
            drows.append((r.mondo_id, names.get(r.mondo_id, ""), y["n_dx"], y["n_dx_hex"],
                          y["n_wear"], y["n_wear_hex"]))
        L += _t(["Mondo", "disease", "dx", "dx + hexagon", "Fitbit", "Fitbit + hexagon"],
                drows)
        L += ["", f"Covered episodes after dx (>= {meta['min_cov']} Fitbit days in the "
              f"{meta['lookback']} before; pooled). Cells: episodes (persons).", ""]
        erows = []
        for r in res["events"].itertuples():
            y = nested_cells({kk: int(getattr(r, kk)) for kk in EV_KEYS}, EV_GROUPS, floor)
            erows.append((r.event_class, f"{y['cov']} ({y['cov_p']})",
                          f"{y['cov_hex']} ({y['cov_hex_p']})"))
        L += _t(["class", "covered", "of those, person has a hexagon"], erows)
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- main

def _schema(client, ds: str, cdr: bool) -> pd.DataFrame:
    where = ("WHERE table_name IN ('person', 'location') OR REGEXP_CONTAINS("
             "LOWER(column_name), r'(^|_)(h3|hex)') OR REGEXP_CONTAINS(LOWER(table_name), "
             "r'chel|h3|hex|location')" if cdr else "")
    try:
        s = query(client, f"SELECT table_name, column_name, data_type FROM "
                          f"`{ds}.INFORMATION_SCHEMA.COLUMNS` {where} "
                          "ORDER BY table_name, ordinal_position", {})
    except Exception as e:  # noqa: BLE001 (not readable from this workspace)
        print(f"[chel] schema of {ds}: {e}", flush=True)
        return pd.DataFrame(columns=["dataset", "table_name", "column_name", "data_type"])
    s.insert(0, "dataset", ds)
    return s


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out-dir", required=True)
    p.add_argument("--chel-dataset", default="", help="comma list of <project>.<dataset>")
    p.add_argument("--max-tb", type=float, default=1.0)
    p.add_argument("--flags", default="rare")
    p.add_argument("--under", default="")
    p.add_argument("--exact", action="store_true")
    p.add_argument("--no-descendants", action="store_true")
    p.add_argument("--min-dx-dates", type=int, default=1)
    p.add_argument("--lookback", type=int, default=30)
    p.add_argument("--min-cov", type=int, default=14)
    p.add_argument("--washout", type=int, default=7)
    p.add_argument("--ip-overnight", action="store_true")
    p.add_argument("--mondo-version", default="2026-06-02")
    p.add_argument("--mondo-cache-dir", default="data/mondo")
    p.add_argument("--tag", default="")
    args = p.parse_args(argv)
    cdr, billing = workspace_env()
    flags = [f.strip() for f in args.flags.split(",") if f.strip()]
    bad = [f for f in flags if f not in _SOURCE_FLAGS]
    if bad:
        raise SystemExit(f"unknown --flags {bad}; known: {_SOURCE_FLAGS}")
    out = Path(args.out_dir) / cdr.split(".")[-1]
    out.mkdir(parents=True, exist_ok=True)
    client = bq_client(billing)

    if args.chel_dataset:
        dsets = [d.strip() for d in args.chel_dataset.split(",") if d.strip()]
    else:
        seen = sorted(set(_wb_datasets() + _project_datasets(client, cdr.split(".")[0])))
        print(f"[chel] datasets seen: {seen or 'none'}", flush=True)
        dsets = chel_candidates(seen, cdr)
    print(f"[chel] searching {dsets} and the CDR", flush=True)
    schema = pd.concat([_schema(client, cdr, True)] + [_schema(client, d, False)
                                                       for d in dsets], ignore_index=True)
    links, indicators = find_links(schema)
    for k in links:
        print(f"[chel] link: {link_name(k)}", flush=True)
    for i in indicators:
        print(f"[chel] indicator table: {i['table']} ({i['hex_col']})", flush=True)
    tag = args.tag or None
    if not links:
        schema.to_csv(out / "chel-schema.tsv", sep="\t", index=False)
        print(schema.to_string(index=False), flush=True)
        raise SystemExit("[chel] no table links a person to a hexagon; the columns searched "
                         f"are above and in {out}/chel-schema.tsv. Rerun with "
                         "CHEL=<project>.<dataset> if the CHEL dataset wasn't found.")

    fcols = query(client, f"""
SELECT table_name, column_name FROM `{cdr}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN UNNEST(@tables)""", {"tables": ("STRING", [t for t, _, _ in _TIMING_TABLES])})
    fb_sql, fb_found = typed_wear_sql(
        cdr, fcols.groupby("table_name")["column_name"].apply(set).to_dict(), intraday=False)
    roots = [x.strip() for x in args.under.split(",") if x.strip()]
    rm = build_rare_map(client, cdr, flags=flags, roots=roots, exact=args.exact,
                        mondo_version=args.mondo_version,
                        cache_dir=Path(args.mondo_cache_dir))
    rmap, names = rm.rmap, rm.names
    base = (timing_ctes(cdr, fb_sql, descendants=not args.no_descendants)
            + events_ctes(None).replace("{cdr}", cdr).rstrip())
    params = {"mondo": ("STRING", rmap["mondo_id"].tolist()),
              "cid": ("INT64", [int(x) for x in rmap["standard_concept_id"]]),
              "min_dx_dates": ("INT64", int(args.min_dx_dates)),
              "washout": ("INT64", int(args.washout)),
              "ip_overnight": ("BOOL", bool(args.ip_overnight))}

    plan = []
    for k in links:
        ctes = cohort_ctes(base, k)
        q = {"all": (LINK_ALL_SELECT.format(link=link_sql(k)), {}),
             "res": (LINK_RES_SELECT.format(link=link_sql(k)), {}),
             "cohort": (ctes + COHORT_HEX_SELECT, params),
             "spread": (ctes + SPREAD_SELECT, {**params, "floor": ("INT64", EGRESS_FLOOR)}),
             "events": (ctes + HEX_EVENTS_SELECT,
                        {**params, "lookback": ("INT64", int(args.lookback))})}
        for i in indicators:
            q[f"ind:{i['table']}"] = (ctes + INDICATOR_SELECT.format(
                table=i["table"], hexpr=_hex_expr("i", i["hex_col"], i["hex_type"])), params)
        plan.append(q)
    est = sum(dry_run_bytes(client, s, prm) for q in plan for s, prm in q.values())
    tb = est / 1e12
    print(f"[chel] dry run total {tb:.3f} TB (~${tb * USD_PER_TB:.2f})", flush=True)
    if tb > args.max_tb:
        raise SystemExit(f"[chel] estimate {tb:.2f} TB is over --max-tb {args.max_tb:g}")

    per_link = []
    for k, q in zip(links, plan):
        print(f"[chel] {link_name(k)} queries…", flush=True)
        r = {kk: query(client, s, prm) for kk, (s, prm) in q.items()}
        per_link.append({
            "all": r["all"], "res": r["res"], "spread": r["spread"],
            "cohort": cohort_rows(r["cohort"]),
            "events": events_hex(r["events"], min_cov=args.min_cov),
            "indicators": {kk[4:]: int(v.iloc[0]["n_persons"]) for kk, v in r.items()
                           if kk.startswith("ind:")}})

    tag = tag or run_name(roots, names, flags, exact=args.exact,
                          descendants=not args.no_descendants,
                          min_dx_dates=args.min_dx_dates)
    meta = {"run": tag, "cdr": cdr, "datasets": dsets, "links": links,
            "indicators": indicators, "fitbit_tables": fb_found, "est_tb": tb,
            "flags": flags, "under": roots, "exact": args.exact,
            "scope": ", ".join(names.get(r, r) for r in roots) or "all rare",
            "lookback": args.lookback, "min_cov": args.min_cov, "washout": args.washout,
            "ip_overnight": bool(args.ip_overnight)}
    text = format_report(meta, schema, links, indicators, per_link, names)
    (out / f"{tag}_chel-report.md").write_text(text)
    schema.to_csv(out / f"{tag}_chel-schema.tsv", sep="\t", index=False)
    (out / f"{tag}_chel-run.json").write_text(json.dumps(meta, indent=1, default=str))
    print(text, flush=True)
    print(f"[chel] wrote {out}/{tag}_chel-report.md", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
