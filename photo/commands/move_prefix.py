from __future__ import annotations

import shutil
from pathlib import Path

from photo.core.filesystem import same_path, unique_destination
from photo.core.reports import RunReport
from photo.core.safety import SafetyError, assert_distinct_paths, assert_safe_source


def run(source: Path, destination: Path, prefix: str, execute: bool, allow_root_path: bool = False) -> Path:
    assert_safe_source(source, allow_root_path)
    assert_distinct_paths(source, destination)
    if same_path(source, destination):
        raise SafetyError("Source and destination must be different paths.")
    report = RunReport("move-prefix")
    destination.mkdir(parents=True, exist_ok=True) if execute else None
    for path in source.glob(f"{prefix}*"):
        if not path.is_file():
            continue
        target = unique_destination(destination / path.name)
        report.operation(action="move", source=str(path), destination=str(target), executed=execute)
        if execute:
            shutil.move(str(path), str(target))
    report.finish({"execute": execute})
    return report.run_dir
