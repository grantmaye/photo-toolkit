from __future__ import annotations

from pathlib import Path

from photo.core.operations import read_operations_csv, reverse_operations, run_operations
from photo.core.reports import RunReport


def run(run_path: Path, execute: bool, collision: str = "suffix") -> Path:
    operations_path = run_path / "operations.csv" if run_path.is_dir() else run_path
    report = RunReport("undo")
    reversals = reverse_operations(read_operations_csv(operations_path))
    run_operations(reversals, report, execute, collision)
    report.finish({"execute": execute, "reversal_operations": len(reversals)})
    return report.run_dir
