---
audit: wearables-rare
date: 2026-10-20
command: make wearables-rare
args: (defaults) --flags rare --min-days 30
commit: fa75c79
mondo: 2026-06-02
notes: >
  Full mondo2omop mapping (SNOMED, ICD10CM and MeSH xrefs via 'Maps to', plus OMOP
  descendants). Population counts match the earlier CHARMPheno Spark run exactly. Most
  top rows are junk: ICD10CM/MeSH codes that map to several standard concepts, one of
  them broad (e.g. gastrointestinal tularemia, 200,247 dx). Superseded by --exact runs.
---

# Wearables × rare disease (All of Us)

Fitbit tables found: activity_summary, heart_rate_summary, sleep_daily_summary · usable wear = >= 30 distinct days · rare = Mondo subsets rare · 5,818 rare Mondo nodes mapped to 5,971 standard concepts (71,015 with descendants)

| population | persons |
|---|--:|
| persons with any condition | 349,815 |
| persons with any Fitbit day | 58,891 |
| persons with >= 30 Fitbit days | 55,650 |
| persons with any rare dx | 270,904 |
| ... and >= 30 Fitbit days | 23,471 |
| ... rare dx on a non-grouping node, with wear | 21,349 |
|   orphanet_rare dx | 119,422 |
|   orphanet_rare dx with wear | 9,874 |
|   gard_rare dx | 265,484 |
|   gard_rare dx with wear | 22,812 |
|   nord_rare dx | 195,714 |
|   nord_rare dx with wear | 16,418 |

## Rare diseases with the most wearables data (top 60; n_wear >= 20)

| Mondo | disease | n_dx | n_wear | % | wear before dx | wear spans dx | sources | note |
|---|---|--:|--:|--:|--:|--:|---|---|
| MONDO:0001916 | gastrointestinal tularemia | 200,247 | 17,126 | 8.6 | 3,587 | 3,220 | gard | SUSPECT broad |
| MONDO:0018381 | osteochondrosis | 91,740 | 7,879 | 8.6 | 1,956 | 1,703 | gard,nord | group, SUSPECT broad |
| MONDO:0005277 | migraine disorder | 49,507 | 5,298 | 10.7 | 1,151 | 1,009 | inferred | group, SUSPECT broad |
| MONDO:0024311 | cancer affecting bone of limb skeleton | 43,788 | 4,609 | 10.5 | 1,381 | 1,189 | gard | group, SUSPECT broad |
| MONDO:0005081 | preeclampsia | 40,360 | 2,700 | 6.7 | 533 | 454 | orphanet,gard | group, SUSPECT broad |
| MONDO:0018920 | peripartum cardiomyopathy | 40,325 | 2,691 | 6.7 | 534 | 455 | orphanet,gard,nord | SUSPECT broad |
| MONDO:0001641 | severe pre-eclampsia | 40,319 | 2,691 | 6.7 | 533 | 454 | gard | group, SUSPECT broad |
| MONDO:0003598 | median nerve neuropathy | 28,307 | 2,658 | 9.4 | 642 | 541 | gard | SUSPECT broad |
| MONDO:0007275 | carpal tunnel syndrome | 27,681 | 2,604 | 9.4 | 629 | 531 | gard | SUSPECT broad |
| MONDO:0004684 | plantar fibromatosis | 21,863 | 2,313 | 10.6 | 680 | 588 | orphanet,gard,nord | SUSPECT broad |
| MONDO:0100431 | migraine without aura | 19,227 | 2,227 | 11.6 | 673 | 597 | inferred | SUSPECT broad |
| MONDO:0005728 | diaphragm disorder | 27,439 | 2,157 | 7.9 | 689 | 588 | gard | group, SUSPECT broad |
| MONDO:0024637 | malignant soft tissue neoplasm | 21,158 | 2,064 | 9.8 | 602 | 529 | gard | group, SUSPECT broad |
| MONDO:0008353 | pruritic urticarial papules and plaques of pregn | 27,252 | 1,796 | 6.6 | 411 | 343 | orphanet,gard,nord | SUSPECT broad |
| MONDO:0008585 | HELLP syndrome | 27,250 | 1,796 | 6.6 | 411 | 343 | orphanet,gard,nord | SUSPECT broad |
| MONDO:0006558 | pemphigoid gestationis | 27,243 | 1,796 | 6.6 | 411 | 343 | orphanet,gard,nord | SUSPECT broad |
| MONDO:0007886 | uterine corpus leiomyoma | 20,097 | 1,694 | 8.4 | 419 | 370 | gard,nord | group, SUSPECT broad |
| MONDO:0005475 | migraine with aura | 13,457 | 1,621 | 12.0 | 498 | 407 | nord | group, SUSPECT broad |
| MONDO:0008559 | thrombophilia due to thrombin defect | 19,742 | 1,334 | 6.8 | 388 | 331 | gard,nord | SUSPECT broad |
| MONDO:0024432 | nerve plexus disorder | 12,127 | 1,232 | 10.2 | 263 | 230 | gard | group, SUSPECT broad |
| MONDO:0006683 | brachial plexus neuropathy | 11,807 | 1,208 | 10.2 | 257 | 224 | gard | group, SUSPECT broad |
| MONDO:0002940 | anal margin basal cell carcinoma | 10,918 | 1,167 | 10.7 | 390 | 343 | gard | SUSPECT broad |
| MONDO:8000018 | benign paroxysmal positional vertigo | 11,822 | 1,126 | 9.5 | 388 | 333 | inferred | SUSPECT broad |
| MONDO:0006682 | brachial plexus neuritis | 10,377 | 1,065 | 10.3 | 212 | 181 | gard | group, SUSPECT broad |
| MONDO:0018882 | vasculitis | 12,671 | 988 | 7.8 | 235 | 204 | gard | group, SUSPECT broad |
| MONDO:0007006 | ulnar neuropathy | 8,741 | 912 | 10.4 | 273 | 233 | inferred | group, SUSPECT broad |
| MONDO:0001458 | ulnar nerve lesion | 8,470 | 887 | 10.5 | 270 | 230 | gard | SUSPECT broad |
| MONDO:0002334 | hematopoietic and lymphoid system neoplasm | 11,816 | 853 | 7.2 | 259 | 218 | gard | group, SUSPECT broad |
| MONDO:0006597 | photosensitivity disease | 8,253 | 835 | 10.1 | 169 | 143 | inferred | group, SUSPECT broad |
| MONDO:0002525 | inherited lipid metabolism disorder | 9,863 | 805 | 8.2 | 123 | 103 | gard | group, SUSPECT broad |
| MONDO:0008207 | chondromalacia patellae | 6,866 | 765 | 11.1 | 154 | 141 | gard,nord | SUSPECT broad |
| MONDO:0013592 | nonsyndromic congenital nail disorder 9 | 8,816 | 678 | 7.7 | 277 | 238 | gard | SUSPECT broad |
| MONDO:0010030 | Sjogren syndrome | 5,474 | 670 | 12.2 | 196 | 162 | orphanet | SUSPECT broad |
| MONDO:0004625 | phlebitis | 8,639 | 661 | 7.7 | 154 | 132 | inferred | group, SUSPECT broad |
| MONDO:0005150 | age-related macular degeneration | 7,094 | 651 | 9.2 | 201 | 173 | gard | group, SUSPECT broad |
| MONDO:0000816 | abdominal obesity-metabolic syndrome | 5,841 | 646 | 11.1 | 198 | 170 | inferred | group, SUSPECT broad |
| MONDO:0011565 | metabolic syndrome X | 5,841 | 646 | 11.1 | 198 | 170 | inferred | SUSPECT broad |
| MONDO:0003225 | bone marrow disorder | 11,434 | 633 | 5.5 | 167 | 142 | gard | group, SUSPECT broad |
| MONDO:0002714 | central nervous system cancer | 7,309 | 632 | 8.6 | 162 | 144 | gard | group, SUSPECT broad |
| MONDO:0001843 | uterus interstitial leiomyoma | 7,214 | 589 | 8.2 | 192 | 174 | gard | SUSPECT broad |
| MONDO:0001609 | agranulocytosis | 7,474 | 541 | 7.2 | 174 | 151 | nord | group, SUSPECT broad |
| MONDO:0016537 | lymphoproliferative syndrome | 6,965 | 536 | 7.7 | 154 | 132 | gard | group, SUSPECT broad |
| MONDO:0005149 | pulmonary hypertension | 10,156 | 514 | 5.1 | 190 | 160 | gard,nord | group, SUSPECT broad |
| MONDO:0001127 | tibialis tendinitis | 4,301 | 510 | 11.9 | 169 | 149 | gard | SUSPECT broad |
| MONDO:0003778 | inborn error of immunity | 6,116 | 502 | 8.2 | 169 | 146 | gard | group, SUSPECT broad |
| MONDO:0001082 | lymph node cancer | 7,346 | 471 | 6.4 | 169 | 142 | gard | group, SUSPECT broad |
| MONDO:0022394 | cervical intraepithelial neoplasia | 4,968 | 462 | 9.3 | 103 | 86 | gard,nord | SUSPECT broad |
| MONDO:0006598 | phototoxic dermatitis | 4,751 | 436 | 9.2 | 67 | 59 | inferred | SUSPECT broad |
| MONDO:0008228 | pernicious anemia | 4,818 | 430 | 8.9 | 108 | 91 | gard,nord | SUSPECT broad |
| MONDO:0002771 | pulmonary fibrosis | 6,371 | 428 | 6.7 | 138 | 116 | gard | group, SUSPECT broad |
| MONDO:0001541 | plantar nerve lesion | 3,296 | 425 | 12.9 | 138 | 123 | gard | SUSPECT broad |
| MONDO:0007915 | systemic lupus erythematosus | 4,989 | 415 | 8.3 | 80 | 68 | orphanet,nord | group, SUSPECT broad |
| MONDO:0015074 | thyroid tumor | 4,169 | 413 | 9.9 | 113 | 94 | gard | group, SUSPECT broad |
| MONDO:0015454 | multiple carboxylase deficiency | 4,125 | 412 | 10.0 | 84 | 79 | gard,nord | group, SUSPECT broad |
| MONDO:0002305 | thrombophilia | 5,311 | 405 | 7.6 | 163 | 144 | gard | group, SUSPECT broad |
| MONDO:0100345 | lactose intolerance | 4,005 | 404 | 10.1 | 89 | 77 | inferred | SUSPECT broad |
| MONDO:0005062 | lymphoma | 4,912 | 373 | 7.6 | 118 | 103 | inferred | group, SUSPECT broad |
| MONDO:0005374 | bone marrow neoplasm | 4,388 | 357 | 8.1 | 86 | 70 | gard | group, SUSPECT broad |
| MONDO:0009960 | inflammatory bowel disease 1 | 3,986 | 355 | 8.9 | 73 | 65 | gard | SUSPECT broad |
| MONDO:0015978 | functional neutrophil defect | 4,466 | 335 | 7.5 | 110 | 94 | gard | group, SUSPECT broad |
