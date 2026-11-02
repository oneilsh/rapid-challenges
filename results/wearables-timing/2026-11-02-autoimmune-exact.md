---
audit: wearables-timing
date: 2026-11-02
command: make wearables-timing-autoimmune
args: --under MONDO:0007179 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact
commit: 43bff75
mondo: 2026-06-02
notes: >
  v8 CDR (R2024Q3R8). Same 102 rare autoimmune diseases as
  wearables-rare/2026-10-20-autoimmune-exact.md. Of 1,808 diagnosed persons with any
  Fitbit day, 482 have data before their first diagnosis and 306 have >= 30 days in
  both the year before and the year after (Sjogren 129, SLE 47, localized scleroderma
  40; every other disease near or under 20). Pre-dx data is real when present: median
  471 days, starting a median 978 days before the diagnosis. NESTED CELLS: some
  differences between published cells are small counts (e.g. any vs activity_summary
  before, 482 vs 479; sleep_daily_summary vs sleep_level after, 387 vs 386; myasthenia
  gravis >= 1 day before vs >= 30 in 365 before, 29 vs 20). Fine inside the team;
  suppress or drop columns before sharing outside it.
---

# Wearables data before and after first diagnosis (All of Us)

CDR: `wb-affable-acorn-7941.R2024Q3R8`

Fitbit tables: activity_summary, heart_rate_summary, sleep_daily_summary, heart_rate_minute_level, steps_intraday, sleep_level · rare = Mondo subsets orphanet_rare, gard_rare, nord_rare, mondo_rare · 102 diseases mapped

Scope: under MONDO:0007179 · exact SNOMED-only mapping

Days = distinct days with any row in that table. Before = strictly before the first diagnosis; after = that day or later. Medians are shown as median (p25–p75), and only where >= 20 persons are behind them. Columns are nested, so differences between cells can be small counts: check before sharing.

## All selected diseases, by kind of data

Persons with any selected diagnosis: 17,127 (first diagnosis = earliest among the selected diseases).

| kind | persons | ≥1 day before | ≥1 day after | ≥30 days in 365 before | ≥30 days in 365 after | both | days before | days after | first wear → dx (days) | dx → last wear (days) |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| any | 1,808 | 482 | 1,732 | 363 | 489 | 306 | 471 (180–1,052) | 246 (96–833) | 978 (348–1,755) | 2,034 (940–3,313) |
| activity_summary | 1,799 | 479 | 1,723 | 356 | 488 | 301 | 462 (177–1,050) | 247 (96–819) | 980 (352–1,754) | 2,038 (939–3,314) |
| heart_rate_minute_level | 1,697 | 337 | 1,623 | 242 | 374 | 193 | 348 (129–710) | 121 (70–578) | 702 (327–1,370) | 2,039 (939–3,336) |
| heart_rate_summary | 1,732 | 344 | 1,664 | 248 | 394 | 205 | 350 (128–706) | 157 (77–622) | 694 (315–1,324) | 2,025 (937–3,310) |
| sleep_daily_summary | 1,727 | 433 | 1,639 | 270 | 387 | 213 | 234 (70–667) | 106 (57–559) | 986 (362–1,731) | 2,046 (941–3,315) |
| sleep_level | 1,727 | 433 | 1,639 | 270 | 386 | 213 | 234 (70–667) | 106 (57–559) | 986 (362–1,731) | 2,046 (941–3,315) |
| steps_intraday | 1,797 | 450 | 1,720 | 329 | 463 | 273 | 506 (176–1,100) | 212 (87–770) | 1,047 (394–1,828) | 2,039 (940–3,313) |

Persons by number of days before the first diagnosis:

| kind | 1-29 | 30-89 | 90-364 | 365-729 | 730+ |
|---|--:|--:|--:|--:|--:|
| any | 32 | 48 | 133 | 90 | 179 |
| activity_summary | 35 | 46 | 133 | 89 | 176 |
| heart_rate_minute_level | 31 | 34 | 111 | 79 | 82 |
| heart_rate_summary | 32 | 36 | 111 | 83 | 82 |
| sleep_daily_summary | 63 | 65 | 127 | 83 | 95 |
| sleep_level | 63 | 65 | 127 | 83 | 95 |
| steps_intraday | 36 | 42 | 113 | 90 | 169 |

Persons by number of days after the first diagnosis:

| kind | 1-29 | 30-89 | 90-364 | 365-729 | 730+ |
|---|--:|--:|--:|--:|--:|
| any | 107 | 257 | 597 | 291 | 480 |
| activity_summary | 105 | 258 | 591 | 298 | 471 |
| heart_rate_minute_level | 152 | 439 | 486 | 226 | 320 |
| heart_rate_summary | 142 | 402 | 521 | 243 | 356 |
| sleep_daily_summary | 250 | 439 | 417 | 232 | 301 |
| sleep_level | 251 | 438 | 417 | 232 | 301 |
| steps_intraday | 109 | 368 | 550 | 236 | 457 |

## By disease (any kind of data; persons with data >= 20; top 40)

| Mondo | disease | n_dx | with data | ≥1 day before | ≥1 day after | ≥30 in 365 before | ≥30 in 365 after | both | days before | days after |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0010030 | Sjogren syndrome | 5,474 | 712 | 201 | 674 | 149 | 206 | 129 | 511 (188–1,078) | 221 (95–776) |
| MONDO:0007915 | systemic lupus erythematosus | 4,989 | 444 | 81 | 431 | 63 | 84 | 47 | 327 (115–796) | 270 (99–812) |
| MONDO:0019562 | localized scleroderma | 1,491 | 201 | 56 | 193 | 46 | 56 | 40 | 523 (162–1,183) | 389 (95–1,233) |
| MONDO:0009688 | myasthenia gravis | 787 | 117 | 29 | 112 | 20 | 33 | <20 | 400 (202–971) | 182 (93–872) |
| MONDO:0005282 | cutaneous lupus erythematosus | 1,260 | 105 | 30 | 102 | 22 | 26 | <20 | 566 (140–1,086) | 270 (92–929) |
| MONDO:8000010 | antiphospholipid syndrome | 1,389 | 99 | 34 | 94 | 24 | 26 | 21 | 508 (174–1,153) | 118 (94–614) |
| MONDO:0005100 | systemic sclerosis | 1,057 | 98 | 22 | 95 | <20 | 23 | <20 | 498 (232–834) | 129 (92–960) |
| MONDO:0019558 | discoid lupus erythematosus | 1,184 | 95 | 30 | 92 | 22 | 24 | <20 | 566 (124–1,086) | 267 (91–946) |
| MONDO:0016264 | autoimmune hepatitis | 948 | 72 | 21 | 69 | <20 | <20 | <20 | 679 (251–1,093) | 139 (87–683) |
| MONDO:0017767 | rheumatic fever | 852 | 61 | 24 | 59 | 23 | 23 | 21 | 522 (222–1,128) | 288 (96–948) |
| MONDO:0020640 | autoimmune encephalitis | 103 | 45 | <20 | 45 | <20 | 24 | <20 | — | 371 (137–516) |
| MONDO:0004680 | primary thrombocytopenia | 507 | 43 | <20 | 42 | <20 | <20 | <20 | — | 365 (89–1,068) |
| MONDO:0019337 | autoimmune bullous skin disease | 537 | 37 | <20 | 35 | <20 | <20 | <20 | — | 259 (99–540) |
| MONDO:0030703 | autoimmune vasculitis | 445 | 37 | <20 | 35 | <20 | <20 | <20 | — | 112 (68–370) |
| MONDO:0016218 | Guillain-Barre syndrome | 398 | 34 | <20 | 32 | <20 | <20 | <20 | — | 150 (100–488) |
| MONDO:0020108 | autoimmune hemolytic anemia | 396 | 32 | <20 | 31 | <20 | <20 | <20 | — | 111 (84–679) |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 221 | 27 | <20 | 27 | <20 | <20 | <20 | — | 221 (96–1,144) |
| MONDO:0016544 | IgG4-related mesenteritis | 321 | 25 | <20 | 21 | <20 | <20 | <20 | — | 112 (77–815) |
| MONDO:0019563 | CREST syndrome | 212 | 25 | <20 | 25 | <20 | <20 | <20 | — | 221 (98–1,152) |

## By disease and kind: persons with ≥1 day before / after the first diagnosis

| disease | activity_summary | heart_rate_minute_level | heart_rate_summary | sleep_daily_summary | sleep_level | steps_intraday |
|---|--:|--:|--:|--:|--:|--:|
| all selected diseases | 479 / 1,723 | 337 / 1,623 | 344 / 1,664 | 433 / 1,639 | 433 / 1,639 | 450 / 1,720 |
| Sjogren syndrome | 199 / 669 | 149 / 639 | 150 / 654 | 185 / 639 | 185 / 639 | 187 / 670 |
| systemic lupus erythematosus | 81 / 430 | 52 / 406 | 57 / 419 | 70 / 409 | 70 / 409 | 74 / 427 |
| localized scleroderma | 55 / 192 | 40 / 179 | 40 / 185 | 51 / 180 | 51 / 180 | 52 / 192 |
| myasthenia gravis | 29 / 112 | 20 / 107 | 20 / 107 | 27 / 109 | 27 / 109 | 28 / 112 |
| cutaneous lupus erythematosus | 30 / 101 | 20 / 95 | 20 / 99 | 28 / 96 | 28 / 96 | 30 / 101 |
| antiphospholipid syndrome | 34 / 91 | 26 / 84 | 26 / 86 | 30 / 86 | 30 / 86 | 33 / 90 |
| systemic sclerosis | 22 / 94 | <20 / 89 | <20 / 92 | 20 / 91 | 20 / 91 | 22 / 94 |
| discoid lupus erythematosus | 30 / 91 | 20 / 85 | 20 / 89 | 28 / 86 | 28 / 86 | 30 / 91 |
| autoimmune hepatitis | 21 / 69 | <20 / 67 | <20 / 68 | <20 / 68 | <20 / 68 | 21 / 69 |
| rheumatic fever | 24 / 59 | <20 / 55 | <20 / 55 | 22 / 58 | 22 / 58 | 24 / 59 |
| autoimmune encephalitis | <20 / 45 | <20 / 41 | <20 / 45 | <20 / 41 | <20 / 41 | <20 / 45 |
| primary thrombocytopenia | <20 / 42 | <20 / 39 | <20 / 39 | <20 / 38 | <20 / 38 | <20 / 42 |
| autoimmune bullous skin disease | <20 / 35 | <20 / 32 | <20 / 32 | <20 / 34 | <20 / 34 | <20 / 35 |
| autoimmune vasculitis | <20 / 35 | <20 / 32 | <20 / 33 | <20 / 32 | <20 / 32 | <20 / 35 |
| Guillain-Barre syndrome | <20 / 32 | <20 / 31 | <20 / 32 | <20 / 31 | <20 / 31 | <20 / 32 |
| autoimmune hemolytic anemia | <20 / 31 | <20 / 26 | <20 / 27 | <20 / 28 | <20 / 28 | <20 / 31 |
| limited cutaneous systemic sclerosis | <20 / 26 | <20 / 26 | <20 / 26 | <20 / 27 | <20 / 27 | <20 / 26 |
| IgG4-related mesenteritis | <20 / 20 | <20 / <20 | <20 / <20 | <20 / 21 | <20 / 21 | <20 / 20 |
| CREST syndrome | <20 / 25 | <20 / 25 | <20 / 25 | <20 / 25 | <20 / 25 | <20 / 25 |
