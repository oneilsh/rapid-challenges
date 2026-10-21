---
audit: wearables-rare
date: 2026-10-21
command: make wearables-rare-exact ARGS="--min-dx-dates 2"
args: --flags rare --exact --min-dx-dates 2
commit: 24ec79d
mondo: 2026-06-02
notes: >
  CDR is the v8 release (R2024Q3R8): 626,396 persons, of whom 349,815 (56%) have any
  condition_occurrence row, i.e. the EHR-linked subset; that number is correct for v8.
  Requiring codes on >= 2 dates cut persons with any rare dx from 199,392 to 145,899.
  The 10 largest nodes cover 55% of them, 25 cover 69%; these are mostly common
  conditions tagged rare (carpal tunnel / median nerve neuropathy, migraine, fibroids,
  BPPV) plus a known Mondo xref error (thrombophilia due to thrombin defect -> venous
  thrombosis). "only" near 0 marks nodes nested inside another node (e.g. carpal tunnel
  inside median nerve neuropathy).
---

# Wearables × rare disease (All of Us)

CDR: `wb-affable-acorn-7941.R2024Q3R8`

Fitbit tables found: activity_summary, heart_rate_summary, sleep_daily_summary · usable wear = >= 30 distinct days · rare = Mondo subsets rare · 5,614 rare Mondo nodes mapped to 5,682 standard concepts (59,686 with descendants)

Scope: exact SNOMED-only mapping · dx on >= 2 distinct dates

| population | persons |
|---|--:|
| persons in CDR (person table) | 626,396 |
| persons with any condition | 349,815 |
| persons with any Fitbit day | 58,891 |
| persons with >= 30 Fitbit days | 55,650 |
| persons with any rare dx | 145,899 |
| ... and >= 30 Fitbit days | 12,469 |
| ... rare dx on a non-grouping node, with wear | 8,991 |
|   orphanet_rare dx | 48,304 |
|   orphanet_rare dx with wear | 4,507 |
|   gard_rare dx | 134,839 |
|   gard_rare dx with wear | 11,348 |
|   nord_rare dx | 87,988 |
|   nord_rare dx with wear | 7,553 |

## Rare diseases with the most wearables data (top 60; n_wear >= 20)

| Mondo | disease | n_dx | n_wear | % | wear before dx | wear spans dx | sources | note |
|---|---|--:|--:|--:|--:|--:|---|---|
| MONDO:0003598 | median nerve neuropathy | 17,550 | 1,572 | 9.0 | 362 | 303 | gard | SUSPECT broad |
| MONDO:0007275 | carpal tunnel syndrome | 17,241 | 1,547 | 9.0 | 356 | 298 | gard | SUSPECT broad |
| MONDO:0100431 | migraine without aura | 12,642 | 1,456 | 11.5 | 424 | 378 | inferred | SUSPECT broad |
| MONDO:0024637 | malignant soft tissue neoplasm | 14,843 | 1,388 | 9.4 | 383 | 334 | gard | group, SUSPECT broad |
| MONDO:0004684 | plantar fibromatosis | 11,435 | 1,252 | 10.9 | 356 | 315 | orphanet,gard,nord | SUSPECT broad |
| MONDO:0005728 | diaphragm disorder | 13,167 | 963 | 7.3 | 260 | 225 | gard | group, SUSPECT broad |
| MONDO:0007886 | uterine corpus leiomyoma | 11,702 | 953 | 8.1 | 192 | 177 | gard,nord | group, SUSPECT broad |
| MONDO:0005475 | migraine with aura | 7,482 | 887 | 11.9 | 261 | 220 | nord | group, SUSPECT broad |
| MONDO:0008559 | thrombophilia due to thrombin defect | 11,550 | 749 | 6.5 | 199 | 172 | gard,nord | SUSPECT broad |
| MONDO:0024432 | nerve plexus disorder | 6,669 | 635 | 9.5 | 132 | 118 | gard | group, SUSPECT broad |
| MONDO:0006683 | brachial plexus neuropathy | 6,515 | 622 | 9.5 | 128 | 114 | gard | group, SUSPECT broad |
| MONDO:0002334 | hematopoietic and lymphoid system neoplasm | 7,808 | 553 | 7.1 | 161 | 142 | gard | group, SUSPECT broad |
| MONDO:0006682 | brachial plexus neuritis | 5,644 | 531 | 9.4 | 101 | 89 | gard | group, SUSPECT broad |
| MONDO:8000018 | benign paroxysmal positional vertigo | 5,220 | 480 | 9.2 | 161 | 146 | inferred | SUSPECT broad |
| MONDO:0018882 | vasculitis | 6,105 | 459 | 7.5 | 107 | 93 | gard | group, SUSPECT broad |
| MONDO:0007006 | ulnar neuropathy | 4,439 | 450 | 10.1 | 138 | 120 | inferred | group, SUSPECT broad |
| MONDO:0001458 | ulnar nerve lesion | 4,310 | 438 | 10.2 | 137 | 119 | gard | SUSPECT broad |
| MONDO:0010030 | Sjogren syndrome | 3,505 | 426 | 12.2 | 123 | 102 | orphanet | SUSPECT broad |
| MONDO:0002714 | central nervous system cancer | 5,227 | 422 | 8.1 | 103 | 94 | gard | group, SUSPECT broad |
| MONDO:0016537 | lymphoproliferative syndrome | 5,309 | 401 | 7.6 | 116 | 99 | gard | group, SUSPECT broad |
| MONDO:0003225 | bone marrow disorder | 7,933 | 398 | 5.0 | 89 | 78 | gard | group, SUSPECT broad |
| MONDO:0005150 | age-related macular degeneration | 4,603 | 397 | 8.6 | 102 | 91 | gard | group, SUSPECT broad |
| MONDO:0011565 | metabolic syndrome X | 3,273 | 370 | 11.3 | 110 | 93 | inferred | SUSPECT broad |
| MONDO:0006597 | photosensitivity disease | 3,633 | 362 | 10.0 | 53 | 50 | inferred | group, SUSPECT broad |
| MONDO:0008207 | chondromalacia patellae | 2,713 | 311 | 11.5 | 53 | 49 | gard,nord | SUSPECT broad |
| MONDO:0005149 | pulmonary hypertension | 6,013 | 305 | 5.1 | 112 | 93 | gard,nord | group, SUSPECT broad |
| MONDO:0007915 | systemic lupus erythematosus | 3,730 | 294 | 7.9 | 46 | 39 | orphanet,nord | group, SUSPECT broad |
| MONDO:0002525 | inherited lipid metabolism disorder | 3,548 | 293 | 8.3 | 50 | 41 | gard | group, SUSPECT broad |
| MONDO:0001082 | lymph node cancer | 4,587 | 288 | 6.3 | 105 | 94 | gard | group, SUSPECT broad |
| MONDO:0015074 | thyroid tumor | 2,961 | 280 | 9.5 | 68 | 55 | gard | group, SUSPECT broad |
| MONDO:0004625 | phlebitis | 3,841 | 279 | 7.3 | 67 | 58 | inferred | group, SUSPECT broad |
| MONDO:0005062 | lymphoma | 3,810 | 279 | 7.3 | 87 | 77 | inferred | group, SUSPECT broad |
| MONDO:0013592 | nonsyndromic congenital nail disorder 9 | 4,056 | 274 | 6.8 | 103 | 91 | gard | SUSPECT broad |
| MONDO:0001127 | tibialis tendinitis | 2,310 | 272 | 11.8 | 85 | 73 | gard | SUSPECT broad |
| MONDO:0002305 | thrombophilia | 3,371 | 266 | 7.9 | 102 | 94 | gard | group, SUSPECT broad |
| MONDO:0003778 | inborn error of immunity | 3,407 | 257 | 7.5 | 78 | 70 | gard | group, SUSPECT broad |
| MONDO:0009960 | inflammatory bowel disease 1 | 2,953 | 251 | 8.5 | 48 | 44 | gard | SUSPECT broad |
| MONDO:0002108 | thyroid cancer | 2,575 | 248 | 9.6 | 60 | 48 | inferred | group, SUSPECT broad |
| MONDO:0022394 | cervical intraepithelial neoplasia | 2,770 | 243 | 8.8 | 53 | 45 | gard,nord | SUSPECT broad |
| MONDO:0011508 | lymphoma, non-Hodgkin, familial | 3,299 | 237 | 7.2 | 77 | 70 | gard,nord | SUSPECT broad |
| MONDO:0001843 | uterus interstitial leiomyoma | 2,935 | 237 | 8.1 | 78 | 74 | gard | SUSPECT broad |
| MONDO:0005374 | bone marrow neoplasm | 2,985 | 236 | 7.9 | 48 | 39 | gard | group, SUSPECT broad |
| MONDO:0004960 | monoclonal gammopathy | 2,718 | 209 | 7.7 | 49 | 41 | gard | group, SUSPECT broad |
| MONDO:0001541 | plantar nerve lesion | 1,599 | 205 | 12.8 | 64 | 59 | gard |  |
| MONDO:0002771 | pulmonary fibrosis | 2,963 | 200 | 6.7 | 58 | 50 | gard | group, SUSPECT broad |
| MONDO:0020283 | uveitis | 2,659 | 189 | 7.1 | 45 | 37 | gard | group, SUSPECT broad |
| MONDO:0018102 | corneal dystrophy | 1,741 | 186 | 10.7 | 48 | 45 | gard,nord | group |
| MONDO:0007017 | vitreous detachment | 1,158 | 180 | 15.5 | 61 | 56 | gard |  |
| MONDO:0020066 | Ehlers-Danlos syndrome | 921 | 179 | 19.4 | 62 | 56 | gard,nord | group |
| MONDO:0006598 | phototoxic dermatitis | 2,028 | 174 | 8.6 | 21 | 21 | inferred | SUSPECT broad |
| MONDO:0015978 | functional neutrophil defect | 2,549 | 171 | 6.7 | 55 | 49 | gard | group, SUSPECT broad |
| MONDO:0017611 | pituitary tumor | 1,801 | 171 | 9.5 | 37 | 35 | gard,nord | group, SUSPECT broad |
| MONDO:0006651 | anterior uveitis | 2,355 | 167 | 7.1 | 41 | 33 | inferred | group, SUSPECT broad |
| MONDO:0001475 | neutropenia | 2,529 | 166 | 6.6 | 53 | 47 | inferred | group, SUSPECT broad |
| MONDO:0021439 | benign neoplasm of pituitary gland | 1,710 | 164 | 9.6 | 37 | 35 | gard |  |
| MONDO:0006814 | iritis | 2,299 | 162 | 7.0 | 41 | 33 | gard | group, SUSPECT broad |
| MONDO:0004773 | iridocyclitis | 2,294 | 161 | 7.0 | 40 | 33 | gard | group, SUSPECT broad |
| MONDO:0003441 | dystonic disorder | 1,647 | 154 | 9.4 | 52 | 46 | gard | group |
| MONDO:0005380 | osteonecrosis | 2,253 | 149 | 6.6 | 33 | 29 | gard,nord | group, SUSPECT broad |
| MONDO:0005059 | leukemia | 1,959 | 149 | 7.6 | 28 | 22 | inferred | group, SUSPECT broad |

## What drives 'persons with any rare dx' (145,899)

Rare nodes ranked by n_dx; persons covered by the k largest nodes:

| top k nodes | persons | % of rare dx |
|--:|--:|--:|
| 1 | 17,550 | 12.0 |
| 5 | 50,953 | 34.9 |
| 10 | 80,184 | 55.0 |
| 25 | 100,877 | 69.1 |
| 50 | 117,598 | 80.6 |
| 100 | 129,726 | 88.9 |
| 250 | 141,369 | 96.9 |
| 500 | 144,479 | 99.0 |
| 1000 | 145,717 | 99.9 |

Largest 25 nodes (only = persons with no other rare dx):

| rank | Mondo | disease | n_dx | only |
|--:|---|---|--:|--:|
| 1 | MONDO:0003598 | median nerve neuropathy | 17,550 | 57 |
| 2 | MONDO:0007275 | carpal tunnel syndrome | 17,241 | 0 |
| 3 | MONDO:0024637 | malignant soft tissue neoplasm | 14,843 | 3,335 |
| 4 | MONDO:0005728 | diaphragm disorder | 13,167 | 3,305 |
| 5 | MONDO:0100431 | migraine without aura | 12,642 | 3,097 |
| 6 | MONDO:0007886 | uterine corpus leiomyoma | 11,702 | 2,572 |
| 7 | MONDO:0008559 | thrombophilia due to thrombin defect | 11,550 | 1,852 |
| 8 | MONDO:0004684 | plantar fibromatosis | 11,435 | 2,688 |
| 9 | MONDO:0003225 | bone marrow disorder | 7,933 | <20 |
| 10 | MONDO:0002334 | hematopoietic and lymphoid system neoplasm | 7,808 | <20 |
| 11 | MONDO:0005475 | migraine with aura | 7,482 | 1,606 |
| 12 | MONDO:0024432 | nerve plexus disorder | 6,669 | <20 |
| 13 | MONDO:0006683 | brachial plexus neuropathy | 6,515 | 0 |
| 14 | MONDO:0018882 | vasculitis | 6,105 | 42 |
| 15 | MONDO:0005149 | pulmonary hypertension | 6,013 | 1,141 |
| 16 | MONDO:0006682 | brachial plexus neuritis | 5,644 | 0 |
| 17 | MONDO:0016537 | lymphoproliferative syndrome | 5,309 | <20 |
| 18 | MONDO:0002714 | central nervous system cancer | 5,227 | 159 |
| 19 | MONDO:8000018 | benign paroxysmal positional vertigo | 5,220 | 1,170 |
| 20 | MONDO:0005246 | osteomyelitis | 4,746 | 0 |
| 21 | MONDO:0005150 | age-related macular degeneration | 4,603 | 938 |
| 22 | MONDO:0001082 | lymph node cancer | 4,587 | 0 |
| 23 | MONDO:0007006 | ulnar neuropathy | 4,439 | 25 |
| 24 | MONDO:0001458 | ulnar nerve lesion | 4,310 | 0 |
| 25 | MONDO:0013592 | nonsyndromic congenital nail disorder 9 | 4,056 | 821 |
