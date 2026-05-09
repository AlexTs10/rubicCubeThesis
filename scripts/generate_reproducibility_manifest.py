#!/usr/bin/env python3
"""Generate a source-archive manifest that is verifiable without `.git`.

The manifest describes the files intentionally included in the external audit
archive. Heavy generated caches, LaTeX intermediates, local dependency trees,
and locally downloaded paper PDFs are excluded from that archive.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "REPRODUCIBILITY_MANIFEST.json"

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".next",
    "node_modules",
    "__pycache__",
    "audit-results",
}

EXCLUDED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".bcf",
    ".blg",
    ".db",
    ".fdb_latexmk",
    ".fls",
    ".lof",
    ".log",
    ".lot",
    ".out",
    ".pkl",
    ".pickle",
    ".run.xml",
    ".sqlite",
    ".synctex.gz",
    ".toc",
    ".xdv",
}

EXCLUDED_PATH_SUFFIXES = {
    ".DS_Store",
    "conj_twist",
    "thesis/main-blx.bib",
}

EXCLUDED_PATH_PREFIXES = {
    "agent_workflow/generated/",
}


def is_included(path: Path) -> bool:
    relative_parts = path.relative_to(ROOT).parts
    if any(part in EXCLUDED_PARTS for part in relative_parts):
        return False
    if any(part.endswith((".egg-info", ".dist-info")) for part in relative_parts):
        return False
    relative_path = path.relative_to(ROOT).as_posix()
    if any(relative_path.startswith(prefix) for prefix in EXCLUDED_PATH_PREFIXES):
        return False
    if any(relative_path.endswith(suffix) for suffix in EXCLUDED_PATH_SUFFIXES):
        return False
    if path.suffix.lower() == ".pdf" and relative_parts[:1] == ("papers",):
        return False
    if any(relative_path.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return False
    return path.is_file()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> None:
    files = sorted(path for path in ROOT.rglob("*") if is_included(path))
    file_hashes = {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in files
        if path != OUTPUT
    }

    manifest = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": ROOT.name,
        "revision": {
            "git_commit": git_value("rev-parse", "--short=12", "HEAD"),
            "git_branch": git_value("branch", "--show-current"),
            "git_dirty": bool(git_value("status", "--porcelain")),
            "note": "Git fields are informational; file hashes below are the archive-verifiable source of truth.",
        },
        "exclusions": {
            "parts": sorted(EXCLUDED_PARTS),
            "suffixes": sorted(EXCLUDED_SUFFIXES),
            "path_suffixes": sorted(EXCLUDED_PATH_SUFFIXES),
            "path_prefixes": sorted(EXCLUDED_PATH_PREFIXES),
            "notes": [
                "papers/**/*.pdf is excluded from audit archives; papers/ documents remain as bibliography metadata.",
                "data/pattern_databases/*.pkl is generated cache data and is excluded from audit archives.",
                "conj_twist is an ignored generated exact-solver data file and is excluded from audit archives.",
                "agent_workflow/generated/ is local workflow output and is excluded to avoid host-specific validation snapshots.",
            ],
        },
        "file_count": len(file_hashes),
        "file_hashes_sha256": file_hashes,
    }

    OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(file_hashes)} file hashes")


if __name__ == "__main__":
    main()
