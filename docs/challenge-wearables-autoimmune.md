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
* **Baselines:** Minimal baseline models will provide a lower performance floor, as well as demonstrations of the submission format and scoring pipeline.  
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
  * **Enforcing declarations:** The rules require each entry to use only its declared data types, and entries in line for a prize are verified before awards (see Technical Implementation).  
  * **Organizer-prepared data:** To avoid misunderstandings about the outcome and leakage of future information, challenge organizers will prepare the cohorts, the prediction dates, and the outcome labels for training data.  
* **Participant task:** For each prediction date, defined as a day with at least 14 days of wearables data in the prior 30, teams output the probability that an ED or inpatient episode starts within the next 30 days, using only data dated before the prediction date. An episode is a run of ED or inpatient visit starts no more than 7 days apart. An inpatient visit counts only as part of a stay: a visit that ends after the day it starts, or inpatient visits on consecutive days. Some sites code recurring same-day encounters as inpatient visits, and without this rule one site supplies nearly half of all episodes.  
* **Expected submissions:** Teams may submit one model per data combination (wearables, EHR and survey, and CHEL data), up to four in total. For each submission:  
  * **Code and model:** the team's code in a GitHub repository at a tagged commit, with one entry point that prepares features from the declared data types in the All of Us CDR and writes predictions, plus the trained model files. The organizers run these in a scoring workspace (see Technical Implementation). Phase 0 settles whether runs use plain Workbench VMs or workflow tools; dsub and Nextflow are supported, each running steps in container images \[8\].  
  * **Declaration** of the data types used.  
  * **Report:** a short methods report (no more than 4 pages) describing the approach, the data types used and why, and an analysis of failure cases. The required contents are to be finalized in Phase 0.  
* **Eligibility:** Researchers with All of Us Controlled Tier access, which requires an institutional data use agreement and completed training and covers the wearables, EHR, survey, and CHEL data. Teams from ineligible institutions may participate through an eligible member, provided they follow all All of Us data use and results export policies. While some data combinations are available in the Registered Tier with fewer access requirements, these data are date shifted, preventing using dates to identify new episodes in V10 vs V9 data.  
* **Team rules:** Teams of up to 5, with one team per person.  
* **Judging and prizes:** Prizes go to the best absolute scores within each declared combination:  
  * **Best wearables-only**, **best wearables \+ EHR and survey**, **best wearables \+ CHEL** and **best wearables \+ EHR and survey \+ CHEL:** the highest primary score among entries declaring that combination.  
  * A combination requires at least 3 eligible entries to be awarded. We announce this at launch, so an unpopular combination goes unawarded.  
  * A panel of clinicians (rheumatology, neurology) and data scientists reviews the top submissions' reports. The panel can disqualify a submission but does not reorder rankings.

## Evaluation Framework

*Define primary and secondary metrics, evaluation datasets, statistical methods, qualitative review where needed, success thresholds, tie-breaking, and requirements for robustness, calibration, generalizability, reproducibility, interpretability, fairness, and failure analysis.*

Only the primary metric, AUPRC as described below, will decide rankings and prizes. Everything else is computed by the organizers from the submitted predictions and reported alongside the rankings, so it adds no work for teams but provides additional valuable information on challenge results.

* **Evaluation datasets:**  
  * **Primary:** the V10 prospective holdout (prediction dates after the V9 data cutoff).  
  * **Evaluation unit:** person-days, with every eligible prediction date scored.  
* **Primary metric:** Area under the precision-recall curve (AUPRC) for the pooled rare autoimmune cohort, which suits a positive rate of roughly 3% per 30-day window.  
* **Value of each data type:** The allowed combinations of data modalities provide a unique opportunity to assess the relative value of additional data modalities beyond wearables:  
  * **Across the field:** To assess the potential impact of additional data modalities beyond wearables, we will compare the best score among entries using a data type against the best score among entries without it (e.g., the best wearables \+ EHR entry against the best wearables-only entry), compared by paired bootstrap. Because these are each group's best entries, no team can inflate the difference artificially, and it answers the question at the level of current methods.  
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

* **Platform configuration:** All work happens in Controlled Tier workspaces on the Researcher Workbench:
  * **Challenge workspace (organizers; shared read-only with registered teams):** the derived V9 tables (cohort, prediction dates, outcome labels, disease assignments), documentation, starter notebooks and baselines. Controlled Tier workspaces can be shared with any researcher who has Controlled Tier access \[9\].
  * **Team workspaces:** each team's own workspaces, for development on V9.
  * **Scoring workspace (organizers only):** where frozen submissions are run on V10.
* **V10 as evaluation holdout:** Once V10 is released, Controlled Tier researchers can open it in their own workspaces, team members included. The holdout stays blind because submissions are frozen before V10 is released:
  * Code is fixed at a tagged commit, and model files are recorded by checksum.
  * A model that changes after the freeze is disqualified.
  * The freeze date is set before the earliest plausible V10 release, not the expected one.
* **Submission format:** each submission has:
  * **Code:** a GitHub repository at a tagged commit, leveraging the workbench's GitHub integration. It needs one entry point, which processes All of Us and writes the predictions table, and an environment file (pip or conda requirements, or a container image for nextflow or dsub submission, depending on feasibility).
    * The Workbench clones Git repositories into new environments automatically, so this adds little work for teams already using Git, and it gives reviewers a fixed record.
  * **Model files:** kept in the team's workspace bucket and listed with checksums in the repository. At the freeze, the team shares its submission workspace with the organizers, who copy the files into the scoring workspace and verify the checksums. Copies between Controlled Tier workspaces are supported \[9\].
  * **Declaration:** the data combination, and the resources requested (CPU or GPU type, memory, expected runtime) within the published limits.
  * **Output:** one table with person ID, prediction date and predicted probability. A submission is rejected if any row is missing, any probability is outside [0, 1], or there are extra columns.
* **Compute environment:**
  * **Scoring runs:** organizers run each submission on a Workbench VM in the scoring workspace, with a GPU where requested, built from the team's environment file.
  * **Workflow tools:** dsub or Nextflow will be evaluated as submission possibilities in Phase 0.
  * **Published limits:** published limits on scoring compute (for example, GPU type and hours per submission) keep inference costs bounded and the same for every team.
  * **Development costs:** teams pay for their own development compute; Workbench accounts start with $300 of credits. There is no practical way to cap what a well-funded team spends on training, and the rules say so openly.
* **Evaluation pipeline:**
  1. Freeze submissions: tagged commits, model checksums, declarations.
  2. After V10 is released, build the holdout labels using the same cohort, prediction date and outcome code as for V9, applied to dates after the V9 cutoff, for existing participants and for participants new to V10.
  3. Run each submission once against the V10 CDR.
  4. Validate the output tables.
  5. Compute the primary and secondary metrics, bootstrap intervals and stratified results.
  6. Verify the submissions in line for a prize (see Anti-gaming controls).
  7. Export the aggregate results (see Data protection).
* **Anti-gaming controls:** Teams' code queries the CDR directly, and V10 contains every outcome, so nothing on the platform can stop a model from looking ahead or reading undeclared data. We therefore trust by default and verify the winners, as many academic challenges do:
  * **Rules:** predictions may use only data dated before the prediction date, and only the declared data types.
  * **As-of helper:** the starter code includes a small helper that applies the prediction-date cutoff to every CDR query. It makes compliance easy and accidental leakage unlikely, at no extra running cost.
  * **One submission per team per combination:** so a team cannot spread entries across many variants.
  * **Verify the winners:** every submission is run once and scored. Before prizes are announced, an organizer carefully reviews the code of each submission in line for a prize: the top entry in each combination and any entries sharing first place, about 4–8 in all. The reviewer checks for data dated on or after the prediction date, undeclared data types and hard-coded data, assisted by LLM screening and, if the pilot shows it is easy, the BigQuery history of the queries the submission ran. A violation means disqualification, and the next entry is verified in turn.
  * **Built-in deterrents:** winners' code and reports are reviewed by the panel and published, and a model that sees its outcome would score suspiciously well.
  * **Limits:** entries below the prize line are not audited. Their scores are reported, and feed the comparison of data types, on trust, and the results say so.
  * **No leaderboard:** a leaderboard would need repeated organizer-run scoring during Phase 1. Teams validate on their own V9 splits instead, with a self-check script and one dry run (see Participant Experience and Support).
* **Security model:** All participant-level work stays inside the All of Us perimeter, in Controlled Tier workspaces. Repositories hold code only. Export of results and models follows the Data protection rules under Evaluation Framework.
* **Auditability:** For every scored submission, the scoring workspace keeps everything needed to rerun the score:
  * the tagged commit and model checksums;
  * the input versions (CDR release and derived-table version);
  * run logs and random seeds;
  * verification notes for prize contenders.

  The scoring code itself lives in a public repository with no data.
* **Baseline implementation:** The organizer baselines described above are packaged in the submission format: a repository, entry point, environment file and model files. They set the score floor, serve as a template for teams, and are the first submissions run through the pipeline.
* **Infrastructure constraints:**
  * BigQuery is billed by data scanned, which makes the minute-level Fitbit tables expensive to query carelessly.
  * GPUs are available, at the scoring team's cost.
* **Workbench pilot (to start now, before Phase 0):** Exercise the parts of this design most likely to fail:
  * a dsub or Nextflow job running a container on Workbench data, with and without a GPU;
  * copying a large model file between Controlled Tier workspaces owned by different users;
  * running a team-style repository and environment file on a fresh VM;
  * whether the BigQuery history of a scoring run (tables read, query text) is easy to pull, to help verify winners;
  * whether a training slice of the data can be published as its own data collection under the All of Us perimeter policy \[10\].

  Workbench documentation suggests individual researchers cannot create data collections, so the last item likely needs help from the program. If it is possible, a held-back V9 slice could support a leaderboard.

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
  * **Tutorials and starter code:** notebooks in the challenge data workspace showing how to load the derived tables and query wearables data cheaply, a worked example from features to a prediction table, the as-of helper, and a template repository showing the entry point, environment file and how to submit.
  * **Baseline models:** the organizer baselines, with code and V9 validation scores.
  * **Self-check script and dry run:** a script that runs a submission's entry point on a small V9 sample the way the scorer will and checks the output format, plus one organizer dry run about four weeks before the freeze, reported as pass or fail with no score.
  * **Challenge office hours:** every two weeks during Phase 1, at alternating times for different time zones, plus a launch webinar and one session before the submission deadline. Sessions are recorded and captioned.
  * **Help desk:** Workbench access and billing questions go to the All of Us support desk. Challenge questions go to a challenge forum or mailbox, answered within two business days, with answers that apply to everyone added to a public FAQ.
* **Accessibility:** Documentation in accessible HTML, as well as PDF. Recorded, captioned sessions. Office hours at more than one time of day. Advance notice of the Controlled Tier access steps, which can take weeks at some institutions.

## Incentives, Outreach, and Partnerships

*Recommend monetary and/or non-monetary incentives, communications and recruitment channels, patient and provider engagement, and partnerships that would strengthen participation, credibility, or downstream adoption.*

* **Monetary incentives:**
  * **Prizes:** a prize for the winner of each awarded data combination (amounts to be set to the budget; for example, an equal amount per combination), with an optional smaller runner-up prize. Combinations with fewer than 3 eligible entries are not awarded, so the prize budget should assume some go unawarded.
  * **Compute credits (optional):** a modest pool, beyond the $300 All of Us starting credits, for student-led or under-resourced teams. This improves access but cannot level spending (see Compute environment).
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
  * **Verily Workbench:** scoring runs, copying files between workspaces, workflow tools, and whether data collections can be published under the All of Us perimeter.
  * **CHEL data team:** documentation of the area-level variables, and their own interest in seeing the data used.
  * **Academic rheumatology and neurology groups:** the clinical panel and later translational work.

## Execution Plan and Resources

*Provide a launch schedule, critical path, responsible parties, staffing, budget assumptions, approvals, dependencies, procurement needs, and operational plan through closeout and results dissemination.*

* **Launch schedule (tentative, set by the V10 release, expected mid-2027):**

| Period | Phase | Main work |
| :---- | :---- | :---- |
| Dec 2026 – Jan 2027 | Pilot, approvals and announcement | Workbench pilot (workflows, cross-workspace copies, data collections), program approvals, rules and prize terms, announcement and pre-registration open |
| Feb – Mar 2027 | Phase 0, preparation | Final cohort and outcome definitions, derived tables, baselines, scoring pipeline, self-check script and as-of helper, end-to-end test on a V9 split |
| Apr – Jun 2027 | Phase 1, open development | Teams develop; office hours; one dry run about four weeks before the freeze; submissions freeze at the end, before V10 is released |
| V10 release + ~6 weeks | Phase 2, blinded evaluation | Build the V10 holdout labels, run submissions, compute scores, verify prize contenders |
| Following 2 months | Phase 3, analysis and reporting | Stratified results, panel review of reports, winners announced, results exported after masking |
| Following ~4 months | Dissemination and closeout | Results session, overview paper with the top teams, featured workspaces, archive of the scoring code and baselines |

* **Critical path:** The steps run in order:
  1. the Workbench pilot shows the submission and scoring design works;
  2. teams obtain Controlled Tier access;
  3. the scoring pipeline works end to end on V9;
  4. submissions freeze;
  5. V10 is released;
  6. the holdout is built;
  7. submissions are scored and prize contenders verified.

  The V10 date is the one fixed external dependency, and the freeze must come before it. If V10 slips, submissions simply stay frozen longer. If V10 might arrive early, the freeze moves earlier, so the schedule never depends on V10 being late.
* **Responsible parties:**
  * **Challenge leads (S. O'Neil, E. Hurwitz):** scientific design, rules, panel, communications, final decisions.
  * **Data scientist:** cohort and labels, baselines, verification of prize contenders, metrics and statistics, office hours on the task and modeling, analysis and the overview paper.
  * **Data engineer:** Workbench pilot, derived tables, scoring workspace and pipeline, model file transfers, cost monitoring.
  * **Clinical panel (rheumatology, neurology) and patient organization advisors:** outcome review and report review.
  * **All of Us program:** V10, workspace provisioning, policy review.
* **Staffing (effort per phase):**

| Phase (months) | Data scientist | Data engineer |
| :---- | :---- | :---- |
| Pilot, approvals and announcement (2) | 25% | 50% |
| Phase 0, preparation (2) | 75% | 100% |
| Phase 1, open development (3) | 40% | 40% |
| Phase 2, blinded evaluation (~1.5) | 75% | 100% |
| Phase 3, analysis and reporting (2) | 75% | 25% |
| Dissemination and closeout (4) | 50% | 15% |
| **Total (~14.5 months)** | **≈ 7.8 person-months** | **≈ 6.8 person-months** |

  That is about 55% of a full-time data scientist and about 45–50% of a full-time data engineer over the life of the challenge.
  * **Phase 1** covers office hours, the FAQ, team questions and the dry run.
  * **Phase 2** assumes up to about 20 scored submissions (four combinations, about five teams each). Each needs one to two days to run and troubleshoot, and verifying the 4–8 prize contenders adds about a day each. More submissions mean more time.
  * **Closeout** covers the overview paper, a results session, featured workspaces and archiving.
  * **Challenge leads** need about 10–15% each throughout, more around launch and writing.
  * **Clinical panel members** need a few days each in Phase 3.
* **Budget assumptions:**
  * **Personnel:** the effort above, at institutional rates.
  * **Organizer cloud costs:** about $5,000 for the pilot, derived-table builds, scoring runs (including GPU time) and bootstrap analysis. Teams' own development compute is not included.
  * **Team compute credits (optional):** a fixed pool for student-led or under-resourced teams, on top of the $300 All of Us starting credits.
  * **Prizes and panel:** prizes per awarded combination, honoraria for the clinical panel and patient advisors.
  * **Dissemination:** results session and travel for presenting teams, open-access publication fees.
* **Approvals:**
  * All of Us program agreement to host a challenge on the Workbench, including organizer-run scoring of team code on V10.
  * Program review of exported results and of any model export.
  * An institutional determination for the organizers' own role (expected to fall under All of Us data use rather than new human subjects research; to be confirmed).
  * Prize terms and eligibility rules approved under the funder's prize authority.
* **Dependencies:** V10 release date and content (Fitbit continuing, EHR refresh). Workbench support for copying model files between Controlled Tier workspaces, and for GPU VMs or batch jobs in the scoring workspace. Continued availability of CHEL and HealthKit in V10.
* **Procurement:** Billing account and funds for organizer workspaces. A method for distributing any team compute credits. A prize disbursement mechanism. Honorarium agreements for the panel and advisors.
* **Operations through closeout:**
  * During Phase 1: regular office hours and an updated FAQ; a written log of rule clarifications sent to all teams; weekly cost monitoring.
  * In Phases 2 and 3: scores checked by a second organizer before release; winners notified before the public announcement.
  * At closeout: the derived-table definitions are published along with the scoring code, so that the benchmark can be rerun on later releases.

## Risks, Assumptions, and Open Decisions

*Identify scientific, data, legal, privacy/security, platform, participation, evaluation, and adoption risks; document key assumptions; and specify decisions or evidence needed before launch.*

**Risks**

* **Scientific:** Wearables may carry little signal ahead of acute episodes in these diseases, or the signal may be swamped by prior utilization in the EHR. This is still a useful result, and the data-type comparison is designed to report it clearly.
* **Data:** Fitbit wear is uneven and mostly absent before episodes (72% of episodes have no covered month). The cohort is skewed toward people who own and wear devices. Diagnosis codes may be loose (see Label quality below). CHEL variables are static snapshots at about 62-mile resolution.
* **Legal and policy:** Prize terms, or the All of Us program's agreement to organizer-run scoring, could be refused or delayed (see Approvals).
* **Privacy and security:** Model exports could memorize participant data. Small subgroups invite derived small counts. Team repositories could carry participant data if notebook outputs are pushed. Mitigations: aggregate-only export with masking, no model export without review, rules on what repositories may hold, and a check for data in prize contenders' repositories.
* **Platform:** Workflow tools may not run as hoped. Copying large model files between workspaces may be slow or blocked. Workbench changes during the challenge could break the scoring pipeline. The V10 release date may move, in either direction. The Workbench pilot is meant to surface the first two before launch.
* **Participation:** Controlled Tier access takes time and is out of reach for some researchers. Compute costs fall on teams, and well-funded teams can spend more. Requiring a GitHub repository is a small extra hurdle. The outcome is rare and noisy, which may discourage people. Some combinations may draw fewer than 3 entries.
* **Evaluation:** The holdout is small (about 500 episodes in about 300 participants), so confidence intervals will be wide and many teams may tie for first. Repeat episodes concentrated in a few participants or sites can dominate the score. Only prize contenders are verified, so lookahead or undeclared data in other entries could go undetected and bias the comparison of data types.
* **Adoption:** Results come from one research cohort with Fitbit devices and may not transfer to clinical populations or other devices. A positive result is a reason for prospective validation, not deployment.

**Assumptions**

* V10 is released on the Workbench around mid-2027, with Fitbit, EHR and CHEL data continuing past the V9 cutoff.
* Organizers can copy frozen model files into their own scoring workspace, run team code there on V10, and export aggregate scores under the dissemination policy.
* Teams can obtain Controlled Tier access within the announcement-to-launch window.
* The V9 split at the V8 cutoff is a reasonable stand-in for the size and makeup of the V10 holdout.
* Staffing and organizer compute estimates hold within about 25%. Phase 0 measurements will confirm this.

**Open items and decisions needed before launch**

* **Label quality:** Diagnosis counts look high relative to known prevalence (e.g., Sjögren syndrome in 5,474 v8 participants). This may reflect enrollment that over-represents people with chronic disease, loose coding, or both. Requiring codes on at least 2 dates, or a specialist visit or disease-specific medication, would tighten labels at the cost of cohort size.  
* **Localized scleroderma:** The disease is largely skin-limited, and in v8 its diagnosis dates looked unreliable (more covered episodes before diagnosis than after; this no longer holds in V9). We propose keeping it in the pooled cohort only, not as a named sub-cohort.  
* **Outcome coding across sites:** Visit types are coded differently across EHR sites. The inpatient-stay rule removes the worst case, but one site still records stays as runs of same-day inpatient visits, and another has many repeat ED visits in a few participants (254 episodes in 26). We need to decide whether to keep ED and inpatient together or use ED visits alone (1,615 covered episodes; a holdout of roughly 400), and whether to limit how much any one participant can weigh in scoring.  
* **V10 and HealthKit:** The counts above are from the V9 Controlled Tier CDR and Fitbit only. V9 adds Apple HealthKit data as a separate dataset (about 19,900 participants, 4,067 of them also with Fitbit). In our cohort, HealthKit covers 774 more ED or inpatient episodes (261 persons) beyond Fitbit's 2,244 (789 persons). Most of that coverage comes from phone or other-app data such as step counts rather than an Apple Watch: watch data alone covers 199 episodes and starts only in 2020\. HealthKit also differs from Fitbit in data types and sources (more than 100 device and app makers), and some rows carry placeholder 1969/1970 timestamps. We plan to keep Fitbit as the basis for the cohort and coverage rule, and are considering offering HealthKit as an optional extra input.  
* **Scoring pipeline:** Choose between plain VMs and workflow tools, how model files move from team workspaces, and the compute limits for scoring. The Workbench pilot informs all three.  
* **Verifying winners:** Decide what the review of prize contenders covers (code, and the BigQuery history of their runs if available), whether LLM-assisted screening is acceptable to the program, and whether a clear accidental violation gets one chance to fix.  
* **Report contents:** Settle the required sections of the team report.  
* **Visit types:** Decide whether observation stays (visit concept 581385\) count as acute episodes.
* **Incentives:** Set prize amounts, whether there is a runner-up prize, and whether to fund team compute credits.
* **Approvals:** Get All of Us program agreement on organizer-run scoring and on results export, plus prize terms from the funder, before the announcement.
* **Freeze date:** Fix it against the earliest plausible V10 release, confirmed with the program.

## References

1. All of Us Research Program. Our Largest Genomic Dataset: Curated Data Repository version 9 (support article, including the Apple HealthKit release). [https\://support.researchallofus.org/hc/en-us/articles/50653909888788](https://support.researchallofus.org/hc/en-us/articles/50653909888788)  
2. Patten, T., Preble, E.A., Master, H. et al. The All of Us Research Program’s wearables dataset. Nat Med 32, 2302–2310 (2026). [https\://doi.org/10.1038/s41591-026-04352-3](https://doi.org/10.1038/s41591-026-04352-3)  
3. Radin JM, Wineinger NE, Topol EJ, Steinhubl SR. Harnessing wearable device data to improve state-level real-time surveillance of influenza-like illness in the USA: a population-based study. *Lancet Digital Health* 2020;2(2):e85–e93.  
4. Quer G, et al. Wearable sensor data and self-reported symptoms for COVID-19 detection. *Nature Medicine* 2021;27:73–77.  
5. Wang WK, Yang R, Pang C, et al. Beyond the Clinic: A Large-Scale Evaluation of Augmenting EHR with Wearable Data for Diverse Health Prediction. arXiv:2509.22920 (2025).  
6. Saez-Rodriguez J, Costello JC, Friend SH, et al. Crowdsourcing biomedical research: leveraging communities as innovation engines. *Nature Reviews Genetics* 2016;17(8):470–486.  
7. Critical Assessment of Genome Interpretation Consortium. CAGI, the Critical Assessment of Genome Interpretation, establishes progress and prospects for computational genetic variant interpretation methods. *Genome Biology* 2024;25:53.  
8. Verily Workbench. Workflows in Verily Workbench: Cromwell, dsub, and Nextflow. [https\://support.workbench.verily.com/docs/technical\_reference/workflows/](https://support.workbench.verily.com/docs/technical_reference/workflows/)
9. All of Us Research Program. Workspace Questions (User Support Hub). [https://support.researchallofus.org/hc/en-us/articles/35016255209876](https://support.researchallofus.org/hc/en-us/articles/35016255209876)
10. Verily Workbench. Perimeter policy. [https://support.workbench.verily.com/docs/guides/governance/perimeter_policy/](https://support.workbench.verily.com/docs/guides/governance/perimeter_policy/)
