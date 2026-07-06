from __future__ import annotations

import shutil
from pathlib import Path

from photo.core.filesystem import media_files, unique_destination
from photo.core.hashing import duplicate_groups
from photo.core.reports import RunReport
from photo.core.safety import SafetyError, assert_distinct_paths, assert_safe_source


def run(
    folder: Path,
    move_to: Path | None,
    delete: bool,
    execute: bool,
    allow_root_path: bool = False,
) -> Path:
    assert_safe_source(folder, allow_root_path)
    if move_to:
        assert_distinct_paths(folder, move_to)
    if delete and not execute:
        raise SafetyError("--delete requires --execute.")
    if execute and not move_to and not delete:
        raise SafetyError("Duplicate changes require --move-to or explicit --delete.")
    report = RunReport("remove-duplicates")
    groups = duplicate_groups(media_files(folder))
    if execute and move_to:
        move_to.mkdir(parents=True, exist_ok=True)
    for digest, paths in groups.items():
        keeper = sorted(paths)[0]
        for duplicate in sorted(paths)[1:]:
            target = unique_destination(move_to / duplicate.name) if move_to else ""
            action = "delete" if delete else "move"
            report.operation(
                action=action,
                sha256=digest,
                keeper=str(keeper),
                duplicate=str(duplicate),
                destination=str(target),
                executed=execute,
            )
            if execute and delete:
                duplicate.unlink()
            elif execute and move_to:
                shutil.move(str(duplicate), str(target))
    report.finish({"execute": execute, "duplicate_groups": len(groups)})
    return report.run_dir
