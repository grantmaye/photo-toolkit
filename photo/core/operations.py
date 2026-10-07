from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from photo.core.filesystem import resolve_destination
from photo.core.metadata import update_metadata
from photo.core.safety import assert_safe_source


SUPPORTED_APPLY_ACTIONS = {"move", "rename", "fix-date", "fix-year", "sidecar-move", "sidecar-rename"}


def write_plan(path: Path, operations: list[dict[str, Any]], command: str = "plan") -> Path:
    # Paths must keep their meaning when a reviewed plan is applied from another cwd.
    operations = [{**row, **{key: str(Path(row[key]).absolute())
                            for key in ("source", "destination") if row.get(key)}}
                  for row in operations]
    payload = {"version": 1, "command": command, "operations": operations}
    path.parent.mkdir(parents=True, exist_ok=True) if path.parent != Path(".") else None
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    return path


def read_plan(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Plan file must be an object with version 1.")
    operations = payload.get("operations")
    if not isinstance(operations, list) or not all(isinstance(row, dict) for row in operations):
        raise ValueError("Plan file must contain an operations list.")
    return operations


def read_operations_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def apply_file_operation(operation: dict[str, Any], collision: str = "suffix") -> tuple[bool, str]:
    action = str(operation.get("action", ""))
    if action not in SUPPORTED_APPLY_ACTIONS:
        return False, f"Unsupported action for apply-plan: {action}"
    if not operation.get("source") or not operation.get("destination"):
        return False, "Operation requires non-empty source and destination paths"
    source = Path(str(operation["source"]))
    destination = Path(str(operation["destination"]))
    assert_safe_source(source)
    assert_safe_source(destination)
    if source.is_symlink() or not source.is_file():
        return False, f"Source must be a regular, non-symlink file: {source}"
    if destination.is_symlink() or destination.is_dir():
        return False, f"Destination must be a file path: {destination}"
    resolved = resolve_destination(source, destination, collision)
    if resolved is None:
        return False, f"Skipped existing destination: {destination}"
    if action in {"fix-date", "fix-year"}:
        if not operation.get("new_datetime"):
            return False, "Metadata operations require new_datetime"
        update_metadata(source, datetime.fromisoformat(str(operation["new_datetime"])))
    resolved.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != resolved.resolve():
        shutil.move(str(source), str(resolved))
    return True, str(resolved)


def reverse_operations(operations: list[dict[str, str]]) -> list[dict[str, str]]:
    reversible = []
    for row in reversed(operations):
        # Older logs without execution evidence are not safe to undo.
        if str(row.get("executed", "")).lower() != "true" or str(row.get("skipped", "")).lower() == "true":
            continue
        action = row.get("action", "")
        source = row.get("source") or row.get("duplicate")
        destination = row.get("destination")
        if action in {"move", "rename", "sidecar-move", "sidecar-rename"} and source and destination:
            reversible.append({"action": "move", "source": destination, "destination": source})
    return reversible


def run_operations(operations: list[dict[str, Any]], report, execute: bool, collision: str) -> None:
    """Record actual completed paths so undo never treats a preview as a mutation."""
    for operation in operations:
        row = {**operation, "executed": False}
        if str(operation.get("skipped", "")).lower() == "true":
            report.operation(**{**row, "skipped": True})
            continue
        if execute:
            try:
                ok, message = apply_file_operation(operation, collision)
                if ok:
                    row.update(executed=True, destination=message)
                else:
                    report.error(operation.get("source", ""), message)
            except (OSError, ValueError, RuntimeError) as exc:
                report.error(operation.get("source", ""), str(exc))
        report.operation(**row)
