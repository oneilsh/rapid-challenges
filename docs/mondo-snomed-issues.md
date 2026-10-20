# Suspected SNOMED CT cross-reference errors in Mondo (release v2026-06-02)

## How these were found

We map Mondo rare diseases to EHR data in OMOP (All of Us) using each disease's own
SNOMED CT cross-reference: `xref: SCTID:…` annotated `MONDO:equivalentTo`. A few rare
diseases came out with implausibly large patient counts. Tracing them showed SNOMED
codes that don't match the Mondo disease.

To look beyond those few, we resolved every `MONDO:equivalentTo` SNOMED cross-reference
on a rare-tagged Mondo term (5,897 codes) to its SNOMED display name. We used the SNOMED
CT International Edition (20250201) on tx.fhir.org, scored each name against the Mondo
label and synonyms, and reviewed the lowest-scoring pairs and a set of genetic-subtype
terms by hand. Most low scores turned out to be legitimate synonyms, such as pellagra ↔
"Niacin deficiency". The pairs below are the ones that don't look right.

Every SNOMED display name below comes from that lookup. Category A has the clearest
cases.

## A. Cross-reference points to a different condition

| Mondo term | SCTID | SNOMED concept | Why it looks wrong |
|---|---|---|---|
| MONDO:0008268 polydactyly-myopia syndrome | 82639001 | Premenstrual tension syndrome | Unrelated condition. Possibly an acronym collision (both abbreviated PMS). |
| MONDO:0011227 short stature-auditory canal atresia-mandibular hypoplasia-skeletal anomalies syndrome | 417081007 | Systolic anterior movement of mitral valve | Unrelated condition. Possibly an acronym collision (both abbreviated SAMS). |
| MONDO:0008559 thrombophilia due to thrombin defect | 111293003 | Venous thrombosis | A possible consequence of the disease, not the disease itself. |
| MONDO:0007791 familial hypocalciuric hypercalcemia 1 | 704166007 | Acquired hypocalciuric hypercalcemia | Acquired is the opposite of familial. The parent, MONDO:0018458, already has 237885008 "Familial hypocalciuric hypercalcemia". |
| MONDO:0009744 neuronal ceroid lipofuscinosis 1 | 720830009 | Congenital neuronal ceroid lipofuscinosis | CLN1 is the infantile form. Congenital NCL is CLN10 (MONDO:0012414 / MONDO:0850001). |
| MONDO:0005638 agnosia | 68345001 | Apraxia | Agnosia and apraxia are distinct disorders. |
| MONDO:0009690 congenital myasthenic syndrome 10 | 230687001 | Myopathy in myasthenia gravis | A congenital myasthenic syndrome is genetic, not autoimmune myasthenia gravis. |
| MONDO:0008518 calcaneonavicular coalition | 62628008 | Multiple synostosis syndrome | A single tarsal coalition versus a multi-joint synostosis syndrome. |

## B. Generic SNOMED concept on a genetic subtype

Here a specific inherited subtype carries the SNOMED code for the general condition,
while the general Mondo term has no SNOMED code or a less fitting one. Anyone mapping
EHR data through Mondo then assigns every patient with the common condition to the rare
subtype. The suggested fix is usually to move the code to the parent.

| Mondo term | SCTID | SNOMED concept | Parent Mondo term (its SNOMED xref) |
|---|---|---|---|
| MONDO:0009960 inflammatory bowel disease 1 | 34000006 | Crohn's disease | The Crohn disease term, MONDO:0005011, carries only 7620006 "Crohn's disease of large bowel". 34000006 seems to belong on MONDO:0005011. |
| MONDO:0011508 lymphoma, non-Hodgkin, familial | 118601006 | Non-Hodgkin's lymphoma (clinical) | MONDO:0018908 non-Hodgkin lymphoma (none) |
| MONDO:0007750 hypercholesterolemia, familial, 1 | 398036000 | Familial hypercholesterolemia | MONDO:0005439 familial hypercholesterolemia (190773008 Hyperbetalipoproteinemia) |
| MONDO:0008791 anencephaly 1 | 89369001 | Anencephalus | MONDO:0000819 anencephaly (none) |
| MONDO:0008115 Feingold syndrome type 1 | 702431004 | Feingold syndrome | MONDO:0015267 Feingold syndrome (none) |
| MONDO:0007378 posterior polymorphous corneal dystrophy 1 | 29504002 | Polymorphous corneal dystrophy | MONDO:0020364 posterior polymorphous corneal dystrophy (none) |
| MONDO:0009227 myofibromatosis, infantile, 1 | 254146000 | Infantile myofibromatosis | MONDO:0016824 infantile myofibromatosis (none) |
| MONDO:0013592 nonsyndromic congenital nail disorder 9 | 87065009 | Dystrophia unguium | MONDO:0019577 anonychia-onychodystrophy syndrome (none). Generic nail dystrophy. |
| MONDO:0009734 hyperinsulinemic hypoglycemia, familial, 1 | 360339005 | Congenital hyperinsulinism | MONDO:0005803 hyperinsulinemic hypoglycemia (42681006 Islet cell hyperplasia) |
| MONDO:0013140 candidiasis, familial, 4 | 235073000 | Familial chronic mucocutaneous candidiasis | MONDO:0015279 chronic mucocutaneous candidiasis (234568006) |
| MONDO:0020721 X-linked sideroblastic anemia 1 | 62677000 | Hereditary sideroblastic anemia | MONDO:0020099 inherited sideroblastic anemia (none) |

## C. SNOMED concept clearly broader or narrower than the Mondo term

These may be deliberate "closest available" choices, but `equivalentTo` overstates
them.

| Mondo term | SCTID | SNOMED concept | Note |
|---|---|---|---|
| MONDO:0015691 hypereosinophilic syndrome | 419455006 | Disorder characterized by eosinophilia | Much broader |
| MONDO:0800026 central hypoventilation syndrome, congenital, 1, with or without Hirschsprung disease | 230499002 | Sleep-related respiratory failure | Much broader |
| MONDO:0016581 conotruncal heart malformations | 218728005 | Interrupted aortic arch | Narrower (one conotruncal defect) |
| MONDO:0004949 neoplasm of mature B-cells | 269476000 | Nodular lymphoma | Narrower |
| MONDO:0015531 non-Langerhans cell histiocytosis | 127069007 | Hemophagocytic syndrome | Narrower / different grouping |
| MONDO:0019632 Lyme disease | 48982009 | Bannwarth syndrome | Narrower (a neuroborreliosis presentation) |
| MONDO:0004686 lattice corneal dystrophy | 1192004 | Familial amyloid neuropathy, Finnish type | Narrower (lattice type II / Meretoja only) |
| MONDO:0018089 double outlet right ventricle | 204299009 | Dextrotransposition of aorta | Different defect, or at best related |
| MONDO:0005696 central nervous system tuberculosis | 186217006 | Tuberculous abscess of brain | Narrower |
| MONDO:0018667 pleural empyema | 405950009 | Abscess of thorax | Broader / different site |

## D. Classification: common acquired conditions under hereditary parents

| Mondo term | Axiom | Note |
|---|---|---|
| MONDO:0007275 carpal tunnel syndrome | `is_a MONDO:0020127 hereditary peripheral neuropathy` (no source) | Classes common carpal tunnel syndrome as hereditary. A familial form exists (OMIM 115430), but the term's SNOMED code, 57406009, is the common condition. |
| MONDO:0007017 vitreous detachment | `is_a MONDO:0020246 inherited vitreoretinopathy` (source EFO:1001238) | Vitreous detachment is overwhelmingly age-related. |

## Reproducing

`make mondo-snomed-review` in https://github.com/oneilsh/rapid-challenges
(`scripts/mondo_snomed_review.py`) regenerates the scored table of all 5,897 pairs
(`results/mondo-snomed-review/`). The table is meant for triage only: string similarity
misses same-words errors like familial versus acquired.
