---
audit: wearables-events (with split and site diagnostics)
date: 2026-11-13
command: make wearables-events-sites FOCUS='site 6' ARGS='--ip-overnight --after 2023-10-01'
args: --site-diagnostics --focus-site 'site 6' --ip-overnight --after 2023-10-01 --under MONDO:0007179 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact (lookback 30, min-cov 14, washout 7)
commit: 4793d47
mondo: 2026-06-02
notes: >
  v9 Controlled Tier CDR (C2025Q4R6), rare autoimmune, inpatient = episode whose
  inpatient rows span a night (first version of --ip-overnight: latest inpatient end
  after earliest inpatient start within the episode). That rule is LEAKY: separate
  same-day inpatient rows a few days apart in one episode count as a stay. Site 6 drops
  from 2,051 to 716 covered episodes, but 674 of its 712 remaining inpatient episodes
  have no single row spanning a night (median 2 visit days, 3 rows per episode).
  Pooled: 2,783 covered episodes in 825 persons (1.42 per 1k wear-days); split test
  set 678 episodes in 335 known persons plus 40 in 28 new. Superseded by the
  row-or-consecutive-day rule (see the next run). NESTED CELLS: as in the earlier
  files (class rows, per-source inpatient columns).
---

# EHR source diagnostics: ED / inpatient episodes (All of Us)

CDR: `wb-silky-artichoke-2408.C2025Q4R6` · run `autoimmune-disease_exact` · source = `src_id` in `visit_occurrence_ext`, labels as in that run's events report

Episodes = the pooled cohort's covered ED / inpatient episodes after the first dx (>= 14 Fitbit days in the 30 days before; visits less than 8 days apart merged; inpatient only with an overnight stay), each at the source of its first day. Medians and percentiles are over persons or episodes at that source and only shown where >= 20 persons stand behind them. Columns are nested: check differences before sharing.

## Per source (>= 20 persons with an episode)

| source | persons | episodes | episodes / person, median | 90th pct | days between episodes, median | visit days / episode, median | visit rows / episode, median | episodes with inpatient row | of those, no overnight stay |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| site 6 | 82 | 716 | 5 | 16.9 | 54.5 | 2 | 3 | 712 | 674 |
| site 1 | 157 | 334 | 1 | 3 | 45 | 1 | 1 | 186 | 61 |
| site 22 | 26 | 254 | 7 | 21 | 34 | 1 | 1 | <20 | <20 |
| site 2 | 112 | 223 | 1 | 4 | 87 | 1 | 1 | 87 | 32 |
| site 4 | 69 | 204 | 2 | 7 | 86 | 1 | 3 | 83 | <20 |
| site 3 | 75 | 203 | 2 | 5.6 | 125 | 1 | 2 | 148 | 55 |
| site 8 | 30 | 102 | 2 | 5.2 | 85.5 | 1 | 1 | 34 | 0 |
| site 7 | 35 | 93 | 2 | 4.6 | 113 | 1 | 2 | <20 | <20 |
| site 9 | 25 | 87 | 2 | 7.6 | 104.5 | 1 | 1 | <20 | 0 |
| site 15 | 22 | 74 | 2 | 7.8 | 46 | 3 | 3 | 67 | 60 |
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
| 2017 | 38 | <20 | 83 | 53 |
| 2018 | 42 | <20 | 111 | 52 |
| 2019 | 61 | <20 | 182 | 99 |
| 2020 | 69 | 25 | 181 | 96 |
| 2021 | 71 | 25 | 242 | 137 |
| 2022 | 94 | 31 | 342 | 182 |
| 2023 | 166 | 58 | 561 | 326 |
| 2024 | 146 | 47 | 326 | 225 |

### Days between a person's consecutive episodes (same group)

| days | focus | other |
|---|--:|--:|
| 8-13 | 26 | 107 |
| 14-20 | 68 | 113 |
| 21-30 | 93 | 169 |
| 31-60 | 164 | 215 |
| 61-180 | 189 | 374 |
| 181+ | 94 | 344 |

### Visit concepts on the episodes' visit rows

| visit concept | name | focus rows | persons | other rows | persons |
|--:|---|--:|--:|--:|--:|
| 9201 | Inpatient Visit | 2,729 | 82 | 1,513 | 289 |
| 9203 | Emergency Room Visit | 76 | 30 | 2,205 | 591 |
| 262 | Emergency Room and Inpatient Visit | 22 | <20 | 118 | 41 |
| 8717 | Inpatient Hospital | <20 | <20 | 610 | 63 |
| 8870 | Emergency Room - Hospital | 0 | 0 | <20 | <20 |
| 38004515 | Hospital | 0 | 0 | 302 | 24 |

### Top conditions on the focus source's episode visits (by episodes)

| concept | name | focus episodes | persons | other episodes | persons |
|--:|---|--:|--:|--:|--:|
| 320128 | Essential hypertension | 43 | 21 | 378 | 167 |
| 140673 | Hypothyroidism | 24 | <20 | 160 | 91 |
| 432867 | Hyperlipidemia | 21 | <20 | 202 | 109 |
| 138384 | Acquired hypothyroidism | 20 | <20 | <20 | <20 |
| 77670 | Chest pain | <20 | <20 | 210 | 143 |
| 257628 | Systemic lupus erythematosus | <20 | <20 | 92 | 47 |
| 437833 | Hypokalemia | <20 | <20 | 55 | 39 |
| 4193704 | Type 2 diabetes mellitus without complication | <20 | <20 | 152 | 66 |
| 436070 | Vitamin D deficiency | <20 | <20 | 21 | <20 |
| 313217 | Atrial fibrillation | <20 | <20 | 85 | 31 |
| 312437 | Dyspnea | <20 | <20 | 180 | 104 |
| 4209423 | Nicotine dependence | <20 | <20 | 49 | 24 |
| 140190 | Disorder of back | <20 | <20 | <20 | <20 |
| 4002818 | Spasm of back muscles | <20 | <20 | <20 | <20 |
| 254443 | Sjögren's syndrome | <20 | <20 | 56 | 35 |

### Top procedures on the focus source's episode visits (by episodes)

| concept | name | focus episodes | persons | other episodes | persons |
|--:|---|--:|--:|--:|--:|
| 2313815 | Electrocardiogram, routine ECG with at least 12 le | 38 | 25 | 241 | 135 |
| 2313816 | Electrocardiogram, routine ECG with at least 12 le | 35 | 22 | 245 | 129 |
| 2213283 | Level IV - Surgical pathology, gross and microscop | <20 | <20 | 48 | 40 |
| 2314215 | Therapeutic, prophylactic, or diagnostic injection | <20 | <20 | 135 | 90 |
| 2314216 | Therapeutic, prophylactic, or diagnostic injection | <20 | <20 | 103 | 64 |
| 2314047 | Noninvasive ear or pulse oximetry for oxygen satur | <20 | <20 | 34 | <20 |
| 2314205 | Intravenous infusion, hydration; each additional h | <20 | <20 | 99 | 67 |
| 2514408 | Subsequent hospital inpatient or observation care, | <20 | <20 | 122 | 71 |
| 725068 | Radiologic examination, chest; single view | <20 | <20 | 118 | 69 |
| 2514405 | Initial hospital inpatient or observation care, pe | <20 | <20 | 71 | 49 |
| 2514409 | Subsequent hospital inpatient or observation care, | <20 | <20 | 112 | 63 |
| 2514414 | Hospital inpatient or observation discharge day ma | <20 | <20 | 82 | 50 |
| 42628094 | Moderate sedation services provided by the same ph | <20 | <20 | <20 | <20 |
| 2314213 | Therapeutic, prophylactic, or diagnostic injection | <20 | <20 | 51 | 33 |
| 2514406 | Initial hospital inpatient or observation care, pe | <20 | <20 | 112 | 61 |

## Pooled episodes with and without the focus source

| | episodes | persons with one |
|---|--:|--:|
| all sources | 2,783 | 825 |
| without site 6 | 2,067 | 745 |

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

Event = an acute-care episode: ED / inpatient visit starts, with visits less than 8 days apart merged, dated by its first day. After / before = strictly after / before the first diagnosis (the dx day itself is excluded). Inpatient = inpatient visits spanning at least one night (same-day inpatient rows dropped). Covered = >= 14 Fitbit days in the 30 days before the event. Cohort = persons with the disease and any Fitbit day. Columns are nested: check differences before sharing.

## All selected diseases

Persons with a selected diagnosis: 23,481 · with Fitbit data: 2,838 · their Fitbit days after dx: 1,959,779

| event class | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| ed_or_inpatient | 10,546 | 1,594 | 2,783 | 825 | 450 | 1.42 | 821 | 269 |
| ed | 6,653 | 1,323 | 1,615 | 639 | 307 | 0.82 | 492 | 199 |
| inpatient | 5,022 | 952 | 1,449 | 436 | 195 | 0.74 | 414 | 140 |

Pooled events after dx by Fitbit days in the 30 days before them:

| event class | 0 | 1-6 | 7-13 | 14-20 | 21+ |
|---|--:|--:|--:|--:|--:|
| ed_or_inpatient | 7,367 | 213 | 183 | 244 | 2,539 |

## By disease (persons with Fitbit data >= 20)

### ed_or_inpatient

| Mondo | disease | with data | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0010030 | Sjogren syndrome | 993 | 3,584 | 556 | 884 | 277 | 158 | 1.37 | 332 | 105 |
| MONDO:0007915 | systemic lupus erythematosus | 645 | 3,135 | 389 | 764 | 194 | 112 | 1.77 | 118 | 38 |
| MONDO:0019562 | localized scleroderma | 317 | 919 | 172 | 222 | 91 | 47 | 0.78 | 85 | 27 |
| MONDO:0020640 | autoimmune encephalitis | 220 | 215 | 79 | 87 | 49 | <20 | 0.63 | 37 | 23 |
| MONDO:8000010 | antiphospholipid syndrome | 172 | 771 | 108 | 194 | 48 | 27 | 1.96 | 66 | 25 |
| MONDO:0009688 | myasthenia gravis | 169 | 808 | 108 | 269 | 63 | 31 | 2.42 | 44 | <20 |
| MONDO:0005282 | cutaneous lupus erythematosus | 152 | 822 | 95 | 253 | 45 | 33 | 2.36 | 46 | <20 |
| MONDO:0016264 | autoimmune hepatitis | 132 | 327 | 65 | 108 | 35 | 20 | 1.14 | 30 | <20 |
| MONDO:0005100 | systemic sclerosis | 132 | 408 | 72 | 93 | 37 | <20 | 0.99 | 33 | <20 |
| MONDO:0019558 | discoid lupus erythematosus | 129 | 726 | 83 | 226 | 39 | 29 | 2.59 | 43 | <20 |
| MONDO:0019527 | undifferentiated connective tissue syndrome | 112 | 193 | 55 | 77 | 32 | <20 | 1.05 | 22 | <20 |
| MONDO:0019337 | autoimmune bullous skin disease | 94 | 438 | 56 | 96 | 32 | <20 | 1.99 | 45 | <20 |
| MONDO:0017767 | rheumatic fever | 59 | 152 | 32 | 31 | <20 | <20 | 0.74 | 38 | <20 |
| MONDO:0030703 | autoimmune vasculitis | 58 | 393 | 38 | 35 | <20 | <20 | 0.89 | <20 | <20 |
| MONDO:0004680 | primary thrombocytopenia | 54 | 287 | 35 | 59 | <20 | <20 | 1.28 | 47 | <20 |
| MONDO:0020108 | autoimmune hemolytic anemia | 51 | 163 | 28 | 38 | <20 | <20 | 1.24 | <20 | <20 |
| MONDO:0016218 | Guillain-Barre syndrome | 51 | 243 | 34 | 122 | 20 | <20 | 3.71 | 22 | <20 |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 45 | 144 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0016544 | IgG4-related mesenteritis | 43 | 98 | 28 | 24 | <20 | <20 | 1.19 | 22 | <20 |
| MONDO:0005854 | mixed connective tissue disease | 41 | 145 | 22 | 30 | <20 | <20 | 1.58 | <20 | <20 |
| MONDO:0850301 | pemphigoid | 34 | 87 | 23 | 20 | <20 | <20 | 1.15 | 35 | <20 |
| MONDO:0019098 | autoimmune thrombocytopenia | 30 | 131 | <20 | 28 | <20 | <20 | 1.23 | <20 | <20 |
| MONDO:0019563 | CREST syndrome | 29 | 47 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0015614 | dermatitis herpetiformis | 27 | 115 | <20 | 23 | <20 | <20 | 1.54 | <20 | <20 |
| MONDO:0016474 | drug-induced lupus erythematosus | 26 | 39 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0015573 | subacute cutaneous lupus erythematosus | 23 | 166 | <20 | 76 | <20 | <20 | 5.16 | <20 | <20 |

## Prospective split at 2023-10-01

Known = diagnosed and with a Fitbit day before 2023-10-01 (would be in a release cut then); new = everyone else in the cohort with Fitbit days after dx on or after 2023-10-01. Train = covered episodes after dx and before 2023-10-01; test = covered episodes on or after 2023-10-01. Follow-up after the split: about 14.1 months of Fitbit data and 15.0 months of visits. "Known" is by date only, so it slightly overcounts persons in the earlier release (late EHR records, Fitbit history synced later); test counts are exact. Columns are nested.

| split class | known persons | still wearing after split | covered train episodes | persons | covered test episodes | persons | test per 1k wear-days | new persons | their covered test episodes | persons |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| ed_or_inpatient | 2,535 | 1,876 | 2,065 | 628 | 678 | 335 | 1.25 | 229 | 40 | 28 |
| ed | 2,535 | 1,876 | 1,199 | 481 | 395 | 239 | 0.73 | 229 | 21 | <20 |
| inpatient | 2,535 | 1,876 | 1,072 | 341 | 357 | 158 | 0.66 | 229 | 20 | <20 |

Known persons' Fitbit days on or after 2023-10-01: 541,444

By disease, ed_or_inpatient (known + new persons >= 20):

| split Mondo | disease | known persons | still wearing after split | covered train episodes | persons | covered test episodes | persons | test per 1k wear-days | new persons | their covered test episodes | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0010030 | Sjogren syndrome | 892 | 642 | 624 | 205 | 237 | 120 | 1.30 | 69 | 23 | <20 |
| MONDO:0007915 | systemic lupus erythematosus | 579 | 404 | 624 | 160 | 133 | 63 | 1.18 | 52 | <20 | <20 |
| MONDO:0019562 | localized scleroderma | 286 | 227 | 163 | 74 | 59 | 32 | 0.85 | 25 | 0 | 0 |
| MONDO:0020640 | autoimmune encephalitis | 190 | 172 | 49 | 30 | 31 | 20 | 0.54 | 29 | <20 | <20 |
| MONDO:8000010 | antiphospholipid syndrome | 150 | 104 | 153 | 36 | 39 | 22 | 1.38 | <20 | <20 | <20 |
| MONDO:0009688 | myasthenia gravis | 150 | 109 | 213 | 44 | 49 | 27 | 1.78 | <20 | <20 | <20 |
| MONDO:0005282 | cutaneous lupus erythematosus | 142 | 96 | 205 | 39 | 45 | <20 | 1.72 | <20 | <20 | <20 |
| MONDO:0005100 | systemic sclerosis | 122 | 98 | 65 | 28 | 23 | <20 | 0.81 | <20 | <20 | <20 |
| MONDO:0019558 | discoid lupus erythematosus | 121 | 78 | 181 | 32 | 42 | <20 | 2.13 | <20 | <20 | <20 |
| MONDO:0016264 | autoimmune hepatitis | 117 | 76 | 69 | 23 | 37 | <20 | 1.57 | <20 | <20 | <20 |
| MONDO:0019527 | undifferentiated connective tissue syndrome | 91 | 77 | 51 | <20 | 23 | <20 | 0.98 | <20 | <20 | <20 |
| MONDO:0019337 | autoimmune bullous skin disease | 82 | 60 | 67 | 25 | 29 | <20 | 1.66 | <20 | 0 | 0 |
| MONDO:0030703 | autoimmune vasculitis | 53 | 36 | 22 | <20 | <20 | <20 | — | <20 | <20 | <20 |
| MONDO:0017767 | rheumatic fever | 52 | 35 | 26 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0004680 | primary thrombocytopenia | 50 | 32 | 48 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016218 | Guillain-Barre syndrome | 48 | 36 | 85 | <20 | 37 | <20 | 3.49 | <20 | 0 | 0 |
| MONDO:0020108 | autoimmune hemolytic anemia | 46 | 32 | 33 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 43 | 36 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016544 | IgG4-related mesenteritis | 35 | 21 | 20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0005854 | mixed connective tissue disease | 30 | 22 | 23 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0850301 | pemphigoid | 30 | 20 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0019098 | autoimmune thrombocytopenia | 28 | 24 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0019563 | CREST syndrome | 28 | 24 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0015614 | dermatitis herpetiformis | 23 | <20 | <20 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0015573 | subacute cutaneous lupus erythematosus | 21 | <20 | 61 | <20 | <20 | <20 | — | <20 | 0 | 0 |
| MONDO:0016474 | drug-induced lupus erythematosus | 20 | <20 | <20 | <20 | <20 | <20 | — | <20 | <20 | <20 |

## By EHR source (all selected diseases)

Source = `src_id` in `visit_occurrence_ext` (All of Us obfuscated EHR source, shown here only by rank). Persons are counted at the source holding most of their visits; covered ED / inpatient episodes after dx at the source of the episode's first day. Other `*_ext` tables with `src_id`: attribute_definition_ext, care_site_ext, cohort_definition_ext, condition_era_ext, condition_occurrence_ext, cost_ext, device_cost_ext, device_exposure_ext, dose_era_ext, drug_cost_ext, drug_era_ext, drug_exposure_ext, location_ext, measurement_ext, observation_ext, observation_period_ext, payer_plan_period_ext, person_ext, procedure_cost_ext, procedure_occurrence_ext, provider_ext, sleep_daily_summary_ext, specimen_ext, survey_conduct_ext, visit_cost_ext, visit_detail_ext, visit_occurrence_ext.

Sources: 55 · with >= 20 cohort persons: 28 · with >= 20 persons with a covered episode: 13

| source | cohort persons | covered episodes | persons with one |
|---|--:|--:|--:|
| site 1 | 512 | 334 | 157 |
| site 2 | 472 | 223 | 112 |
| site 3 | 198 | 203 | 75 |
| site 4 | 185 | 204 | 69 |
| site 5 | 110 | 70 | 38 |
| site 6 | 101 | 716 | 82 |
| site 7 | 93 | 93 | 35 |
| site 8 | 92 | 102 | 30 |
| site 9 | 88 | 87 | 25 |
| site 10 | 80 | <20 | <20 |
| site 11 | 72 | 43 | 23 |
| site 12 | 70 | <20 | <20 |
| site 13 | 57 | 67 | <20 |
| site 14 | 55 | 46 | 20 |
| site 15 | 48 | 74 | 22 |
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
