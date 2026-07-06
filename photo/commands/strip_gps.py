from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import media_files
from photo.core.metadata import strip_gps_metadata
from photo.core.reports import RunReport
from photo.core.safety import assert_safe_source


def run(folder: Path, execute: bool, allow_root_path: bool = False) -> Path:
    assert_safe_source(folder, allow_root_path)
    report = RunReport("strip-gps")
    for path in media_files(folder):
        report.operation(
            action="strip-gps",
            source=str(path),
            warning="Back up photos before removing metadata.",
            executed=execute,
        )
        if execute:
            try:
                strip_gps_metadata(path)
            except Exception as exc:
                report.error(path, str(exc))
    report.finish({"execute": execute, "warning": "Back up photos before removing metadata."})
    return report.run_dir
