# nextflow-probe

Phase 0 platform test for the wearables challenge: can a Nextflow job on the Workbench do
what a submission needs? It runs a handful of tiny tasks on Google Batch and writes one
`summary.md` to the workspace bucket:

| task | question | default image |
|---|---|---|
| `whoami` | which service account, project, zone and machine a Batch worker gets | Google Cloud SDK (`gcr.io`) |
| `network` | which outside hosts a worker can reach: PyPI, GitHub, Docker Hub, Hugging Face, GCS, BigQuery | same |
| `cdr` | can the worker query the CDR: a dry run, two masked counts, and a dry-run write that should be denied | same |
| `dockerhub` | can a task pull from Docker Hub (`python:3.12-slim`) | Docker Hub |
| `gpu` | with `--gpu`: can a task get a T4 and see it with `nvidia-smi` | Docker Hub (`nvidia/cuda`) |

`dockerhub` and `gpu` are allowed to fail; the summary then says "no output". Counts use the
audits' rule (1–19 → `<20`), and nothing is participant-level. The summary does name the
workspace project and service account, so paste it back here rather than filing it in this
public repo.

Verily's docs say Workbench runs Nextflow 25.10 on Google Batch. The `google-batch` profile
follows their CLI guide: private IP only, the workspace `network` and `subnetwork`, and the
workspace service account. A "no internet" result from `network` is therefore a finding, not
a bug.

## Run from a terminal (`wb nextflow`)

On a Workbench VM, in a clone of this repo (`make setup` already done):

```bash
make nextflow-probe          # add GPU=1 to also request a T4
```

This runs from `RUNS_DIR/nextflow-probe`, so `.nextflow/` and the log stay out of the repo.
Batch writes the work files to `$WORKSPACE_BUCKET/rapid/nextflow-probe/work`, and the summary goes to
`$WORKSPACE_BUCKET/rapid/nextflow-probe/<timestamp>/summary.md`. To print the latest:

```bash
make nextflow-probe-summary
```

If a run fails, check `RUNS_DIR/nextflow-probe/.nextflow.log` and `wb gcloud batch jobs list`.
Region mismatches are the usual cause: pass `ARGS='--region <region>'` if the workspace
isn't in `us-central1`.

## Run from the Workflows page

This is the route a scoring workspace would use, so it is worth trying second.

1. Go to Workflows, then Add workflow. Choose Git repository, point it at this repo, and pick
   `platform-tests/nextflow-probe/main.nf` as type Nextflow.
2. Put a params file in a workspace bucket. Since `WORKSPACE_CDR` may not be set there, give
   the values explicitly:
   ```yaml
   cdr: <project>.<dataset>       # from .workspace_env
   billing: <workspace project>
   ```
3. Create a new job with no profile. Workbench supplies the Batch settings. Then choose the
   params file and an output folder.

The summary's `outdir` and `workDir` lines show where Workbench put things. If `outdir`
is still the default `nextflow-probe-out`, Workbench doesn't set `params.outdir` for us.
In that case, add `outdir: gs://...` to the params file.
