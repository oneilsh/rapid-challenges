"""Plots for a wearables-events report.

Reads the masked markdown report (`<run>_events-report.md`, or a filed copy under
results/), never the CDR: "<20" cells are drawn as hollow marks in a shaded band, never
as a value.

    python -m audits.wearables_events_plots REPORT.md [--out-dir DIR]

writes <run>_events-plot-{pooled,coverage,disease-persons,disease-rates}.png next to the
report (or in DIR).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

from audits.wearables_timing_plots import (AFTER, BEFORE, GRID, INK, INK2, MASK, SURFACE,
                                           THIRD, _fig, _style, _top_legend, md_tables,
                                           parse_count)

CLASSES = ("ed_or_inpatient", "related")
CLASS_LABEL = {"ed_or_inpatient": "any ED / inpatient episode", "ed": "ED",
               "inpatient": "inpatient", "related": "disease-related episode"}
# Person-count series on the per-disease plot: (column, label, color).
PERSON_SERIES = (("persons", "with an episode after dx", THIRD),
                 ("persons.1", "with a covered episode", BEFORE),
                 ("persons with ≥2", "with ≥2 covered episodes", AFTER))
BAND_X = 13.4


def read_report(text: str) -> dict:
    """Tables by role: pooled, coverage, disease[<class>], visit_types."""
    m = re.search(r"Covered = >= (\d+) Fitbit days", text)
    t = {"disease": {}, "min_cov": int(m.group(1)) if m else 14}
    for cap, df in md_tables(text):
        df = df.copy()
        df.columns = _dedupe(list(df.columns))
        c0 = df.columns[0]
        if c0 == "event class" and "events after dx" in df.columns:
            t["pooled"] = df
        elif c0 == "event class":
            t["coverage"] = df
        elif c0 == "Mondo" and cap.startswith("### "):
            t["disease"][cap[4:].strip()] = df
        elif c0 == "visit concept":
            t["visit_types"] = df
    return t


def _dedupe(cols: list) -> list:
    """Repeated headers ('persons' twice) as 'persons', 'persons.1', like pandas."""
    seen, out = {}, []
    for c in cols:
        out.append(c if c not in seen else f"{c}.{seen[c]}")
        seen[c] = seen.get(c, 0) + 1
    return out


def _dot(ax, v, y, color, *, marker="o", size=7):
    if v == MASK:
        ax.plot(BAND_X, y, marker, markerfacecolor="none", markeredgecolor=color,
                markersize=size, markeredgewidth=1.4)
    else:
        ax.plot(v, y, marker, color=color, markersize=size, markeredgecolor=SURFACE,
                markeredgewidth=1.5, zorder=3)


def _log_axis(ax, plt, n_rows):
    ax.axvspan(9, 20, color=GRID, alpha=0.6, linewidth=0)
    ax.text(BAND_X, -1.4, "<20\n(masked)", ha="center", va="bottom", fontsize=7, color=INK2)
    ax.set_xscale("log")
    ax.set_xlim(9, None)
    ax.set_ylim(-1.5, n_rows)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))


def plot_pooled(t: dict, plt):
    """All selected diseases, by episode class: episodes (left) and persons (right)."""
    p = t["pooled"]
    classes = list(p["event class"])
    fig = _fig(plt, 12, 0.6 * len(classes) + 2.0)
    axes = fig.subplots(1, 2, sharey=True)
    series = ((axes[0], (("events after dx", "all episodes after dx", INK2),
                         ("covered events", "covered episodes", BEFORE),
                         ("covered events before dx", "covered episodes before dx", THIRD)),
               "Episodes"),
              (axes[1], (("persons", "persons with an episode", INK2),
                         ("persons.1", "with a covered episode", BEFORE),
                         ("persons with ≥2", "with ≥2 covered", AFTER)),
               "Persons"))
    for ax, ser, title in series:
        _style(ax)
        for k, (col, label, color) in enumerate(ser):
            for r, v in enumerate(p[col].map(parse_count)):
                y = len(classes) - 1 - r + (1 - k) * 0.2
                _dot(ax, v, y, color)
            ax.plot([], [], "o", color=color, label=label)
        _log_axis(ax, plt, len(classes))
        ax.set_yticks(range(len(classes))[::-1], [CLASS_LABEL.get(c, c) for c in classes])
        ax.set_xlabel(f"{title.lower()} (log scale)", fontsize=9, color=INK2)
        _top_legend(ax, title, ncol=3)
    fig.suptitle("ED / inpatient episodes, all selected diseases (covered = enough Fitbit "
                 "data in the window before)", x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout()
    return fig


def plot_coverage(t: dict, plt):
    """Episodes after dx by Fitbit days in the lookback, one panel per class; bins at or
    above the report's coverage threshold (covered episodes) in blue."""
    c = t["coverage"]
    bins = list(c.columns[1:])
    fig = _fig(plt, 10, 4.0)
    axes = fig.subplots(1, len(c), squeeze=False).ravel()
    for ax, (_, r) in zip(axes, c.iterrows()):
        _style(ax)
        ax.grid(axis="x", visible=False)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        vals = [parse_count(v) for v in r[bins]]
        covered = [int(re.match(r"\d+", b).group()) >= t["min_cov"] for b in bins]
        top = max([v for v in vals if v != MASK] + [20])
        for i, v in enumerate(vals):
            if v == MASK:
                ax.bar(i, top * 0.02, width=0.7, color="none", hatch="////",
                       edgecolor=BEFORE if covered[i] else INK2)
                ax.text(i, top * 0.04, MASK, ha="center", va="bottom", fontsize=8, color=INK2)
            else:
                ax.bar(i, v, width=0.7, color=BEFORE if covered[i] else INK2,
                       edgecolor=SURFACE)
                ax.text(i, v, f"{int(v):,}", ha="center", va="bottom", fontsize=8, color=INK2)
        ax.set_xticks(range(len(bins)), bins)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_title(CLASS_LABEL.get(r["event class"], r["event class"]), fontsize=10,
                     color=INK, loc="left")
        ax.set_xlabel(f"Fitbit days in the window before the episode (blue = covered, "
                      f">= {t['min_cov']})", fontsize=9, color=INK2)
    axes[0].set_ylabel("episodes after dx", fontsize=9, color=INK2)
    fig.suptitle("How much Fitbit data precedes each episode", x=0.01, ha="left",
                 fontsize=12, color=INK)
    fig.tight_layout()
    return fig


def _shown_diseases(d: pd.DataFrame) -> pd.DataFrame:
    """Diseases with at least one colored (person) count >= 20 in this table."""
    cols = [c for c, _, _ in PERSON_SERIES]
    keep = d[cols].map(lambda v: parse_count(v) != MASK and parse_count(v) > 0).any(axis=1)
    return d[keep].reset_index(drop=True)


def plot_disease_persons(t: dict, plt):
    """Per disease, one panel per class: persons with data (gray tick), with an episode
    after dx, with a covered one, with >= 2 covered (log scale)."""
    base = _shown_diseases(t["disease"]["ed_or_inpatient"])
    names = list(base["disease"])
    fig = _fig(plt, 13, max(4.5, 0.5 * len(names) + 2.2))
    axes = fig.subplots(1, len(CLASSES), sharey=True)
    for ax, cls in zip(axes, CLASSES):
        d = t["disease"][cls].set_index("disease")
        _style(ax)
        for r, name in enumerate(names):
            row = d.loc[name]
            y = len(names) - 1 - r
            v = parse_count(row["with data"])
            ax.plot(BAND_X if v == MASK else v, y + 0.3, "|", color=INK2, markersize=9,
                    markeredgewidth=2)
            for k, (col, _, color) in enumerate(PERSON_SERIES):
                _dot(ax, parse_count(row[col]), y + 0.1 - k * 0.2, color)
        ax.plot([], [], "|", color=INK2, markersize=9, markeredgewidth=2,
                label="with Fitbit data")
        for _, label, color in PERSON_SERIES:
            ax.plot([], [], "o", color=color, label=label)
        ax.plot([], [], "o", markerfacecolor="none", markeredgecolor=INK2, label="hollow = <20")
        _log_axis(ax, plt, len(names))
        ax.set_yticks(range(len(names))[::-1], [n[:40] for n in names])
        ax.set_xlabel("persons (log scale)", fontsize=9, color=INK2)
        _top_legend(ax, CLASS_LABEL[cls], ncol=3)
    fig.suptitle("Persons with ED / inpatient episodes after the first diagnosis, by disease",
                 x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout()
    return fig


def plot_disease_rates(t: dict, plt):
    """Covered episodes per 1,000 Fitbit days after dx, per disease and class (shown only
    where the report gives a rate, i.e. >= 20 covered episodes)."""
    base = _shown_diseases(t["disease"]["ed_or_inpatient"])
    names = list(base["disease"])
    col = "covered per 1k wear-days"
    fig = _fig(plt, 9, max(4.0, 0.42 * len(names) + 2.0))
    ax = fig.add_subplot(1, 1, 1)
    _style(ax)
    for k, (cls, color) in enumerate(zip(CLASSES, (BEFORE, AFTER))):
        d = t["disease"][cls].set_index("disease")
        for r, name in enumerate(names):
            v = d.loc[name, col]
            if v not in ("—", ""):
                ax.plot(float(v), len(names) - 1 - r + (0.5 - k) * 0.3, "o", color=color,
                        markersize=7, markeredgecolor=SURFACE, markeredgewidth=1.5)
        ax.plot([], [], "o", color=color, label=CLASS_LABEL[cls])
    pooled = t["pooled"].set_index("event class")
    for cls, color in zip(CLASSES, (BEFORE, AFTER)):
        if cls in pooled.index and pooled.loc[cls, col] not in ("—", ""):
            ax.axvline(float(pooled.loc[cls, col]), color=color, linewidth=1, linestyle=":")
    ax.plot([], [], color=INK2, linestyle=":", label="all selected diseases")
    ax.set_yticks(range(len(names))[::-1], [n[:40] for n in names])
    ax.set_xlim(0, None)
    ax.set_xlabel("covered episodes per 1,000 Fitbit days after dx (missing = fewer than 20 "
                  "covered episodes)", fontsize=9, color=INK2)
    _top_legend(ax, "Episode rate while wearing a Fitbit, by disease", ncol=3)
    fig.tight_layout()
    return fig


PLOTS = {"pooled": plot_pooled, "coverage": plot_coverage,
         "disease-persons": plot_disease_persons, "disease-rates": plot_disease_rates}


def write_plots(report_text: str, out_dir: Path, prefix: str = "") -> list[Path]:
    """The PLOTS as `out_dir/<prefix><name>.png`."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = read_report(report_text)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, fn in PLOTS.items():
        fig = fn(t, plt)
        path = out_dir / f"{prefix}{name}.png"
        fig.savefig(path, dpi=150, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.2)
        plt.close(fig)
        written.append(path)
    return written


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("report")
    p.add_argument("--out-dir", default="", help="default: the report's folder")
    args = p.parse_args(argv)
    report = Path(args.report)
    out = Path(args.out_dir) if args.out_dir else report.parent
    stem = report.stem.removesuffix("_events-report")
    for path in write_plots(report.read_text(), out, prefix=f"{stem}_events-plot-"):
        print(f"[plots] wrote {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
