"""Plots for a wearables-timing report.

Reads the masked markdown report (`wearables_timing_<tag>.md`, or a filed copy under
results/), never the CDR, so the plots carry only what the report already publishes:
"<20" cells are drawn as hollow / hatched marks labeled "<20", never as a value.

    python -m audits.wearables_timing_plots REPORT.md --out-dir DIR

writes DIR/{pooled_bins,pooled_medians,disease_counts,disease_medians}.png.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import pandas as pd

# Reference palette (dataviz skill, light mode): slots 1-3 validate all-pairs.
BEFORE, AFTER, THIRD = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#fcfcfb"
MASK = "<20"


def parse_count(s: str):
    """'1,808' -> 1808.0; '<20' -> MASK; '0' -> 0.0."""
    s = str(s).strip()
    return MASK if s == MASK else float(s.replace(",", ""))


def parse_iqr(s: str):
    """'471 (180–1,052)' -> (471, 180, 1052); '—' -> None."""
    m = re.match(r"([\d,]+) \(([\d,]+)–([\d,]+)\)", str(s).strip())
    return tuple(float(g.replace(",", "")) for g in m.groups()) if m else None


def md_tables(text: str) -> list[tuple[str, pd.DataFrame]]:
    """Every markdown table in `text`, as (the nearest non-table line above it, frame of
    strings)."""
    out, caption, rows = [], "", []
    for line in text.splitlines() + [""]:
        if line.startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
            continue
        if rows:
            body = [r for r in rows[1:] if not set("".join(r)) <= set("-:")]
            out.append((caption, pd.DataFrame(body, columns=rows[0])))
            rows = []
        if line.strip():
            caption = line.strip()
    return out


def read_report(text: str) -> dict:
    """The report's tables by role: pooled, bins_before, bins_after, diseases, kinds."""
    t = {}
    for cap, df in md_tables(text):
        c0 = df.columns[0]
        if c0 == "kind" and "persons" in df.columns:
            t["pooled"] = df
        elif c0 == "kind":
            t["bins_before" if "before" in cap else "bins_after"] = df
        elif c0 == "Mondo":
            t["diseases"] = df
        elif c0 == "disease":
            t["kinds"] = df
    return t


def _style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _top_legend(ax, title, handles=None, labels=None, ncol=4):
    """Title, then the legend in one row between it and the plot (never over data)."""
    kw = {"handles": handles, "labels": labels} if handles else {}
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=ncol, frameon=False,
              fontsize=8, labelcolor=INK, borderaxespad=0.3, handletextpad=0.3, **kw)
    ax.set_title(title, fontsize=10, color=INK, loc="left", pad=8 + 14 * math.ceil(
        len(ax.get_legend().get_texts()) / ncol))


def _fig(plt, w, h):
    fig = plt.figure(figsize=(w, h), facecolor=SURFACE)
    return fig


def plot_pooled_bins(t: dict, plt):
    """Small multiples, one per kind: persons by days of data before (left) and after
    (right) the first diagnosis."""
    bb, ba = t["bins_before"], t["bins_after"]
    labs = list(bb.columns[1:])
    kinds = list(bb["kind"])
    vals = [[parse_count(v) for v in bb.iloc[i, 1:]] + [parse_count(v) for v in ba.iloc[i, 1:]]
            for i in range(len(kinds))]
    top = max([v for row in vals for v in row if v != MASK] + [20])
    ncol = 4
    nrow = math.ceil((len(kinds) + 1) / ncol)
    fig = _fig(plt, 3.3 * ncol, 2.6 * nrow)
    y = list(range(len(labs)))[::-1]
    for i, k in enumerate(kinds):
        ax = fig.add_subplot(nrow, ncol, i + 1)
        _style(ax)
        for side, sign, color, off in (("before", -1, BEFORE, 0), ("after", 1, AFTER, len(labs))):
            for j, yy in enumerate(y):
                v = vals[i][off + j]
                if v == MASK:
                    ax.barh(yy, sign * top * 0.04, height=0.7, color="none", edgecolor=color,
                            hatch="////", linewidth=0.8)
                    ax.text(sign * top * 0.06, yy, MASK, va="center",
                            ha="right" if sign < 0 else "left", fontsize=7, color=INK2)
                else:
                    ax.barh(yy, sign * v, height=0.7, color=color, edgecolor=SURFACE,
                            linewidth=1)
        ax.axvline(0, color=INK2, linewidth=0.8)
        ax.set_xlim(-top * 1.08, top * 1.08)
        ax.set_yticks(y, labs if i % ncol == 0 else [""] * len(labs))
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{abs(int(x)):,}"))
        ax.set_title(k, fontsize=10, color=INK, loc="left")
    ax = fig.add_subplot(nrow, ncol, len(kinds) + 1)
    ax.axis("off")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BEFORE),
                       plt.Rectangle((0, 0), 1, 1, color=AFTER)],
              labels=["days before first dx (left)", "days on/after first dx (right)"],
              loc="center left", frameon=False, fontsize=9, labelcolor=INK)
    fig.suptitle("Persons by days of Fitbit data, by kind (all selected diseases)",
                 x=0.01, ha="left", fontsize=12, color=INK)
    fig.supylabel("days of data (bin)", fontsize=9, color=INK2)
    fig.supxlabel("persons", fontsize=9, color=INK2)
    fig.tight_layout()
    return fig


def _range_rows(ax, labels, series, plt):
    """Dot (median) + line (p25-p75) per row for each (name, color, [iqr or None])."""
    n = len(series)
    for s, (name, color, iqrs) in enumerate(series):
        off = ((n - 1) / 2 - s) * 0.28
        for r, q in enumerate(iqrs):
            if q is None:
                continue
            yy = len(labels) - 1 - r + off
            ax.plot([q[1], q[2]], [yy, yy], color=color, linewidth=2, solid_capstyle="round")
            ax.plot(q[0], yy, "o", color=color, markersize=7, markeredgecolor=SURFACE,
                    markeredgewidth=1.5, label=name if r == 0 or all(
                        x is None for x in iqrs[:r]) else None)
    ax.set_yticks(range(len(labels))[::-1], labels)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))


def plot_pooled_medians(t: dict, plt):
    p = t["pooled"]
    kinds = list(p["kind"])
    fig = _fig(plt, 12, 0.5 * len(kinds) + 1.8)
    ax1, ax2 = fig.add_subplot(1, 2, 1), fig.add_subplot(1, 2, 2)
    for ax in (ax1, ax2):
        _style(ax)
    _range_rows(ax1, kinds, [("before first dx", BEFORE, [parse_iqr(v) for v in p["days before"]]),
                             ("on/after first dx", AFTER, [parse_iqr(v) for v in p["days after"]])], plt)
    _top_legend(ax1, "Days of data per person: median (p25–p75)")
    ax1.set_xlabel("distinct days with data", fontsize=9, color=INK2)
    _range_rows(ax2, [""] * len(kinds), [
        ("first wear day → first dx", BEFORE, [parse_iqr(v) for v in p["first wear → dx (days)"]]),
        ("first dx → last wear day", AFTER, [parse_iqr(v) for v in p["dx → last wear (days)"]])], plt)
    _top_legend(ax2, "Calendar span around the first dx: median (p25–p75)")
    ax2.set_xlabel("days", fontsize=9, color=INK2)
    fig.suptitle("Fitbit data around the first diagnosis, by kind (all selected diseases; "
                 "persons with ≥1 day on that side)", x=0.01, ha="left", fontsize=12,
                 color=INK)
    fig.tight_layout()
    return fig


def plot_disease_counts(t: dict, plt):
    """Per disease (log scale): persons with any data, with >= 1 day before the first dx,
    and with enough data in the window on both sides. Masked cells sit in a shaded
    '<20' band as hollow markers."""
    d = t["diseases"]
    both = next(c for c in d.columns if c == "both")
    series = [("with any Fitbit data", BEFORE, "with data"),
              ("≥1 day before first dx", AFTER, "≥1 day before"),
              ("≥30 days in the year before AND after", THIRD, both)]
    names = list(d["disease"])
    fig = _fig(plt, 9, 0.36 * len(names) + 1.8)
    ax = fig.add_subplot(1, 1, 1)
    _style(ax)
    ax.axvspan(9, 20, color=GRID, alpha=0.6, linewidth=0)
    ax.text(13.4, -1.5, "<20\n(masked)", ha="center", va="bottom", fontsize=7, color=INK2)
    for s, (label, color, col) in enumerate(series):
        off = (1 - s) * 0.22
        for r, v in enumerate(d[col].map(parse_count)):
            yy = len(names) - 1 - r + off
            if v == MASK:
                ax.plot(13.4, yy, "o", markerfacecolor="none", markeredgecolor=color,
                        markersize=7, markeredgewidth=1.5)
            else:
                ax.plot(v, yy, "o", color=color, markersize=7, markeredgecolor=SURFACE,
                        markeredgewidth=1.5, label=label if r == 0 else None)
    ax.set_xscale("log")
    ax.set_xlim(9, None)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_yticks(range(len(names))[::-1], [n[:40] for n in names])
    ax.set_xlabel("persons (log scale)", fontsize=9, color=INK2)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(plt.Line2D([], [], marker="o", linestyle="none", markerfacecolor="none",
                              markeredgecolor=INK2, markersize=7, markeredgewidth=1.5))
    labels.append("hollow = <20 (masked)")
    _top_legend(ax, "Persons with Fitbit data around the first diagnosis, by disease",
                handles, labels, ncol=2)
    ax.set_ylim(-1.6, len(names))
    fig.tight_layout()
    return fig


def plot_disease_medians(t: dict, plt):
    d = t["diseases"]
    names = [n[:40] for n in d["disease"]]
    fig = _fig(plt, 9, 0.36 * len(names) + 1.8)
    ax = fig.add_subplot(1, 1, 1)
    _style(ax)
    _range_rows(ax, names, [("before first dx", BEFORE, [parse_iqr(v) for v in d["days before"]]),
                            ("on/after first dx", AFTER, [parse_iqr(v) for v in d["days after"]])], plt)
    ax.set_xlabel("distinct days with any Fitbit data (no range = fewer than 20 persons on "
                  "that side)", fontsize=9, color=INK2)
    _top_legend(ax, "Days of data per person, by disease: median (p25–p75)")
    fig.tight_layout()
    return fig


# --- participant-level (Workbench only) ------------------------------------------------
# Everything below draws one point per person from the PER_PERSON_SELECT rows. The output
# is participant-level: it must stay on the Workbench (written under a DO_NOT_EGRESS
# folder, which .gitignore blocks) and is never part of a report.
NO_EGRESS = "PARTICIPANT-LEVEL: do not egress"
PATIENT_PLOTS = {
    # name: (x column, y column, x label, y label, title, transform)
    "patients_days": ("days_before", "days_after", "days of data before first dx",
                      "days of data on/after first dx",
                      "Days of Fitbit data before vs after the first diagnosis", None),
    "patients_span": ("lead_days", "follow_days", "first wear day (years relative to first dx)",
                      "last wear day (years relative to first dx)",
                      "When each person's Fitbit data starts and ends, relative to the "
                      "first diagnosis", "span"),
}


def facet_order(per: pd.DataFrame, kind: str, max_facets: int, all_id: str) -> list:
    """ALL first, then diseases by persons with this kind of data, largest first."""
    n = per[per["src"] == kind].groupby("mondo_id").size().sort_values(ascending=False)
    rest = [m for m in n.index if m != all_id]
    return ([all_id] if all_id in n.index else []) + rest[:max_facets]


def plot_patient_facets(per: pd.DataFrame, names: dict, plt, *, x, y, xlabel, ylabel,
                        title, transform=None, kind="any", max_facets=20,
                        all_id="ALL", min_window_days=30):
    """Faceted dot plot, one facet per disease, one point per person (kind `kind`).
    Day counts go on symmetric-log axes (0 and thousands both readable); the "span"
    transform plots first / last wear day in years relative to the dx, linear."""
    order = facet_order(per, kind, max_facets, all_id)
    d = per[per["src"] == kind]
    ncol = 5
    nrow = max(1, math.ceil(len(order) / ncol))
    fig = plt.figure(figsize=(3.0 * ncol, 2.8 * nrow + 0.8), facecolor=SURFACE)
    axes = fig.subplots(nrow, ncol, sharex=True, sharey=True, squeeze=False).ravel()
    for ax in axes[len(order):]:
        ax.axis("off")
    for ax, m in zip(axes, order):
        g = d[d["mondo_id"] == m]
        xs, ys = g[x].astype(float), g[y].astype(float)
        if transform == "span":           # years relative to dx (negative = before)
            xs, ys = -xs / 365.25, ys / 365.25
        _style(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.axvline(0, color=MUTED, linewidth=0.8)
        ax.axhline(0, color=MUTED, linewidth=0.8)
        if transform is None:
            ax.axvline(min_window_days, color=MUTED, linewidth=0.8, linestyle=":")
            ax.axhline(min_window_days, color=MUTED, linewidth=0.8, linestyle=":")
        ax.scatter(xs, ys, s=9, color=BEFORE, alpha=0.45, linewidths=0)
        if transform is None:
            ax.set_xscale("symlog", linthresh=30)
            ax.set_yscale("symlog", linthresh=30)
        label = "all selected diseases" if m == all_id else names.get(m, m)
        ax.set_title(f"{str(label)[:34]} (n={len(g):,})", fontsize=8.5, color=INK, loc="left")
    if transform is None:
        fmt = plt.FuncFormatter(lambda v, _: f"{int(v):,}")
        axes[0].xaxis.set_major_formatter(fmt)
        axes[0].yaxis.set_major_formatter(fmt)
    fig.supxlabel(xlabel, fontsize=9, color=INK2)
    fig.supylabel(ylabel, fontsize=9, color=INK2)
    fig.suptitle(f"{title}; one point per person, kind = {kind}  ·  {NO_EGRESS}",
                 x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout()
    return fig


def write_patient_plots(per: pd.DataFrame, names: dict, out_dir: Path, *, kinds=("any",),
                        max_facets=20, all_id="ALL", min_window_days=30) -> list[Path]:
    """Participant-level PNGs into `out_dir`, which must be named *DO_NOT_EGRESS*."""
    if "DO_NOT_EGRESS" not in out_dir.name:
        raise ValueError(f"participant-level plots need a DO_NOT_EGRESS folder, got {out_dir}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for kind in kinds:
        for name, (x, y, xl, yl, title, tr) in PATIENT_PLOTS.items():
            fig = plot_patient_facets(per, names, plt, x=x, y=y, xlabel=xl, ylabel=yl,
                                      title=title, transform=tr, kind=kind,
                                      max_facets=max_facets, all_id=all_id,
                                      min_window_days=min_window_days)
            path = out_dir / f"{name}_{kind}.png"
            fig.savefig(path, dpi=150, facecolor=SURFACE, bbox_inches="tight",
                        pad_inches=0.2)
            plt.close(fig)
            written.append(path)
    return written


PLOTS = {"pooled_bins": plot_pooled_bins, "pooled_medians": plot_pooled_medians,
         "disease_counts": plot_disease_counts, "disease_medians": plot_disease_medians}


def write_plots(report_text: str, out_dir: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = read_report(report_text)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, fn in PLOTS.items():
        fig = fn(t, plt)
        path = out_dir / f"{name}.png"
        fig.savefig(path, dpi=150, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.2)
        plt.close(fig)
        written.append(path)
    return written


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("report")
    p.add_argument("--out-dir", default="",
                   help="default: the report path without .md")
    args = p.parse_args(argv)
    report = Path(args.report)
    out = Path(args.out_dir) if args.out_dir else report.with_suffix("")
    for path in write_plots(report.read_text(), out):
        print(f"[plots] wrote {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
