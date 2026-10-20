.PHONY: help setup deps test wearables-rare wearables-rare-exact wearables-rare-autoimmune

REPO_ROOT     := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
WORKSPACE_ENV := $(REPO_ROOT)/.workspace_env
# Audit outputs go outside the repo tree, to the bucket-backed workspace mount (survives
# VM deletion); override with RUNS_DIR=... .
RUNS_DIR      ?= /home/jupyter/workspace/dataproc-staging-getting-started-with-registered-tier-data-copy
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
	@echo "Locally:"
	@echo "  make test                  - unit tests (uv run pytest)"

setup:
	python3 $(REPO_ROOT)/rapidaudit/setup_workspace.py --out $(WORKSPACE_ENV) $(if $(CDR),--cdr=$(CDR))

# The VM image's google-* packages can be mutually out of date; upgrade them as a set.
deps:
	python3 -m pip install --user --upgrade google-cloud-bigquery google-api-core google-cloud-core

$(WORKSPACE_ENV):
	$(MAKE) setup

test:
	uv run pytest -q

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
