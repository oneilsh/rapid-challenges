---
audit: wearables-rare
date: 2026-10-20
command: make wearables-rare-autoimmune
args: --under MONDO:0007179 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact
commit: defb113
mondo: 2026-06-02
notes: >
  Rare autoimmune diseases only, each mapped through its own standard SNOMED concept
  (plus OMOP descendants). 102 of the 192 candidate diseases mapped. "SUSPECT broad"
  fires above 0.5% of persons with any condition (~1,750), so Sjogren and SLE are
  flagged by size, not because of a bad mapping.
---

# Wearables × rare disease (All of Us)

Fitbit tables found: activity_summary, heart_rate_summary, sleep_daily_summary · usable wear = >= 30 distinct days · rare = Mondo subsets orphanet_rare, gard_rare, nord_rare, mondo_rare · 102 rare Mondo nodes mapped to 104 standard concepts (383 with descendants)

Scope: under MONDO:0007179 · exact SNOMED-only mapping

| population | persons |
|---|--:|
| persons with any condition | 349,815 |
| persons with any Fitbit day | 58,891 |
| persons with >= 30 Fitbit days | 55,650 |
| persons with any rare dx | 17,127 |
| ... and >= 30 Fitbit days | 1,707 |
| ... rare dx on a non-grouping node, with wear | 954 |
|   orphanet_rare dx | 14,859 |
|   orphanet_rare dx with wear | 1,501 |
|   gard_rare dx | 10,130 |
|   gard_rare dx with wear | 930 |
|   nord_rare dx | 9,775 |
|   nord_rare dx with wear | 879 |

## Rare diseases with the most wearables data (top 60; n_wear >= 20)

| Mondo | disease | n_dx | n_wear | % | wear before dx | wear spans dx | sources | note |
|---|---|--:|--:|--:|--:|--:|---|---|
| MONDO:0010030 | Sjogren syndrome | 5,474 | 670 | 12.2 | 196 | 162 | orphanet | SUSPECT broad |
| MONDO:0007915 | systemic lupus erythematosus | 4,989 | 415 | 8.3 | 80 | 68 | orphanet,nord | group, SUSPECT broad |
| MONDO:0019562 | localized scleroderma | 1,491 | 196 | 13.1 | 56 | 48 | orphanet,gard | group |
| MONDO:0009688 | myasthenia gravis | 787 | 110 | 14.0 | 29 | 24 | orphanet,gard,nord | group |
| MONDO:0005282 | cutaneous lupus erythematosus | 1,260 | 95 | 7.5 | 30 | 27 | gard,nord | group |
| MONDO:8000010 | antiphospholipid syndrome | 1,389 | 93 | 6.7 | 33 | 29 | orphanet,gard | group |
| MONDO:0005100 | systemic sclerosis | 1,057 | 88 | 8.3 | 21 | <20 | orphanet,gard,nord | group |
| MONDO:0019558 | discoid lupus erythematosus | 1,184 | 86 | 7.3 | 30 | 27 | orphanet,gard,nord |  |
| MONDO:0016264 | autoimmune hepatitis | 948 | 67 | 7.1 | 20 | <20 | orphanet,gard,nord | group |
| MONDO:0017767 | rheumatic fever | 852 | 59 | 6.9 | 24 | 22 | orphanet,gard,nord |  |
| MONDO:0020640 | autoimmune encephalitis | 103 | 45 | 43.7 | <20 | <20 | gard,nord |  |
| MONDO:0004680 | primary thrombocytopenia | 507 | 40 | 7.9 | <20 | <20 | gard | group |
| MONDO:0019337 | autoimmune bullous skin disease | 537 | 34 | 6.3 | <20 | <20 | gard | group |
| MONDO:0030703 | autoimmune vasculitis | 445 | 34 | 7.6 | <20 | <20 | gard | group |
| MONDO:0016218 | Guillain-Barre syndrome | 398 | 33 | 8.3 | <20 | <20 | gard,nord | group |
| MONDO:0020108 | autoimmune hemolytic anemia | 396 | 31 | 7.8 | <20 | <20 | gard,nord | group |
| MONDO:0016358 | limited cutaneous systemic sclerosis | 221 | 25 | 11.3 | <20 | <20 | gard,nord | group |
| MONDO:0019563 | CREST syndrome | 212 | 24 | 11.3 | <20 | <20 | gard |  |
| MONDO:0016544 | IgG4-related mesenteritis | 321 | 23 | 7.2 | <20 | <20 | gard |  |
