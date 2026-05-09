#!/usr/bin/env python3
"""Create a deterministic ChatGPT Pro audit ZIP from the manifest include policy."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from generate_reproducibility_manifest import OUTPUT, ROOT, is_included, main as write_manifest


PACKAGE_DIR = ROOT / "audit-results" / "packages"
DOS_EPOCH = 315532800


def archive_paths() -> list[Path]:
    paths = [path for path in ROOT.rglob("*") if is_included(path)]
    if OUTPUT not in paths:
        paths.append(OUTPUT)
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def main() -> None:
    write_manifest()
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = PACKAGE_DIR / f"repo-audit-{datetime.now().strftime('%Y%m%d-%H%M')}.zip"

    source_epoch = int(os.environ.get("SOURCE_DATE_EPOCH", DOS_EPOCH))
    normalized_time = datetime.fromtimestamp(max(source_epoch, DOS_EPOCH), tz=timezone.utc)
    zip_timestamp = (
        normalized_time.year,
        normalized_time.month,
        normalized_time.day,
        normalized_time.hour,
        normalized_time.minute,
        normalized_time.second,
    )

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in archive_paths():
            info = ZipInfo(path.relative_to(ROOT).as_posix(), date_time=zip_timestamp)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())

    print(zip_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
