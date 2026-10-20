---
audit: wearables-rare
date: 2026-10-20
command: make wearables-rare-exact
args: --flags rare --exact
commit: e6cc8a5
mondo: 2026-06-02
notes: >
  All Mondo rare (incl. inferred), each disease mapped only through its own standard
  SNOMED concept (plus OMOP descendants). The mapping-explosion junk is gone
  (tularemia, osteochondrosis, the preeclampsia cluster), but 199,392 of 349,815
  persons with a condition still have a "rare" dx. What remains: common conditions
  that GARD/inferred tag rare (carpal tunnel, vitreous detachment, migraine), and
  genetic-locus entries tagged omim_susceptibility whose SNOMED xref is the common
  clinical disease (inflammatory bowel disease 1 -> Crohn's disease, familial
  non-Hodgkin lymphoma -> non-Hodgkin lymphoma, thrombophilia due to thrombin defect).
---

# Wearables × rare disease (All of Us)

Fitbit tables found: activity_summary, heart_rate_summary, sleep_daily_summary · usable wear = >= 30 distinct days · rare = Mondo subsets rare · 5,614 rare Mondo nodes mapped to 5,682 standard concepts (59,686 with descendants)

Scope: exact SNOMED-only mapping

| population | persons |
|---|--:|
| persons with any condition | 349,815 |
| persons with any Fitbit day | 58,891 |
| persons with >= 30 Fitbit days | 55,650 |
| persons with any rare dx | 199,392 |
| ... and >= 30 Fitbit days | 17,869 |
| ... rare dx on a non-grouping node, with wear | 13,808 |
|   orphanet_rare dx | 78,698 |
|   orphanet_rare dx with wear | 7,274 |
|   gard_rare dx | 187,386 |
|   gard_rare dx with wear | 16,567 |
|   nord_rare dx | 132,791 |
|   nord_rare dx with wear | 11,697 |

## Rare diseases with the most wearables data (top 60; n_wear >= 20)

| Mondo | disease | n_dx | n_wear | % | wear before dx | wear spans dx | sources | note |
|---|---|--:|--:|--:|--:|--:|---|---|
| MONDO:0003598 | median nerve neuropathy | 28,307 | 2,658 | 9.4 | 642 | 541 | gard | SUSPECT broad |
| MONDO:0007275 | carpal tunnel syndrome | 27,681 | 2,604 | 9.4 | 629 | 531 | gard | SUSPECT broad |
| MONDO:0004684 | plantar fibromatosis | 21,863 | 2,313 | 10.6 | 680 | 588 | orphanet,gard,nord | SUSPECT broad |
| MONDO:0100431 | migraine without aura | 19,227 | 2,227 | 11.6 | 673 | 597 | inferred | SUSPECT broad |
| MONDO:0005728 | diaphragm disorder | 27,439 | 2,157 | 7.9 | 689 | 588 | gard | group, SUSPECT broad |
| MONDO:0024637 | malignant soft tissue neoplasm | 21,158 | 2,064 | 9.8 | 602 | 529 | gard | group, SUSPECT broad |
| MONDO:0007886 | uterine corpus leiomyoma | 20,097 | 1,694 | 8.4 | 419 | 370 | gard,nord | group, SUSPECT broad |
| MONDO:0005475 | migraine with aura | 13,457 | 1,621 | 12.0 | 498 | 407 | nord | group, SUSPECT broad |
| MONDO:0008559 | thrombophilia due to thrombin defect | 19,742 | 1,334 | 6.8 | 388 | 331 | gard,nord | SUSPECT broad |
| MONDO:0024432 | nerve plexus disorder | 12,127 | 1,232 | 10.2 | 263 | 230 | gard | group, SUSPECT broad |
| MONDO:0006683 | brachial plexus neuropathy | 11,807 | 1,208 | 10.2 | 257 | 224 | gard | group, SUSPECT broad |
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
| MONDO:0011565 | metabolic syndrome X | 5,841 | 646 | 11.1 | 198 | 170 | inferred | SUSPECT broad |
| MONDO:0003225 | bone marrow disorder | 11,434 | 633 | 5.5 | 167 | 142 | gard | group, SUSPECT broad |
| MONDO:0002714 | central nervous system cancer | 7,309 | 632 | 8.6 | 162 | 144 | gard | group, SUSPECT broad |
| MONDO:0001843 | uterus interstitial leiomyoma | 7,214 | 589 | 8.2 | 192 | 174 | gard | SUSPECT broad |
| MONDO:0016537 | lymphoproliferative syndrome | 6,965 | 536 | 7.7 | 154 | 132 | gard | group, SUSPECT broad |
| MONDO:0005149 | pulmonary hypertension | 10,156 | 514 | 5.1 | 190 | 160 | gard,nord | group, SUSPECT broad |
| MONDO:0001127 | tibialis tendinitis | 4,301 | 510 | 11.9 | 169 | 149 | gard | SUSPECT broad |
| MONDO:0003778 | inborn error of immunity | 6,116 | 502 | 8.2 | 169 | 146 | gard | group, SUSPECT broad |
| MONDO:0001082 | lymph node cancer | 7,346 | 471 | 6.4 | 169 | 142 | gard | group, SUSPECT broad |
| MONDO:0022394 | cervical intraepithelial neoplasia | 4,968 | 462 | 9.3 | 103 | 86 | gard,nord | SUSPECT broad |
| MONDO:0006598 | phototoxic dermatitis | 4,751 | 436 | 9.2 | 67 | 59 | inferred | SUSPECT broad |
| MONDO:0002771 | pulmonary fibrosis | 6,371 | 428 | 6.7 | 138 | 116 | gard | group, SUSPECT broad |
| MONDO:0001541 | plantar nerve lesion | 3,296 | 425 | 12.9 | 138 | 123 | gard | SUSPECT broad |
| MONDO:0007915 | systemic lupus erythematosus | 4,989 | 415 | 8.3 | 80 | 68 | orphanet,nord | group, SUSPECT broad |
| MONDO:0015074 | thyroid tumor | 4,169 | 413 | 9.9 | 113 | 94 | gard | group, SUSPECT broad |
| MONDO:0002305 | thrombophilia | 5,311 | 405 | 7.6 | 163 | 144 | gard | group, SUSPECT broad |
| MONDO:0005062 | lymphoma | 4,912 | 373 | 7.6 | 118 | 103 | inferred | group, SUSPECT broad |
| MONDO:0005374 | bone marrow neoplasm | 4,388 | 357 | 8.1 | 86 | 70 | gard | group, SUSPECT broad |
| MONDO:0009960 | inflammatory bowel disease 1 | 3,986 | 355 | 8.9 | 73 | 65 | gard | SUSPECT broad |
| MONDO:0015978 | functional neutrophil defect | 4,466 | 335 | 7.5 | 110 | 94 | gard | group, SUSPECT broad |
| MONDO:0001475 | neutropenia | 4,431 | 327 | 7.4 | 107 | 92 | inferred | group, SUSPECT broad |
| MONDO:0018102 | corneal dystrophy | 2,772 | 322 | 11.6 | 107 | 92 | gard,nord | group, SUSPECT broad |
| MONDO:0001745 | subserous uterine fibroid | 3,956 | 316 | 8.0 | 108 | 93 | gard | SUSPECT broad |
| MONDO:0011508 | lymphoma, non-Hodgkin, familial | 4,169 | 305 | 7.3 | 108 | 95 | gard,nord | SUSPECT broad |
| MONDO:0020283 | uveitis | 4,280 | 301 | 7.0 | 79 | 69 | gard | group, SUSPECT broad |
| MONDO:0001543 | lesion of sciatic nerve | 2,941 | 300 | 10.2 | 118 | 103 | gard | group, SUSPECT broad |
| MONDO:0002108 | thyroid cancer | 3,114 | 298 | 9.6 | 72 | 58 | inferred | group, SUSPECT broad |
| MONDO:0004960 | monoclonal gammopathy | 3,729 | 297 | 8.0 | 78 | 64 | gard | group, SUSPECT broad |
| MONDO:0003441 | dystonic disorder | 3,033 | 294 | 9.7 | 98 | 85 | gard | group, SUSPECT broad |
| MONDO:0007017 | vitreous detachment | 1,785 | 288 | 16.1 | 109 | 102 | gard | SUSPECT broad |
| MONDO:0005380 | osteonecrosis | 3,830 | 286 | 7.5 | 69 | 60 | gard,nord | group, SUSPECT broad |
| MONDO:0001905 | bicipital tenosynovitis | 2,775 | 283 | 10.2 | 72 | 64 | gard | SUSPECT broad |
| MONDO:0001664 | submucous uterine fibroid | 3,031 | 278 | 9.2 | 71 | 65 | gard | SUSPECT broad |
| MONDO:0019052 | inborn errors of metabolism | 2,707 | 278 | 10.3 | 100 | 90 | gard | group, SUSPECT broad |
| MONDO:0008268 | polydactyly-myopia syndrome | 2,066 | 274 | 13.3 | 45 | 43 | orphanet,gard | SUSPECT broad |
| MONDO:0019013 | non-histaminic angioedema | 3,718 | 270 | 7.3 | 64 | 57 | gard,nord | SUSPECT broad |
