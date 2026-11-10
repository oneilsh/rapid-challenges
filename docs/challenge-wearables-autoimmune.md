# Wearables for Rare Autoimmune Disease: Predicting Acute Care Episodes

*Draft challenge description. Cohort and outcome counts are from the All of Us v8 CDR
(R2024Q3R8), masked to All of Us egress rules (1–19 shown as `<20`); V9 counts are
pending. Source runs: `results/wearables-timing/` and `results/wearables-events/`.
Numbered references are listed at the end.*

## **Purpose and Scope**

*Define the rare disease problem, target population or use context, intended users, boundaries of the challenge, and the decision or capability the challenge is intended to improve.*

Here we propose a challenge to test whether daily data from consumer wearables, alone or
combined with EHR and genomic data, can anticipate emergency and inpatient care in
patients with rare systemic autoimmune disease.

* **Problem:** Rare systemic autoimmune diseases such as Sjögren syndrome, systemic lupus
  erythematosus (SLE) and myasthenia gravis follow a relapsing course. Flares, infections
  under immunosuppression and crises frequently end in an emergency department (ED) visit
  or hospital admission. Between clinic visits, care teams have little visibility into
  how a patient is doing, and the EHR typically records a deterioration only once the
  patient has already arrived for acute care.
* **Need:** A signal between visits that changes before an acute episode, early enough
  that it could support a phone call, an earlier appointment or a medication review.
  Consumer wearables record heart rate, activity and sleep continuously, but whether
  these data carry useful early warning in rare autoimmune disease has not been tested
  at any meaningful scale.
* **Opportunity:** All of Us links wearables data to EHR records for tens of thousands of
  participants: Fitbit data for more than 68,000 participants in V9, and Apple HealthKit
  data released alongside V9 as a separate dataset [1, 2]. To our knowledge this
  includes the largest wearables-linked cohort of rare autoimmune patients available to
  researchers. Early access to the unreleased V10 data makes a prospective holdout
  possible: models are frozen on V9 and scored on follow-up time that no participant has
  seen.
* **Target population:** All of Us participants with a rare autoimmune diagnosis and
  wearables data. We define rare autoimmune diseases as those in the Mondo autoimmune
  disease subtree tagged rare by Orphanet, GARD, NORD or Mondo, each mapped to the EHR
  through its own SNOMED concept. In v8, 17,127 participants carry one of these
  diagnoses and 1,808 of them have Fitbit data, including 712 with Sjögren syndrome, 444
  with SLE and 117 with myasthenia gravis.
* **Expected outputs:** Models that, on any day with recent wearables data, estimate the
  probability that an ED or inpatient episode begins in the next 30 days. Every model
  uses wearables data; teams may add EHR and survey data, genomic data, or both. Each
  submission consists of code and a trained model run through an organizer-provided
  harness, plus a short report. All modeling happens inside the All of Us Researcher
  Workbench, and no participant-level data leaves it.
* **Users:** Researchers developing digital biomarkers and multimodal risk models for
  rare disease; developers of wearable and remote monitoring tools; clinical teams and
  remote monitoring programs evaluating whether such tools are worth pursuing; and the
  RAPID program, which gains a reusable benchmark.
* **Boundaries:** The challenge evaluates retrospective and prospective-holdout
  prediction, not a deployed alerting system, and prediction begins after diagnosis
  rather than aiming to diagnose. Wearables data are limited to what All of Us already
  holds. Wearables are required in every submission; EHR and survey data and genomic
  data are optional. All work stays within All of Us data use and egress rules.
* **Capability improved:** Methods and evidence for risk stratification between visits
  in rare autoimmune disease, along with a direct measure of what each data type
  contributes: wearables on their own, and the gain from adding EHR or genomic data.

## **Scientific and Technical Rationale**

*Explain why the problem is important now, the current state-of-the-art gap, relevant baselines, and why a challenge is an appropriate mechanism for accelerating progress.*

* **Why now:** All of Us now holds one of the largest wearables datasets linked to
  health records [2], and V9 extends it with more Fitbit participants and Apple
  HealthKit data [1]. Prior work has shown that resting heart rate, sleep and activity
  shift ahead of influenza-like illness [3] and COVID-19 [4], and that adding wearables
  to EHR data improves prediction of several chronic conditions in All of Us [5]. We
  hypothesize that autoimmune flares and infections under immunosuppression, which share
  much of the same systemic inflammatory response, leave similar traces.
* **Gap:** Wearable studies in autoimmune disease have mostly been small, single-site,
  and focused on common conditions such as rheumatoid arthritis and inflammatory bowel
  disease, and large-scale wearables-plus-EHR work has targeted common diseases rather
  than acute events in rare ones [5]. Several key challenges remain for rare autoimmune
  disease: there is no shared benchmark or agreed outcome definition, small cohorts make
  overfitting easy and method comparison difficult, and no evaluation separates the
  value of wearables from that of the EHR history that accompanies them.
* **Feasibility (v8):** Among rare autoimmune patients with Fitbit data, 2,282 ED or
  inpatient episodes after diagnosis are preceded by at least 14 days of Fitbit data in
  the prior 30 days. These occur in 414 participants, 241 of whom have two or more. The
  rate works out to 2.3 episodes per 1,000 days of wear, or roughly a 7% chance of an
  episode in any 30-day window. Sjögren syndrome contributes 825 such episodes (154
  participants), SLE 577 (99) and myasthenia gravis 228 (28). Most episodes, however,
  have no wearables data at all in the month before them (74%); usable data depends on
  when patients wear their devices, not on how strict the coverage threshold is.
* **Baselines:** Baselines are reference points, not competitors, and we intend them to
  be quick first-pass efforts rather than tuned models:
  * **Personal-baseline heuristic (wearables only):** for each prediction date, the
    change in the past week's resting heart rate (or median daytime heart rate where
    resting heart rate is unavailable) and daily steps relative to the person's own
    previous two months. It needs no training and sets the floor every wearables-only
    model must clear.
  * **EHR-only:** regularized logistic regression on prior utilization (counts of past ED
    and inpatient episodes and outpatient visits), age and sex. Prior utilization is
    usually the strongest single predictor of future utilization, so even this simple
    model should be hard to beat by much.
  * **Genomic:** whether a germline genome adds anything here is an open question.
    Because it is fixed for life, it can shift baseline risk (e.g., HLA type, autoimmune
    polygenic risk, drug metabolism variants) but not timing. We expect a small gain at
    most, and the challenge is designed to measure it rather than assume it.
* **Why a challenge:** Only an organizer can hold the prospective V10 holdout. Methods
  for sparse, irregular, multimodal time series are evolving quickly, including
  time-series foundation models and self-supervised pretraining on wearables, and a
  common task with blinded scoring is the most direct way to compare them fairly. Teams
  may also train on the tens of thousands of wearables users without these diagnoses and
  be evaluated on the rare cohort, which rewards methods that transfer from common to
  rare data. Community challenges with blinded evaluation have a strong track record in
  biomedicine: the DREAM Challenges, running since 2006, have posed dozens of
  prediction problems on held-out clinical and molecular data [6], and the Critical
  Assessment of Genome Interpretation (CAGI) has run 50 blinded challenges predicting
  phenotypes from genetic variants, scored by independent assessors [7].

## **Objectives and Intended Impact**

*Specify the capabilities or innovations to be stimulated or measured and the expected value to patients, caregivers, providers, researchers, developers, or health systems.*

**Objectives**

* Predict the start of an ED or inpatient episode in the next 30 days from preceding
  wearables data, with or without EHR and survey data and genomic data, in rare
  autoimmune patients.
* Measure what each data type contributes: wearables alone, and the gain from adding EHR
  and survey data or genomic data, overall and per disease.
* Encourage methods that learn from the large general wearables population and transfer
  to small rare disease cohorts.

**Impact**

The challenge itself produces methods, a benchmark and evidence, not changes in care.
The impacts below depend on later validation and deployment work that the challenge is
meant to inform.

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

## **Challenge Structure**

*Recommend the competition format, phases, timeline, participant tasks, expected submissions, eligibility, team rules, judging, and any progression or down-selection process.*

* **Format:** A challenge run on the All of Us Researcher Workbench, with one task, one
  evaluation set and one leaderboard.
  * **Wearables required:** Every submission uses wearables data.
  * **Data combinations:** Each entry declares one of four combinations: wearables only;
    wearables + EHR and survey data (treated as one data type); wearables + genomic data;
    or wearables + EHR and survey + genomic data. Teams may enter one or several. All
    entries are scored on the same participants and prediction dates, and the leaderboard
    lists each entry's combination.
  * **Enforcing declarations:** At scoring time the harness gives each entry only the
    input data for its declared combination, for example through a separate evaluation
    workspace or input set per combination (Controlled Tier for those with genomic
    data). Teams develop on V9 however they like, but a model scored as wearables-only
    never sees EHR or genomic inputs, and no team touches V10 directly.
* **Organizer-prepared data:** To avoid misunderstandings about the outcome and leakage
  of future information, we prepare the cohort, the prediction dates, the outcome labels
  for training data, and the input data available as of each prediction date. Teams are
  free to engineer their own features from these inputs, but the harness controls what
  data a model can see.
* **Participant task:** For each prediction date, defined as a day with at least 14 days
  of wearables data in the prior 30, teams output the probability that an ED or
  inpatient episode starts within the next 30 days, using only data dated before the
  prediction date. An episode is a run of ED or inpatient visit starts no more than 7
  days apart.
* **Phases and timeline (proposed):**
  * **Phase 0, preparation (about 2 months):** We finalize cohort and outcome
    definitions on V9, prepare the input data, build the baselines and the submission
    harness, and test scoring end to end.
  * **Phase 1, open development (about 3 months):** Teams develop on V9 against a
    person-level validation split, with a leaderboard masked to egress rules.
  * **Phase 2, blinded evaluation (about 1 month):** We run frozen submissions on the V10
    holdout, which covers new follow-up time after the V9 cutoff for existing
    participants as well as participants new to V10.
  * **Phase 3, analysis and reporting (about 2 months):** Stratified results, review of
    team reports, and winners' write-ups.
* **Expected submissions:**
  * **Code and model:** a container image with the team's code, which prepares features
    from the organizer-provided inputs, plus a trained model, run through the harness.
    The harness will likely be built on the Workbench's workflow tools (Cromwell/WDL,
    dsub and Nextflow are supported, each running steps in container images [8]); the
    exact mechanism, including which image registries are allowed, will be settled in
    Phase 0.
  * **Declaration** of the data types used.
  * **Report:** a short methods report (no more than 4 pages) describing the approach,
    the data types used and why, and an analysis of failure cases. The required
    contents are still to be finalized.
* **Eligibility:** Researchers with All of Us Registered Tier access, which requires an
  institutional data use agreement and completed training and covers the wearables, EHR
  and survey data. Using genomic data additionally requires Controlled Tier access.
  Teams from ineligible institutions may participate through an eligible member.
* **Team rules:** Teams of up to 5, with one team per person. Leaderboard submissions are
  limited in Phase 1, and final code must reproduce the submitted predictions.
* **Judging and prizes:** The primary metric determines the leaderboard. Prizes go to
  absolute scores within each declared combination, never to the difference between a
  team's entries, which a team could inflate with a deliberately weak wearables-only
  entry:
  * **Best wearables-only**, **best wearables + EHR and survey**, **best wearables +
    genomic** and **best wearables + EHR and survey + genomic:** the highest primary
    score among entries declaring that combination.
  * A combination requires at least 3 eligible entries to be awarded. We announce this at
    launch, so an unpopular combination simply goes unawarded.
  * An overall prize across combinations is optional; it would most likely go to an
    entry that also wins its combination.
  * A panel of clinicians (rheumatology, neurology) and data scientists reviews the top
    submissions' reports. The panel can disqualify a submission but does not reorder
    rankings.
* **Down-selection:** Teams whose submission beats the personal-baseline heuristic on the
  Phase 1 validation split advance to Phase 2. This serves as a quality
  gate only, with no cap on the number of teams.

## **Evaluation Framework**

*Define primary and secondary metrics, evaluation datasets, statistical methods, qualitative review where needed, success thresholds, tie-breaking, and requirements for robustness, calibration, generalizability, reproducibility, interpretability, fairness, and failure analysis.*

Only the primary metric decides rankings and prizes. Everything else is computed by the
organizers from the submitted predictions and reported alongside the rankings, so it adds
no work for teams.

* **Evaluation datasets:**
  * **Primary:** the V10 prospective holdout (prediction dates after the V9 data cutoff).
  * **Secondary:** a held-out person-level split of V9.
  * **Evaluation unit:** person-days, with every eligible prediction date scored.
* **Primary metric:** Area under the precision-recall curve (AUPRC) for the pooled rare
  autoimmune cohort, which suits a positive rate of roughly 7% per 30-day window.
* **Value of each data type:** Reported, not scored, so there is nothing to gain by
  gaming it.
  * **Across the field:** the best score among entries using a data type against the best
    score among entries without it (e.g., the best wearables + EHR entry against the best
    wearables-only entry), compared by paired bootstrap. Because these are each group's
    best entries, no single team can inflate the difference, and it answers the
    question at the level of current methods.
  * **Within methods:** for teams that enter more than one combination, the difference
    between their own entries (e.g., their wearables + EHR entry against their
    wearables-only entry), summarized across teams. This shows how consistently added
    data helps, as context for the field-level result.
  * **Wearables over the EHR:** the best entries using EHR and survey data against the
    organizers' EHR-only baseline on the same prediction dates. Because this baseline is
    deliberately simple, we treat this comparison as a reference point and not as a
    precise estimate of what wearables add.
* **Statistical methods:** Confidence intervals come from bootstrap resampling of
  participants rather than person-days (1,000 resamples), so that repeat episodes from a
  single person do not inflate certainty. To avoid chains of overlapping intervals
  merging every team into one group, each team is compared with the top-scoring team by
  paired bootstrap; teams whose difference from the leader is not significant share
  first place, and the remaining teams are ranked by point estimate.
* **Success thresholds:**
  * Every submission must beat the personal-baseline heuristic.
  * We consider a data type to add value if the lower 95% bound of the field-level
    difference described above is above 0.
* **Tie-breaking:** Better calibration (lower Brier score), then earlier final
  submission.
* **Calibration:** Brier score, calibration slope and intercept, and reliability curves
  for every submission. Calibration serves as the first tie-breaker, and poorly
  calibrated models are flagged in the results.
* **Site heterogeneity:** All of Us EHR data come from many health care provider
  organizations, each recorded as an obfuscated source code (`src_id`), and coding and
  utilization practices differ between them. For each submission we report AUPRC by
  site group on the V10 holdout, along with a summary of the spread (e.g., the range and
  the lowest-scoring group). Because rare disease patients with wearables data are spread
  thinly across sites, sites will be pooled into groups large enough to report. This is
  scored and reported but not prized; a held-out-site evaluation is not feasible, since
  teams see every site in V9.
* **Robustness:** Results per named disease (Sjögren syndrome, SLE, myasthenia gravis)
  where counts allow, and by amount of recent wear (14–20 vs 21 or more days in the
  30-day window).
* **Subgroups:** AUPRC and calibration by sex, age band, and race and ethnicity, wherever
  each subgroup has at least 20 participants. All of Us data, although extensive, are not
  a random sample, and wearables data come from participants who chose to share their
  own devices (or joined a device study); the results therefore also describe who in the
  cohort has wearables data at all.
* **Reproducibility:** We rerun final submissions through the harness with fixed seeds,
  and predictions must match the submitted ones within tolerance.
* **Interpretability and failure analysis:** Covered in each team's report, reviewed
  qualitatively by the panel for clinical plausibility. Any analysis of missed episodes
  or false alarms uses aggregate, masked summaries.
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
* **V9 and V10 counts:** All counts above are from v8 and Fitbit only. They need to be
  confirmed on V9, along with how much Apple HealthKit data the cohort has and the timing
  and access terms for V10.
* **Genomic overlap:** We have not yet checked how many cohort participants, or how many
  with covered episodes, also have whole-genome data. If coverage is partial, we need to
  decide whether genomic entries are scored on the full cohort (allowing missing genomes)
  or on the genome subset.
* **Harness:** Choose the workflow mechanism and allowed image registries, how inputs are
  truncated at each prediction date, and how compute is provided and limited.
* **Site groups:** Count how many EHR sites (`src_id`) the cohort spans and how many
  covered episodes each has (the events audit now reports this), and choose site groups
  large enough to report. Participants seen at more than one site need a rule (e.g.,
  assignment to the site holding most of their visits).
* **Evaluation workspaces:** Confirm that the Workbench can provide per-combination
  workspaces or input sets for scoring, including a Controlled Tier one for genomic
  entries.
* **Report contents:** Settle the required sections of the team report.
* **Visit types:** Decide whether observation stays (visit concept 581385) count as acute
  episodes.

## **References**

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
