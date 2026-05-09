#!/usr/bin/env python3
"""Generate the native exact corner pattern database cache."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.korf.corner_database import DEFAULT_CORNER_DB_PATH, create_corner_database


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the full native corner pattern database.")
    parser.add_argument(
        "--output",
        default=DEFAULT_CORNER_DB_PATH,
        help="output cache path",
    )
    parser.add_argument(
        "--move-cache-dir",
        default="data/pattern_databases/native_exact",
        help="directory for auxiliary native move-table caches",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="regenerate even when the output cache already exists",
    )
    args = parser.parse_args()

    create_corner_database(
        load_if_exists=not args.force,
        save_path=args.output,
        generate_if_missing=True,
        require_complete=True,
        verbose=True,
        move_cache_dir=args.move_cache_dir,
    )


if __name__ == "__main__":
    main()
