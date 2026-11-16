"""HEXAGON MAP of the autoimmune cohort (PARTICIPANT-LEVEL GEOGRAPHY: DO NOT EGRESS).

Counts persons per CHEL H3 hexagon (resolution 3) and draws them on a map of the
contiguous US: persons with a selected diagnosis, and those of them with Fitbit data.
Diseases are selected as in wearables_events (`--under`, `--flags`, `--exact`, ...).

A person's hexagon is their LATEST one in the CHEL location history (by `start_date`,
read as a date where it parses, else as text); entries that are not 15-digit H3 indexes
(a placeholder value in V9) are dropped. The link table is found as in wearables_chel
(`--chel-dataset`, default: the dataset whose name looks like CHEL).

Hexagon shapes come from the AMIA 2026 RWD workshop's GeoPackage (`h3_res3.gpkg`, 934 US
resolution-3 hexagons, keyed by h3_id), downloaded once into --geo-cache-dir. Needs
geopandas (in the Workbench image).

EGRESS: per-hexagon counts include small cells, so every output is named
`<run>_DO_NOT_EGRESS_chel-map*` and stays on the Workbench.
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

import pandas as pd

from audits import wearables_chel as ch
from audits.wearables_healthkit import _project_datasets, _wb_datasets
from audits.wearables_rare import _SOURCE_FLAGS, build_rare_map
from audits.wearables_timing import run_name, timing_ctes, typed_wear_sql, _TIMING_TABLES
from rapidaudit.aou import bq_client, query, workspace_env
from rapidaudit.egress import cell

GPKG_URL = ("https://raw.githubusercontent.com/rwdcollaborative/amia-2026-rwd-workshop/"
            "3c190c69cb4c3d4fac98a5b6bc698cc423712823/staging/data/h3_res3.gpkg")
CONUS = (-125, 24, -66, 50)   # lon / lat box for the map
BLUES = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def latest_hex_sql(link: dict, date_col: str | None) -> str:
    """(person_id, h): each person's latest valid H3 index from a direct link table."""
    h = ch._hex_expr("t", link["hex_col"], link["hex_type"])
    sd = (f", t.{date_col} AS sd" if date_col else ", CAST(NULL AS STRING) AS sd")
    order = ("COALESCE(SAFE_CAST(sd AS DATE), SAFE.PARSE_DATE('%m/%d/%Y', sd)) DESC NULLS "
             "LAST, sd DESC" if date_col else "h")
    return (f"SELECT person_id, ARRAY_AGG(h ORDER BY {order} LIMIT 1)[OFFSET(0)] AS h FROM ("
            f"SELECT SAFE_CAST(t.{link['person_col']} AS INT64) AS person_id, {h} AS h{sd} "
            f"FROM `{link['table']}` t) WHERE LENGTH(h) = 15 GROUP BY person_id")


# Persons per hexagon; ctes = timing_ctes(...) + `,\nlatest AS (...)`.
HEX_COUNTS_SELECT = """
SELECT l.h AS h3_id, COUNT(DISTINCT c.person_id) AS n_dx,
       COUNT(DISTINCT w.person_id) AS n_fitbit
FROM cohort c
JOIN latest l ON l.person_id = c.person_id
LEFT JOIN (SELECT DISTINCT person_id FROM wear_days) w ON w.person_id = c.person_id
GROUP BY l.h
"""


def fetch_gpkg(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / "h3_res3.gpkg"
    if not (dest.exists() and dest.stat().st_size > 0):
        print(f"[chel-map] downloading {GPKG_URL}", flush=True)
        urllib.request.urlretrieve(GPKG_URL, dest)  # noqa: S310 (pinned public file)
    return dest


def draw(counts: pd.DataFrame, gpkg: Path, png: Path, title: str) -> dict:
    """Two panels (persons with the dx / with Fitbit too) on a log scale; hexagons with
    nobody in grey. Returns how many persons fell outside the map / the shapes."""
    import geopandas as gpd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, LogNorm

    hexes = gpd.read_file(gpkg)
    df = hexes.merge(counts, on="h3_id", how="left").fillna({"n_dx": 0, "n_fitbit": 0})
    conus = df.cx[CONUS[0]:CONUS[2], CONUS[1]:CONUS[3]].to_crs(epsg=5070)
    cmap = LinearSegmentedColormap.from_list("blues", BLUES)
    fig, axes = plt.subplots(1, 2, figsize=(18, 6.5))
    for ax, col, label in zip(axes, ("n_dx", "n_fitbit"),
                              ("with a selected diagnosis", "... and Fitbit data")):
        conus[conus[col] == 0].plot(ax=ax, color="#ececea", edgecolor="white", linewidth=0.3)
        pop = conus[conus[col] > 0]
        if len(pop):
            pop.plot(ax=ax, column=col, cmap=cmap, edgecolor="white", linewidth=0.3,
                     norm=LogNorm(vmin=1, vmax=max(2, pop[col].max())), legend=True,
                     legend_kwds={"label": "persons per hexagon (log)", "shrink": 0.6})
        ax.set_title(f"Persons {label}: {int(conus[col].sum()):,} in "
                     f"{int((conus[col] > 0).sum()):,} hexagons")
        ax.set_axis_off()
    fig.suptitle(f"{title} — DO NOT EGRESS (small cells)")
    plt.tight_layout()
    fig.savefig(png, dpi=150)
    plt.close(fig)
    known = set(hexes["h3_id"])
    return {"persons_dx": int(counts["n_dx"].sum()),
            "persons_dx_on_map": int(conus["n_dx"].sum()),
            "persons_dx_no_shape": int(counts.loc[~counts["h3_id"].isin(known), "n_dx"].sum())}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out-dir", required=True)
    p.add_argument("--chel-dataset", default="")
    p.add_argument("--geo-cache-dir", default="data/geo")
    p.add_argument("--flags", default="rare")
    p.add_argument("--under", default="")
    p.add_argument("--exact", action="store_true")
    p.add_argument("--no-descendants", action="store_true")
    p.add_argument("--min-dx-dates", type=int, default=1)
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

    dsets = ([d.strip() for d in args.chel_dataset.split(",") if d.strip()]
             if args.chel_dataset else
             ch.chel_candidates(sorted(set(_wb_datasets() + _project_datasets(
                 client, cdr.split(".")[0]))), cdr))
    schema = pd.concat([ch._schema(client, d, False) for d in dsets], ignore_index=True)
    links = [k for k in ch.find_links(schema)[0] if k["kind"] == "direct"]
    if not links:
        raise SystemExit(f"[chel-map] no person + hexagon table in {dsets}")
    link = links[0]
    ds, tbl = link["table"].rsplit(".", 1)
    cols = set(schema.loc[(schema["dataset"] == ds) & (schema["table_name"] == tbl),
                          "column_name"])
    date_col = "start_date" if "start_date" in cols else None
    print(f"[chel-map] link {ch.link_name(link)}; latest by {date_col or '(none)'}",
          flush=True)

    fcols = query(client, f"""
SELECT table_name, column_name FROM `{cdr}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN UNNEST(@tables)""", {"tables": ("STRING", [t for t, _, _ in _TIMING_TABLES])})
    fb_sql, _ = typed_wear_sql(
        cdr, fcols.groupby("table_name")["column_name"].apply(set).to_dict(), intraday=False)
    roots = [x.strip() for x in args.under.split(",") if x.strip()]
    rm = build_rare_map(client, cdr, flags=flags, roots=roots, exact=args.exact,
                        mondo_version=args.mondo_version,
                        cache_dir=Path(args.mondo_cache_dir))
    ctes = (timing_ctes(cdr, fb_sql, descendants=not args.no_descendants)
            + f",\nlatest AS ({latest_hex_sql(link, date_col)})\n")
    params = {"mondo": ("STRING", rm.rmap["mondo_id"].tolist()),
              "cid": ("INT64", [int(x) for x in rm.rmap["standard_concept_id"]]),
              "min_dx_dates": ("INT64", int(args.min_dx_dates))}
    print("[chel-map] persons per hexagon…", flush=True)
    counts = query(client, ctes + HEX_COUNTS_SELECT, params)

    tag = args.tag or run_name(roots, rm.names, flags, exact=args.exact,
                               descendants=not args.no_descendants,
                               min_dx_dates=args.min_dx_dates)
    stem = out / f"{tag}_DO_NOT_EGRESS_chel-map"
    counts.sort_values("n_dx", ascending=False).to_csv(f"{stem}.tsv", sep="\t", index=False)
    scope = ", ".join(rm.names.get(r, r) for r in roots) or "all rare"
    info = draw(counts, fetch_gpkg(Path(args.geo_cache_dir)), Path(f"{stem}.png"),
                f"{scope}: latest CHEL hexagon (H3 res 3)")
    print("[chel-map] " + ", ".join(f"{k} {cell(v)}" for k, v in info.items()), flush=True)
    print(f"[chel-map] wrote {stem}.png and .tsv (Workbench only: small cells)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
