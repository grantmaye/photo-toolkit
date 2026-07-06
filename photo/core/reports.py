from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RunReport:
    command: str
    root: Path = Path("photo-toolkit-runs")
    run_dir: Path = field(init=False)
    operations: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.run_dir = self.root / timestamp
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def operation(self, **row: Any) -> None:
        self.operations.append(row)

    def error(self, path: str | Path, error: str) -> None:
        self.errors.append({"path": str(path), "error": error})

    def write_csv(self, name: str, rows: list[dict[str, Any]]) -> Path:
        path = self.run_dir / name
        keys = sorted({key for row in rows for key in row.keys()})
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def finish(self, extra: dict[str, Any] | None = None) -> Path:
        summary = {
            "command": self.command,
            "operations": len(self.operations),
            "errors": len(self.errors),
            "run_dir": str(self.run_dir),
        }
        if extra:
            summary.update(extra)
        self.write_csv("operations.csv", self.operations)
        self.write_csv("errors.csv", self.errors)
        (self.run_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        lines = [f"{key}: {value}" for key, value in summary.items()]
        (self.run_dir / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return self.run_dir


def write_csv(path: Path, rows: list[dict[str, Any]]) -> Path:
    keys = sorted({key for row in rows for key in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    return path
