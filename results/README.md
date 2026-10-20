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
