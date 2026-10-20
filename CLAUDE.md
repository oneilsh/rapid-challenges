# CLAUDE.md

Participant-count audits for RAPID challenges on the All of Us Workbench. See README.md
for layout and how to run.

## Rules

- **Egress:** every participant count leaving an audit goes through
  `rapidaudit.egress.mask_counts` / `cell` (1–19 → `<20`; 0 stays `0`). Never write a
  percentage, ratio or difference computed from a masked count. Flag nested rows (parent
  minus child) when a table is meant to be shared.
- **No data in the repo.** Audits write to `--out-dir` under `RUNS_DIR`, never to the
  tree. `.gitignore` blocks `*.tsv`, `*.csv`, `data/` and `runs/`. Keep it that way.
- **Can't run locally.** The CDR is only reachable from the Workbench. Locally, test the
  pure pandas functions (`make test`); Spark/BigQuery code paths are cluster-only, so the
  user runs them and pastes back the masked output.
- **Driver-only Python.** Audits use Spark-native joins/groupBys plus pandas on the
  driver, so `spark-submit` in client mode with `PYTHONPATH` works and no `--py-files`
  are needed. If an audit adds a Python UDF, it needs a zip of `rapidaudit/` on
  `--py-files`.
- **Code copied from CHARMPheno** (`~/Documents/projects/tislab/CHARM/CHARMPheno`,
  `analysis/cloud/`) keeps a provenance line naming the source file and commit. Look
  there first for reusable cluster helpers (OMOP reads, Mondo/HPO mapping, concept
  hierarchies) and copy them in rather than importing across repos.
