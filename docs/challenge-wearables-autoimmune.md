# AoU Wearables - Diagnostic inference

**Developers/Writers of the Challenge:** Shawn O'Neil, Tony Patelunas

*Repo copy of the challenge description, kept in sync with the shared Google Doc. Counts
are from the All of Us V9 Controlled Tier CDR (C2025Q4R6), masked to All of Us egress
rules; source runs are in `results/wearables-events/` (2026-11-13, inpatient-stay rule).*

## Purpose and Scope

*Define the rare disease problem, target population or use context, intended users, boundaries of the challenge, and the decision or capability the challenge is intended to improve.*

Here we propose a challenge to test whether daily data from consumer wearables, alone or
combined with EHR and genomic data, can anticipate emergency and inpatient care in
patients with rare systemic autoimmune disease.

* **Problem:** Rare systemic autoimmune diseases such as Sjögren syndrome, systemic lupus
  erythematosus (SLE) and myasthenia gravis follow a relapsing course. Flares, infections
  under immunosuppression and crises frequently end in an emergency department (ED) visit
  or hospital admission. Between clinic visits, care teams have little visibility into
  how a patient is doing, and flares or other complications are difficult to predict or
  prevent.
* **Need:** A signal between visits that changes before an acute episode, early enough
  that it could support proactive care. Consumer wearables record heart rate, activity
  and sleep continuously, but whether these data carry useful early warning in rare
  autoimmune disease has not been tested at any meaningful scale.
* **Opportunity:** All of Us links wearables data to EHR records for tens of thousands of
  participants: Fitbit data for more than 68,000 participants in V9, and Apple HealthKit
  data released alongside V9 as a separate dataset [1, 2]. To our knowledge this
  includes the largest wearables-linked cohort of rare autoimmune patients available to
  researchers. Timing the challenge with the upcoming V10 release (expected mid-2027)
  makes a prospective holdout on unseen data for evaluation possible.
* **Target population:** All of Us participants with a rare autoimmune diagnosis and
  wearables data. We define rare autoimmune diseases as those in the Mondo autoimmune
  disease subtree tagged rare by Orphanet, GARD, NORD or Mondo, each mapped to the OMOP
  EHR data through SNOMED mappings. In V9, 23,481 participants carry one of these
  diagnoses and 2,838 of them have Fitbit data, including 993 with Sjögren syndrome, 645
  with SLE and 169 with myasthenia gravis.
* **Expected outputs:** Models that, on any day with recent wearables data, estimate the
  probability that an ED or inpatient episode begins in the next 30 days. All challenge
  models will require the use of wearables data, and teams may add EHR and survey data,
  genomic data, or both, according to their interest and skillset. All modeling and
  evaluation will happen inside the All of Us Researcher Workbench, and no
  participant-level data will be exportable; model exports will be restricted until
  deemed free of potentially re-identifying information.
* **Users:** Initial users will be researchers developing digital biomarkers and
  multimodal risk models for rare disease, and developers of wearable and remote
  monitoring tools. In later translational work, clinical teams and remote monitoring
  programs may use challenge results to evaluate whether such tools are worth pursuing.
  Finally, the RAPID program itself, which will gain a reusable benchmark.
* **Boundaries:** The challenge evaluates retrospective and prospective-holdout
  prediction, not a deployed alerting system, and prediction begins after diagnosis
  rather than aiming to diagnose. Wearables data are limited to what All of Us already
  holds. All work stays within All of Us data use and egress rules.
* **Capability improved:** Methods and evidence for risk stratification between visits
  in rare autoimmune disease, along with a direct measure of what each data type
  contributes: wearables on their own, and the gain from adding EHR or genomic data.

## Scientific and Technical Rationale

*Explain why the problem is important now, the current state-of-the-art gap, relevant baselines, and why a challenge is an appropriate mechanism for accelerating progress.*

* **Why now:** All of Us now holds one of the largest wearables datasets linked to
  health records [2], and V9 extends it with more Fitbit participants and Apple
  HealthKit data [1]. Prior work has shown that resting heart rate, sleep and activity
  shift ahead of influenza-like illness [3] and COVID-19 [4], and that adding wearables
  to EHR data improves prediction of several chronic conditions in All of Us [5]. We
  hypothesize that autoimmune flares and infections under immunosuppression, which share
  much of the same systemic inflammatory response, provide similar signal.
* **Gap:** Wearable studies in autoimmune disease have mostly been small, single-site,
  and focused on common conditions such as rheumatoid arthritis and inflammatory bowel
  disease, and large-scale wearables-plus-EHR work has targeted common diseases rather
  than acute events in rare ones [5]. Several key challenges remain for rare autoimmune
  disease: there is no shared benchmark or agreed outcome definition, small cohorts make
  overfitting easy and method comparison difficult, and no evaluation separates the
  value of wearables from that of the EHR history or genomic information that may
  accompany them.
* **Feasibility (V9):** Among rare autoimmune patients with Fitbit data, 2,244 ED visits
  or inpatient stays after diagnosis are preceded by at least 14 days of Fitbit data in
  the prior 30 days. These occur in 789 participants, 405 of whom have two or more. The
  rate works out to about 1.2 episodes per 1,000 days of wear, or roughly a 3% chance of
  an episode in any 30-day window. Sjögren syndrome contributes 700 such episodes (260
  participants), SLE 620 (190) and myasthenia gravis 234 (61); ED visits alone account
  for 1,615 (639 participants). Most episodes, however, have no wearables data at all in
  the month before them (72%).
* **Prospective holdout size:** Splitting V9 at the V8 data cutoff stands in for the V10
  holdout. In the 14 months after that date, participants already diagnosed and wearing
  a Fitbit had 538 covered episodes (307 participants), and newly enrolled or newly
  wearing participants added 28 more. If V10 adds a similar span of follow-up, we expect
  a holdout of roughly 500 episodes in roughly 300 participants.
* **Baselines:** Minimal baseline models will provide a lower performance floor, as well
  as demonstrations of submission and evaluation harnesses.
  * **Personal-baseline heuristic (wearables only):** for each prediction date, the
    change in the past week's resting heart rate (or median daytime heart rate where
    resting heart rate is unavailable) and daily steps relative to the person's own
    previous two months can serve as a minimal predictive signal.
  * **Wearables + EHR + surveys:** Baseline models utilizing both wearables and EHR data
    will combine wearables-only heuristic metrics as well as EHR signals such as age,
    sex, and prior utilization (counts of past ED and inpatient episodes and outpatient
    visits) in basic regularized logistic regression.
  * **Wearables + Genomic:** whether a germline genome adds anything here is an open
    question. Because it is fixed for life, it can shift baseline risk (e.g., HLA type,
    autoimmune polygenic risk, drug metabolism variants) but not timing. We expect a
    small gain at most, and the challenge is designed to measure it rather than assume
    it.
* **Why a challenge:** Methods for sparse, irregular, multimodal time series are
  evolving quickly, including time-series foundation models and self-supervised
  pretraining on wearables, and a common task with blinded scoring is the most direct
  way to compare them fairly. Teams may also train on the tens of thousands of wearables
  users without these diagnoses and be evaluated on the rare cohort, which rewards
  methods that transfer from common to rare data. Community challenges with blinded
  evaluation have a strong track record in biomedicine: the DREAM Challenges, running
  since 2006, have posed dozens of prediction problems on held-out clinical and
  molecular data [6], and the Critical Assessment of Genome Interpretation (CAGI) has
  run 50 blinded challenges predicting phenotypes from genetic variants, scored by
  independent assessors [7].

## Objectives and Intended Impact

*Specify the capabilities or innovations to be stimulated or measured and the expected value to patients, caregivers, providers, researchers, developers, or health systems.*

**Objectives**

* Predict the occurrence of an ED or inpatient episode in the next 30 days from
  preceding wearables data, with or without EHR and survey data and genomic data, in
  rare autoimmune patients.
* Measure what each data type contributes: wearables alone, and the gain from adding EHR
  and survey data or genomic data, overall and per rare autoimmune disease.
* Encourage methods that learn from the large general wearables population and transfer
  to small rare disease cohorts.

**Impact**

The challenge itself produces methods, a benchmark and evidence. The impacts below
depend on later validation and deployment work that the challenge is meant to inform.

* **Patients and caregivers:** If wearables prove informative, they could eventually
  support earlier contact before a flare or infection becomes an admission, using
  devices that many patients already own.
* **Providers:** Validated models could later feed risk lists for nurse outreach or
  earlier appointments, in diseases where specialist time is scarce. A negative result
  is also useful, as it would steer clinical programs away from monitoring that does not
  pay off.
* **Researchers and developers:** A standard outcome definition, cohort and benchmark for
  wearables in rare disease, with baselines and failure analyses for later studies to
  build on.
* **Health systems:** Early evidence on whether passive remote monitoring merits
  investment for high-cost rare disease populations, before committing to deployment
  studies.

## Challenge Structure

*Recommend the competition format, phases, timeline, participant tasks, expected submissions, eligibility, team rules, judging, and any progression or down-selection process.*

* **Format:** A challenge run on the All of Us Researcher Workbench:
  * **Wearables required:** Every submission uses wearables data.
  * **Data combinations:** Each entry declares one of four combinations: wearables only;
    wearables + EHR and survey data (treated as one data type); wearables + genomic data;
    or wearables + EHR and survey + genomic data. Teams may enter one or several. All
    entries are scored on the same participants and prediction dates, and the leaderboard
    lists each entry's combination.
  * **Enforcing declarations:** At scoring time an evaluation harness will give each
    entry only the input data for its declared combination, for example through a
    separate evaluation workspace or input set per combination (Controlled Tier for those
    with genomic data). No team can access V10 evaluation data during model development.
  * **Organizer-prepared data:** To avoid misunderstandings about the outcome and leakage
    of future information, challenge organizers will prepare the cohorts, the prediction
    dates, and the outcome labels for training data.
* **Participant task:** For each prediction date, defined as a day with at least 14 days
  of wearables data in the prior 30, teams output the probability that an ED or
  inpatient episode starts within the next 30 days, using only data dated before the
  prediction date. An episode is a run of ED or inpatient visit starts no more than 7
  days apart. An inpatient visit counts only as part of a stay: a visit that ends after
  the day it starts, or inpatient visits on consecutive days. Some sites code recurring
  same-day encounters as inpatient visits, and without this rule one site supplied
  nearly half of all episodes.
* **Phases and timeline (proposed):**
  * **Phase 0, preparation (about 2 months):** Challenge organizers finalize cohort and
    outcome definitions on V9, prepare the input data, build the baselines and the
    submission harness, and test scoring end to end.
  * **Phase 1, open development (about 3 months):** Teams develop on V9 training data.
  * **Phase 2, blinded evaluation (about 1 month):** Organizers run frozen submissions on
    the V10 holdout, which covers new follow-up time after the V9 cutoff for existing
    participants as well as participants new to V10.
  * **Phase 3, analysis and reporting (about 2 months):** Stratified results, review of
    team reports, and winners' write-ups.
* **Expected submissions:** As described above, teams may submit one or more models
  utilizing different data combinations (wearables, EHR and survey, and genomic data).
  For each submission:
  * **Code and model:** a container image with the team's code, which prepares features
    from the declared All of Us data inputs, plus a trained model, run through the
    harness. The harness will likely be built on the Workbench's workflow tools
    (Cromwell/WDL, dsub and Nextflow are supported, each running steps in container
    images [8]); the exact mechanism, including which image registries are allowed, will
    be settled in Phase 0.
  * **Declaration** of the data types used.
  * **Report:** a short methods report (no more than 4 pages) describing the approach,
    the data types used and why, and an analysis of failure cases. The required
    contents are still to be finalized.
* **Eligibility:** Researchers with All of Us Registered Tier access, which requires an
  institutional data use agreement and completed training and covers the wearables, EHR
  and survey data. Using genomic data additionally requires Controlled Tier access.
  Teams from ineligible institutions may participate through an eligible member,
  provided they follow all All of Us data use and results export policies.
* **Team rules:** Teams of up to 5, with one team per person.
* **Judging and prizes:** Prizes go to the best absolute scores within each declared
  combination:
  * **Best wearables-only**, **best wearables + EHR and survey**, **best wearables +
    genomic** and **best wearables + EHR and survey + genomic:** the highest primary
    score among entries declaring that combination.
  * A combination requires at least 3 eligible entries to be awarded. We announce this at
    launch, so an unpopular combination simply goes unawarded.
  * A panel of clinicians (rheumatology, neurology) and data scientists reviews the top
    submissions' reports. The panel can disqualify a submission but does not reorder
    rankings.

## Evaluation Framework

*Define primary and secondary metrics, evaluation datasets, statistical methods, qualitative review where needed, success thresholds, tie-breaking, and requirements for robustness, calibration, generalizability, reproducibility, interpretability, fairness, and failure analysis.*

Only the primary metric, AUPRC as described below, will decide rankings and prizes.
Everything else is computed by the organizers from the submitted predictions and
reported alongside the rankings, so it adds no work for teams but provides additional
valuable information on challenge results.

* **Evaluation datasets:**
  * **Primary:** the V10 prospective holdout (prediction dates after the V9 data cutoff).
  * **Evaluation unit:** person-days, with every eligible prediction date scored.
* **Primary metric:** Area under the precision-recall curve (AUPRC) for the pooled rare
  autoimmune cohort, which suits a positive rate of roughly 3% per 30-day window.
* **Value of each data type:** The allowed combinations of data modalities provide a
  unique opportunity to assess the relative value of additional data modalities beyond
  wearables:
  * **Across the field:** the best score among entries using a data type against the best
    score among entries without it (e.g., the best wearables + EHR entry against the best
    wearables-only entry), compared by paired bootstrap. Because these are each group's
    best entries, no single team can inflate the difference, and it answers the
    question at the level of current methods.
  * **Within methods:** for teams that enter more than one combination, the difference
    between their own entries (e.g., their wearables + EHR entry against their
    wearables-only entry), summarized across teams. This shows how consistently added
    data helps, as context for the field-level result.
* **Statistical methods:** 95% confidence intervals for AUPRC will come from bootstrap
  resampling of participants rather than person-days (1,000 resamples), so that repeat
  episodes from a single person do not inflate certainty. Each team is compared with the
  top-scoring team by paired bootstrap; teams whose difference from the leader is not
  significant share first place, and the remaining teams are ranked by point estimate.
* **Tie-breaking:** Better calibration (lower Brier score), then earlier final
  submission.
* **Calibration:** Brier score for every submission.
* **Site heterogeneity:** All of Us EHR data come from many health care provider
  organizations, each recorded as an obfuscated source code (`src_id`), and coding and
  utilization practices differ between them. For each submission we will report the
  spread and variance of AUPRC across sites. This is scored and reported but not prized;
  a held-out-site evaluation is not feasible, since teams see every site in V9 and
  per-site counts of rare autoimmune disease are likely to be small.
* **Robustness:** Results per named disease (Sjögren syndrome, SLE, myasthenia gravis)
  where counts allow, and by amount of recent wear (14–20 vs 21 or more days in the
  30-day window).
* **Subgroups:** AUPRC and calibration by sex, age band, and race and ethnicity, wherever
  each subgroup has at least 20 participants.
* **Interpretability and failure analysis:** Covered in each team's report, reviewed
  qualitatively by the panel for clinical plausibility.
* **Data protection:** All metrics are computed inside the Workbench. Only aggregate
  results leave it, with counts from 1 to 19 masked and no statistic derived from a
  masked count. It is possible that some models themselves may be exportable, but
  challenge organizers will take care to evaluate the potential for re-identification
  risk.

## Open Items and Risks

* **Label quality:** Diagnosis counts look high relative to known prevalence (e.g.,
  Sjögren syndrome in 5,474 v8 participants). This may reflect enrollment that
  over-represents people with chronic disease, loose coding, or both. Requiring codes on
  at least 2 dates, or a specialist visit or disease-specific medication, would tighten
  labels at the cost of cohort size.
* **Localized scleroderma:** The disease is largely skin-limited, and in v8 its diagnosis
  dates looked unreliable (more covered episodes before diagnosis than after; this no
  longer holds in V9). We propose keeping it in the pooled cohort only, not as a named
  sub-cohort.
* **Outcome coding across sites:** Visit types are coded differently across EHR sites.
  The inpatient-stay rule removes the worst case, but one site still records stays as
  runs of same-day inpatient visits, and another has many repeat ED visits in a few
  participants (254 episodes in 26). We need to decide whether to keep ED and inpatient
  together or use ED visits alone (1,615 covered episodes; a holdout of roughly 400), and
  whether to limit how much any one participant can weigh in scoring.
* **V10 and HealthKit:** The counts above are from the V9 Controlled Tier CDR and Fitbit
  only. We still need to check how much Apple HealthKit data the cohort has, and confirm
  the timing, follow-up span and access terms for V10. If V10 adds less follow-up than
  expected, a fallback is to split V9 into training and held-out evaluation data using
  workspace data access controls, which needs to be tested on the platform.
* **Genomic overlap:** We have not yet checked how many cohort participants, or how many
  with wearables-covered ED or inpatient episodes, also have whole-genome data. It is
  possible that genomics data use is not feasible.
* **Harness:** Choose the workflow mechanism and allowed image registries, how inputs are
  truncated at each prediction date, and how compute is provided and limited.
* **Evaluation workspaces:** Confirm that the Workbench can provide per-combination
  workspaces or input sets for scoring, including a Controlled Tier one for genomic
  entries.
* **Report contents:** Settle the required sections of the team report.
* **Visit types:** Decide whether observation stays (visit concept 581385) count as acute
  episodes.

## References

1. All of Us Research Program. Our Largest Genomic Dataset: Curated Data Repository
   version 9 (support article, including the Apple HealthKit release).
   https://support.researchallofus.org/hc/en-us/articles/50653909888788
2. The All of Us Research Program's wearables dataset. *Nature Medicine* (2026).
   https://www.nature.com/articles/s41591-026-04352-3 *(authors and citation details to
   be confirmed)*
3. Radin JM, Wineinger NE, Topol EJ, Steinhubl SR. Harnessing wearable device data to
   improve state-level real-time surveillance of influenza-like illness in the USA: a
   population-based study. *Lancet Digital Health* 2020;2(2):e85–e93.
4. Quer G, et al. Wearable sensor data and self-reported symptoms for COVID-19 detection.
   *Nature Medicine* 2021;27:73–77.
5. Wang WK, Yang R, Pang C, et al. Beyond the Clinic: A Large-Scale Evaluation of
   Augmenting EHR with Wearable Data for Diverse Health Prediction. arXiv:2509.22920
   (2025).
6. Saez-Rodriguez J, Costello JC, Friend SH, et al. Crowdsourcing biomedical research:
   leveraging communities as innovation engines. *Nature Reviews Genetics*
   2016;17(8):470–486.
7. Critical Assessment of Genome Interpretation Consortium. CAGI, the Critical Assessment
   of Genome Interpretation, establishes progress and prospects for computational
   genetic variant interpretation methods. *Genome Biology* 2024;25:53.
8. Verily Workbench. Workflows in Verily Workbench: Cromwell, dsub, and Nextflow.
   https://support.workbench.verily.com/docs/technical_reference/workflows/
