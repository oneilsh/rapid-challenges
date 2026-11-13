---
audit: wearables-events (site diagnostics)
date: 2026-11-13
command: make wearables-events-sites FOCUS='site 6'
args: --site-diagnostics --focus-site 'site 6' --under MONDO:0007179 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact (lookback 30, min-cov 14, washout 7)
commit: 5441f38
mondo: 2026-06-02
notes: >
  v9 Controlled Tier CDR (C2025Q4R6), rare autoimmune. The events report printed after
  the diagnostics is the same run's output and matches 2026-11-13-autoimmune-exact-v9-split.md
  (no split section in this run). Site 6 (89 persons) holds 2,051 of the 4,705 covered
  episodes: median 15 per person, almost all a single same-day "Inpatient Visit" (9201)
  row with no overnight stay, recurring every 8-60 days, recorded with chronic conditions
  (hypertension, hypothyroidism, hyperlipidemia) and almost no inpatient care
  procedure codes. Present every year since 2015, so it was in v8 as well. Likely
  outpatient hospital encounters coded as inpatient at that site. Without site 6: 2,654
  episodes in 810 persons. Smaller same-day-inpatient patterns at sites 15, 1, 2.
  NESTED CELLS: site 6 episodes with an inpatient row (2,047) vs all its episodes
  (2,051) imply 4 without one; do not share the per-source table beyond the team as is.
---

# EHR source diagnostics: ED / inpatient episodes (All of Us)

CDR: `wb-silky-artichoke-2408.C2025Q4R6` · run `autoimmune-disease_exact` · source = `src_id` in `visit_occurrence_ext`, labels as in that run's events report

Episodes = the pooled cohort's covered ED / inpatient episodes after the first dx (>= 14 Fitbit days in the 30 days before; visits less than 8 days apart merged), each at the source of its first day. Medians and percentiles are over persons or episodes at that source and only shown where >= 20 persons stand behind them. Columns are nested: check differences before sharing.

## Per source (>= 20 persons with an episode)

| source | persons | episodes | episodes / person, median | 90th pct | days between episodes, median | visit days / episode, median | visit rows / episode, median | episodes with inpatient row | of those, no overnight stay |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| site 6 | 89 | 2,051 | 15 | 45.2 | 27 | 1 | 1 | 2,047 | 2,009 |
| site 1 | 170 | 538 | 1 | 5 | 30 | 1 | 1 | 390 | 265 |
| site 2 | 130 | 322 | 1 | 5 | 53 | 1 | 1 | 186 | 131 |
| site 22 | 26 | 254 | 7 | 21 | 34 | 1 | 1 | <20 | <20 |
| site 3 | 79 | 227 | 2 | 6 | 121.5 | 1 | 2 | 172 | 79 |
| site 4 | 72 | 211 | 2 | 7 | 88 | 1 | 3 | 90 | <20 |
| site 15 | 27 | 159 | 3 | 10.4 | 35 | 1 | 1 | 152 | 145 |
| site 8 | 30 | 103 | 2 | 5.2 | 91 | 1 | 1 | 35 | <20 |
| site 7 | 38 | 99 | 1.5 | 4.3 | 117 | 1 | 2 | <20 | <20 |
| site 9 | 25 | 87 | 2 | 7.6 | 104.5 | 1 | 1 | <20 | 0 |
| site 5 | 38 | 71 | 1 | 4 | 178 | 1 | 1 | 27 | <20 |
| site 11 | 24 | 68 | 1.5 | 5 | 91 | 1 | 1 | 36 | 26 |
| site 14 | 20 | 48 | 1 | 5 | 95 | 1 | 1 | <20 | <20 |

## Focus: site 6 against all other sources

Chosen with --focus-site.

### Episodes by start year

| year | focus episodes | persons | other episodes | persons |
|--:|--:|--:|--:|--:|
| 2012 | 0 | 0 | <20 | <20 |
| 2013 | <20 | <20 | <20 | <20 |
| 2014 | <20 | <20 | <20 | <20 |
| 2015 | 29 | <20 | <20 | <20 |
| 2016 | 67 | <20 | 39 | 20 |
| 2017 | 97 | <20 | 96 | 55 |
| 2018 | 147 | 22 | 135 | 58 |
| 2019 | 189 | 27 | 230 | 108 |
| 2020 | 214 | 33 | 222 | 111 |
| 2021 | 258 | 35 | 326 | 162 |
| 2022 | 242 | 38 | 451 | 211 |
| 2023 | 414 | 68 | 702 | 375 |
| 2024 | 380 | 59 | 435 | 256 |

### Days between a person's consecutive episodes (same group)

| days | focus | other |
|---|--:|--:|
| 8-13 | 334 | 177 |
| 14-20 | 414 | 205 |
| 21-30 | 384 | 242 |
| 31-60 | 477 | 310 |
| 61-180 | 303 | 496 |
| 181+ | 50 | 414 |

### Visit concepts on the episodes' visit rows

| visit concept | name | focus rows | persons | other rows | persons |
|--:|---|--:|--:|--:|--:|
| 9201 | Inpatient Visit | 4,351 | 89 | 1,778 | 338 |
| 9203 | Emergency Room Visit | 76 | 30 | 2,205 | 591 |
| 262 | Emergency Room and Inpatient Visit | 22 | <20 | 118 | 41 |
| 8717 | Inpatient Hospital | <20 | <20 | 858 | 89 |
| 8870 | Emergency Room - Hospital | 0 | 0 | <20 | <20 |
| 38004515 | Hospital | 0 | 0 | 443 | 43 |

### Top conditions on the focus source's episode visits (by episodes)

| concept | name | focus episodes | persons | other episodes | persons |
|--:|---|--:|--:|--:|--:|
| 320128 | Essential hypertension | 66 | 25 | 411 | 180 |
| 140673 | Hypothyroidism | 38 | <20 | 169 | 94 |
| 138384 | Acquired hypothyroidism | 34 | <20 | <20 | <20 |
| 432867 | Hyperlipidemia | 34 | <20 | 231 | 124 |
| 257628 | Systemic lupus erythematosus | 24 | <20 | 98 | 50 |
| 312437 | Dyspnea | 21 | <20 | 192 | 112 |
| 4305080 | Abnormal breathing | 20 | <20 | <20 | <20 |
| 4193704 | Type 2 diabetes mellitus without complication | <20 | <20 | 166 | 71 |
| 77670 | Chest pain | <20 | <20 | 222 | 152 |
| 436070 | Vitamin D deficiency | <20 | <20 | 29 | 22 |
| 437833 | Hypokalemia | <20 | <20 | 58 | 41 |
| 140190 | Disorder of back | <20 | <20 | <20 | <20 |
| 4002818 | Spasm of back muscles | <20 | <20 | <20 | <20 |
| 437827 | Pure hypercholesterolemia | <20 | <20 | 78 | 29 |
| 440704 | Chronic pain syndrome | <20 | <20 | 21 | <20 |

### Top procedures on the focus source's episode visits (by episodes)

| concept | name | focus episodes | persons | other episodes | persons |
|--:|---|--:|--:|--:|--:|
| 2313815 | Electrocardiogram, routine ECG with at least 12 le | 39 | 26 | 251 | 140 |
| 2313816 | Electrocardiogram, routine ECG with at least 12 le | 36 | 23 | 249 | 132 |
| 2213283 | Level IV - Surgical pathology, gross and microscop | 29 | 21 | 62 | 49 |
| 2314215 | Therapeutic, prophylactic, or diagnostic injection | <20 | <20 | 143 | 97 |
| 2314216 | Therapeutic, prophylactic, or diagnostic injection | <20 | <20 | 107 | 68 |
| 42628094 | Moderate sedation services provided by the same ph | <20 | <20 | <20 | <20 |
| 2314205 | Intravenous infusion, hydration; each additional h | <20 | <20 | 104 | 72 |
| 725068 | Radiologic examination, chest; single view | <20 | <20 | 122 | 73 |
| 2314047 | Noninvasive ear or pulse oximetry for oxygen satur | <20 | <20 | 34 | <20 |
| 2514408 | Subsequent hospital inpatient or observation care, | <20 | <20 | 126 | 75 |
| 2514405 | Initial hospital inpatient or observation care, pe | <20 | <20 | 74 | 52 |
| 2514409 | Subsequent hospital inpatient or observation care, | <20 | <20 | 112 | 63 |
| 2514414 | Hospital inpatient or observation discharge day ma | <20 | <20 | 84 | 52 |
| 2314213 | Therapeutic, prophylactic, or diagnostic injection | <20 | <20 | 55 | 37 |
| 2514406 | Initial hospital inpatient or observation care, pe | <20 | <20 | 115 | 63 |

## Pooled episodes with and without the focus source

| | episodes | persons with one |
|---|--:|--:|
| all sources | 4,705 | 897 |
| without site 6 | 2,654 | 810 |

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
