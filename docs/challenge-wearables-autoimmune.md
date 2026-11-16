**AoU Wearables \- Predicting Inpatient and ED Episodes**  
**Developers/Writers of the Challenge:** Shawn O’Neil,  Eric Hurwitz

## Purpose and Scope

*Define the rare disease problem, target population or use context, intended users, boundaries of the challenge, and the decision or capability the challenge is intended to improve.*

Here we propose a challenge to test whether daily data from consumer wearables, alone or combined with EHR and genomic data, can anticipate emergency and inpatient care in patients with rare systemic autoimmune disease.

* **Problem:** Rare systemic autoimmune diseases such as Sjögren syndrome, systemic lupus erythematosus (SLE) and myasthenia gravis follow a relapsing course. Flares, infections under immunosuppression and crises frequently end in an emergency department (ED) visit or hospital admission. Between clinic visits, care teams have little visibility into how a patient is doing, and flares or other complications are difficult to predict or prevent.  
* **Need:** A signal between visits that changes before an acute episode, early enough that it could support proactive care. Consumer wearables record heart rate, activity and sleep continuously, but whether these data carry useful early warning in rare autoimmune disease has not been tested at any meaningful scale.  
* **Opportunity:** All of Us links wearables data to EHR records for tens of thousands of participants: Fitbit data for more than 68,000 participants in V9, and Apple HealthKit data released alongside V9 as a separate dataset (Figure 1\) \[1, 2\]. Therefore, this could be one of the largest wearables-linked cohorts of rare autoimmune patients available to researchers. Timing the challenge with the upcoming V10 release (expected mid-2027) makes a prospective holdout on unseen data for evaluation possible. Moreover, All of Us recently released the CLAD Hexagonal Environmental Linkage (CHEL) dataset, linking patients to geographical locations at a resolution of approximately 62 miles, alongside a wide array of area-level environmental and social variables that may inform analyses (Figure 2).  
* **Target population:** All of Us participants with a rare autoimmune diagnosis and wearables data. We define rare autoimmune diseases as those in the Mondo autoimmune disease subtree tagged rare by Orphanet, GARD, NORD or Mondo, each mapped to the OMOP EHR data through existing SNOMED mappings. In V9, 23,481 participants carry one of these diagnoses and 2,838 of them have Fitbit data, including 993 with Sjögren syndrome, 645 with SLE and 169 with myasthenia gravis (Figure 2).  
* **Expected outputs:** Models that, on any day with recent wearables data, estimate the probability that an ED or inpatient episode begins in the next 30 days. All challenge models will require the use of wearables data, and teams may add EHR and survey data, CHEL data, or both, according to their interest and skillset. All modeling and evaluation will happen inside the All of Us Researcher Workbench, and no participant-level data will be exportable; model exports will be restricted until deemed free of potentially re-identifying information.  
* **Users:** Initial users will be researchers developing digital biomarkers and multimodal risk models for rare disease, and developers of wearable and remote monitoring tools. In later translational work, clinical teams and remote monitoring programs may use challenge results to evaluate whether such tools are worth pursuing. Finally, the RAPID program itself will gain a reusable benchmark.  
* **Boundaries:** The challenge evaluates retrospective and prospective-holdout prediction, not a deployed alerting system, and prediction begins after diagnosis rather than aiming to diagnose. Wearables data are limited to what All of Us already holds. All work stays within All of Us data use and egress rules.  
* **Capability improved:** Methods and evidence for risk stratification between visits in rare autoimmune disease, along with a direct measure of what each data type contributes: wearables on their own, and the gain from adding EHR or CHEL data.

MAP1  
**Figure 1:** Wearable data availability in the All of Us research program. **a**, Cumulative count of participants contributing Fitbit data over time from the BYOD program (black line) and the WEAR study (blue line). Vertical lines indicate the start of enrollment for the All of Us Research Program (gray) and WEAR study (blue). **b**, Geographic distribution of participants in the WEAR program (n \= 25,072). **c**, Geographic distribution of participants in the BYOD study (n \= 33,946). Reproduced from Patten et al. 2026 \[2\].

MAP2  
**Figure 1:** Heatmap distribution of rare autoimmune patients with overlapping wearables data in the H3 hex system; cells with fewer than 20 patients have been masked for patient privacy. Each cell is associated with a variety of area-level environmental and social variables which may provide additional signal for autoimmune patients.

## Scientific and Technical Rationale

*Explain why the problem is important now, the current state-of-the-art gap, relevant baselines, and why a challenge is an appropriate mechanism for accelerating progress.*

* **Why now:** All of Us now holds one of the largest wearables datasets linked to health records \[2\]. Prior work has shown that resting heart rate, sleep and activity shift ahead of influenza-like illness \[3\] and COVID-19 \[4\], and that adding wearables to EHR data improves prediction of several chronic conditions in All of Us \[5\]. We hypothesize that autoimmune flares and infections under immunosuppression, which share much of the same systemic inflammatory response, provide similar signal.  
* **Gap:** Wearable studies in autoimmune disease have mostly been small, single-site, and focused on common conditions such as rheumatoid arthritis and inflammatory bowel disease, and large-scale wearables-plus-EHR work has targeted common diseases rather than acute events in rare ones \[5\]. Several key challenges remain for rare autoimmune disease: there is no shared benchmark or agreed outcome definition, small cohorts make overfitting easy and method comparison difficult, and no evaluation separates the value of wearables from that of the EHR history or other information that may accompany them.  
* **Feasibility (V9):** Among rare autoimmune patients with Fitbit data, 2,244 ED visits or inpatient stays after diagnosis are preceded by at least 14 days of Fitbit data in the prior 30 days. These occur in 789 participants, 405 of whom have two or more. The rate works out to about 1.2 episodes per 1,000 days of wear, or roughly a 3% chance of an episode in any 30-day window. Sjögren syndrome contributes 700 such episodes (260 participants), SLE 620 (190) and myasthenia gravis 234 (61); ED visits alone account for 1,615 (639 participants). Most episodes, however, have no wearables data at all in the month before them (72%).  
* **Prospective holdout size:** Splitting V9 at the V8 data cutoff stands in for the V10 holdout. In the 14 months after that date, participants already diagnosed and wearing a Fitbit had 538 covered episodes (307 participants), and newly enrolled or newly wearing participants added 28 more. If V10 adds a similar span of follow-up, we expect a holdout of roughly 500 episodes in roughly 300 participants.  
* **Baselines:** Minimal baseline models will provide a lower performance floor, as well as demonstrations of submission and evaluation harnesses.  
  * **Personal-baseline heuristic (wearables only):** for each prediction date, the change in the past week's resting heart rate (or median daytime heart rate where resting heart rate is unavailable) and daily steps relative to the person's own previous two months can serve as a minimal predictive signal.  
  * **Wearables \+ EHR \+ surveys:** Baseline models utilizing both wearables and EHR data will combine wearables-only heuristic metrics as well as EHR signals such as age, sex, and prior utilization (counts of past ED and inpatient episodes and outpatient visits) in basic regularized logistic regression.  
  * **Wearables \+ CHEL:** whether area-level environmental or social variables adds anything here is an open question. The variables provided by CHEL within the All of Us workbench are a recent snapshot in time, and the baseline model will use a subset of these; participants may identify longitudinal datasets that provide both spatial and temporal resolution.  
* **Why a challenge:** Methods for sparse, irregular, multimodal time series are evolving quickly, including time-series foundation models and self-supervised pretraining on wearables, and a common task with blinded scoring is the most direct way to compare them fairly. Teams may also train on the tens of thousands of wearables users without these diagnoses and be evaluated on the rare cohort, which rewards methods that transfer from common to rare data. Community challenges with blinded evaluation have a strong track record in biomedicine: the DREAM Challenges, running since 2006, have posed dozens of prediction problems on held-out clinical and molecular data \[6\], and the Critical Assessment of Genome Interpretation (CAGI) has run 50 blinded challenges predicting phenotypes from genetic variants, scored by independent assessors \[7\].

## Objectives and Intended Impact

*Specify the capabilities or innovations to be stimulated or measured and the expected value to patients, caregivers, providers, researchers, developers, or health systems.*

**Objectives**

* Predict the occurrence of an ED or inpatient episode in the next 30 days from preceding wearables data, with or without EHR and survey data and CHEL data, in rare autoimmune patients.  
* Measure what each data type contributes: wearables alone, and the gain from adding EHR and survey data or CHEL data, overall and per rare autoimmune disease.  
* Encourage methods that learn from the large general wearables population and transfer to small rare disease cohorts.

**Impact**

The challenge itself produces methods, a benchmark and evidence. The impacts below depend on later validation and deployment work that the challenge is meant to inform.

* **Patients and caregivers:** If wearables prove informative, they could eventually support earlier contact before a flare or infection becomes an admission, using devices that many patients already own.  
* **Providers:** Validated models could later feed risk lists for proactive outreach or earlier appointments, in diseases where specialist time is scarce. A negative result is also useful, as it would steer clinical programs away from monitoring that does not pay off.  
* **Researchers and developers:** A standard outcome definition, cohort and benchmark for wearables in rare disease, with baselines and failure analyses for later studies to build on.  
* **Health systems:** Early evidence on whether passive remote monitoring merits investment for high-cost rare disease populations, before committing to deployment studies.

## Challenge Structure

*Recommend the competition format, phases, timeline, participant tasks, expected submissions, eligibility, team rules, judging, and any progression or down-selection process.*

* **Format:** A challenge run on the All of Us Researcher Workbench:  
  * **Wearables required:** Every submission must use wearables data.  
  * **Data combinations:** Each entry declares one of four combinations: wearables only; wearables \+ EHR and survey data (treated as one data type); wearables \+ CHEL data; or wearables \+ EHR and survey \+ CHEL data. Teams may enter one or several.  
  * **Enforcing declarations:** At scoring time an evaluation harness will give each entry only the input data for its declared combination, for example through a separate evaluation workspace or input set per combination. No team can access V10 evaluation data during model development.  
  * **Organizer-prepared data:** To avoid misunderstandings about the outcome and leakage of future information, challenge organizers will prepare the cohorts, the prediction dates, and the outcome labels for training data.  
* **Participant task:** For each prediction date, defined as a day with at least 14 days of wearables data in the prior 30, teams output the probability that an ED or inpatient episode starts within the next 30 days, using only data dated before the prediction date. An episode is a run of ED or inpatient visit starts no more than 7 days apart. An inpatient visit counts only as part of a stay: a visit that ends after the day it starts, or inpatient visits on consecutive days. Some sites code recurring same-day encounters as inpatient visits, and without this rule one site supplied nearly half of all episodes.  
* **Phases and timeline (proposed):**  
  * **Phase 0, preparation (about 2 months):** Challenge organizers finalize cohort and outcome definitions on V9, prepare the input data, build the baselines and the submission harness, and test scoring end to end.  
  * **Phase 1, open development (about 3 months):** Teams develop on V9 training data.  
  * **Phase 2, blinded evaluation (about 1 month):** Organizers run frozen submissions on the V10 holdout, which covers new follow-up time after the V9 cutoff for existing participants as well as participants new to V10.  
  * **Phase 3, analysis and reporting (about 2 months):** Stratified results, review of team reports, and winners' write-ups.  
* **Expected submissions:** As described above, teams may submit one or more models utilizing different data combinations (wearables, EHR and survey, and CHEL data). For each submission:  
  * **Code and model:** a container image with the team's code, which prepares features from the declared All of Us data inputs, plus a trained model, run through the harness. The harness will likely be built on the Workbench's workflow tools (dsub and Nextflow are supported, each running steps in container images \[8\]); the exact mechanism, including which image registries are allowed, will be settled in Phase 0\.  
  * **Declaration** of the data types used.  
  * **Report:** a short methods report (no more than 4 pages) describing the approach, the data types used and why, and an analysis of failure cases. The required contents are still to be finalized.  
* **Eligibility:** Researchers with All of Us Controlled Tier access, which requires an institutional data use agreement and completed training and covers the wearables, EHR, survey, and CHEL data. Teams from ineligible institutions may participate through an eligible member, provided they follow all All of Us data use and results export policies. While some data combinations are available in the Registered Tier with fewer access requirements, these data are date shifted, preventing using dates to identify new episodes in V10 vs V9 data.  
* **Team rules:** Teams of up to 5, with one team per person.  
* **Judging and prizes:** Prizes go to the best absolute scores within each declared combination:  
  * **Best wearables-only**, **best wearables \+ EHR and survey**, **best wearables \+ CHEL** and **best wearables \+ EHR and survey \+ CHEL:** the highest primary score among entries declaring that combination.  
  * A combination requires at least 3 eligible entries to be awarded. We announce this at launch, so an unpopular combination simply goes unawarded.  
  * A panel of clinicians (rheumatology, neurology) and data scientists reviews the top submissions' reports. The panel can disqualify a submission but does not reorder rankings.

## Evaluation Framework

*Define primary and secondary metrics, evaluation datasets, statistical methods, qualitative review where needed, success thresholds, tie-breaking, and requirements for robustness, calibration, generalizability, reproducibility, interpretability, fairness, and failure analysis.*

Only the primary metric, AUPRC as described below, will decide rankings and prizes. Everything else is computed by the organizers from the submitted predictions and reported alongside the rankings, so it adds no work for teams but provides additional valuable information on challenge results.

* **Evaluation datasets:**  
  * **Primary:** the V10 prospective holdout (prediction dates after the V9 data cutoff).  
  * **Evaluation unit:** person-days, with every eligible prediction date scored.  
* **Primary metric:** Area under the precision-recall curve (AUPRC) for the pooled rare autoimmune cohort, which suits a positive rate of roughly 3% per 30-day window.  
* **Value of each data type:** The allowed combinations of data modalities provide a unique opportunity to assess the relative value of additional data modalities beyond wearables:  
  * **Across the field:** the best score among entries using a data type against the best score among entries without it (e.g., the best wearables \+ EHR entry against the best wearables-only entry), compared by paired bootstrap. Because these are each group's best entries, no single team can inflate the difference, and it answers the question at the level of current methods.  
  * **Within methods:** for teams that enter more than one combination, the difference between their own entries (e.g., their wearables \+ EHR entry against their wearables-only entry), summarized across teams. This shows how consistently added data helps, as context for the field-level result.  
* **Statistical methods:** 95% confidence intervals for AUPRC will come from bootstrap resampling of participants rather than person-days (1,000 resamples), so that repeat episodes from a single person do not inflate certainty. Each team is compared with the top-scoring team by paired bootstrap; teams whose difference from the leader is not significant share first place, and the remaining teams are ranked by point estimate.  
* **Tie-breaking:** Better calibration (lower Brier score), then earlier final submission.  
* **Calibration:** Brier score for every submission.  
* **Site heterogeneity:** All of Us EHR data come from many health care provider organizations, each recorded as an obfuscated source code (`src_id`), and coding and utilization practices differ between them. For each submission we will report the spread and variance of AUPRC across sites. This is scored and reported but not prized; a held-out-site evaluation is not feasible, since teams see every site in V9 and per-site counts of rare disease are small.  
* **Robustness:** Results per named disease (Sjögren syndrome, SLE, myasthenia gravis) where counts allow, and by amount of recent wear (14–20 vs 21 or more days in the 30-day window).  
* **Subgroups:** AUPRC and calibration by sex, age band, and race and ethnicity, wherever each subgroup has at least 20 participants.  
* **Interpretability and failure analysis:** Covered in each team's report, reviewed qualitatively by the panel for clinical plausibility.  
* **Data protection:** All metrics are computed inside the Workbench. Per All of Us policy, only aggregate results may be exported, with counts from 1 to 19 masked and no statistic derived from a masked count. It is possible that some models themselves may be exportable, but challenge organizers will take care to evaluate the potential for re-identification risk.

## Technical Implementation

*Describe the platform configuration, submission format, compute environment, security model, evaluation pipeline, anti-gaming controls, auditability, baseline implementation, and infrastructure constraints.*

* **Platform configuration:** Everything runs on the All of Us Researcher Workbench, Controlled Tier, in three kinds of workspace:
  * **Challenge data workspace (organizers, shared read-only with registered teams):** the V9 training cohort, prediction dates, outcome labels and disease assignments as derived tables, plus documentation, starter notebooks and baselines. Teams copy from it into their own workspaces.
  * **Team workspaces (teams):** each team's own Controlled Tier workspaces, where they develop on V9 with any of the data they are entitled to.
  * **Scoring workspaces (organizers only):** one input set per declared data combination, holding the V10 holdout. No team member is ever added to these.
* **Submission format:**
  * **Container image:** pushed to an allowed registry and referenced by its digest, so the scored image cannot change after submission.
  * **Model artifacts:** trained weights and any lookup tables, inside the image or in a bucket the harness reads.
  * **Manifest:** team, declared data combination, entry point, and resources requested (CPU, memory, GPU, time).
  * **Output:** one table per run with person ID, prediction date and predicted probability. The harness rejects anything missing a row, with probabilities outside [0, 1], or with extra columns.
* **Compute environment:** The harness runs each submission as a batch job (dsub or Nextflow, settled in Phase 0) with fixed resource ceilings, for example a set number of CPUs and memory, an optional single GPU, and a wall-clock limit per run. During Phase 1 teams pay for their own development compute through their Workbench billing; the challenge pays for scoring.
* **Security model:**
  * Holdout data live only in the scoring workspaces, and only organizers have access.
  * Containers run with no network access. Inputs are mounted read-only, and only the prediction table is collected.
  * Each run sees only the tables for its declared combination; for example, a wearables-only run receives no EHR, survey or CHEL tables.
  * Nothing leaves the Workbench except aggregate scores that have passed the All of Us dissemination rules (1–19 masked).
* **Evaluation pipeline:**
  1. Build the V10 holdout from the V10 CDR: the same cohort, prediction date and outcome code as V9, applied to dates after the V9 cutoff.
  2. Run every frozen submission on its combination's inputs.
  3. Validate the output tables.
  4. Compute the primary and secondary metrics, bootstrap intervals and stratified results.
  5. Apply egress masking and export the aggregate results.

  The same pipeline runs on a V9 validation split during Phase 1, so it has been tested end to end before the real scoring.
* **Anti-gaming controls:**
  * **No holdout access:** the holdout is new follow-up time and new participants that do not exist in V9, and teams never see it.
  * **Frozen submissions:** the image is identified by its digest and the manifest is locked at the Phase 1 deadline.
  * **Limited submissions:** at most two final submissions per combination per team, and only the better one counts.
  * **Validation leaderboard limits:** the Phase 1 leaderboard scores a time-based V9 split with a weekly submission limit, so teams can check their pipeline without repeatedly tuning to the leaderboard.
  * **No future data:** a model must not use data dated on or after a prediction date. Per-date truncated inputs would multiply compute by the number of prediction dates, so the harness provides the full holdout inputs and then checks causality. It reruns each submission with all data after several random cutoff dates removed. Predictions for dates before each cutoff must not change, beyond floating-point tolerance. Submissions that fail are disqualified.
  * **Declared combinations:** enforced by which inputs each run receives, not trusted from the manifest.
* **Auditability:** Everything needed to repeat a score is stored in the scoring workspace:
  * the scoring code, versioned in a public repository that holds no data;
  * input versions (CDR release and derived-table version), image digests, manifests, run logs and random seeds;
  * the masked result exports.

  Any score can be rerun from these.
* **Baseline implementation:** The organizers write the baselines described above (personal-baseline heuristic; regularized logistic regression on wearables, EHR and survey features; the same with a subset of CHEL variables) in Python, packaged in the same container format as team submissions. They serve three purposes: the floor for scoring, a worked example of a valid submission, and a check of the harness.
* **Infrastructure constraints:**
  * Compute is billed per workspace. BigQuery is billed by data scanned, which makes the minute-level Fitbit tables expensive to query carelessly; the starter code shows the cheaper patterns.
  * GPU availability and the list of allowed image registries depend on the Workbench.
  * V10's release date sets the date of Phase 2 (see Execution Plan).
  * Model weights cannot be exported until they are reviewed for re-identification risk, so trained models stay on the Workbench by default.

## Participant Experience and Support

*Identify target participant communities and the documentation, tutorials, data dictionaries, starter code, baseline models, office hours, help desk, and accessibility support needed for successful participation.*

* **Target communities:**
  * Machine learning for health researchers working on time series, irregular sampling and foundation models.
  * Digital biomarker and wearables groups.
  * Biomedical informatics groups already working in All of Us.
  * Rheumatology and neurology researchers with an interest in data.
  * Trainees: graduate students and postdocs, through their institution's data use agreement.

  Teams that combine a clinician with a modeler are encouraged.
* **What we will reuse from All of Us:** The program already maintains:
  * Workbench documentation and the User Support Hub;
  * training required for Controlled Tier access;
  * tutorial and featured workspaces, including some covering Fitbit data;
  * the Data Dictionary and Data Browser;
  * its office hours.

  The challenge materials link to these rather than duplicating them.
* **What the challenge adds:**
  * **Challenge handbook:** the task, outcome and episode definitions, prediction dates, data combinations, submission rules, timeline, scoring and prize rules, in one place.
  * **Data dictionary for the derived tables:** cohort, prediction dates, labels, disease mapping (Mondo to OMOP), and how the cohort and labels were built. It links to the All of Us documentation for Fitbit, HealthKit, EHR, survey and CHEL data.
  * **Tutorials and starter code:** notebooks in the challenge data workspace showing how to load the derived tables and query wearables data cheaply, a worked example from features to a prediction table, and how to build, test and submit a container.
  * **Baseline models:** the organizer baselines, with code and V9 validation scores.
  * **Local test harness:** a small script that runs a submission container on a V9 sample the same way the scorer will, including the causality check, so teams can catch problems before submitting.
  * **Challenge office hours:** every two weeks during Phase 1, at alternating times for different time zones, plus a launch webinar and one session before the submission deadline. Sessions are recorded and captioned.
  * **Help desk:** Workbench access and billing questions go to the All of Us support desk. Challenge questions go to a challenge forum or mailbox, answered within two business days, with answers that apply to everyone added to a public FAQ.
* **Accessibility:** Documentation in accessible HTML, as well as PDF. Recorded, captioned sessions. Office hours at more than one time of day. Advance notice of the Controlled Tier access steps, which can take weeks at some institutions. Compute support (see Incentives) so that teams without large grants can take part.

## Incentives, Outreach, and Partnerships

*Recommend monetary and/or non-monetary incentives, communications and recruitment channels, patient and provider engagement, and partnerships that would strengthen participation, credibility, or downstream adoption.*

* **Monetary incentives:**
  * **Prizes:** a prize for the winner of each awarded data combination (amounts to be set to the budget; for example, an equal amount per combination), with an optional smaller runner-up prize. Combinations with fewer than 3 eligible entries are not awarded, so the prize budget should assume some go unawarded.
  * **Compute credits:** Workbench compute credits for registered teams during Phase 1, perhaps tiered with extra credits for student-led teams. This lowers the main practical barrier, since development on minute-level wearables data is not free.
* **Non-monetary incentives:**
  * Co-authorship for top teams on the challenge overview paper.
  * Invitations to present at a results session, for example a workshop at AMIA or a machine learning for health venue.
  * Publication of winning methods as All of Us featured workspaces, with credit to the team.
  * A lasting benchmark for later papers to cite.
* **Communications and recruitment:**
  * All of Us researcher newsletters and the Research Hub.
  * AMIA working groups.
  * Machine learning for health communities (ML4H, CHIL), as well as relevant mailing lists and preprint announcements.
  * Rheumatology and neurology societies.
  * Institutional All of Us leads who manage data use agreements.
  * The RAPID program's own channels.

  Announce at least 8 weeks before Phase 1 opens, so that teams have time to get Controlled Tier access.
* **Patient and provider engagement:**
  * Patient organizations for the named diseases (for example, the Sjögren's Foundation, the Lupus Foundation of America and the Myasthenia Gravis Foundation of America) and NORD for the rare disease community overall. They can review the outcome definition and how results are described, help explain what an early warning would mean to patients, and share the results.
  * Clinicians on the review panel, together with the patient organizations, can say which kinds of error matter most, such as how many false alarms would be acceptable.
* **Partnerships:**
  * **All of Us program and Data and Research Center:** V10 timing, scoring workspaces, policy review of exported results and model exports, and possible co-promotion.
  * **Verily Workbench:** harness mechanism, allowed registries and GPU availability.
  * **CHEL data team:** documentation of the area-level variables, and their own interest in seeing the data used.
  * **Academic rheumatology and neurology groups:** the clinical panel and later translational work.

## Execution Plan and Resources

*Provide a launch schedule, critical path, responsible parties, staffing, budget assumptions, approvals, dependencies, procurement needs, and operational plan through closeout and results dissemination.*

* **Launch schedule (tentative, set by the V10 release, expected mid-2027):**

| Period | Phase | Main work |
| :---- | :---- | :---- |
| Dec 2026 – Jan 2027 | Approvals and announcement | Program approvals, rules and prize terms, harness mechanism chosen, announcement and pre-registration open |
| Feb – Mar 2027 | Phase 0, preparation | Final cohort and outcome definitions, derived tables, baselines, harness and causality check, end-to-end test on a V9 split |
| Apr – Jun 2027 | Phase 1, open development | Teams develop; validation leaderboard; office hours; submissions freeze at the end |
| V10 release + ~6 weeks | Phase 2, blinded evaluation | Build the V10 holdout, run and check submissions, compute scores |
| Following 2 months | Phase 3, analysis and reporting | Stratified results, panel review of reports, winners announced, results exported after masking |
| Following ~3 months | Dissemination and closeout | Results session, overview paper, featured workspaces, archive of the harness and scoring code |

* **Critical path:** Controlled Tier access for teams, then the harness working end to end on V9, then the Phase 1 freeze, then the V10 release, then the holdout build, then scoring. The V10 date is the one fixed external dependency. If V10 slips, Phase 1 stays open longer, or submissions stay frozen until V10 arrives; the schedule does not depend on V10 coming early.
* **Responsible parties:**
  * **Challenge leads (S. O'Neil, E. Hurwitz):** scientific design, rules, panel, communications, final decisions.
  * **Data scientist:** cohort and labels, baselines, metrics and statistics, office hours on the task and modeling.
  * **Data engineer:** derived tables, scoring workspaces, harness, container pipeline, causality checks, cost monitoring.
  * **Clinical panel (rheumatology, neurology) and patient organization advisors:** outcome review and report review.
  * **All of Us program:** V10, workspace provisioning, policy review.
* **Staffing (effort per phase):**

| Phase (months) | Data scientist | Data engineer |
| :---- | :---- | :---- |
| Approvals and announcement (2) | 10% | 10% |
| Phase 0, preparation (2) | 50% | 75% |
| Phase 1, open development (3) | 25% | 25% |
| Phase 2, blinded evaluation (~1.5) | 50% | 75% |
| Phase 3, analysis and reporting (2) | 50% | 10% |
| Dissemination and closeout (3) | 15% | 5% |
| **Total (~13.5 months)** | **≈ 4.2 person-months** | **≈ 3.9 person-months** |

  These come to about 30% of a full-time data scientist and about 30% of a full-time data engineer over roughly 13–14 months, front-loaded in Phase 0 and Phase 2. The challenge leads need about 5–10% each throughout, more around launch and reporting. Clinical panel members need a few days each in Phase 3.
* **Budget assumptions:**
  * **Personnel:** the effort above, at institutional rates.
  * **Organizer cloud costs:** derived-table builds, scoring runs and bootstrap analysis. Expected to be modest, low thousands of US dollars, but measured in Phase 0 by timing the baselines and a large test submission.
  * **Team compute credits:** a fixed pool, for example a set amount per registered team, with a limit on the number of funded teams.
  * **Prizes and panel:** prizes per awarded combination, honoraria for the clinical panel and patient advisors.
  * **Dissemination:** results session and travel for presenting teams, open-access publication fees.
* **Approvals:**
  * All of Us program agreement to host a challenge on the Workbench, including organizer-run scoring of team containers on V10.
  * Program review of exported results and of any model export.
  * An institutional determination for the organizers' own role (expected to fall under All of Us data use rather than new human subjects research; to be confirmed).
  * Prize terms and eligibility rules approved under the funder's prize authority.
* **Dependencies:** V10 release date and content (Fitbit continuing, EHR refresh). Workbench support for organizer-only scoring workspaces and containerized batch jobs. Continued availability of CHEL and HealthKit in V10.
* **Procurement:** Billing account and funds for organizer workspaces. A method for distributing team compute credits. A prize disbursement mechanism. Honorarium agreements for the panel and advisors.
* **Operations through closeout:**
  * During Phase 1: regular office hours and an updated FAQ; a written log of rule clarifications sent to all teams; weekly cost monitoring.
  * In Phases 2 and 3: a documented scoring run, with results checked by a second organizer before release; the panel review; winners notified, then a public announcement.
  * At closeout: the harness, scoring code and baselines archived publicly (no data); the derived-table definitions published so that the benchmark can be rerun on later releases; the overview paper submitted.

## Risks, Assumptions, and Open Decisions

*Identify scientific, data, legal, privacy/security, platform, participation, evaluation, and adoption risks; document key assumptions; and specify decisions or evidence needed before launch.*

**Risks**

* **Scientific:** Wearables may carry little signal ahead of acute episodes in these diseases, or the signal may be swamped by prior utilization in the EHR. This is still a useful result, and the data-type comparison is designed to report it clearly.
* **Data:** Fitbit wear is uneven and mostly absent before episodes (72% of episodes have no covered month). The cohort is skewed toward people who own and wear devices. Diagnosis codes may be loose (see Label quality below). CHEL variables are static snapshots at about 62-mile resolution.
* **Legal and policy:** Prize eligibility under the funder's rules, and All of Us terms for an organizer running other teams' code on Controlled Tier data, need sign-off before launch.
* **Privacy and security:** Model exports could memorize participant data. Small subgroups invite derived small counts. Mitigations: no network access during scoring, aggregate-only export with masking, and no model export without review.
* **Platform:** The harness mechanism, GPU availability or registry rules may not support the plan as written. Workbench changes during the challenge could break the harness. The V10 release may slip.
* **Participation:** Controlled Tier access takes time and is out of reach for some researchers; compute costs fall on teams; the outcome is rare and noisy, which may discourage people. Some combinations may draw fewer than 3 entries.
* **Evaluation:** The holdout is small (about 500 episodes in about 300 participants), so confidence intervals will be wide and many teams may tie for first. Repeat episodes concentrated in a few participants or sites can dominate the score.
* **Adoption:** Results come from one research cohort with Fitbit devices and may not transfer to clinical populations or other devices. A positive result is a reason for prospective validation, not deployment.

**Assumptions**

* V10 is released on the Workbench around mid-2027, with Fitbit, EHR and CHEL data continuing past the V9 cutoff.
* Organizers can run team containers on V10 data in workspaces that teams cannot access, and can export aggregate scores under the dissemination policy.
* Teams can obtain Controlled Tier access within the announcement-to-launch window.
* The V9 split at the V8 cutoff is a reasonable stand-in for the size and makeup of the V10 holdout.
* Staffing and organizer compute estimates hold within about 25%. Phase 0 measurements will confirm this.

**Open items and decisions needed before launch**

* **Label quality:** Diagnosis counts look high relative to known prevalence (e.g., Sjögren syndrome in 5,474 v8 participants). This may reflect enrollment that over-represents people with chronic disease, loose coding, or both. Requiring codes on at least 2 dates, or a specialist visit or disease-specific medication, would tighten labels at the cost of cohort size.  
* **Localized scleroderma:** The disease is largely skin-limited, and in v8 its diagnosis dates looked unreliable (more covered episodes before diagnosis than after; this no longer holds in V9). We propose keeping it in the pooled cohort only, not as a named sub-cohort.  
* **Outcome coding across sites:** Visit types are coded differently across EHR sites. The inpatient-stay rule removes the worst case, but one site still records stays as runs of same-day inpatient visits, and another has many repeat ED visits in a few participants (254 episodes in 26). We need to decide whether to keep ED and inpatient together or use ED visits alone (1,615 covered episodes; a holdout of roughly 400), and whether to limit how much any one participant can weigh in scoring.  
* **V10 and HealthKit:** The counts above are from the V9 Controlled Tier CDR and Fitbit only. V9 adds Apple HealthKit data as a separate dataset (about 19,900 participants, 4,067 of them also with Fitbit). In our cohort, HealthKit covers 774 more ED or inpatient episodes (261 persons) beyond Fitbit's 2,244 (789 persons). Most of that coverage comes from phone or other-app data such as step counts rather than an Apple Watch: watch data alone covers 199 episodes and starts only in 2020\. HealthKit also differs from Fitbit in data types and sources (more than 100 device and app makers), and some rows carry placeholder 1969/1970 timestamps. We plan to keep Fitbit as the basis for the cohort and coverage rule, and are considering offering HealthKit as an optional extra input.  
* **Harness:** Choose the workflow mechanism and allowed image registries, how inputs are truncated at each prediction date, and how compute is provided and limited.  
* **Evaluation workspaces:** Confirm that the Workbench can provide per-combination workspaces or input sets for scoring.  
* **Report contents:** Settle the required sections of the team report.  
* **Visit types:** Decide whether observation stays (visit concept 581385\) count as acute episodes.
* **Incentives:** Set prize amounts, whether there is a runner-up prize, and the size of the team compute-credit pool.
* **Phase 1 leaderboard:** Choose the V9 validation split (time cutoff) and the weekly submission limit, or whether to have a leaderboard at all.
* **Causality check:** Settle the number of random cutoffs, the tolerance, and how a failed check is handled (disqualify, or allow one fix).
* **Approvals:** Get All of Us program agreement on organizer-run scoring and on results export, plus prize terms from the funder, before the announcement.

## References

1. All of Us Research Program. Our Largest Genomic Dataset: Curated Data Repository version 9 (support article, including the Apple HealthKit release). [https\://support.researchallofus.org/hc/en-us/articles/50653909888788](https://support.researchallofus.org/hc/en-us/articles/50653909888788)  
2. Patten, T., Preble, E.A., Master, H. et al. The All of Us Research Program’s wearables dataset. Nat Med 32, 2302–2310 (2026). [https\://doi.org/10.1038/s41591-026-04352-3](https://doi.org/10.1038/s41591-026-04352-3)  
3. Radin JM, Wineinger NE, Topol EJ, Steinhubl SR. Harnessing wearable device data to improve state-level real-time surveillance of influenza-like illness in the USA: a population-based study. *Lancet Digital Health* 2020;2(2):e85–e93.  
4. Quer G, et al. Wearable sensor data and self-reported symptoms for COVID-19 detection. *Nature Medicine* 2021;27:73–77.  
5. Wang WK, Yang R, Pang C, et al. Beyond the Clinic: A Large-Scale Evaluation of Augmenting EHR with Wearable Data for Diverse Health Prediction. arXiv:2509.22920 (2025).  
6. Saez-Rodriguez J, Costello JC, Friend SH, et al. Crowdsourcing biomedical research: leveraging communities as innovation engines. *Nature Reviews Genetics* 2016;17(8):470–486.  
7. Critical Assessment of Genome Interpretation Consortium. CAGI, the Critical Assessment of Genome Interpretation, establishes progress and prospects for computational genetic variant interpretation methods. *Genome Biology* 2024;25:53.  
8. Verily Workbench. Workflows in Verily Workbench: Cromwell, dsub, and Nextflow. [https\://support.workbench.verily.com/docs/technical\_reference/workflows/](https://support.workbench.verily.com/docs/technical_reference/workflows/)
