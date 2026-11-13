.PHONY: help setup deps test wearables-rare wearables-rare-exact wearables-rare-autoimmune wearables-timing wearables-timing-autoimmune wearables-timing-cardio wearables-timing-patients wearables-events wearables-events-split plot-wearables-timing plot-wearables-events mondo-snomed-review

REPO_ROOT     := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
WORKSPACE_ENV := $(REPO_ROOT)/.workspace_env
# Audit outputs go outside the repo tree, to the bucket-backed workspace mount (survives
# VM deletion); override with RUNS_DIR=... .
RUNS_DIR      ?= /home/dataproc/workspace/dataproc-staging-bayesian-phenotyping-for-rare-disease-v9/rapid
# (the earlier V8 workspace used /home/jupyter/workspace/dataproc-staging-getting-started-with-registered-tier-data-copy)
MONDO_CACHE   ?= $(REPO_ROOT)/data/mondo
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

test:
	uv run pytest -q

MONDO_VERSION ?= 2026-06-02
mondo-snomed-review:
	PYTHONPATH=$(REPO_ROOT) uv run python $(REPO_ROOT)/scripts/mondo_snomed_review.py \
	    --mondo-version $(MONDO_VERSION) --cache-dir $(MONDO_CACHE) \
	    --out $(REPO_ROOT)/results/mondo-snomed-review/$(MONDO_VERSION)-rare-snomed-review.tsv

WEAR_OUT ?= $(RUNS_DIR)/wearables-rare
wearables-rare: $(WORKSPACE_ENV)
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
wearables-timing: $(WORKSPACE_ENV)
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
wearables-events: $(WORKSPACE_ENV)
	mkdir -p "$(EVENTS_OUT)" && $(RUN) $(REPO_ROOT)/audits/wearables_events.py \
	    --out-dir "$(EVENTS_OUT)" --mondo-cache-dir "$(MONDO_CACHE)" \
	    $(SCOPE_ARGS) $(ARGS) 2>&1 | tee -a "$(EVENTS_OUT)/wearables_events_log.md"

# Events + a prospective split at AFTER: run on V9 with the V8 cutoff to see what one
# release adds (a stand-in for what V10 would add as a holdout).
AFTER ?= 2023-10-01
wearables-events-split:
	$(MAKE) wearables-events ARGS="--after $(AFTER) $(ARGS)"

# PNGs from a masked wearables-timing report (a filed results/ copy works), next to it.
REPORT ?=
plot-wearables-timing:
	PYTHONPATH=$(REPO_ROOT) uv run python -m audits.wearables_timing_plots $(REPORT)

plot-wearables-events:
	PYTHONPATH=$(REPO_ROOT) uv run python -m audits.wearables_events_plots $(REPORT)
