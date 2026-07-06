from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import associated_files, media_files, resolve_destination, retarget_associated_file
from photo.core.metadata import build_fixed_year, filename_with_datetime, update_metadata
from photo.core.reports import RunReport
from photo.core.safety import assert_safe_source


def run(
    folder: Path,
    year: int,
    execute: bool,
    allow_root_path: bool = False,
    collision: str = "suffix",
    include_sidecars: bool = True,
    include_live_photos: bool = True,
) -> Path:
    assert_safe_source(folder, allow_root_path)
    report = RunReport("fix-year")
    seen: set[Path] = set()
    for path in media_files(folder):
        if path in seen:
            continue
        try:
            captured = build_fixed_year(path, year)
            primary_target = path.with_name(filename_with_datetime(path, captured))
            for associated in associated_files(path, include_sidecars, include_live_photos):
                seen.add(associated)
                target = retarget_associated_file(path, primary_target, associated)
                resolved = resolve_destination(associated, target, collision)
                action = "fix-year" if associated == path else "sidecar-rename"
                report.operation(
                    action=action,
                    source=str(associated),
                    destination=str(resolved or target),
                    new_datetime=captured.isoformat(sep=" "),
                    collision=collision,
                    executed=execute,
                    skipped=resolved is None,
                )
                if execute and resolved:
                    if associated == path:
                        update_metadata(path, captured)
                    if resolved != associated:
                        associated.rename(resolved)
        except Exception as exc:
            report.error(path, str(exc))
    report.finish({"execute": execute})
    return report.run_dir
