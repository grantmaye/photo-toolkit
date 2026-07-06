from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import associated_files, media_files, resolve_destination, retarget_associated_file
from photo.core.metadata import capture_datetime, filename_with_datetime
from photo.core.reports import RunReport
from photo.core.safety import assert_safe_source


def run(
    folder: Path,
    execute: bool,
    allow_root_path: bool = False,
    collision: str = "suffix",
    include_sidecars: bool = True,
    include_live_photos: bool = True,
) -> Path:
    assert_safe_source(folder, allow_root_path)
    report = RunReport("rename-from-exif")
    seen: set[Path] = set()
    for path in media_files(folder):
        if path in seen:
            continue
        captured, source = capture_datetime(path)
        if not captured:
            report.error(path, "No capture date found")
            continue
        primary_target = path.with_name(filename_with_datetime(path, captured))
        for associated in associated_files(path, include_sidecars, include_live_photos):
            seen.add(associated)
            target = retarget_associated_file(path, primary_target, associated)
            resolved = resolve_destination(associated, target, collision)
            action = "rename" if associated == path else "sidecar-rename"
            report.operation(
                action=action,
                source=str(associated),
                destination=str(resolved or target),
                date_source=source,
                collision=collision,
                executed=execute,
                skipped=resolved is None,
            )
            if execute and resolved and resolved != associated:
                associated.rename(resolved)
    report.finish({"execute": execute})
    return report.run_dir
