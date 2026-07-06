from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import media_files, unique_destination
from photo.core.metadata import capture_datetime, filename_with_datetime
from photo.core.reports import RunReport
from photo.core.safety import assert_safe_source


def run(folder: Path, execute: bool, allow_root_path: bool = False) -> Path:
    assert_safe_source(folder, allow_root_path)
    report = RunReport("rename-from-exif")
    for path in media_files(folder):
        captured, source = capture_datetime(path)
        if not captured:
            report.error(path, "No capture date found")
            continue
        target = unique_destination(path.with_name(filename_with_datetime(path, captured)))
        report.operation(
            action="rename",
            source=str(path),
            destination=str(target),
            date_source=source,
            executed=execute,
        )
        if execute and target != path:
            path.rename(target)
    report.finish({"execute": execute})
    return report.run_dir
