from __future__ import annotations

from pathlib import Path
from typing import Any

from photo.core.filesystem import associated_files, media_files, resolve_destination, retarget_associated_file
from photo.core.metadata import build_fixed_date, build_fixed_year, capture_datetime, filename_with_datetime
from photo.core.operations import write_plan
from photo.core.reports import RunReport
from photo.core.safety import assert_distinct_paths, assert_safe_source


def _rename_operations(
    folder: Path,
    mode: str,
    date: str | None,
    year: int | None,
    collision: str,
    include_sidecars: bool,
    include_live_photos: bool,
) -> list[dict[str, Any]]:
    operations = []
    seen: set[Path] = set()
    for path in media_files(folder):
        if path in seen:
            continue
        if mode == "fix-date":
            if not date:
                raise ValueError("fix-date plans require --date.")
            captured = build_fixed_date(path, date)
            source = "planned-date"
        elif mode == "fix-year":
            if year is None:
                raise ValueError("fix-year plans require --year.")
            captured = build_fixed_year(path, year)
            source = "planned-year"
        else:
            captured, source = capture_datetime(path)
            if not captured:
                continue
        primary_target = path.with_name(filename_with_datetime(path, captured))
        for associated in associated_files(path, include_sidecars, include_live_photos):
            seen.add(associated)
            target = retarget_associated_file(path, primary_target, associated)
            resolved = resolve_destination(associated, target, collision)
            action = mode if associated == path and mode in {"fix-date", "fix-year"} else "rename"
            operations.append(
                {
                    "action": action if associated == path else "sidecar-rename",
                    "source": str(associated),
                    "destination": str(resolved or target),
                    "date_source": source,
                    "new_datetime": captured.isoformat(sep=" "),
                    "collision": collision,
                    "skipped": resolved is None,
                }
            )
    return operations


def _move_prefix_operations(
    source: Path,
    destination: Path,
    prefix: str,
    collision: str,
    include_sidecars: bool,
    include_live_photos: bool,
) -> list[dict[str, Any]]:
    assert_distinct_paths(source, destination)
    operations = []
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
            operations.append(
                {
                    "action": "move" if associated == path else "sidecar-move",
                    "source": str(associated),
                    "destination": str(resolved or target),
                    "collision": collision,
                    "skipped": resolved is None,
                }
            )
    return operations


def run(
    folder: Path,
    output: Path,
    mode: str = "rename-from-exif",
    date: str | None = None,
    year: int | None = None,
    move_from: Path | None = None,
    move_to: Path | None = None,
    prefix: str | None = None,
    collision: str = "suffix",
    allow_root_path: bool = False,
    include_sidecars: bool = True,
    include_live_photos: bool = True,
) -> Path:
    report = RunReport("plan")
    operations: list[dict[str, Any]]
    if mode == "move-prefix":
        source = move_from or folder
        if not move_to or not prefix:
            raise ValueError("move-prefix plans require --move-to and --prefix.")
        assert_safe_source(source, allow_root_path)
        operations = _move_prefix_operations(source, move_to, prefix, collision, include_sidecars, include_live_photos)
    elif mode in {"rename-from-exif", "fix-date", "fix-year"}:
        assert_safe_source(folder, allow_root_path)
        operations = _rename_operations(folder, mode, date, year, collision, include_sidecars, include_live_photos)
    else:
        raise ValueError(f"Unsupported plan mode: {mode}")
    write_plan(output, operations)
    for operation in operations:
        report.operation(**operation, executed=False)
    report.finish({"output": str(output), "planned_operations": len(operations), "mode": mode})
    return report.run_dir
