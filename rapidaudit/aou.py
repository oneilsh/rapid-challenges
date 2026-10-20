"""AoU Workbench I/O: the workspace env, CDR table reads, and the cached Mondo download.

`read_bq` and `download_cached` are copied from CHARMPheno
analysis/cloud/anchor_selection_cloud.py (`_read_bq`, `_download_cached`, commit 220ed138).
"""
from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

_MONDO_RELEASE = (
    "https://github.com/monarch-initiative/mondo/releases/download/v{v}/{f}"
)


def workspace_env() -> tuple[str, str]:
    """(WORKSPACE_CDR, GOOGLE_CLOUD_PROJECT), or exit if `.workspace_env` wasn't sourced."""
    cdr, billing = os.environ.get("WORKSPACE_CDR"), os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not cdr or not billing:
        raise SystemExit("WORKSPACE_CDR and GOOGLE_CLOUD_PROJECT must be set (source "
                         ".workspace_env; the make targets do)")
    return cdr, billing


def download_cached(version: str, filename: str, cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / f"{version}_{filename}"
    if dest.exists() and dest.stat().st_size > 0:
        sys.stderr.write(f"[mondo] cache hit {dest}\n")
        return dest
    url = _MONDO_RELEASE.format(v=version, f=filename)
    sys.stderr.write(f"[mondo] downloading {url}\n")
    urllib.request.urlretrieve(url, dest)  # noqa: S310 (trusted Monarch release URL)
    return dest


def read_bq(spark, cdr_dataset: str, billing_project: str, table: str):
    return (
        spark.read.format("bigquery")
        .option("table", f"{cdr_dataset}.{table}")
        .option("parentProject", billing_project)
        .load()
    )
