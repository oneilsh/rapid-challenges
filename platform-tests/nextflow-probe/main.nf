#!/usr/bin/env nextflow
/*
 * Phase 0 platform test: can a Nextflow job on the Workbench do what a challenge
 * submission needs? Each process answers one question and writes a small text file;
 * `summarize` gathers them into summary.md in the output folder.
 *
 *   whoami    - which service account the Batch worker runs as, which project/region
 *   network   - which outside hosts a worker can reach (PyPI, GitHub, Docker Hub, HF)
 *   cdr       - can the worker query the CDR in BigQuery (dry run + masked counts)
 *   dockerhub - can a task pull an image from Docker Hub (Google images are the default)
 *   gpu       - (--gpu) can a task get a GPU, and does the driver load
 *
 * Counts go through the same rule as the audits: 1-19 -> <20, 0 stays 0.
 * Nothing participant-level is written.
 */

params.cdr     = System.getenv('WORKSPACE_CDR')         // <project>.<dataset>
params.billing = System.getenv('GOOGLE_CLOUD_PROJECT')  // project billed for queries
params.outdir  = 'nextflow-probe-out'
params.gpu     = false

process whoami {
    output: path 'whoami.txt'
    script:
    """
    {
      echo "## whoami"
      echo "host: \$(hostname)"
      md=http://metadata.google.internal/computeMetadata/v1
      for k in instance/service-accounts/default/email project/project-id instance/zone instance/machine-type; do
        echo "\$k: \$(curl -s -m 5 -H 'Metadata-Flavor: Google' \$md/\$k || echo '?')"
      done
      echo "image: \$(. /etc/os-release && echo \$PRETTY_NAME)"
      echo "bq: \$(bq version 2>&1 | tail -1)"
    } > whoami.txt
    """
}

process network {
    output: path 'network.txt'
    script:
    """
    echo "## network (HTTP status, or 'unreachable')" > network.txt
    for u in https://pypi.org/simple/ https://github.com https://registry-1.docker.io/v2/ \\
             https://huggingface.co https://storage.googleapis.com https://bigquery.googleapis.com; do
      code=\$(curl -s -o /dev/null -m 10 -w '%{http_code}' "\$u") || code=unreachable
      echo "\$u: \$code" >> network.txt
    done
    """
}

process cdr {
    input:
    val cdr
    val billing

    output:
    path 'cdr.txt'

    script:
    """
    # numbers 1-19 -> <20; anything else (0, >= 20, an error message) passes through
    mask() { awk '{ print (\$0 ~ /^[0-9]+\$/ && \$1 >= 1 && \$1 <= 19) ? "<20" : \$0 }'; }
    q() { bq --quiet --project_id=${billing} query --use_legacy_sql=false --format=csv "\$@"; }
    {
      echo "## cdr ${cdr} (billed to ${billing})"
      echo "dry run, persons: \$(q --dry_run 'SELECT COUNT(DISTINCT person_id) FROM `${cdr}.person`' 2>&1 | tail -1)"
      echo "persons: \$(q 'SELECT COUNT(DISTINCT person_id) FROM `${cdr}.person`' 2>&1 | tail -1 | mask)"
      echo "persons with Fitbit activity: \$(q 'SELECT COUNT(DISTINCT person_id) FROM `${cdr}.activity_summary`' 2>&1 | tail -1 | mask)"
      echo "write to CDR, dry run (should be denied): \$(q --dry_run 'CREATE TABLE `${cdr}.nf_probe` AS SELECT 1 AS x' 2>&1 | tail -1 | cut -c1-200)"
    } > cdr.txt
    """
}

process dockerhub {
    container 'python:3.12-slim'
    errorStrategy 'ignore'
    output: path 'dockerhub.txt'
    script:
    """
    echo "## dockerhub: pulled python:3.12-slim, \$(python --version)" > dockerhub.txt
    """
}

process gpu {
    container 'nvidia/cuda:12.4.1-base-ubuntu22.04'
    accelerator 1, type: 'nvidia-tesla-t4'
    machineType 'n1-standard-4'
    errorStrategy 'ignore'
    output: path 'gpu.txt'
    script:
    """
    { echo "## gpu"; nvidia-smi -L 2>&1; } > gpu.txt
    """
}

process summarize {
    publishDir params.outdir, mode: 'copy'
    input:
    path parts

    output:
    path 'summary.md'

    script:
    """
    {
      echo "# nextflow-probe ${workflow.runName} (${workflow.start})"
      echo "nextflow ${nextflow.version}, profile ${workflow.profile}, workDir ${workflow.workDir}"
      echo "outdir ${params.outdir}"
      for f in whoami network cdr dockerhub gpu; do
        echo
        if [ -f \$f.txt ]; then cat \$f.txt; else echo "## \$f: no output (failed, skipped or not requested)"; fi
      done
    } > summary.md
    """
}

workflow {
    if (!params.cdr || !params.billing)
        error "Set --cdr <project>.<dataset> and --billing <project> (or WORKSPACE_CDR / GOOGLE_CLOUD_PROJECT)"
    parts = whoami()
        .mix(network(), cdr(params.cdr, params.billing), dockerhub())
    if (params.gpu) parts = parts.mix(gpu())
    summarize(parts.collect())
}
