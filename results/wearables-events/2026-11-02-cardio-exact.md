---
audit: wearables-events
date: 2026-11-02
command: make wearables-events SCOPE=cardio
args: --under MONDO:0004995 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact (lookback 30, min-cov 14)
commit: 0f0f171
mondo: 2026-06-02
notes: >
  v8 CDR, rare cardiovascular disorders (many are common conditions tagged rare: migraine
  with aura, vasculitis, pulmonary hypertension...). Events here are acute visit DATES,
  not episodes: multi-day inpatient stays with a visit row per day count once per day
  (63k inpatient visits for 2,260 persons), which inflates inpatient and covered counts;
  fixed afterwards by collapsing visits into episodes. Visit types 8717 Inpatient
  Hospital and 8870-style CMS place-of-service codes may sit outside the 9201/9203/262
  hierarchy and be missed. 76% of events after dx have no Fitbit day in the 30 days
  before. NESTED CELLS: some differences between published cells are small counts.
---

# Wearables x ED / inpatient events (All of Us)

CDR: `wb-affable-acorn-7941.R2024Q3R8`

Fitbit tables: activity_summary, heart_rate_summary, sleep_daily_summary · rare = Mondo subsets orphanet_rare, gard_rare, nord_rare, mondo_rare · 402 diseases mapped

Scope: under MONDO:0004995 · exact SNOMED-only mapping

Event = a distinct (person, date) with an ED or inpatient visit start. After / before = strictly after / before the first diagnosis (the dx day itself is excluded). Covered = >= 14 Fitbit days in the 30 days before the event. Related = the disease coded on that visit or day. Cohort = persons with the disease and any Fitbit day. Columns are nested: check differences before sharing.

## All selected diseases

Persons with a selected diagnosis: 52,004 · with Fitbit data: 4,733 · their Fitbit days after dx: 2,528,243

| event class | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| ed_or_inpatient | 43,287 | 2,656 | 8,951 | 1,182 | 743 | 3.54 | 2,785 | 403 |
| ed | 15,047 | 2,015 | 2,656 | 763 | 400 | 1.05 | 610 | 271 |
| inpatient | 31,004 | 1,974 | 6,806 | 780 | 461 | 2.69 | 2,289 | 256 |
| related | 2,774 | 724 | 579 | 205 | 90 | 0.23 | <20 | <20 |

Pooled events after dx by Fitbit days in the 30 days before them:

| event class | 0 | 1-6 | 7-13 | 14-20 | 21+ |
|---|--:|--:|--:|--:|--:|
| ed_or_inpatient | 33,077 | 665 | 594 | 813 | 8,138 |
| related | 2,114 | 44 | 37 | 49 | 530 |

## By disease (persons with Fitbit data >= 20)

### ed_or_inpatient

| Mondo | disease | with data | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0005475 | migraine with aura | 1,718 | 13,289 | 892 | 2,869 | 387 | 241 | 3.40 | 1,108 | 150 |
| MONDO:0018882 | vasculitis | 1,048 | 12,852 | 656 | 2,644 | 289 | 189 | 4.35 | 635 | 92 |
| MONDO:0005149 | pulmonary hypertension | 558 | 4,998 | 324 | 969 | 135 | 90 | 4.91 | 693 | 78 |
| MONDO:0019013 | non-histaminic angioedema | 299 | 3,935 | 190 | 527 | 76 | 53 | 3.07 | 81 | 25 |
| MONDO:0015530 | trigeminal autonomic cephalalgia | 219 | 2,116 | 131 | 417 | 66 | 40 | 3.77 | 224 | 31 |
| MONDO:0009468 | pseudotumor cerebri | 197 | 1,544 | 99 | 239 | 39 | 25 | 3.61 | 27 | <20 |
| MONDO:0005081 | preeclampsia | 167 | 1,194 | 109 | 175 | 39 | 22 | 1.79 | 51 | <20 |
| MONDO:0002824 | extrinsic cardiomyopathy | 139 | 1,851 | 90 | 258 | 44 | 27 | 2.98 | 72 | <20 |
| MONDO:0042981 | aortic valve stenosis | 134 | 1,047 | 89 | 340 | 47 | 32 | 4.70 | 290 | 25 |
| MONDO:0011479 | postural orthostatic tachycardia syndrome | 129 | 787 | 50 | 257 | 29 | 22 | 6.72 | 58 | <20 |
| MONDO:0005045 | hypertrophic cardiomyopathy | 127 | 977 | 65 | 244 | 25 | <20 | 3.78 | 114 | <20 |
| MONDO:0019809 | congenital aortic valve insufficiency | 116 | 1,536 | 80 | 776 | 40 | 30 | 7.92 | 62 | <20 |
| MONDO:0015924 | pulmonary arterial hypertension | 111 | 1,708 | 78 | 162 | 34 | <20 | 3.23 | <20 | <20 |
| MONDO:0015691 | hypereosinophilic syndrome | 84 | 1,031 | 52 | 211 | 23 | <20 | 5.13 | 96 | <20 |
| MONDO:0007154 | arteriovenous malformations of the brain | 75 | 1,136 | 39 | 237 | <20 | <20 | 7.78 | 95 | <20 |
| MONDO:0008538 | temporal arteritis | 72 | 391 | 37 | 191 | <20 | <20 | 4.37 | 29 | <20 |
| MONDO:0001280 | choroiditis | 63 | 369 | 29 | 61 | <20 | <20 | 1.60 | 30 | <20 |
| MONDO:0004802 | pulmonary eosinophilia | 63 | 850 | 41 | 207 | 21 | <20 | 6.71 | 93 | <20 |
| MONDO:0004496 | myocarditis | 58 | 617 | 35 | 57 | <20 | <20 | 1.87 | <20 | <20 |
| MONDO:0005832 | lymphangitis | 52 | 409 | 35 | 78 | <20 | <20 | 3.04 | <20 | <20 |
| MONDO:0018925 | familial or sporadic hemiplegic migraine | 45 | 169 | 22 | 32 | <20 | <20 | 1.26 | 36 | <20 |
| MONDO:0002303 | central retinal vein occlusion | 44 | 169 | 25 | 33 | <20 | <20 | 1.43 | <20 | <20 |
| MONDO:0015529 | paroxysmal Hemicrania | 43 | 743 | 26 | 114 | <20 | <20 | 4.90 | <20 | <20 |
| MONDO:0015203 | coronary artery congenital malformation | 39 | 259 | 26 | 65 | <20 | <20 | 3.52 | <20 | <20 |
| MONDO:0000565 | infective endocarditis | 38 | 663 | 31 | 107 | <20 | <20 | 6.13 | 121 | <20 |
| MONDO:0030703 | autoimmune vasculitis | 37 | 764 | 21 | 26 | <20 | <20 | 2.30 | <20 | <20 |
| MONDO:0012105 | granulomatosis with polyangiitis | 33 | 261 | 21 | 51 | <20 | <20 | 1.71 | 0 | 0 |
| MONDO:0019018 | Tako-tsubo cardiomyopathy | 31 | 936 | 22 | 130 | <20 | <20 | 7.06 | 57 | <20 |
| MONDO:0017388 | celiac trunk compression syndrome | 29 | 259 | <20 | 31 | <20 | <20 | 2.80 | <20 | <20 |
| MONDO:0006021 | Prinzmetal angina | 28 | 321 | <20 | 25 | <20 | <20 | 1.62 | <20 | <20 |
| MONDO:0003159 | vascular hemostatic disease | 28 | 367 | <20 | 174 | <20 | <20 | 16.25 | 268 | <20 |
| MONDO:0005979 | thoracic outlet syndrome | 28 | 235 | <20 | 62 | <20 | <20 | 3.70 | 26 | <20 |
| MONDO:0006794 | hypersensitivity vasculitis | 26 | 242 | <20 | 20 | <20 | <20 | 1.72 | <20 | <20 |
| MONDO:0017735 | congenital aortic valve stenosis | 25 | 135 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0018615 | hemicrania continua | 23 | 77 | <20 | 38 | <20 | <20 | 4.67 | <20 | <20 |
| MONDO:0019180 | hereditary hemorrhagic telangiectasia | 23 | 23 | <20 | <20 | <20 | 0 | — | <20 | <20 |
| MONDO:0006978 | splenic infarction | 22 | 94 | <20 | <20 | <20 | <20 | — | 101 | <20 |
| MONDO:0007191 | Behcet disease | 22 | 81 | <20 | 38 | <20 | <20 | 4.12 | <20 | <20 |

### related

| Mondo | disease | with data | events after dx | persons | covered events | persons | persons with ≥2 | covered per 1k wear-days | covered events before dx | persons |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| MONDO:0005475 | migraine with aura | 1,718 | 423 | 132 | 101 | 38 | <20 | 0.12 | 0 | 0 |
| MONDO:0018882 | vasculitis | 1,048 | 337 | 99 | 76 | 22 | <20 | 0.12 | 0 | 0 |
| MONDO:0005149 | pulmonary hypertension | 558 | 425 | 107 | 77 | 35 | <20 | 0.39 | <20 | <20 |
| MONDO:0019013 | non-histaminic angioedema | 299 | 57 | 23 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0015530 | trigeminal autonomic cephalalgia | 219 | 23 | <20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0009468 | pseudotumor cerebri | 197 | 198 | 46 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0005081 | preeclampsia | 167 | 36 | 25 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0002824 | extrinsic cardiomyopathy | 139 | 82 | 20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0042981 | aortic valve stenosis | 134 | 99 | 32 | 51 | 22 | <20 | 0.71 | 0 | 0 |
| MONDO:0011479 | postural orthostatic tachycardia syndrome | 129 | 103 | 26 | 42 | <20 | <20 | 1.10 | 0 | 0 |
| MONDO:0005045 | hypertrophic cardiomyopathy | 127 | 197 | 35 | 33 | <20 | <20 | 0.51 | 0 | 0 |
| MONDO:0019809 | congenital aortic valve insufficiency | 116 | 140 | 37 | 65 | <20 | <20 | 0.66 | <20 | <20 |
| MONDO:0015924 | pulmonary arterial hypertension | 111 | 46 | <20 | <20 | <20 | 0 | — | 0 | 0 |
| MONDO:0015691 | hypereosinophilic syndrome | 84 | 26 | <20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0007154 | arteriovenous malformations of the brain | 75 | 37 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0008538 | temporal arteritis | 72 | 35 | <20 | 25 | <20 | <20 | 0.57 | 0 | 0 |
| MONDO:0001280 | choroiditis | 63 | <20 | <20 | <20 | <20 | 0 | — | 0 | 0 |
| MONDO:0004802 | pulmonary eosinophilia | 63 | 24 | <20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0004496 | myocarditis | 58 | 52 | <20 | 0 | 0 | 0 | — | <20 | <20 |
| MONDO:0005832 | lymphangitis | 52 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0018925 | familial or sporadic hemiplegic migraine | 45 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0002303 | central retinal vein occlusion | 44 | <20 | <20 | <20 | <20 | 0 | — | 0 | 0 |
| MONDO:0015529 | paroxysmal Hemicrania | 43 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0015203 | coronary artery congenital malformation | 39 | <20 | <20 | <20 | <20 | 0 | — | 0 | 0 |
| MONDO:0000565 | infective endocarditis | 38 | 76 | <20 | <20 | <20 | <20 | — | <20 | <20 |
| MONDO:0030703 | autoimmune vasculitis | 37 | <20 | <20 | <20 | <20 | 0 | — | 0 | 0 |
| MONDO:0012105 | granulomatosis with polyangiitis | 33 | 69 | <20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0019018 | Tako-tsubo cardiomyopathy | 31 | 74 | <20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0017388 | celiac trunk compression syndrome | 29 | 20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0006021 | Prinzmetal angina | 28 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0003159 | vascular hemostatic disease | 28 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0005979 | thoracic outlet syndrome | 28 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0006794 | hypersensitivity vasculitis | 26 | 28 | <20 | <20 | <20 | 0 | — | 0 | 0 |
| MONDO:0017735 | congenital aortic valve stenosis | 25 | 0 | 0 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0018615 | hemicrania continua | 23 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0019180 | hereditary hemorrhagic telangiectasia | 23 | <20 | <20 | 0 | 0 | 0 | — | 0 | 0 |
| MONDO:0006978 | splenic infarction | 22 | <20 | <20 | <20 | <20 | <20 | — | 0 | 0 |
| MONDO:0007191 | Behcet disease | 22 | 24 | <20 | <20 | <20 | <20 | — | 0 | 0 |

## Visit types for the cohort (top 15 by visits)

| visit concept | name | visits | persons |
|--:|---|--:|--:|
| 9202 | Outpatient Visit | 1,062,385 | 4,644 |
| 581477 | Office Visit | 225,950 | 1,893 |
| 32036 | Laboratory Visit | 114,881 | 2,281 |
| 581458 | Pharmacy visit | 76,635 | 714 |
| 5083 | Telehealth | 69,236 | 1,366 |
| 9201 | Inpatient Visit | 63,335 | 2,260 |
| 9203 | Emergency Room Visit | 29,832 | 2,567 |
| 581479 | Ambulatory Rehabilitation Visit | 17,214 | 603 |
| 42898160 | Non-hospital institution Visit | 15,286 | 195 |
| 8756 | Outpatient Hospital | 5,988 | 329 |
| 38004515 | Hospital | 4,996 | 140 |
| 581476 | Home Visit | 3,228 | 385 |
| 262 | Emergency Room and Inpatient Visit | 2,811 | 628 |
| 38004338 | Pharmacy | 2,631 | 91 |
| 8717 | Inpatient Hospital | 2,119 | 168 |
