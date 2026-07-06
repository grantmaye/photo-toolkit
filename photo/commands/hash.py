from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import media_files
from photo.core.hashing import hash_manifest
from photo.core.reports import RunReport, write_csv
from photo.core.safety import assert_safe_source


def run(folder: Path, output: Path = Path("hashes.csv"), allow_root_path: bool = False) -> Path:
    assert_safe_source(folder, allow_root_path)
    report = RunReport("hash")
    rows = hash_manifest(media_files(folder))
    write_csv(output, rows)
    for row in rows:
        report.operation(action="hash", **row)
    report.finish({"output": str(output)})
    return report.run_dir
