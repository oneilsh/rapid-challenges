.PHONY: help setup test wearables-rare

REPO_ROOT     := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
WORKSPACE_ENV := $(REPO_ROOT)/.workspace_env
# Audit outputs go to a workspace run dir, never the repo tree. Same default as
# CHARMPheno's analysis/cloud/Makefile; override with RUNS_DIR=... .
RUNS_DIR      ?= /home/dataproc/workspace/dataproc-staging-getting-started-with-registered-tier-data-copy/runs
MONDO_CACHE   ?= $(REPO_ROOT)/data/mondo
# Optional manual CDR override for setup (an external read-only project that
# `wb resource list` doesn't surface). Persists in .workspace_env afterwards.
CDR           ?=
# Extra --conf key=value pairs for spark-submit.
SPARK_CONF    ?=

# Driver-only Python (pandas + Spark-native ops), so client mode with PYTHONPATH
# is enough; nothing needs shipping to executors via --py-files.
SPARK_SUBMIT = . $(WORKSPACE_ENV) && PYTHONPATH=$(REPO_ROOT):$$PYTHONPATH spark-submit \
	    --master yarn \
	    --deploy-mode client \
	    --driver-memory 8g \
	    --conf spark.executor.cores=2 \
	    --conf spark.executor.memory=4g \
	    --conf spark.executor.memoryOverhead=2g \
	    --conf spark.task.maxFailures=8 \
	    --conf spark.dynamicAllocation.enabled=false \
	    --conf spark.executor.instances=12 \
	    $(foreach kv,$(SPARK_CONF),--conf $(kv))

default: help

help:
	@echo "On the AoU Dataproc master:"
	@echo "  make setup                 - discover project/CDR/buckets via 'wb' -> .workspace_env"
	@echo "                               (pass CDR=<proj>.<ds> if not auto-discovered)"
	@echo "  make wearables-rare        - wearables x rare disease census -> RUNS_DIR/wearables-rare/"
	@echo "      ARGS='--flags gard_rare --min-days 90'"
	@echo "Locally:"
	@echo "  make test                  - unit tests (uv run pytest)"

setup:
	python3 $(REPO_ROOT)/rapidaudit/setup_workspace.py --out $(WORKSPACE_ENV) $(if $(CDR),--cdr=$(CDR))

$(WORKSPACE_ENV):
	$(MAKE) setup

test:
	uv run pytest -q

WEAR_OUT ?= $(RUNS_DIR)/wearables-rare
wearables-rare: $(WORKSPACE_ENV)
	mkdir -p "$(WEAR_OUT)" && $(SPARK_SUBMIT) \
	    $(REPO_ROOT)/audits/wearables_rare.py \
	    --out-dir "$(WEAR_OUT)" --mondo-cache-dir "$(MONDO_CACHE)" \
	    $(ARGS) 2>&1 | tee -a "$(WEAR_OUT)/wearables_rare_log.md"
