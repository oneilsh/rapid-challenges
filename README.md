# rapid-challenges

Participant-count audits for the RAPID TA1 challenges, run on the All of Us Workbench
(plain Python on a Workbench VM, querying the CDR in BigQuery). Each audit answers a
question like "how many participants have X and Y, broken down by Z", and writes
egress-safe tables.

## Layout

| path | what |
|---|---|
| `audits/` | one BigQuery-backed script per audit (`wearables_rare.py`: Fitbit x Mondo rare disease) |
| `rapidaudit/egress.py` | the small-count rule: 1–19 → `<20`, 0 stays 0 |
| `rapidaudit/aou.py` | workspace env, `query` (parameterized SQL → pandas), cached Mondo download |
| `rapidaudit/mondo_to_omop_mapping.py` | Mondo → OMOP standard Condition (port of Monarch's mondo2omop) |
| `rapidaudit/setup_workspace.py` | writes `.workspace_env` from the `wb` CLI |
| `docs/handoffs/` | session handoffs and per-audit notes |

Shared code was copied from CHARMPheno (`analysis/cloud/`); each copied file names its
source commit. This repo doesn't depend on CHARMPheno at runtime.

## Running on the Workbench

From a Workbench VM (no Dataproc cluster needed), in a clone of this repo:

```bash
make setup                     # once per VM; add CDR=<project>.<dataset> if needed
make wearables-rare            # default: --flags rare --min-days 30
make wearables-rare ARGS="--flags orphanet_rare --min-days 90"
```

Outputs go to `$(RUNS_DIR)/<audit>/`, outside the repo. The default `RUNS_DIR` is the
bucket-backed workspace mount
`/home/jupyter/workspace/dataproc-staging-getting-started-with-registered-tier-data-copy`,
so results survive VM deletion. Override with `RUNS_DIR=...`.

## Egress

All of Us forbids publishing participant counts from 1 to 19. Every audit table goes
through `rapidaudit.egress.mask_counts` before it is written. Also check before sharing:

- **No derived columns next to a mask.** A percentage or difference can back out a
  masked count. Drop it, or compute it only where every input is ≥ 20.
- **Nested rows.** A parent count minus a child count can reveal a small number even
  when both cells are ≥ 20 (for example the `group` rows in the wearables census).

## Local tests

```bash
make test        # uv run pytest; pure pandas/SQL-building logic only, no BigQuery needed
```

## Adding an audit

1. Write `audits/<name>.py` with an `argparse` `main()` and a required `--out-dir`.
   Keep the pure logic (row building, formatting) in plain functions so it can be tested.
2. Mask every count column with `mask_counts` before writing.
3. Add a `<name>` target to the `Makefile` modeled on `wearables-rare`.
4. Add `tests/test_<name>.py` for the pure functions.
