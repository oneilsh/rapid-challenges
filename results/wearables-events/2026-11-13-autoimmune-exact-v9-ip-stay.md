---
audit: wearables-events (with split and site diagnostics)
date: 2026-11-13
command: make wearables-events-sites FOCUS='site 6' ARGS='--ip-overnight --after 2023-10-01'
args: --site-diagnostics --focus-site 'site 6' --ip-overnight --after 2023-10-01 --under MONDO:0007179 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact (lookback 30, min-cov 14, washout 7)
commit: cdbb686
mondo: 2026-06-02
notes: >
  v9 Controlled Tier CDR (C2025Q4R6), rare autoimmune, inpatient = a stay (a visit row
  ending after its start day, or inpatient rows on consecutive days). Pooled: 2,244
  covered ED-or-inpatient episodes in 789 persons (405 with >= 2), 1.15 per 1k
  wear-days; ED 1,615 / 639; inpatient stays 874 / 385. Split at the v8 cutoff: test
  538 covered episodes in 307 known persons plus 28 in 24 new (ED 395 / 239). Site 6
  falls to 306 episodes in 70 persons, now mostly runs of same-day inpatient rows on
  consecutive days (could be stays logged per day). Site 22 unchanged: 254 ED episodes in
  26 persons. NESTED CELLS: as in the earlier files; also, this file and the other
  2026-11-13 v9 files differ only in the inpatient rule, so differences between them
  (e.g. per-source persons) can be small counts: share at most one variant beyond the team.
---

# EHR source diagnostics: ED / inpatient episodes (All of Us)

CDR: `wb-silky-artichoke-2408.C2025Q4R6` · run `autoimmune-disease_exact` · source = `src_id` in `visit_occurrence_ext`, labels as in that run's events report

Episodes = the pooled cohort's covered ED / inpatient episodes after the first dx (>= 14 Fitbit days in the 30 days before; visits less than 8 days apart merged; inpatient only with a stay: a row ending after its start day or rows on consecutive days), each at the source of its first day. Medians and percentiles are over persons or episodes at that source and only shown where >= 20 persons stand behind them. Columns are nested: check differences before sharing.

## Per source (>= 20 persons with an episode)

| source | persons | episodes | episodes / person, median | 90th pct | days between episodes, median | visit days / episode, median | visit rows / episode, median | episodes with inpatient row | of those, no single row spanning a night |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| site 6 | 70 | 306 | 2.5 | 8 | 74 | 3 | 4 | 302 | 264 |
| site 1 | 150 | 293 | 1 | 3 | 54 | 1 | 1 | 145 | 20 |
| site 22 | 26 | 254 | 7 | 21 | 34 | 1 | 1 | <20 | <20 |
| site 4 | 69 | 204 | 2 | 7 | 86 | 1 | 3 | 83 | <20 |
| site 2 | 107 | 200 | 1 | 4 | 106 | 1 | 1 | 64 | <20 |
| site 3 | 75 | 200 | 2 | 5.6 | 124 | 1 | 2 | 145 | 52 |
| site 8 | 30 | 102 | 2 | 5.2 | 85.5 | 1 | 1 | 34 | 0 |
| site 7 | 35 | 93 | 2 | 4.6 | 113 | 1 | 2 | <20 | <20 |
| site 9 | 25 | 87 | 2 | 7.6 | 104.5 | 1 | 1 | <20 | 0 |
| site 5 | 38 | 70 | 1 | 4 | 253 | 1 | 1 | 26 | 0 |
| site 14 | 20 | 46 | 1 | 5 | 86 | 1 | 1 | <20 | 0 |
| site 11 | 23 | 43 | 1 | 3.8 | 126.5 | 1 | 1 | <20 | <20 |

## Focus: site 6 against all other sources

Chosen with --focus-site.

### Episodes by start year

| year | focus episodes | persons | other episodes | persons |
|--:|--:|--:|--:|--:|
| 2012 | 0 | 0 | <20 | <20 |
| 2014 | <20 | <20 | <20 | <20 |
| 2015 | <20 | <20 | <20 | <20 |
| 2016 | <20 | <20 | 24 | <20 |
| 2017 | 23 | <20 | 82 | 53 |
| 2018 | <20 | <20 | 100 | 50 |
| 2019 | 29 | <20 | 172 | 96 |
| 2020 | 25 | <20 | 176 | 94 |
| 2021 | 29 | <20 | 222 | 133 |
| 2022 | 36 | 20 | 323 | 175 |
| 2023 | 80 | 36 | 527 | 312 |
| 2024 | 60 | 28 | 297 | 211 |

### Days between a person's consecutive episodes (same group)

| days | focus | other |
|---|--:|--:|
| 8-13 | <20 | 100 |
| 14-20 | 23 | 91 |
| 21-30 | 27 | 149 |
| 31-60 | 46 | 196 |
| 61-180 | 65 | 350 |
| 181+ | 64 | 332 |

### Visit concepts on the episodes' visit rows

| visit concept | name | focus rows | persons | other rows | persons |
|--:|---|--:|--:|--:|--:|
| 9201 | Inpatient Visit | 1,498 | 70 | 1,484 | 285 |
| 9203 | Emergency Room Visit | 76 | 30 | 2,205 | 591 |
| 262 | Emergency Room and Inpatient Visit | 22 | <20 | 118 | 41 |
| 8717 | Inpatient Hospital | <20 | <20 | 424 | 52 |
| 8870 | Emergency Room - Hospital | 0 | 0 | <20 | <20 |
| 38004515 | Hospital | 0 | 0 | 56 | <20 |

### Top conditions on the focus source's episode visits (by episodes)

| concept | name | focus episodes | persons | other episodes | persons |
|--:|---|--:|--:|--:|--:|
| 320128 | Essential hypertension | 31 | <20 | 370 | 165 |
| 77670 | Chest pain | <20 | <20 | 207 | 141 |
| 140673 | Hypothyroidism | <20 | <20 | 153 | 89 |
| 312437 | Dyspnea | <20 | <20 | 173 | 100 |
| 437833 | Hypokalemia | <20 | <20 | 53 | 39 |
| 4209423 | Nicotine dependence | <20 | <20 | 48 | 23 |
| 313217 | Atrial fibrillation | <20 | <20 | 78 | 31 |
| 138384 | Acquired hypothyroidism | <20 | <20 | <20 | <20 |
| 257628 | Systemic lupus erythematosus | <20 | <20 | 89 | 46 |
| 4193704 | Type 2 diabetes mellitus without complication | <20 | <20 | 145 | 63 |
| 432867 | Hyperlipidemia | <20 | <20 | 190 | 105 |
| 254761 | Cough | <20 | <20 | 60 | 45 |
| 44784217 | Cardiac arrhythmia | <20 | <20 | 36 | 32 |
| 318736 | Migraine | <20 | <20 | 71 | 48 |
| 197320 | Acute kidney injury | <20 | <20 | 55 | 46 |

### Top procedures on the focus source's episode visits (by episodes)

| concept | name | focus episodes | persons | other episodes | persons |
|--:|---|--:|--:|--:|--:|
| 2313815 | Electrocardiogram, routine ECG with at least 12 le | 37 | 24 | 233 | 133 |
| 2313816 | Electrocardiogram, routine ECG with at least 12 le | 34 | 21 | 244 | 129 |
| 2314215 | Therapeutic, prophylactic, or diagnostic injection | <20 | <20 | 135 | 90 |
| 2314216 | Therapeutic, prophylactic, or diagnostic injection | <20 | <20 | 103 | 64 |
| 2314205 | Intravenous infusion, hydration; each additional h | <20 | <20 | 99 | 67 |
| 2314047 | Noninvasive ear or pulse oximetry for oxygen satur | <20 | <20 | 34 | <20 |
| 2514408 | Subsequent hospital inpatient or observation care, | <20 | <20 | 122 | 71 |
| 725068 | Radiologic examination, chest; single view | <20 | <20 | 118 | 69 |
| 2514405 | Initial hospital inpatient or observation care, pe | <20 | <20 | 71 | 49 |
| 2514409 | Subsequent hospital inpatient or observation care, | <20 | <20 | 112 | 63 |
| 2514414 | Hospital inpatient or observation discharge day ma | <20 | <20 | 82 | 50 |
| 2314213 | Therapeutic, prophylactic, or diagnostic injection | <20 | <20 | 51 | 33 |
| 2514406 | Initial hospital inpatient or observation care, pe | <20 | <20 | 112 | 61 |
| 2213283 | Level IV - Surgical pathology, gross and microscop | <20 | <20 | 46 | 38 |
| 725069 | Radiologic examination, chest; 2 views | <20 | <20 | 108 | 76 |

## Pooled episodes with and without the focus source

| | episodes | persons with one |
|---|--:|--:|
| all sources | 2,244 | 789 |
| without site 6 | 1,938 | 720 |

Persons can have episodes at more than one source, so the rows overlap.

[events] wrote /home/dataproc/workspace/dataproc-staging-bayesian-phenotyping-for-rare-disease-v9/rapid/wearables-events/C2025Q4R6/autoimmune-disease_exact_site-diag-report.md
[events] plot /home/dataproc/workspace/dataproc-staging-bayesian-phenotyping-for-rare-disease-v9/rapid/wearables-events/C2025Q4R6/autoimmune-disease_exact_events-plot-pooled.png
[events] plot /home/dataproc/workspace/dataproc-staging-bayesian-phenotyping-for-rare-disease-v9/rapid/wearables-events/C2025Q4R6/autoimmune-disease_exact_events-plot-coverage.png
[events] plot /home/dataproc/workspace/dataproc-staging-bayesian-phenotyping-for-rare-disease-v9/rapid/wearables-events/C2025Q4R6/autoimmune-disease_exact_events-plot-disease-persons.png
[events] plot /home/dataproc/workspace/dataproc-staging-bayesian-phenotyping-for-rare-disease-v9/rapid/wearables-events/C2025Q4R6/autoimmune-disease_exact_events-plot-disease-rates.png
# Wearables x ED / inpatient events (All of Us)

CDR: `wb-silky-artichoke-2408.C2025Q4R6`

Fitbit tables: activity_summary, heart_rate_summary, sleep_daily_summary · rare = Mondo subsets orphanet_rare, gard_rare, nord_rare, mondo_rare · 102 diseases mapped

Scope: under MONDO:0007179 · exact SNOMED-only mapping

Event = an acute-care episode: ED / inpatient visit starts, with visits less than 8 days apart merged, dated by its first day. After / before = strictly after / before the first diagnosis (the dx day itself is excluded). Inpatient = an inpatient stay: a visit row ending after the day it starts, or inpatient rows on consecutive days (isolated same-day inpatient rows dropped). Covered = >= 14 Fitbit days in the 30 days before the event. Cohort = persons with the disease and any Fitbit day. Columns are nested: check differences before sharing.

## All selected diseases

Persons with a selected diagnosis: 23,481 · with Fitbit data: 2,838 · their Fitbit days after dx: 1,959,779

| event class | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| ed_or_inpatient | 9,048 | 1,559 | 2,244 | 789 | 405 | 1.15 | 669 | 257 |
| ed | 6,653 | 1,323 | 1,615 | 639 | 307 | 0.82 | 492 | 199 |
| inpatient | 3,438 | 893 | 874 | 385 | 142 | 0.45 | 255 | 123 |

Pooled events after dx by Fitbit days in the 30 days before them:

| event class | 0 | 1-6 | 7-13 | 14-20 | 21+ |
|---|--:|--:|--:|--:|--:|
| ed_or_inpatient | 6,492 | 171 | 141 | 207 | 2,037 |

## By disease (persons with Fitbit data >= 20)

### ed_or_inpatient

| Mondo | disease | with data | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0010030 | Sjogren syndrome | 993 | 2,943 | 539 | 700 | 260 | 141 | 1.08 | 261 | 100 |
| MONDO:0007915 | systemic lupus erythematosus | 645 | 2,801 | 386 | 620 | 190 | 106 | 1.43 | 107 | 37 |
| MONDO:0019562 | localized scleroderma | 317 | 794 | 165 | 188 | 87 | 38 | 0.66 | 48 | 24 |
| MONDO:0020640 | autoimmune encephalitis | 220 | 180 | 78 | 77 | 47 | <20 | 0.56 | 35 | 23 |
| MONDO:8000010 | antiphospholipid syndrome | 172 | 603 | 107 | 134 | 47 | 25 | 1.35 | 52 | 25 |
| MONDO:0009688 | myasthenia gravis | 169 | 747 | 106 | 234 | 61 | 29 | 2.11 | 44 | <20 |
| MONDO:0005282 | cutaneous lupus erythematosus | 152 | 670 | 94 | 191 | 42 | 27 | 1.78 | 23 | <20 |
| MONDO:0016264 | autoimmune hepatitis | 132 | 296 | 65 | 99 | 35 | <20 | 1.04 | 28 | <20 |
| MONDO:0005100 | systemic sclerosis | 132 | 331 | 72 | 71 | 35 | <20 | 0.76 | 33 | <20 |
| MONDO:0019558 | discoid lupus erythematosus | 129 | 574 | 82 | 164 | 36 | 23 | 1.88 | 20 | <20 |
| MONDO:0019527 | undifferentiated connective tissue syndrome | 112 | 160 | 53 | 57 | 29 | <20 | 0.78 | <20 | <20 |
| MONDO:0019337 | autoimmune bullous skin disease | 94 | 401 | 53 | 83 | 30 | <20 | 1.72 | 27 | <20 |
| MONDO:0017767 | rheumatic fever | 59 | 151 | 32 | 31 | <20 | <20 | 0.74 | 37 | <20 |
| MONDO:0030703 | autoimmune vasculitis | 58 | 345 | 38 | 30 | <20 | <20 | 0.76 | <20 | <20 |
| MONDO:0004680 | primary thrombocytopenia | 54 | 285 | 35 | 59 | <20 | <20 | 1.28 | 47 | <20 |
| MONDO:0020108 | autoimmune hemolytic anemia | 51 | 153 | 28 | 32 | <20 | <20 | 1.04 | <20 | <20 |
| MONDO:0016218 | Guillain-Barre syndrome | 51 | 182 | 33 | 79 | <20 | <20 | 2.40 | <20 | <20 |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 45 | 101 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0016544 | IgG4-related mesenteritis | 43 | 83 | 28 | 23 | <20 | <20 | 1.14 | 22 | <20 |
| MONDO:0005854 | mixed connective tissue disease | 41 | 95 | 20 | 22 | <20 | <20 | 1.16 | <20 | <20 |
| MONDO:0850301 | pemphigoid | 34 | 79 | 21 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0019098 | autoimmune thrombocytopenia | 30 | 94 | <20 | 22 | <20 | <20 | 0.97 | <20 | <20 |
| MONDO:0019563 | CREST syndrome | 29 | 46 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0015614 | dermatitis herpetiformis | 27 | 103 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0016474 | drug-induced lupus erythematosus | 26 | 35 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0015573 | subacute cutaneous lupus erythematosus | 23 | 160 | <20 | 73 | <20 | <20 | 4.96 | <20 | <20 |

## Prospective split at 2023-10-01

Known = diagnosed and with a Fitbit day before 2023-10-01 (would be in a release cut then); new = everyone else in the cohort with Fitbit days after dx on or after 2023-10-01. Train = covered episodes after dx and before 2023-10-01; test = covered episodes on or after 2023-10-01. Follow-up after the split: about 14.1 months of Fitbit data and 15.0 months of visits. "Known" is by date only, so it slightly overcounts persons in the earlier release (late EHR records, Fitbit history synced later); test counts are exact. Columns are nested.

| split class | known persons | still wearing after split | covered train episodes | persons | covered test episodes | persons | test per 1k wear-days | new persons | their covered test episodes | persons |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| ed_or_inpatient | 2,535 | 1,876 | 1,678 | 596 | 538 | 307 | 0.99 | 229 | 28 | 24 |
| ed | 2,535 | 1,876 | 1,199 | 481 | 395 | 239 | 0.73 | 229 | 21 | <20 |
| inpatient | 2,535 | 1,876 | 658 | 296 | 208 | 126 | 0.38 | 229 | <20 | <20 |

Known persons' Fitbit days on or after 2023-10-01: 541,444

By disease, ed_or_inpatient (known + new persons >= 20):

| split Mondo | disease | known persons | still wearing after split | covered train episodes | persons | covered test episodes | persons | test per 1k wear-days | new persons | their covered test episodes | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0010030 | Sjogren syndrome | 892 | 642 | 507 | 191 | 179 | 111 | 0.98 | 69 | <20 | <20 |
| MONDO:0007915 | systemic lupus erythematosus | 579 | 404 | 497 | 154 | 116 | 59 | 1.03 | 52 | <20 | <20 |
| MONDO:0019562 | localized scleroderma | 286 | 227 | 143 | 72 | 45 | 28 | 0.65 | 25 | 0 | 0 |
| MONDO:0020640 | autoimmune encephalitis | 190 | 172 | 48 | 29 | 24 | <20 | 0.42 | 29 | <20 | <20 |
| MONDO:0009688 | myasthenia gravis | 150 | 109 | 189 | 42 | 39 | 26 | 1.42 | <20 | <20 | <20 |
| MONDO:8000010 | antiphospholipid syndrome | 150 | 104 | 104 | 35 | 28 | <20 | 0.99 | <20 | <20 | <20 |
| MONDO:0005282 | cutaneous lupus erythematosus | 142 | 96 | 151 | 36 | 38 | <20 | 1.45 | <20 | <20 | <20 |
| MONDO:0005100 | systemic sclerosis | 122 | 98 | 49 | 26 | <20 | <20 | — | <20 | <20 | <20 |
| MONDO:0019558 | discoid lupus erythematosus | 121 | 78 | 127 | 29 | 35 | <20 | 1.77 | <20 | <20 | <20 |
| MONDO:0016264 | autoimmune hepatitis | 117 | 76 | 67 | 23 | 31 | <20 | 1.31 | <20 | <20 | <20 |
| MONDO:0019527 | undifferentiated connective tissue syndrome | 91 | 77 | 31 | <20 | 23 | <20 | 0.98 | <20 | <20 | <20 |
| MONDO:0019337 | autoimmune bullous skin disease | 82 | 60 | 57 | 22 | 26 | <20 | 1.49 | <20 | 0 | 0 |
| MONDO:0030703 | autoimmune vasculitis | 53 | 36 | <20 | <20 | <20 | <20 | — | <20 | <20 | <20 |
| MONDO:0017767 | rheumatic fever | 52 | 35 | 26 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0004680 | primary thrombocytopenia | 50 | 32 | 48 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016218 | Guillain-Barre syndrome | 48 | 36 | 49 | <20 | 30 | <20 | 2.83 | <20 | 0 | 0 |
| MONDO:0020108 | autoimmune hemolytic anemia | 46 | 32 | 29 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 43 | 36 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016544 | IgG4-related mesenteritis | 35 | 21 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0005854 | mixed connective tissue disease | 30 | 22 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0850301 | pemphigoid | 30 | 20 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0019563 | CREST syndrome | 28 | 24 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0019098 | autoimmune thrombocytopenia | 28 | 24 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0015614 | dermatitis herpetiformis | 23 | <20 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0015573 | subacute cutaneous lupus erythematosus | 21 | <20 | 58 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016474 | drug-induced lupus erythematosus | 20 | <20 | <20 | <20 | <20 | <20 | — | <20 | <20 | <20 |

## By EHR source (all selected diseases)

Source = `src_id` in `visit_occurrence_ext` (All of Us obfuscated EHR source, shown here only by rank). Persons are counted at the source holding most of their visits; covered ED / inpatient episodes after dx at the source of the episode's first day. Other `*_ext` tables with `src_id`: attribute_definition_ext, care_site_ext, cohort_definition_ext, condition_era_ext, condition_occurrence_ext, cost_ext, device_cost_ext, device_exposure_ext, dose_era_ext, drug_cost_ext, drug_era_ext, drug_exposure_ext, location_ext, measurement_ext, observation_ext, observation_period_ext, payer_plan_period_ext, person_ext, procedure_cost_ext, procedure_occurrence_ext, provider_ext, sleep_daily_summary_ext, specimen_ext, survey_conduct_ext, visit_cost_ext, visit_detail_ext, visit_occurrence_ext.

Sources: 55 · with >= 20 cohort persons: 28 · with >= 20 persons with a covered episode: 12

| source | cohort persons | covered episodes | persons with one |
|---|--:|--:|--:|
| site 1 | 512 | 293 | 150 |
| site 2 | 472 | 200 | 107 |
| site 3 | 198 | 200 | 75 |
| site 4 | 185 | 204 | 69 |
| site 5 | 110 | 70 | 38 |
| site 6 | 101 | 306 | 70 |
| site 7 | 93 | 93 | 35 |
| site 8 | 92 | 102 | 30 |
| site 9 | 88 | 87 | 25 |
| site 10 | 80 | <20 | <20 |
| site 11 | 72 | 43 | 23 |
| site 12 | 70 | <20 | <20 |
| site 13 | 57 | 67 | <20 |
| site 14 | 55 | 46 | 20 |
| site 15 | 48 | 25 | <20 |
| site 16 | 46 | 39 | <20 |
| site 17 | 45 | <20 | <20 |
| site 18 | 43 | <20 | <20 |
| site 19 | 40 | 23 | <20 |
| site 20 | 40 | 22 | <20 |
| site 21 | 37 | 0 | 0 |
| site 22 | 34 | 254 | 26 |
| site 23 | 34 | <20 | <20 |
| site 24 | 29 | <20 | <20 |
| site 25 | 28 | <20 | <20 |
| site 26 | 26 | <20 | <20 |
| site 27 | 25 | <20 | <20 |
| site 28 | 20 | 36 | <20 |
| site 29 | <20 | <20 | <20 |
| site 30 | <20 | 21 | <20 |
| Participant Portal: TPC | <20 | 0 | 0 |
| site 32 | <20 | <20 | <20 |
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
