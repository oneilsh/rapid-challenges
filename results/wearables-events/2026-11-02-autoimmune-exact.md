---
audit: wearables-events
date: 2026-11-02
command: make wearables-events
args: --under MONDO:0007179 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact (lookback 30, min-cov 14, washout 7)
commit: 7a730d8
mondo: 2026-06-02
notes: >
  v8 CDR, rare autoimmune, events = acute-care episodes (ED / inpatient visit starts
  within 7 days merged). 2,282 covered episodes after dx in 414 persons (241 with >= 2):
  2.33 per 1,000 Fitbit days, about a 7% chance per 30-day window. Disease-related
  ("related") episodes: 317 covered in 115 persons. Per disease: Sjogren 825 / 154
  persons, SLE 577 / 99, localized scleroderma 174 / 49, myasthenia gravis 228 / 28.
  74% of episodes after dx have no Fitbit day in the 30 days before. Localized
  scleroderma has more covered episodes before its dx (214) than after (174). The
  report's "Related" definition line still says "visit or day"; it means any visit or
  day of the episode. NESTED CELLS: some differences between published cells are small
  counts.
---

# Wearables x ED / inpatient events (All of Us)

CDR: `wb-affable-acorn-7941.R2024Q3R8`

Fitbit tables: activity_summary, heart_rate_summary, sleep_daily_summary · rare = Mondo subsets orphanet_rare, gard_rare, nord_rare, mondo_rare · 102 diseases mapped

Scope: under MONDO:0007179 · exact SNOMED-only mapping

Event = an acute-care episode: ED / inpatient visit starts, with visits less than 8 days apart merged, dated by its first day. After / before = strictly after / before the first diagnosis (the dx day itself is excluded). Covered = >= 14 Fitbit days in the 30 days before the event. Related = the disease coded on that visit or day. Cohort = persons with the disease and any Fitbit day. Columns are nested: check differences before sharing.

## All selected diseases

Persons with a selected diagnosis: 17,127 · with Fitbit data: 1,808 · their Fitbit days after dx: 978,181

| event class | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| ed_or_inpatient | 9,877 | 940 | 2,282 | 414 | 241 | 2.33 | 775 | 137 |
| ed | 4,104 | 691 | 743 | 256 | 126 | 0.76 | 221 | 88 |
| inpatient | 6,693 | 713 | 1,730 | 292 | 157 | 1.77 | 621 | 95 |
| related | 1,541 | 333 | 317 | 115 | 55 | 0.32 | <20 | <20 |

Pooled events after dx by Fitbit days in the 30 days before them:

| event class | 0 | 1-6 | 7-13 | 14-20 | 21+ |
|---|--:|--:|--:|--:|--:|
| ed_or_inpatient | 7,262 | 181 | 152 | 172 | 2,110 |
| related | 1,187 | 24 | <20 | 22 | 295 |

## By disease (persons with Fitbit data >= 20)

### ed_or_inpatient

| Mondo | disease | with data | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0010030 | Sjogren syndrome | 712 | 3,690 | 351 | 825 | 154 | 94 | 2.30 | 250 | 53 |
| MONDO:0007915 | systemic lupus erythematosus | 444 | 2,920 | 244 | 577 | 99 | 57 | 2.44 | 86 | <20 |
| MONDO:0019562 | localized scleroderma | 201 | 828 | 101 | 174 | 49 | 25 | 1.18 | 214 | 20 |
| MONDO:0009688 | myasthenia gravis | 117 | 580 | 55 | 228 | 28 | <20 | 3.43 | 28 | <20 |
| MONDO:0005282 | cutaneous lupus erythematosus | 105 | 928 | 65 | 278 | 29 | 21 | 4.81 | 95 | <20 |
| MONDO:8000010 | antiphospholipid syndrome | 99 | 814 | 61 | 110 | 21 | <20 | 2.90 | 81 | <20 |
| MONDO:0005100 | systemic sclerosis | 98 | 492 | 48 | 131 | <20 | <20 | 2.65 | 22 | <20 |
| MONDO:0019558 | discoid lupus erythematosus | 95 | 857 | 59 | 261 | 25 | <20 | 5.00 | 96 | <20 |
| MONDO:0016264 | autoimmune hepatitis | 72 | 217 | 33 | 50 | <20 | <20 | 1.48 | 27 | <20 |
| MONDO:0017767 | rheumatic fever | 61 | 174 | 35 | 34 | <20 | <20 | 0.93 | 23 | <20 |
| MONDO:0020640 | autoimmune encephalitis | 45 | <20 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0004680 | primary thrombocytopenia | 43 | 255 | 31 | 41 | <20 | <20 | 1.32 | 33 | <20 |
| MONDO:0030703 | autoimmune vasculitis | 37 | 415 | 21 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0019337 | autoimmune bullous skin disease | 37 | 324 | 21 | 78 | <20 | <20 | 5.59 | <20 | <20 |
| MONDO:0016218 | Guillain-Barre syndrome | 34 | 132 | 21 | 39 | <20 | <20 | 3.01 | <20 | <20 |
| MONDO:0020108 | autoimmune hemolytic anemia | 32 | 133 | <20 | 58 | <20 | <20 | 3.74 | 22 | <20 |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 27 | 175 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0019563 | CREST syndrome | 25 | 21 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0016544 | IgG4-related mesenteritis | 25 | 98 | <20 | <20 | <20 | <20 | — | 23 | <20 |

### related

| Mondo | disease | with data | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0010030 | Sjogren syndrome | 712 | 392 | 103 | 79 | 36 | <20 | 0.22 | <20 | <20 |
| MONDO:0007915 | systemic lupus erythematosus | 444 | 543 | 130 | 77 | 34 | <20 | 0.33 | <20 | <20 |
| MONDO:0019562 | localized scleroderma | 201 | 67 | <20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0009688 | myasthenia gravis | 117 | 136 | 20 | 28 | <20 | <20 | 0.42 | 0 | 0 |
| MONDO:0005282 | cutaneous lupus erythematosus | 105 | 96 | <20 | 24 | <20 | <20 | 0.42 | 0 | 0 |
| MONDO:8000010 | antiphospholipid syndrome | 99 | 155 | 29 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0005100 | systemic sclerosis | 98 | 135 | <20 | 56 | <20 | <20 | 1.13 | 0 | 0 |
| MONDO:0019558 | discoid lupus erythematosus | 95 | 77 | <20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0016264 | autoimmune hepatitis | 72 | 38 | <20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0017767 | rheumatic fever | 61 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0020640 | autoimmune encephalitis | 45 | 0 | 0 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0004680 | primary thrombocytopenia | 43 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0030703 | autoimmune vasculitis | 37 | <20 | <20 | <20 | <20 | 0 | — | 0 | 0 |
| MONDO:0019337 | autoimmune bullous skin disease | 37 | 22 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0016218 | Guillain-Barre syndrome | 34 | 21 | <20 | <20 | <20 | 0 | — | 0 | 0 |
| MONDO:0020108 | autoimmune hemolytic anemia | 32 | 21 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 27 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0019563 | CREST syndrome | 25 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0016544 | IgG4-related mesenteritis | 25 | <20 | <20 | 0 | 0 | 0 | — | <20 | <20 |

## Visit types for the cohort (top 15 by visits)

| visit concept | name | visits | persons |
|--:|---|--:|--:|
| 9202 | Outpatient Visit | 385,099 | 1,766 |
| 581477 | Office Visit | 89,131 | 783 |
| 32036 | Laboratory Visit | 42,723 | 805 |
| 581458 | Pharmacy visit | 32,762 | 286 |
| 5083 | Telehealth | 25,068 | 464 |
| 9201 | Inpatient Visit | 22,867 | 836 |
| 42898160 | Non-hospital institution Visit | 11,273 | 91 |
| 9203 | Emergency Room Visit | 9,970 | 866 |
| 581479 | Ambulatory Rehabilitation Visit | 5,786 | 221 |
| 8756 | Outpatient Hospital | 3,134 | 121 |
| 38004515 | Hospital | 2,345 | 54 |
| 581385 | Observation Room | 1,871 | 87 |
| 581476 | Home Visit | 1,239 | 142 |
| 262 | Emergency Room and Inpatient Visit | 995 | 212 |
| 8717 | Inpatient Hospital | 611 | 70 |
