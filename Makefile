.PHONY: help setup deps test runs-dir wearables-rare wearables-rare-exact wearables-rare-autoimmune wearables-timing wearables-timing-autoimmune wearables-timing-cardio wearables-timing-patients wearables-events wearables-events-split wearables-events-sites wearables-healthkit wearables-chel wearables-chel-map nf-bucket nextflow-probe nextflow-probe-summary plot-wearables-timing plot-wearables-events mondo-snomed-review

REPO_ROOT     := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
WORKSPACE_ENV := $(REPO_ROOT)/.workspace_env
# Audit outputs go outside the repo tree, to the bucket-backed workspace mount (survives
# VM deletion); override with RUNS_DIR=... .
RUNS_DIR      ?= $(HOME)/workspace/dataproc-staging-bayesian-phenotyping-for-rare-disease-v9/rapid
# ($(HOME) is /home/jupyter on a plain VM, /home/dataproc on a Dataproc cluster; the bucket
# mounts under ~/workspace either way. The earlier V8 workspace used ~/workspace/dataproc-staging-getting-started-with-registered-tier-data-copy)
MONDO_CACHE   ?= $(REPO_ROOT)/data/mondo
# The folder RUNS_DIR sits in must already exist (the bucket mount): otherwise mkdir -p
# would quietly create a local folder that dies with the VM.
RUNS_PARENT    = $(patsubst %/,%,$(dir $(RUNS_DIR)))
# Optional manual CDR override for setup (an external read-only project that
# `wb resource list` doesn't surface). Persists in .workspace_env afterwards.
CDR           ?=
# Audits run as plain Python on a Workbench VM, querying the CDR in BigQuery
# (google-cloud-bigquery); no Spark or Dataproc cluster needed.
RUN = . $(WORKSPACE_ENV) && PYTHONPATH=$(REPO_ROOT):$$PYTHONPATH python3

default: help

help:
	@echo "On an AoU Workbench VM:"
	@echo "  make setup                 - discover project/CDR/buckets via 'wb' -> .workspace_env"
	@echo "                               (pass CDR=<proj>.<ds> if not auto-discovered)"
	@echo "  make deps                  - upgrade the BigQuery client stack together (fixes"
	@echo "                               mismatched google-api-core errors)"
	@echo "  make wearables-rare        - wearables x rare disease census -> RUNS_DIR/wearables-rare/"
	@echo "      ARGS='--flags gard_rare --min-days 90'"
	@echo "  make wearables-rare-exact  - all Mondo rare diseases, exact SNOMED mapping"
	@echo "  make wearables-rare-autoimmune - same, rare autoimmune diseases only, exact SNOMED"
	@echo "                               mapping (add ARGS=--no-descendants for codes only)"
	@echo "  make wearables-timing-autoimmune - rare autoimmune: Fitbit data by kind, before vs"
	@echo "                               after first dx -> RUNS_DIR/wearables-timing/"
	@echo "      ARGS='--no-intraday --window-days 180'"
	@echo "Locally:"
	@echo "  make test                  - unit tests (uv run pytest)"
	@echo "  make wearables-timing-cardio - same, rare cardiovascular disorders (MONDO:0004995)"
	@echo "  make wearables-timing-patients [SCOPE=cardio] - + participant-level dot plots"
	@echo "                               (Workbench only, *_DO_NOT_EGRESS; PATIENT_FACETS=12)"
	@echo "  make wearables-events [SCOPE=cardio] - ED / inpatient visits vs Fitbit coverage"
	@echo "                               -> RUNS_DIR/wearables-events/ (ARGS='--lookback 30 --min-cov 14')"
	@echo "  make plot-wearables-timing REPORT=results/wearables-timing/<run>.md"
	@echo "  make wearables-events-split [AFTER=2023-10-01] - + prospective split at AFTER (V8"
	@echo "                               cutoff by default; run on V9 to size a V10 holdout)"
	@echo "  make wearables-events-sites [FOCUS='site 6'] - + EHR source diagnostics report"
	@echo "      (any events target: ARGS=--ip-overnight counts inpatient only with a night)"
	@echo "  make wearables-healthkit [HK=<project>.<dataset>] - Apple HealthKit tables, who has"
	@echo "                               them, and the ED / inpatient episodes they cover that"
	@echo "                               Fitbit doesn't -> RUNS_DIR/wearables-healthkit/"
	@echo "  make wearables-chel [CHEL=<project>.<dataset>] - Fitbit + autoimmune persons placed"
	@echo "                               in a CHEL H3 hexagon -> RUNS_DIR/wearables-chel/"
	@echo "  make wearables-chel-map    - persons per CHEL hexagon, mapped (Workbench only:"
	@echo "                               *_DO_NOT_EGRESS_chel-map.png / .tsv)"
	@echo "  make plot-wearables-events REPORT=results/wearables-events/<run>.md"
	@echo "                             - PNGs from a (masked) timing report -> results/.../<run>/"
	@echo "  make mondo-snomed-review   - score Mondo rare-disease SNOMED xrefs against SNOMED"
	@echo "                               names (tx.fhir.org) -> results/mondo-snomed-review/"

setup:
	python3 $(REPO_ROOT)/rapidaudit/setup_workspace.py --out $(WORKSPACE_ENV) $(if $(CDR),--cdr=$(CDR))

# The VM image's google-* packages can be mutually out of date; upgrade them as a set.
deps:
	python3 -m pip install --user --upgrade google-cloud-bigquery google-api-core google-cloud-core

$(WORKSPACE_ENV):
	$(MAKE) setup

runs-dir:
	@test -d "$(RUNS_PARENT)" || { echo "RUNS_DIR's parent $(RUNS_PARENT) does not exist (bucket not mounted here?); ls ~/workspace and pass RUNS_DIR=..." >&2; exit 1; }

test:
	uv run pytest -q

MONDO_VERSION ?= 2026-06-02
mondo-snomed-review:
	PYTHONPATH=$(REPO_ROOT) uv run python $(REPO_ROOT)/scripts/mondo_snomed_review.py \
	    --mondo-version $(MONDO_VERSION) --cache-dir $(MONDO_CACHE) \
	    --out $(REPO_ROOT)/results/mondo-snomed-review/$(MONDO_VERSION)-rare-snomed-review.tsv

WEAR_OUT ?= $(RUNS_DIR)/wearables-rare
wearables-rare: $(WORKSPACE_ENV) | runs-dir
	mkdir -p "$(WEAR_OUT)" && $(RUN) $(REPO_ROOT)/audits/wearables_rare.py \
	    --out-dir "$(WEAR_OUT)" --mondo-cache-dir "$(MONDO_CACHE)" \
	    $(ARGS) 2>&1 | tee -a "$(WEAR_OUT)/wearables_rare_log.md"

# All Mondo rare diseases (the default `rare` union), mapped only via each disease's own
# standard SNOMED concept.
wearables-rare-exact:
	$(MAKE) wearables-rare ARGS="--exact $(ARGS)"

# Rare autoimmune diseases (Mondo subtree MONDO:0007179; Orphanet/GARD/NORD/Mondo rare, not
# inferred), mapped only via each disease's own standard SNOMED concept.
AUTOIMMUNE_ARGS = --under MONDO:0007179 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact
wearables-rare-autoimmune:
	$(MAKE) wearables-rare ARGS="$(AUTOIMMUNE_ARGS) $(ARGS)"

# Fitbit data by kind (daily summaries + intraday), before vs after each person's first
# diagnosis. Same disease selection options as wearables-rare.
TIMING_OUT ?= $(RUNS_DIR)/wearables-timing
wearables-timing: $(WORKSPACE_ENV) | runs-dir
	mkdir -p "$(TIMING_OUT)" && $(RUN) $(REPO_ROOT)/audits/wearables_timing.py \
	    --out-dir "$(TIMING_OUT)" --mondo-cache-dir "$(MONDO_CACHE)" \
	    $(ARGS) 2>&1 | tee -a "$(TIMING_OUT)/wearables_timing_log.md"

wearables-timing-autoimmune:
	$(MAKE) wearables-timing ARGS="$(AUTOIMMUNE_ARGS) $(ARGS)"

# Rare cardiovascular disorders (Mondo subtree MONDO:0004995), same rules as autoimmune.
CARDIO_ARGS = --under MONDO:0004995 --flags orphanet_rare,gard_rare,nord_rare,mondo_rare --exact
wearables-timing-cardio:
	$(MAKE) wearables-timing ARGS="$(CARDIO_ARGS) $(ARGS)"

# PARTICIPANT-LEVEL faceted dot plots (one point per person; plain and with marginal
# histograms) in a *_DO_NOT_EGRESS folder under TIMING_OUT. View on the Workbench only.
# SCOPE=autoimmune|cardio; intraday tables skipped (they track the daily summaries).
SCOPE          ?= autoimmune
SCOPE_ARGS      = $(if $(filter cardio,$(SCOPE)),$(CARDIO_ARGS),$(AUTOIMMUNE_ARGS))
PATIENT_KINDS  ?= any
PATIENT_FACETS ?= 12
wearables-timing-patients:
	$(MAKE) wearables-timing ARGS="$(SCOPE_ARGS) --no-intraday --patient-plots $(PATIENT_KINDS) --patient-facets $(PATIENT_FACETS) $(ARGS)"

# ED / inpatient visits after (and before) the first dx, and how many have Fitbit data in
# the lookback window before them. SCOPE=autoimmune|cardio, as for the patient plots.
EVENTS_OUT ?= $(RUNS_DIR)/wearables-events
wearables-events: $(WORKSPACE_ENV) | runs-dir
	mkdir -p "$(EVENTS_OUT)" && $(RUN) $(REPO_ROOT)/audits/wearables_events.py \
	    --out-dir "$(EVENTS_OUT)" --mondo-cache-dir "$(MONDO_CACHE)" \
	    $(SCOPE_ARGS) $(ARGS) 2>&1 | tee -a "$(EVENTS_OUT)/wearables_events_log.md"

# Events + a prospective split at AFTER: run on V9 with the V8 cutoff to see what one
# release adds (a stand-in for what V10 would add as a holdout).
AFTER ?= 2023-10-01
wearables-events-split:
	$(MAKE) wearables-events ARGS="--after $(AFTER) $(ARGS)"

# Events + EHR-source diagnostics (<run>_site-diag-report.md). FOCUS='site N' picks the
# source to compare against the rest (default: most episodes per person).
FOCUS ?=
wearables-events-sites:
	$(MAKE) wearables-events ARGS="--site-diagnostics $(if $(FOCUS),--focus-site '$(FOCUS)') $(ARGS)"

# Apple HealthKit (stand-alone dataset next to the V9 CDR): finds the dataset (or HK=...),
# reports its tables, and counts HealthKit vs Fitbit coverage in the cohort and of covered
# ED / inpatient episodes (inpatient-stay rule, as in the challenge draft).
HK_OUT ?= $(RUNS_DIR)/wearables-healthkit
HK ?=
wearables-healthkit: $(WORKSPACE_ENV) | runs-dir
	mkdir -p "$(HK_OUT)" && $(RUN) $(REPO_ROOT)/audits/wearables_healthkit.py \
	    --out-dir "$(HK_OUT)" --mondo-cache-dir "$(MONDO_CACHE)" $(if $(HK),--hk-dataset '$(HK)') \
	    --ip-overnight $(SCOPE_ARGS) $(ARGS) 2>&1 | tee -a "$(HK_OUT)/wearables_healthkit_log.md"

# CHEL (V9 CT off-cycle `C_v9_R2_clad_chel_hex_offcycle`, "CLAD CHEL & Location Data"):
# finds how persons link to an H3 hexagon and counts the Fitbit + autoimmune cohort
# that can be placed (no hexagon ids printed).
CHEL_OUT ?= $(RUNS_DIR)/wearables-chel
CHEL ?=
wearables-chel: $(WORKSPACE_ENV) | runs-dir
	mkdir -p "$(CHEL_OUT)" && $(RUN) $(REPO_ROOT)/audits/wearables_chel.py \
	    --out-dir "$(CHEL_OUT)" --mondo-cache-dir "$(MONDO_CACHE)" $(if $(CHEL),--chel-dataset '$(CHEL)') \
	    --ip-overnight $(SCOPE_ARGS) $(ARGS) 2>&1 | tee -a "$(CHEL_OUT)/wearables_chel_log.md"

# Map of the cohort per CHEL hexagon (latest residence). Small cells: DO_NOT_EGRESS.
wearables-chel-map: $(WORKSPACE_ENV) | runs-dir
	mkdir -p "$(CHEL_OUT)" && $(RUN) $(REPO_ROOT)/audits/wearables_chel_map.py \
	    --out-dir "$(CHEL_OUT)" --mondo-cache-dir "$(MONDO_CACHE)" \
	    --geo-cache-dir "$(REPO_ROOT)/data/geo" $(if $(CHEL),--chel-dataset '$(CHEL)') \
	    $(SCOPE_ARGS) $(ARGS) 2>&1 | tee -a "$(CHEL_OUT)/wearables_chel_log.md"

# Phase 0 platform test: a small Nextflow job on Google Batch (platform-tests/nextflow-probe/).
# Runs from RUNS_DIR so .nextflow/ and logs stay out of the repo; summary.md lands in the
# bucket that RUNS_DIR is mounted from (its folder under ~/workspace is the Workbench
# resource id; override with NF_BUCKET=gs://...). GPU=1 also asks for a T4.
NF_OUT = $(RUNS_DIR)/nextflow-probe
NF_BUCKET ?= $(shell wb resolve --id $(notdir $(RUNS_PARENT)) 2>/dev/null)
NF_GS = $(patsubst %/,%,$(NF_BUCKET))/rapid/nextflow-probe
nf-bucket:
	@case "$(NF_BUCKET)" in gs://*) ;; *) echo "Could not resolve the bucket for $(RUNS_PARENT) (got '$(NF_BUCKET)'); pass NF_BUCKET=gs://..." >&2; exit 1;; esac

nextflow-probe: $(WORKSPACE_ENV) nf-bucket | runs-dir
	mkdir -p "$(NF_OUT)" && . $(WORKSPACE_ENV) && cd "$(NF_OUT)" && \
	wb nextflow run $(REPO_ROOT)/platform-tests/nextflow-probe/main.nf -profile google-batch \
	    -w "$(NF_GS)/work" --outdir "$(NF_GS)/$$(date +%Y%m%d-%H%M%S)" \
	    $(if $(GPU),--gpu) $(ARGS) 2>&1 | tee -a "$(NF_OUT)/nextflow_probe_log.md"

# Print the newest summary.md.
nextflow-probe-summary: nf-bucket
	@gcloud storage cat "$$(gcloud storage ls '$(NF_GS)/*/summary.md' | sort | tail -1)"

# PNGs from a masked wearables-timing report (a filed results/ copy works), next to it.
REPORT ?=
plot-wearables-timing:
	PYTHONPATH=$(REPO_ROOT) uv run python -m audits.wearables_timing_plots $(REPORT)

plot-wearables-events:
	PYTHONPATH=$(REPO_ROOT) uv run python -m audits.wearables_events_plots $(REPORT)
