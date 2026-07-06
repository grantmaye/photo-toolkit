from __future__ import annotations

import shutil
from pathlib import Path

from photo.core.filesystem import associated_files, resolve_destination, retarget_associated_file, same_path
from photo.core.reports import RunReport
from photo.core.safety import SafetyError, assert_distinct_paths, assert_safe_source


def run(
    source: Path,
    destination: Path,
    prefix: str,
    execute: bool,
    allow_root_path: bool = False,
    collision: str = "suffix",
    include_sidecars: bool = True,
    include_live_photos: bool = True,
) -> Path:
    assert_safe_source(source, allow_root_path)
    assert_distinct_paths(source, destination)
    if same_path(source, destination):
        raise SafetyError("Source and destination must be different paths.")
    report = RunReport("move-prefix")
    destination.mkdir(parents=True, exist_ok=True) if execute else None
    seen: set[Path] = set()
    for path in source.glob(f"{prefix}*"):
        if not path.is_file():
            continue
        for associated in associated_files(path, include_sidecars, include_live_photos):
            if associated in seen:
                continue
            seen.add(associated)
            target = retarget_associated_file(path, destination / path.name, associated)
            resolved = resolve_destination(associated, target, collision)
            action = "move" if associated == path else "sidecar-move"
            report.operation(
                action=action,
                source=str(associated),
                destination=str(resolved or target),
                collision=collision,
                executed=execute,
                skipped=resolved is None,
            )
            if execute and resolved:
                resolved.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(associated), str(resolved))
    report.finish({"execute": execute})
    return report.run_dir
