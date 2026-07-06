from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from photo.core.filesystem import resolve_destination
from photo.core.metadata import update_metadata


SUPPORTED_APPLY_ACTIONS = {"move", "rename", "fix-date", "fix-year", "sidecar-move", "sidecar-rename"}


def write_plan(path: Path, operations: list[dict[str, Any]], command: str = "plan") -> Path:
    payload = {"version": 1, "command": command, "operations": operations}
    path.parent.mkdir(parents=True, exist_ok=True) if path.parent != Path(".") else None
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    return path


def read_plan(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    operations = payload.get("operations", [])
    if not isinstance(operations, list):
        raise ValueError("Plan file must contain an operations list.")
    return operations


def read_operations_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def apply_file_operation(operation: dict[str, Any], collision: str = "suffix") -> tuple[bool, str]:
    action = str(operation.get("action", ""))
    if action not in SUPPORTED_APPLY_ACTIONS:
        return False, f"Unsupported action for apply-plan: {action}"
    source = Path(str(operation.get("source", "")))
    destination = Path(str(operation.get("destination", "")))
    if not source.exists():
        return False, f"Source does not exist: {source}"
    resolved = resolve_destination(source, destination, collision)
    if resolved is None:
        return False, f"Skipped existing destination: {destination}"
    if action in {"fix-date", "fix-year"} and operation.get("new_datetime"):
        update_metadata(source, datetime.fromisoformat(str(operation["new_datetime"])))
    resolved.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(resolved))
    return True, str(resolved)


def reverse_operations(operations: list[dict[str, str]]) -> list[dict[str, str]]:
    reversible = []
    for row in reversed(operations):
        action = row.get("action", "")
        source = row.get("source") or row.get("duplicate")
        destination = row.get("destination")
        if action in {"move", "rename", "sidecar-move", "sidecar-rename"} and source and destination:
            reversible.append({"action": "move", "source": destination, "destination": source})
    return reversible
