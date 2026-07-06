from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import media_files, unique_destination
from photo.core.metadata import build_fixed_year, filename_with_datetime, update_metadata
from photo.core.reports import RunReport
from photo.core.safety import assert_safe_source


def run(folder: Path, year: int, execute: bool, allow_root_path: bool = False) -> Path:
    assert_safe_source(folder, allow_root_path)
    report = RunReport("fix-year")
    for path in media_files(folder):
        try:
            captured = build_fixed_year(path, year)
            target = unique_destination(path.with_name(filename_with_datetime(path, captured)))
            report.operation(
                action="fix-year",
                source=str(path),
                destination=str(target),
                new_datetime=captured.isoformat(sep=" "),
                executed=execute,
            )
            if execute:
                update_metadata(path, captured)
                if target != path:
                    path.rename(target)
        except Exception as exc:
            report.error(path, str(exc))
    report.finish({"execute": execute})
    return report.run_dir
