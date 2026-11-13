---
audit: wearables-events
date: 2026-11-13
command: make wearables-events-split
args: --after 2023-10-01 --under MONDO:0007179 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact (lookback 30, min-cov 14, washout 7)
commit: 92f8ba4
mondo: 2026-06-02
notes: >
  v9 Controlled Tier CDR (C2025Q4R6), rare autoimmune, with a prospective split at the
  v8 data cutoff (2023-10-01) as a stand-in for a v10 holdout. Overall vs v8: 4,705
  covered episodes after dx in 897 persons (529 with >= 2), 2.40 per 1k Fitbit days
  (v8: 2,282 / 414). Split: about 14 months of Fitbit follow-up after 2023-10-01. Known
  persons (dx and Fitbit before the split): 2,535, 1,876 still wearing after it; 3,510
  covered train episodes in 694 persons; 1,118 covered test episodes in 382 persons
  (2.06 per 1k wear-days); new persons add 77 test episodes in 33 persons. EHR sources:
  55, 28 with >= 20 cohort persons, 13 with >= 20 persons with a covered episode; site
  6 has 2,051 covered episodes in 89 persons (about 23 each), likely a site-specific
  visit-coding pattern worth checking. NESTED CELLS: in the split table, new persons'
  test episodes by class (ed 21, inpatient 60, either 77) imply 4 episodes that are
  both ED and inpatient; do not share that table beyond the team without collapsing the
  class rows.
---

# Wearables x ED / inpatient events (All of Us)

CDR: `wb-silky-artichoke-2408.C2025Q4R6`

Fitbit tables: activity_summary, heart_rate_summary, sleep_daily_summary · rare = Mondo subsets orphanet_rare, gard_rare, nord_rare, mondo_rare · 102 diseases mapped

Scope: under MONDO:0007179 · exact SNOMED-only mapping

Event = an acute-care episode: ED / inpatient visit starts, with visits less than 8 days apart merged, dated by its first day. After / before = strictly after / before the first diagnosis (the dx day itself is excluded). Covered = >= 14 Fitbit days in the 30 days before the event. Cohort = persons with the disease and any Fitbit day. Columns are nested: check differences before sharing.

## All selected diseases

Persons with a selected diagnosis: 23,481 · with Fitbit data: 2,838 · their Fitbit days after dx: 1,959,779

| event class | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| ed_or_inpatient | 15,816 | 1,680 | 4,705 | 897 | 529 | 2.40 | 1,505 | 302 |
| ed | 6,653 | 1,323 | 1,615 | 639 | 307 | 0.82 | 492 | 199 |
| inpatient | 10,609 | 1,140 | 3,466 | 559 | 304 | 1.77 | 1,127 | 194 |

Pooled events after dx by Fitbit days in the 30 days before them:

| event class | 0 | 1-6 | 7-13 | 14-20 | 21+ |
|---|--:|--:|--:|--:|--:|
| ed_or_inpatient | 10,428 | 366 | 317 | 378 | 4,327 |

## By disease (persons with Fitbit data >= 20)

### ed_or_inpatient

| Mondo | disease | with data | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0010030 | Sjogren syndrome | 993 | 5,433 | 584 | 1,529 | 303 | 192 | 2.37 | 579 | 121 |
| MONDO:0007915 | systemic lupus erythematosus | 645 | 4,398 | 409 | 1,163 | 207 | 124 | 2.69 | 172 | 42 |
| MONDO:0019562 | localized scleroderma | 317 | 1,522 | 182 | 392 | 104 | 57 | 1.38 | 254 | 32 |
| MONDO:0020640 | autoimmune encephalitis | 220 | 405 | 96 | 163 | 62 | 26 | 1.18 | 52 | 26 |
| MONDO:8000010 | antiphospholipid syndrome | 172 | 1,303 | 111 | 334 | 50 | 29 | 3.38 | 125 | 26 |
| MONDO:0009688 | myasthenia gravis | 169 | 1,020 | 109 | 380 | 63 | 33 | 3.43 | 47 | <20 |
| MONDO:0005282 | cutaneous lupus erythematosus | 152 | 1,284 | 99 | 415 | 47 | 35 | 3.88 | 151 | <20 |
| MONDO:0016264 | autoimmune hepatitis | 132 | 441 | 69 | 146 | 36 | 21 | 1.53 | 68 | <20 |
| MONDO:0005100 | systemic sclerosis | 132 | 659 | 76 | 199 | 37 | 21 | 2.12 | 55 | <20 |
| MONDO:0019558 | discoid lupus erythematosus | 129 | 1,185 | 87 | 388 | 41 | 31 | 4.44 | 148 | <20 |
| MONDO:0019527 | undifferentiated connective tissue syndrome | 112 | 367 | 60 | 161 | 35 | 21 | 2.20 | 39 | <20 |
| MONDO:0019337 | autoimmune bullous skin disease | 94 | 601 | 56 | 172 | 32 | 20 | 3.57 | 105 | <20 |
| MONDO:0017767 | rheumatic fever | 59 | 174 | 36 | 40 | <20 | <20 | 0.95 | 42 | <20 |
| MONDO:0030703 | autoimmune vasculitis | 58 | 513 | 38 | 49 | <20 | <20 | 1.24 | <20 | <20 |
| MONDO:0004680 | primary thrombocytopenia | 54 | 292 | 36 | 60 | <20 | <20 | 1.30 | 47 | <20 |
| MONDO:0016218 | Guillain-Barre syndrome | 51 | 423 | 36 | 237 | 23 | <20 | 7.21 | 32 | <20 |
| MONDO:0020108 | autoimmune hemolytic anemia | 51 | 225 | 30 | 83 | <20 | <20 | 2.71 | 24 | <20 |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 45 | 246 | 20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0016544 | IgG4-related mesenteritis | 43 | 170 | 30 | 37 | <20 | <20 | 1.84 | 32 | <20 |
| MONDO:0005854 | mixed connective tissue disease | 41 | 275 | 23 | 64 | <20 | <20 | 3.37 | 30 | <20 |
| MONDO:0850301 | pemphigoid | 34 | 121 | 23 | 42 | <20 | <20 | 2.41 | 86 | <20 |
| MONDO:0019098 | autoimmune thrombocytopenia | 30 | 237 | <20 | 61 | <20 | <20 | 2.68 | <20 | <20 |
| MONDO:0019563 | CREST syndrome | 29 | 54 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0015614 | dermatitis herpetiformis | 27 | 159 | <20 | 48 | <20 | <20 | 3.20 | <20 | <20 |
| MONDO:0016474 | drug-induced lupus erythematosus | 26 | 48 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0015573 | subacute cutaneous lupus erythematosus | 23 | 192 | <20 | 90 | <20 | <20 | 6.11 | 38 | <20 |

## Prospective split at 2023-10-01

Known = diagnosed and with a Fitbit day before 2023-10-01 (would be in a release cut then); new = everyone else in the cohort with Fitbit days after dx on or after 2023-10-01. Train = covered episodes after dx and before 2023-10-01; test = covered episodes on or after 2023-10-01. Follow-up after the split: about 14.1 months of Fitbit data and 15.0 months of visits. "Known" is by date only, so it slightly overcounts persons in the earlier release (late EHR records, Fitbit history synced later); test counts are exact. Columns are nested.

| split class | known persons | still wearing after split | covered train episodes | persons | covered test episodes | persons | test per 1k wear-days | new persons | their covered test episodes | persons |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| ed_or_inpatient | 2,535 | 1,876 | 3,510 | 694 | 1,118 | 382 | 2.06 | 229 | 77 | 33 |
| ed | 2,535 | 1,876 | 1,199 | 481 | 395 | 239 | 0.73 | 229 | 21 | <20 |
| inpatient | 2,535 | 1,876 | 2,572 | 441 | 834 | 230 | 1.54 | 229 | 60 | 20 |

Known persons' Fitbit days on or after 2023-10-01: 541,444

By disease, ed_or_inpatient (known + new persons >= 20):

| split Mondo | disease | known persons | still wearing after split | covered train episodes | persons | covered test episodes | persons | test per 1k wear-days | new persons | their covered test episodes | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0010030 | Sjogren syndrome | 892 | 642 | 1,112 | 229 | 372 | 134 | 2.04 | 69 | 45 | <20 |
| MONDO:0007915 | systemic lupus erythematosus | 579 | 404 | 960 | 170 | 188 | 70 | 1.67 | 52 | <20 | <20 |
| MONDO:0019562 | localized scleroderma | 286 | 227 | 247 | 83 | 140 | 45 | 2.02 | 25 | <20 | <20 |
| MONDO:0020640 | autoimmune encephalitis | 190 | 172 | 89 | 41 | 66 | 26 | 1.15 | 29 | <20 | <20 |
| MONDO:0009688 | myasthenia gravis | 150 | 109 | 307 | 45 | 63 | 27 | 2.29 | <20 | <20 | <20 |
| MONDO:8000010 | antiphospholipid syndrome | 150 | 104 | 269 | 37 | 62 | 23 | 2.19 | <20 | <20 | <20 |
| MONDO:0005282 | cutaneous lupus erythematosus | 142 | 96 | 343 | 41 | 65 | <20 | 2.49 | <20 | <20 | <20 |
| MONDO:0005100 | systemic sclerosis | 122 | 98 | 149 | 28 | 44 | <20 | 1.54 | <20 | <20 | <20 |
| MONDO:0019558 | discoid lupus erythematosus | 121 | 78 | 319 | 34 | 62 | <20 | 3.14 | <20 | <20 | <20 |
| MONDO:0016264 | autoimmune hepatitis | 117 | 76 | 89 | 23 | 51 | <20 | 2.16 | <20 | <20 | <20 |
| MONDO:0019527 | undifferentiated connective tissue syndrome | 91 | 77 | 118 | 21 | 39 | 21 | 1.65 | <20 | <20 | <20 |
| MONDO:0019337 | autoimmune bullous skin disease | 82 | 60 | 121 | 26 | 51 | <20 | 2.92 | <20 | 0 | 0 |
| MONDO:0030703 | autoimmune vasculitis | 53 | 36 | 33 | <20 | <20 | <20 | — | <20 | <20 | <20 |
| MONDO:0017767 | rheumatic fever | 52 | 35 | 33 | <20 | <20 | <20 | — | <20 | <20 | <20 |
| MONDO:0004680 | primary thrombocytopenia | 50 | 32 | 49 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016218 | Guillain-Barre syndrome | 48 | 36 | 172 | <20 | 65 | <20 | 6.13 | <20 | 0 | 0 |
| MONDO:0020108 | autoimmune hemolytic anemia | 46 | 32 | 71 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 43 | 36 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016544 | IgG4-related mesenteritis | 35 | 21 | 31 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0005854 | mixed connective tissue disease | 30 | 22 | 53 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0850301 | pemphigoid | 30 | 20 | 29 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0019563 | CREST syndrome | 28 | 24 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0019098 | autoimmune thrombocytopenia | 28 | 24 | 34 | <20 | 27 | <20 | 3.65 | <20 | 0 | 0 |
| MONDO:0015614 | dermatitis herpetiformis | 23 | <20 | 27 | <20 | 21 | <20 | 3.94 | <20 | 0 | 0 |
| MONDO:0015573 | subacute cutaneous lupus erythematosus | 21 | <20 | 75 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016474 | drug-induced lupus erythematosus | 20 | <20 | <20 | <20 | <20 | <20 | — | <20 | <20 | <20 |

## By EHR source (all selected diseases)

Source = `src_id` in `visit_occurrence_ext` (All of Us obfuscated EHR source, shown here only by rank). Persons are counted at the source holding most of their visits; covered ED / inpatient episodes after dx at the source of the episode's first day. Other `*_ext` tables with `src_id`: attribute_definition_ext, care_site_ext, cohort_definition_ext, condition_era_ext, condition_occurrence_ext, cost_ext, device_cost_ext, device_exposure_ext, dose_era_ext, drug_cost_ext, drug_era_ext, drug_exposure_ext, location_ext, measurement_ext, observation_ext, observation_period_ext, payer_plan_period_ext, person_ext, procedure_cost_ext, procedure_occurrence_ext, provider_ext, sleep_daily_summary_ext, specimen_ext, survey_conduct_ext, visit_cost_ext, visit_detail_ext, visit_occurrence_ext.

Sources: 55 · with >= 20 cohort persons: 28 · with >= 20 persons with a covered episode: 13

| source | cohort persons | covered episodes | persons with one |
|---|--:|--:|--:|
| site 1 | 512 | 538 | 170 |
| site 2 | 472 | 322 | 130 |
| site 3 | 198 | 227 | 79 |
| site 4 | 185 | 211 | 72 |
| site 5 | 110 | 71 | 38 |
| site 6 | 101 | 2,051 | 89 |
| site 7 | 93 | 99 | 38 |
| site 8 | 92 | 103 | 30 |
| site 9 | 88 | 87 | 25 |
| site 10 | 80 | <20 | <20 |
| site 11 | 72 | 68 | 24 |
| site 12 | 70 | <20 | <20 |
| site 13 | 57 | 67 | <20 |
| site 14 | 55 | 48 | 20 |
| site 15 | 48 | 159 | 27 |
| site 16 | 46 | 39 | <20 |
| site 17 | 45 | <20 | <20 |
| site 18 | 43 | <20 | <20 |
| site 19 | 40 | 38 | <20 |
| site 20 | 40 | 22 | <20 |
| site 21 | 37 | <20 | <20 |
| site 22 | 34 | 254 | 26 |
| site 23 | 34 | <20 | <20 |
| site 24 | 29 | <20 | <20 |
| site 25 | 28 | <20 | <20 |
| site 26 | 26 | <20 | <20 |
| site 27 | 25 | 41 | <20 |
| site 28 | 20 | 36 | <20 |
| site 29 | <20 | <20 | <20 |
| site 30 | <20 | 34 | <20 |
| Participant Portal: TPC | <20 | 0 | 0 |
| site 32 | <20 | 73 | <20 |
| site 33 | <20 | <20 | <20 |
| site 34 | <20 | 0 | 0 |
| site 35 | <20 | <20 | <20 |
| Participant Portal: PTSC | <20 | 0 | 0 |
| site 37 | <20 | <20 | <20 |
| site 38 | <20 | <20 | <20 |
| site 39 | <20 | 0 | 0 |
| site 40 | <20 | <20 | <20 |
| site 41 | <20 | 0 | 0 |
| site 42 | <20 | <20 | <20 |
| site 43 | <20 | <20 | <20 |
| site 44 | <20 | 0 | 0 |
| site 45 | <20 | 0 | 0 |
| site 46 | <20 | 0 | 0 |
| site 47 | <20 | 0 | 0 |
| site 48 | <20 | 0 | 0 |
| site 49 | <20 | 0 | 0 |
| site 50 | <20 | 0 | 0 |
| site 51 | <20 | 0 | 0 |
| site 52 | <20 | 0 | 0 |
| site 53 | <20 | 0 | 0 |
| site 54 | <20 | 0 | 0 |
| site 55 | <20 | 0 | 0 |

## Visit types for the cohort (top 15 by visits)

| visit concept | name | visits | persons |
|--:|---|--:|--:|
| 9202 | Outpatient Visit | 639,011 | 2,822 |
| 581477 | Office Visit | 207,239 | 1,688 |
| 581458 | Pharmacy visit | 109,227 | 608 |
| 32036 | Laboratory Visit | 57,993 | 948 |
| 722455 | Telehealth | 41,184 | 766 |
| 9201 | Inpatient Visit | 33,970 | 1,316 |
| 32693 | Health examination | 27,369 | 69 |
| 9203 | Emergency Room Visit | 15,994 | 1,657 |
| 581385 | Observation Room | 10,599 | 287 |
| 581479 | Ambulatory Rehabilitation Visit | 9,370 | 292 |
| 8756 | Outpatient Hospital | 4,035 | 160 |
| 8717 | Inpatient Hospital | 3,465 | 218 |
| 38004515 | Hospital | 3,099 | 73 |
| 581476 | Home Visit | 1,998 | 229 |
| 42898160 | Non-hospital institution Visit | 1,643 | 82 |
