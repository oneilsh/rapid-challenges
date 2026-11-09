# Wearables for Rare Autoimmune Disease: Predicting Acute Care Episodes

*Draft challenge description. Counts are from the All of Us v8 CDR (R2024Q3R8), masked
to All of Us egress rules (1–19 shown as `<20`); V9 counts are pending. Source runs:
`results/wearables-timing/` and `results/wearables-events/`.*

## **Purpose and Scope**

*Define the rare disease problem, target population or use context, intended users, boundaries of the challenge, and the decision or capability the challenge is intended to improve.*

Here we propose a challenge to test whether daily data from consumer wearables, linked to
the EHR, can anticipate emergency and inpatient care in patients with rare systemic
autoimmune disease.

* **Problem:** Rare systemic autoimmune diseases such as Sjögren syndrome, systemic lupus
  erythematosus (SLE) and myasthenia gravis follow a relapsing course. Flares, infections
  under immunosuppression and crises frequently end in an emergency department (ED) visit
  or hospital admission. Between clinic visits, care teams have little visibility into
  how a patient is doing, and the EHR typically records a deterioration only once the
  patient has already arrived for acute care.
* **Need:** A signal between visits that changes before an acute episode, early enough
  to act on with a phone call, an earlier appointment or a medication review. Consumer
  wearables record heart rate, activity and sleep continuously, but whether these data
  carry useful early warning in rare autoimmune disease has not been tested at any
  meaningful scale.
* **Opportunity:** All of Us links Fitbit data to EHR records for tens of thousands of
  participants; to our knowledge this includes the largest wearables-linked cohort of
  rare autoimmune patients available to researchers. Early access to the unreleased V10
  data makes a prospective holdout possible: models are frozen on V9 and scored on
  follow-up time that no participant has seen.
* **Target population:** All of Us participants with a rare autoimmune diagnosis and
  Fitbit data. We define rare autoimmune diseases as those in the Mondo autoimmune
  disease subtree tagged rare by Orphanet, GARD, NORD or Mondo, each mapped to the EHR
  through its own SNOMED concept. In v8, 17,127 participants carry one of these
  diagnoses and 1,808 of them have Fitbit data, including 712 with Sjögren syndrome, 444
  with SLE and 117 with myasthenia gravis.
* **Expected outputs:** Models that, on any day with recent wearables data, estimate the
  probability that an ED or inpatient episode begins in the next 30 days, accompanied by
  a short methods and failure-analysis report. Every model uses wearables data; teams may
  add EHR and survey data, genomic data, or both. All modeling happens inside the All of
  Us Researcher Workbench, and no participant-level data leaves it.
* **Users:** Rheumatology and neurology care teams and remote monitoring programs;
  researchers developing digital biomarkers for rare disease; developers of wearable and
  remote monitoring tools; and the RAPID program, which gains a reusable benchmark.
* **Boundaries:** The challenge evaluates retrospective and prospective-holdout
  prediction, not a deployed alerting system, and prediction begins after diagnosis
  rather than aiming to diagnose. Wearables data are limited to the Fitbit data already
  collected by All of Us (daily summaries and minute-level heart rate, steps and sleep).
  Wearables are required in every submission; EHR and genomic data are optional. All
  work stays within All of Us data use and egress rules.
* **Capability improved:** Risk stratification between visits for rare autoimmune
  patients, along with a direct measure of what each data type contributes: wearables on
  their own, and the gain from adding EHR or genomic data.

## **Scientific and Technical Rationale**

*Explain why the problem is important now, the current state-of-the-art gap, relevant baselines, and why a challenge is an appropriate mechanism for accelerating progress.*

* **Why now:** All of Us v8 contains Fitbit data for 58,891 participants (55,650 with at
  least 30 days of data) linked to their EHR, and V9 extends both. Prior work has shown
  that resting heart rate and sleep shift ahead of influenza-like illness and COVID-19
  (e.g., Radin et al., *Lancet Digital Health* 2020; Quer et al., *Nature Medicine*
  2021). We hypothesize that autoimmune flares and infections under immunosuppression,
  which share much of the same systemic inflammatory response, leave similar traces.
* **Gap:** Wearable studies in autoimmune disease have mostly been small, single-site,
  and focused on common conditions such as rheumatoid arthritis and inflammatory bowel
  disease. Despite growing interest in digital biomarkers, several key challenges remain
  for rare autoimmune disease: there is no shared benchmark or agreed outcome
  definition, small cohorts make overfitting easy and method comparison difficult, and
  no evaluation separates the value of wearables from that of the EHR history that
  accompanies them.
* **Feasibility (v8):** Among rare autoimmune patients with Fitbit data, 2,282 ED or
  inpatient episodes after diagnosis are preceded by at least 14 days of Fitbit data in
  the prior 30 days. These occur in 414 participants, 241 of whom have two or more. The
  rate works out to 2.3 episodes per 1,000 days of wear, or roughly a 7% chance of an
  episode in any 30-day window. Sjögren syndrome contributes 825 such episodes (154
  participants), SLE 577 (99) and myasthenia gravis 228 (28). Most episodes, however,
  have no wearables data at all in the month before them (74%); usable data is driven by
  when patients wear their devices, not by how strict the coverage threshold is.
* **Baselines:**
  * **EHR-only:** regularized logistic regression and gradient-boosted trees on prior
    utilization (past ED and inpatient visits), diagnoses, medications, labs, age and sex.
  * **Wearables heuristics:** deviation of resting heart rate, step count and sleep
    duration from each person's own rolling baseline.
  * **Combined:** the EHR-only models with wearables features added.
  * **Genomic:** whether a germline genome adds anything here is an open question.
    Because it is fixed for life, it can shift baseline risk (e.g., HLA type, autoimmune
    polygenic risk, drug metabolism variants) but not timing. We expect a small gain at
    most, and the challenge is designed to measure it rather than assume it.
* **Why a challenge:** Only an organizer can hold the prospective V10 holdout. Methods
  for sparse, irregular, multimodal time series are evolving quickly, including
  time-series foundation models and self-supervised pretraining on wearables, and a
  common task with blinded scoring is the most direct way to compare them fairly.
  Teams may also train on the roughly 55,000 Fitbit users without these diagnoses and be
  evaluated on the rare cohort, which rewards methods that transfer from common to rare
  data. DREAM and CAGI have shown this format works well for clinical prediction.

## **Objectives and Intended Impact**

*Specify the capabilities or innovations to be stimulated or measured and the expected value to patients, caregivers, providers, researchers, developers, or health systems.*

**Objectives**

* Predict the start of an ED or inpatient episode in the next 30 days from preceding
  wearables data, with or without EHR and genomic data, in rare autoimmune patients.
* Measure what each data type contributes: wearables alone, and the gain from adding EHR
  or genomic data, overall and per disease.
* Encourage methods that learn from the large general Fitbit population and transfer to
  small rare disease cohorts.
* Secondary (exploratory): detect an upcoming first diagnosis of rare systemic
  autoimmune disease from pre-diagnosis wearables data. In v8, 363 patients have at
  least 30 days of Fitbit data in the year before diagnosis.

**Impact**

* **Patients and caregivers:** Earlier contact before a flare or infection becomes an
  admission, using devices that many patients already own and without additional clinic
  visits.
* **Providers:** A ranked list of patients at rising risk between visits, supporting
  nurse outreach or earlier appointments in diseases where specialist time is scarce.
* **Researchers and developers:** A standard outcome definition, cohort and benchmark for
  wearables in rare disease, with published baselines and failure analyses for later
  studies to build on.
* **Health systems:** Evidence on whether passive remote monitoring can reduce avoidable
  acute care in high-cost rare disease populations, before investing in deployment.

## **Challenge Structure**

*Recommend the competition format, phases, timeline, participant tasks, expected submissions, eligibility, team rules, judging, and any progression or down-selection process.*

* **Format:** A code-submission challenge on the All of Us Researcher Workbench, with one
  task, one evaluation set and one leaderboard.
  * **Wearables required:** Every submission uses Fitbit data.
  * **Other data optional:** Teams may add EHR and survey data, genomic data, or both,
    and declare which they used. All submissions are scored on the same participants and
    prediction dates, and the leaderboard lists each entry's data types.
  * **Required reduced model:** Each team also submits a wearables-only version of its
    approach (Fitbit data plus age and sex), so that the gain from added data is measured
    within each team's method rather than by comparing different teams.
  * **Why not one track per combination:** Genomics is a different skill set, and some
    combinations would likely draw few or no entries. A single leaderboard with optional
    data types avoids empty tracks while still measuring each data type's value.
* **Participant task:** For each prediction date, defined as a day with at least 14
  Fitbit days in the prior 30, teams output the probability that an ED or inpatient
  episode starts within the next 30 days, using only data dated before the prediction
  date. An episode is a run of ED or inpatient visit starts no more than 7 days apart.
* **Phases and timeline (proposed):**
  * **Phase 0, preparation (about 2 months):** We finalize cohort and outcome definitions
    on V9, build and publish baselines, and run the scoring pipeline end to end.
  * **Phase 1, open development (about 3 months):** Teams develop on V9 against a
    person-level validation split, with a leaderboard masked to egress rules.
  * **Phase 2, blinded evaluation (about 1 month):** Organizers run frozen code on the
    V10 holdout, which covers new follow-up time after the V9 cutoff for existing
    participants as well as participants new to V10.
  * **Phase 3, analysis and reporting (about 2 months):** Robustness, fairness and
    failure analyses, qualitative review, and winners' write-ups.
* **Expected submissions:** Containerized or notebook code that trains (or loads) the
  model and writes predictions for a supplied list of prediction dates, for both the
  full model and its wearables-only version; a declaration of the data types used; a
  model card; and a methods and failure-analysis report of no more than 4 pages.
* **Eligibility:** Researchers with All of Us Registered Tier access, which requires an
  institutional data use agreement and completed training and covers the Fitbit, EHR and
  survey data. Using genomic data additionally requires Controlled Tier access. Teams
  from ineligible institutions may participate through an eligible member.
* **Team rules:** Teams of up to 5, with one team per person. Daily leaderboard
  submissions are limited in Phase 1. External data that could identify participants
  and manual labeling of the evaluation set are not allowed, and final code must
  reproduce the submitted predictions.
* **Judging and prizes:** The primary metric determines the leaderboard. Prize
  categories are:
  * **Best overall:** the highest primary score with any combination of data types.
  * **Best wearables-only:** the highest score among the required wearables-only models.
  * **Largest gain from EHR data** and **largest gain from genomic data:** the largest
    improvement of a team's full model over its own wearables-only version, among teams
    that added that data type.
  * A category requires at least 3 eligible entries to be awarded. We announce this at
    launch, so an unpopular combination simply goes unawarded.
  * A panel of clinicians (rheumatology, neurology) and data scientists reviews the top
    submissions for clinical plausibility, failure analysis and reproducibility. The
    panel can disqualify a submission but does not reorder rankings.
* **Down-selection:** Teams whose wearables-only model beats the personal-baseline
  heuristic on the Phase 1 validation split advance to Phase 2. This serves as a quality
  gate only, with no cap on the number of teams.

## **Evaluation Framework**

*Define primary and secondary metrics, evaluation datasets, statistical methods, qualitative review where needed, success thresholds, tie-breaking, and requirements for robustness, calibration, generalizability, reproducibility, interpretability, fairness, and failure analysis.*

* **Evaluation datasets:**
  * **Primary:** the V10 prospective holdout (prediction dates after the V9 data cutoff).
  * **Secondary:** a held-out person-level split of V9.
  * **Evaluation unit:** person-days, with every eligible prediction date scored.
* **Primary metric:** Area under the precision-recall curve (AUPRC) for the pooled rare
  autoimmune cohort, which suits a positive rate of roughly 7% per 30-day window.
* **Value of each data type:**
  * **Added data:** each team's AUPRC gain of its full model over its own wearables-only
    version, reported by the data types added (EHR, genomic, both). This determines the
    gain prizes.
  * **Wearables over the EHR:** for teams using EHR data, the AUPRC gain over the
    organizers' EHR-only baseline on the same prediction dates. This is the central
    scientific result: whether wearables add anything to what the EHR already contains.
* **Secondary metrics:**
  * AUROC.
  * Sensitivity and positive predictive value when flagging the top 5% of person-days.
  * Calibration: Brier score, calibration slope and intercept, and reliability curves.
  * Lead time from the first alert to the episode.
  * Each of the above per named disease (Sjögren syndrome, SLE, myasthenia gravis) where
    counts allow.
* **Statistical methods:** Confidence intervals come from bootstrap resampling of
  participants rather than person-days (1,000 resamples), so that repeat episodes from a
  single person do not inflate certainty. Differences between teams and against
  baselines use a paired bootstrap, and teams whose 95% intervals for the difference
  overlap share a rank band.
* **Success thresholds:**
  * Wearables-only models must beat the personal-baseline heuristic.
  * Submissions using EHR data succeed if the lower 95% bound of their AUPRC gain over
    the EHR-only baseline is above 0 on the V10 holdout.
  * A data-type gain counts, and is prize-eligible, only if the lower 95% bound of the
    full model's gain over the team's wearables-only version is above 0.
* **Tie-breaking:** Better calibration (lower Brier score), then fewer input feature
  groups, then earlier final submission.
* **Robustness:** Performance by amount of recent wear (14–20 vs 21 or more days in the
  30-day window), by device type, and under simulated wear gaps.
* **Generalizability:**
  * Leave-one-disease-out results.
  * Performance by contributing EHR site.
  * Transfer from the general Fitbit population, with models trained without any rare
    autoimmune data and scored on the rare cohort.
* **Fairness:** Performance by sex, age band, race and ethnicity, and income wherever each
  subgroup has at least 20 participants. All of Us data, although extensive, are not a
  random sample, and Fitbit data come from participants who chose to share their own
  devices; the report therefore also describes who in the cohort has wearables data at
  all.
* **Calibration:** Required in each report; poorly calibrated models are flagged
  regardless of rank.
* **Reproducibility:** Organizers rerun final code from a clean Workbench environment
  with fixed seeds, and predictions must match within tolerance.
* **Interpretability:** Each team reports which inputs drive its predictions, through
  aggregate feature attributions and ablation of wearables features. The qualitative
  panel reviews these for clinical plausibility.
* **Failure analysis:** Each team characterizes missed episodes and false alarms using
  aggregate, masked summaries (e.g., by episode type, disease, and wear pattern before
  the episode).
* **Qualitative review:** A clinician panel assesses the top submissions' reports for
  plausibility and potential clinical use.
* **Data protection:** All metrics are computed inside the Workbench. Only aggregate
  results leave it, with counts from 1 to 19 masked and no statistic derived from a
  masked count.

## **Open items before launch**

* **Label quality:** Diagnosis counts look high relative to known prevalence (e.g.,
  Sjögren syndrome in 5,474 v8 participants). This may reflect enrollment that
  over-represents people with chronic disease, loose coding, or both. Requiring codes on
  at least 2 dates, or a specialist visit or disease-specific medication, would tighten
  labels at the cost of cohort size.
* **Localized scleroderma:** The disease is largely skin-limited, and its diagnosis dates
  appear unreliable (more covered episodes before diagnosis than after). We propose
  keeping it in the pooled cohort only, not as a named sub-cohort.
* **V9 and V10 counts:** All numbers above are from v8 and need to be confirmed on V9,
  along with the timing and access terms for V10.
* **Genomic overlap:** We have not yet checked how many cohort participants, or how many
  with covered episodes, also have whole-genome data. If coverage is partial, we need to
  decide whether genomic entries are scored on the full cohort (allowing missing genomes)
  or on the genome subset.
* **Visit types:** Decide whether observation stays (visit concept 581385) count as acute
  episodes.
