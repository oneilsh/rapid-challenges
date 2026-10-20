# CLAUDE.md

Participant-count audits for RAPID challenges on the All of Us Workbench. See README.md
for layout and how to run.

## Rules

- **Egress:** every participant count leaving an audit goes through
  `rapidaudit.egress.mask_counts` / `cell` (1–19 → `<20`; 0 stays `0`). Never write a
  percentage, ratio or difference computed from a masked count. Flag nested rows (parent
  minus child) when a table is meant to be shared.
- **No data in the repo** except masked results. Audits write to `--out-dir` under
  `RUNS_DIR`, never to the tree. `.gitignore` blocks `*.tsv`, `*.csv`, `data/` and
  `runs/`, except `results/**/*.tsv`.
- **Filing results.** When the user pastes a run's output, save it unedited as
  `results/<audit>/YYYY-MM-DD-<short-name>.md` with the YAML header the existing files
  use (command, args, commit, Mondo release, notes), and add a row to the index in
  `results/README.md`. Check every count is 0, ≥ 20 or `<20` before committing.
- **Can't run locally.** The CDR is only reachable from the Workbench. Locally, test the
  pure functions (`make test`); BigQuery code paths only run on the Workbench, so the
  user runs them and pastes back the masked output.
- **BigQuery, not Spark.** The Workbench VM has no Dataproc cluster. Audits push the
  heavy joins and `COUNT(DISTINCT ...)`s into SQL via `rapidaudit.aou.query`, pass small
  lookup tables as array query parameters (the CDR dataset is read-only), and only pull
  aggregated rows into pandas. CHARMPheno's drivers are Spark: port them, don't copy.
- **Code copied from CHARMPheno** (`~/Documents/projects/tislab/CHARM/CHARMPheno`,
  `analysis/cloud/`) keeps a provenance line naming the source file and commit. Look
  there first for reusable helpers (OMOP reads, Mondo/HPO mapping, concept
  hierarchies) and copy them in rather than importing across repos.
