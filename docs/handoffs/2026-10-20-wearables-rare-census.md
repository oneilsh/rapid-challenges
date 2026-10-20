---
title: "Handoff: AoU wearables x rare disease census"
type: handoff
created: 2026-10-20
tags: [charm, charmpheno, rapid, allofus, wearables, rare-disease]
---

# Handoff: AoU wearables x rare disease census

Context for picking this up in a new session. It feeds the RAPID TA1 "wearables" challenge tab: how many All of Us participants have Fitbit data AND a rare-disease diagnosis, and which rare diseases have the most wearables data.

## Where the code lives

> **Update 2026-10-20:** the census now lives in this repo as `audits/wearables_rare.py`
> (run with `make wearables-rare ARGS="..."`), with shared helpers in `rapidaudit/`. It
> also writes `wearables_rare_<tag>_all.tsv`: every mapped rare disease, nothing dropped,
> counts 1–19 shown as `<20`. The CHARMPheno copy below is the original.

- **Repo:** CHARMPheno (`~/Documents/projects/tislab/CHARM/CHARMPheno`)
- **Commit:** `8867b48b` (2026-10-13), written in a Claude Code web session: https://claude.ai/code/session_019K2iN9nZNuZUzMV1pczi96
- **Branch:** only on `origin/claude/dismech-ribbon`. It is NOT on the local working branch (`claude/gated-conditional-voi` as of 10/19), which is why a local search didn't find it.
- **Files:**
  - `analysis/cloud/diag_wearables_rare.py` (303 lines, Spark census driver)
  - `analysis/cloud/Makefile`: target `diag-wearables-rare`
  - `tests/scripts/test_diag_wearables_rare.py`

## How to run (AoU Workbench, Dataproc)

```bash
git fetch && git checkout claude/dismech-ribbon   # or: git cherry-pick 8867b48b
cd analysis/cloud
make diag-wearables-rare                                            # default: --flags rare --min-days 30
make diag-wearables-rare GPR_ARGS="--flags gard_rare --min-days 90" # example variant
```

Output goes to `$(RUNS_DIR)/wearables-rare/` (a workspace run dir, never the repo tree): `wearables_rare_<tag>.md`, `.tsv`, `.json`, plus `wearables_rare_log.md`.

**Script arguments:**
- `--out-dir`: required.
- `--flags`: which Mondo rare subsets to use. Default `rare`. Other choices are `orphanet_rare`, `gard_rare`, `nord_rare`, `inferred_rare` and `mondo_rare`.
- `--min-days`: minimum distinct Fitbit days. Default 30.
- `--top`: how many diseases to list. Default 60.
- `--suspect-share`: default 0.005. A disease is flagged "suspect" when its diagnosed count is above this share of everyone with a condition.
- `--mondo-version`: default `2026-06-02`.
- `--mondo-cache-dir`: default `data/mondo`.

## Method

- **What counts as rare:** Mondo's rare-disease subsets (`rare` is the union; `orphanet_rare`, `gard_rare` and `nord_rare` are the individual sources). Mondo diseases are mapped to OMOP through the repo's port of Monarch's mondo2omop (`mondo_to_omop_mapping.build_mondo_to_omop`). That goes from a Mondo `same_as` cross-reference (SNOMED, ICD10CM or MeSH) to an OMOP concept, then follows "Maps to" to a standard Condition. Each standard concept is then widened to all its OMOP descendants via `concept_ancestor`.
- **What counts as wearables data:** the Fitbit daily-summary tables (`activity_summary`, `heart_rate_summary`, `sleep_daily_summary`, whichever exist in this CDR). A person's wear is the number of distinct days with any summary, plus their first and last day. The headline counts require at least `--min-days`.
- **Columns reported per disease:**
  - `n_dx`: people with any diagnosis in that disease's concept subtree.
  - `n_wear`: of those, people who also meet the Fitbit minimum.
  - `n_wear_before`: of those, people whose Fitbit data starts on or before their first diagnosis (the early-detection case).
  - `n_wear_span`: of those, people whose Fitbit date range covers the first diagnosis.
- **Flags:**
  - `group`: another mapped rare disease sits under this one, so its counts include its children's.
  - `suspect`: `n_dx` is too large to be a rare disease, which usually means an over-broad SNOMED cross-reference.
- **Small-count rule:** rows with `n_wear` under 20 are dropped, and any remaining cell from 1 to 19 prints as "<20".

## Results so far (default run, >= 30 Fitbit days)

| population | persons |
|---|--:|
| persons with any condition | 349,815 |
| persons with any Fitbit day | 58,891 |
| persons with >= 30 Fitbit days | 55,650 |
| persons with any rare dx | 270,904 |
| ... and >= 30 Fitbit days | 23,471 |
| ... rare dx on a non-grouping node, with wear | 21,349 |
| orphanet_rare dx | 119,422 |
| orphanet_rare dx with wear | 9,874 |
| gard_rare dx | 265,484 |
| gard_rare dx with wear | 22,812 |
| nord_rare dx | 195,714 |
| nord_rare dx with wear | 16,418 |

## Caveats and open questions

1. **The "rare" definition is too broad as it stands.** 270,904 of 349,815 people with any condition (77%) have a "rare" diagnosis, and GARD alone covers 265,484. A small number of common, over-broad mappings is almost certainly driving this. Before quoting a headline number, look at the per-disease table's `suspect` and `group` flags and work out which few nodes contribute most of the people.
2. **These numbers don't match Eric Hurwitz's.** The RAPID challenge notes say "Eric Hurwitz found about 2,300 participants with a rare disease phenotype and Fitbit data." The strictest cut here (Orphanet with wear) is 9,874, about 4x higher. Eric presumably used a narrower definition, possibly a curated disease list, stricter wear criteria, or a different CDR version. Ask him for his definition before either number goes into the challenge write-up.
3. **Possible next cuts:**
   - Exclude `suspect` nodes and recount.
   - Require `n_wear_before` for an early-detection framing.
   - Raise `--min-days` to 90 or more.
   - Restrict to people who also have genomic data, for the overlap with the "two-sided synthetic genomics" tab.
4. **The branch question:** decide whether to merge `8867b48b` into the working branch or keep it as a side branch. The code is a self-contained diagnostic: it doesn't use the model fit or any cache keys.

## Related

- RAPID TA1 challenges: [challenge sheet](https://docs.google.com/spreadsheets/d/1RiujmIydt7s6M8xdVTWheb9WGp0tpzs56I22BvCPCNQ/edit?gid=0#gid=0), [Drive folder](https://drive.google.com/drive/folders/19iqBQltMonsKb6B8MpsOKzSZ1OLj1iy0), [meeting agenda doc](https://docs.google.com/document/d/183Js9G2ucwNvZ1HBnw0S8jEfu-yy8c_QQ9WWnA_rIWk/edit)
- [[rapid-representation-learning-challenge-doc]] (shelved 2026-10-19 in favor of the wearables and two-sided synthetic genomics tabs)
