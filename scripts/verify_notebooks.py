#!/usr/bin/env python3
"""Lightweight source-ZIP notebook smoke check.

The thesis notebooks are educational artifacts. This script validates that each
notebook is parseable JSON, has a kernelspec/language declaration when present,
and contains at least one cell. It intentionally does not execute notebooks,
because the heavier execution path depends on interactive widgets and optional
long-running solver cells.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_DIR = ROOT / "notebooks"


def check_notebook(path: Path) -> tuple[bool, str]:
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"

    cells = notebook.get("cells")
    if not isinstance(cells, list) or not cells:
        return False, "missing non-empty cells list"

    metadata = notebook.get("metadata", {})
    kernelspec = metadata.get("kernelspec")
    language_info = metadata.get("language_info")
    if kernelspec is None and language_info is None:
        return False, "missing kernelspec/language metadata"

    return True, f"{len(cells)} cells"


def main() -> int:
    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    if not notebooks:
        print("No notebooks found under notebooks/")
        return 1

    failed = False
    for notebook in notebooks:
        ok, message = check_notebook(notebook)
        status = "PASS" if ok else "FAIL"
        print(f"{status} {notebook.relative_to(ROOT)} - {message}")
        failed = failed or not ok

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
