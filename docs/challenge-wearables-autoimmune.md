# Wearables for Rare Autoimmune Disease: Predicting Acute Care Episodes

*Draft challenge description. Counts are from the All of Us v8 CDR (R2024Q3R8), masked
to All of Us egress rules (1–19 shown as `<20`); V9 counts are pending. Source runs:
`results/wearables-timing/` and `results/wearables-events/`.*

## **Purpose and Scope**

*Define the rare disease problem, target population or use context, intended users, boundaries of the challenge, and the decision or capability the challenge is intended to improve.*

The challenge asks whether passive data from consumer wearables, linked to the EHR, can
anticipate acute deterioration in people living with rare systemic autoimmune disease.

* **Problem:** Rare systemic autoimmune diseases (Sjögren syndrome, systemic lupus
  erythematosus, myasthenia gravis, systemic sclerosis, antiphospholipid syndrome and
  others) run a relapsing course. Flares, infections on immunosuppression and crises
  (e.g., myasthenic crisis) often end in an emergency department (ED) visit or hospital
  admission. Between clinic visits, care teams see nothing; the EHR records the
  deterioration only once the patient is already in acute care.
* **Need:** A signal between visits that rises before an acute episode, early enough to
  act on (a call, an earlier appointment, a medication review). Consumer wearables
  record heart rate, activity and sleep every day, at no cost to the health system, but
  whether they carry usable early warning in these diseases has not been tested at
  scale.
* **Opportunity:** All of Us links Fitbit data to EHR records for tens of thousands of
  participants, including the largest wearables-linked cohort of rare autoimmune
  patients we are aware of. Early access to the unreleased V10 data allows a genuinely
  prospective holdout: models are frozen on V9 and scored on follow-up time no one has
  seen.
* **Target population:** All of Us participants with a rare autoimmune diagnosis (Mondo
  autoimmune disease subtree, Orphanet / GARD / NORD / Mondo rare subsets, each disease
  mapped through its own SNOMED concept) and Fitbit data. In v8: 17,127 diagnosed
  participants, 1,808 with Fitbit data. Named sub-cohorts: Sjögren syndrome (712 with
  Fitbit data), systemic lupus erythematosus (444), myasthenia gravis (117).
* **Expected outputs:** A model that, on any day with recent wearables data, gives a
  calibrated probability of an ED or inpatient episode starting in the next 30 days, plus
  a short methods and failure-analysis report. Models run inside the All of Us
  Researcher Workbench; no participant-level data leaves it.
* **Users:** Rheumatology and neurology care teams and remote-monitoring programs;
  researchers developing digital biomarkers for rare disease; developers of wearable and
  remote patient monitoring tools; the RAPID program, as a reusable benchmark.
* **Boundaries:** Retrospective and prospective-holdout prediction only, not a deployed
  alerting system. Not a diagnostic task (Task 1 starts after diagnosis). Fitbit data as
  collected in All of Us (daily summaries and minute-level heart rate, steps and sleep);
  no new device data collection. All work stays within All of Us data use and egress
  rules.
* **Capability improved:** Risk stratification between visits for rare autoimmune
  patients, and an honest answer to whether consumer wearables add predictive value
  beyond what the EHR already knows.

## **Scientific and Technical Rationale**

*Explain why the problem is important now, the current state-of-the-art gap, relevant baselines, and why a challenge is an appropriate mechanism for accelerating progress.*

* **Why now:** All of Us v8 holds Fitbit data for 58,891 participants (55,650 with at
  least 30 days), linked to their EHR. V9 extends that, and early V10 access makes a
  prospective evaluation possible. Consumer wearables have already shown pre-symptomatic
  signal for acute illness: resting heart rate and sleep changes ahead of influenza-like
  illness and COVID-19 (e.g., Radin et al., *Lancet Digital Health* 2020; Quer et al.,
  *Nature Medicine* 2021). Autoimmune flares and infections on immunosuppression
  involve the same systemic inflammation.
* **Gap:** Wearable studies in autoimmune disease are small, single-site, and mostly in
  common conditions (rheumatoid arthritis, inflammatory bowel disease). For rare
  autoimmune diseases there is no shared benchmark, no agreed outcome definition, and no
  evaluation that separates the value of wearables from the value of the EHR history
  alongside it. Small cohorts make it easy to overfit and hard to compare methods.
* **Feasibility (v8):** Among rare autoimmune patients with Fitbit data, 2,282 ED or
  inpatient episodes after diagnosis have at least 14 days of Fitbit data in the 30 days
  before them, in 414 participants (241 with two or more). That is 2.3 episodes per 1,000
  days of wear, roughly a 7% chance of an episode in any 30-day window. Sjögren syndrome
  contributes 825 such episodes (154 participants), lupus 577 (99), myasthenia gravis
  228 (28).
* **Baselines:**
  * EHR-only: regularized logistic regression and gradient-boosted trees on prior
    utilization (past ED and inpatient visits), diagnoses, medications, labs, age and sex.
  * Wearables heuristics: deviation of resting heart rate, step count and sleep duration
    from each person's own rolling baseline.
  * Combined: the EHR-only models with the wearables features added.
* **Why a challenge:** The prospective V10 holdout can only be held by an organizer.
  Methods for sparse, irregular, multimodal time series are moving quickly (time-series
  foundation models, self-supervised pretraining on wearables), and a common task with
  blinded scoring is the fastest way to compare them fairly. Training is allowed on the
  roughly 55,000 Fitbit users without these diseases, then evaluated on the rare cohort,
  which rewards methods that transfer from common to rare data. The DREAM and CAGI
  challenges show this model works for clinical prediction.

## **Objectives and Intended Impact**

*Specify the capabilities or innovations to be stimulated or measured and the expected value to patients, caregivers, providers, researchers, developers, or health systems.*

**Objectives**

* Predict the start of an ED or inpatient episode in the next 30 days from the preceding
  wearables data and EHR history, in rare autoimmune patients.
* Measure how much wearables add over an EHR-only model, overall and per disease.
* Stimulate methods that learn from the large general Fitbit population and transfer to
  small rare disease cohorts.
* Secondary (exploratory): detect upcoming first diagnosis of a rare systemic autoimmune
  disease from pre-diagnosis wearables data (v8: 363 patients with at least 30 days of
  Fitbit data in the year before diagnosis).

**Impact**

* **Patients and caregivers:** Earlier contact before a flare or infection becomes an
  admission. Wearables that many patients already own become part of their care, without
  extra clinic visits.
* **Providers:** A ranked list of patients at rising risk between visits, for nurse
  outreach or earlier appointments, in diseases where specialist time is scarce.
* **Researchers and developers:** A standard outcome definition, cohort and benchmark for
  wearables in rare disease, with published baselines and failure analyses that later
  studies can build on.
* **Health systems:** Evidence on whether passive remote monitoring can reduce avoidable
  acute care in high-cost rare disease populations, before investing in deployment.

## **Challenge Structure**

*Recommend the competition format, phases, timeline, participant tasks, expected submissions, eligibility, team rules, judging, and any progression or down-selection process.*

* **Format:** Code-submission challenge on the All of Us Researcher Workbench. Two
  tracks scored on the same cohort:
  * **Combined:** wearables plus EHR and survey data.
  * **Wearables-only:** Fitbit data plus age and sex.
* **Participant task (primary):** For each prediction date, meaning a day with at least
  14 Fitbit days in the prior 30, output the probability that an ED or inpatient
  episode starts within the next 30 days. Inputs are any data dated before the
  prediction date. An episode is a run of ED or inpatient visit starts no more than 7
  days apart.
* **Phases and timeline (proposed):**
  * **Phase 0, preparation (about 2 months):** finalize cohort and outcome definitions
    on V9, build and publish baselines, run the scoring pipeline end to end.
  * **Phase 1, open development (about 3 months):** teams develop on V9 with a public
    validation split and leaderboard (person-level split, scores masked to egress
    rules).
  * **Phase 2, blinded evaluation (about 1 month):** frozen code is run by organizers on
    the V10 holdout: new follow-up time after the V9 cutoff for existing participants,
    plus participants new in V10.
  * **Phase 3, analysis and reporting (about 2 months):** robustness, fairness and
    failure analyses, qualitative review, winners' write-ups.
* **Expected submissions:** Containerized or notebook code that trains (or loads) the
  model and writes predictions for a supplied list of prediction dates; a model card;
  a methods and failure-analysis report of no more than 4 pages.
* **Eligibility:** Researchers with All of Us Registered Tier access (institutional data
  use agreement and completed training), which is required to touch the data. Teams
  outside eligible institutions may join through an eligible member.
* **Team rules:** Teams of up to 5; one team per person. Limited daily leaderboard
  submissions in Phase 1. No external data that could identify participants, and no
  manual labeling of the evaluation set. Final code must reproduce the submitted
  predictions.
* **Judging:** The primary metric decides track rankings. A panel of clinicians
  (rheumatology, neurology) and data scientists reviews the top submissions for clinical
  plausibility, failure analysis and reproducibility; the panel can disqualify a
  submission but does not reorder rankings.
* **Down-selection:** Teams that beat the EHR-only baseline on the Phase 1 validation
  split advance to Phase 2. This is a quality gate only, with no cap on the number of
  teams.

## **Evaluation Framework**

*Define primary and secondary metrics, evaluation datasets, statistical methods, qualitative review where needed, success thresholds, tie-breaking, and requirements for robustness, calibration, generalizability, reproducibility, interpretability, fairness, and failure analysis.*

* **Evaluation datasets:**
  * **Primary:** V10 prospective holdout (prediction dates after the V9 data cutoff).
  * **Secondary:** a held-out person-level split of V9.
  * **Evaluation unit:** person-days, with every eligible prediction date scored.
* **Primary metric:** Area under the precision-recall curve (AUPRC) for the pooled rare
  autoimmune cohort. It suits the roughly 7% positive rate per 30-day window.
* **Wearables value:** The gain in AUPRC of the combined model over the organizers'
  EHR-only baseline on the same prediction dates. This is reported for every team and
  is the headline scientific result.
* **Secondary metrics:**
  * AUROC.
  * Sensitivity and positive predictive value when flagging the top 5% of person-days.
  * Calibration: Brier score, calibration slope and intercept, and reliability curves.
  * Lead time from the first alert to the episode.
  * All of these per named disease (Sjögren syndrome, lupus, myasthenia gravis) where
    counts allow.
* **Statistical methods:** Confidence intervals by bootstrap resampling of participants,
  not person-days, so repeat episodes from one person don't inflate certainty (1,000
  resamples). Paired bootstrap for differences between teams and against baselines.
  Teams whose 95% intervals for the difference overlap share a rank band.
* **Success thresholds:**
  * A submission succeeds if the lower 95% bound of its AUPRC gain over the EHR-only
    baseline is above 0 on the V10 holdout.
  * Wearables-only submissions must beat the personal-baseline heuristic.
* **Tie-breaking:** Better calibration (lower Brier score), then fewer input feature
  groups, then earlier final submission.
* **Robustness:** Performance by amount of recent wear (14–20 vs 21 or more days in
  the 30-day window), by device type, and with simulated wear gaps.
* **Generalizability:**
  * Leave-one-disease-out results.
  * Performance by contributing EHR site.
  * Transfer from the general Fitbit population (models trained without any rare
    autoimmune data, scored on the rare cohort).
* **Fairness:** Performance by sex, age band, race and ethnicity, and income where every
  subgroup has at least 20 participants. The report also notes who in the cohort has
  Fitbit data at all, since participants bring their own devices and that skews who has
  wearables.
* **Calibration:** Required in the report; poorly calibrated models are flagged
  regardless of rank.
* **Reproducibility:** Organizers rerun final code from a clean Workbench environment
  with fixed seeds; predictions must match within tolerance.
* **Interpretability:** Each team reports which inputs drive predictions (aggregate
  feature attributions, ablation of wearables features). The qualitative panel reviews
  these for clinical plausibility.
* **Failure analysis:** Each team characterizes missed episodes and false alarms using
  aggregate, masked summaries (e.g., by episode type, disease, wear pattern before the
  episode).
* **Qualitative review:** Clinician panel assessment of the top submissions' reports for
  plausibility and potential clinical use.
* **Data protection:** All metrics are computed inside the Workbench. Only aggregate
  results leave, with counts from 1 to 19 masked and no statistic derived from a masked
  count.

## **Open items before launch**

* **Label quality:** Diagnoses per disease look inflated relative to known prevalence
  (e.g., Sjögren syndrome in 5,474 v8 participants), which suggests either self-selected
  enrollment or loose coding. The options are to require codes on at least 2 dates, or
  a specialist visit or disease-specific medication, and both would shrink the cohort.
* **Localized scleroderma:** It has a skin-limited course and its diagnosis dates look
  unreliable (more covered episodes before its diagnosis than after). It is proposed as
  pooled-cohort only, not a named sub-cohort.
* **V9 and V10 counts:** All numbers above are v8. Confirm them on V9, and confirm the
  timing and access terms for V10.
* **Visit types:** Decide whether observation stays (visit concept 581385) count as acute
  episodes.
