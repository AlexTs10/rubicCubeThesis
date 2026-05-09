#!/usr/bin/env python3
"""Create a reproducible ChatGPT Pro audit ZIP from the manifest include policy."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from generate_reproducibility_manifest import OUTPUT, ROOT, is_included, main as write_manifest


PACKAGE_DIR = ROOT / "audit-results" / "packages"


def archive_paths() -> list[Path]:
    paths = [path for path in ROOT.rglob("*") if is_included(path)]
    if OUTPUT not in paths:
        paths.append(OUTPUT)
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def main() -> None:
    write_manifest()
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = PACKAGE_DIR / f"repo-audit-{datetime.now().strftime('%Y%m%d-%H%M')}.zip"

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in archive_paths():
            archive.write(path, path.relative_to(ROOT).as_posix())

    print(zip_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
