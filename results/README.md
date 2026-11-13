# Results

Masked audit outputs copied back from the All of Us Workbench, one folder per audit and
one file per run (`YYYY-MM-DD-<short-name>.md`, plus the matching `.tsv` files if wanted).

**Only egress-safe files belong here:** every participant count is 0, ≥ 20 or `<20`
(see `rapidaudit/egress.py`). Never put raw or participant-level outputs here.

Each file starts with a header recording the run: the date, the `make` command, the repo
commit and the Mondo release. The rest is the run's output, unedited.

## Index

### wearables-rare

| file | scope | headline (rare dx with ≥ 30 Fitbit days) |
|---|---|--:|
| [2026-10-20-all-rare-default.md](wearables-rare/2026-10-20-all-rare-default.md) | all Mondo `rare` (incl. inferred), full mondo2omop mapping | 23,471 (inflated by junk mappings) |
| [2026-10-20-autoimmune-exact.md](wearables-rare/2026-10-20-autoimmune-exact.md) | rare autoimmune (MONDO:0007179), exact SNOMED mapping | 1,707 |
| [2026-10-20-all-rare-exact.md](wearables-rare/2026-10-20-all-rare-exact.md) | all Mondo `rare` (incl. inferred), exact SNOMED mapping | 17,869 (still inflated: common conditions tagged rare) |
| [2026-10-21-all-rare-exact-dx2.md](wearables-rare/2026-10-21-all-rare-exact-dx2.md) | as above, dx on ≥ 2 dates; adds CDR id and coverage breakdown | 12,469 (top 10 nodes = 55% of rare dx) |

### wearables-timing

| file | scope | headline |
|---|---|--:|
| [2026-11-02-autoimmune-exact.md](wearables-timing/2026-11-02-autoimmune-exact.md) (plots: `2026-11-02-autoimmune-exact_plot-*.png`) | rare autoimmune (MONDO:0007179), exact SNOMED mapping; Fitbit days by kind before / after first dx | 306 with ≥ 30 days in the year before and after (482 with any pre-dx day) |

### wearables-events

| file | scope | headline |
|---|---|--:|
| [2026-11-02-cardio-exact.md](wearables-events/2026-11-02-cardio-exact.md) | rare cardiovascular (MONDO:0004995), exact SNOMED; events = acute visit dates (before episode grouping) | 8,951 covered ED / inpatient events after dx in 1,182 persons (743 with ≥ 2); inflated by per-day inpatient rows |
| [2026-11-02-autoimmune-exact.md](wearables-events/2026-11-02-autoimmune-exact.md) (plots: `2026-11-02-autoimmune-exact_events-plot-*.png`) | rare autoimmune (MONDO:0007179), exact SNOMED; acute-care episodes (7-day washout) | 2,282 covered episodes after dx in 414 persons (241 with ≥ 2); 2.33 per 1k Fitbit days |
| [2026-11-13-autoimmune-exact-v9-split.md](wearables-events/2026-11-13-autoimmune-exact-v9-split.md) (plots: `2026-11-13-autoimmune-exact-v9-split_events-plot-*.png`) | v9 Controlled Tier, rare autoimmune, exact SNOMED; episodes + prospective split at the v8 cutoff (2023-10-01) | 4,705 covered episodes after dx in 897 persons; ~14 months after the split: 1,118 covered test episodes in 382 known persons (+77 in 33 new) |
| [2026-11-13-autoimmune-exact-v9-site-diag.md](wearables-events/2026-11-13-autoimmune-exact-v9-site-diag.md) | v9 Controlled Tier, rare autoimmune; EHR source diagnostics, focus site 6 | site 6: 2,051 of 4,705 covered episodes in 89 persons, almost all same-day "inpatient" rows recurring every 8-60 days, every year since 2015; without it 2,654 in 810 persons |
