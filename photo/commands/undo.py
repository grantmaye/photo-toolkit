from __future__ import annotations

from pathlib import Path

from photo.core.operations import apply_file_operation, read_operations_csv, reverse_operations
from photo.core.reports import RunReport


def run(run_path: Path, execute: bool, collision: str = "suffix") -> Path:
    operations_path = run_path / "operations.csv" if run_path.is_dir() else run_path
    report = RunReport("undo")
    reversals = reverse_operations(read_operations_csv(operations_path))
    for operation in reversals:
        report.operation(**operation, executed=execute)
        if execute:
            ok, message = apply_file_operation(operation, collision)
            if not ok:
                report.error(operation.get("source", ""), message)
    report.finish({"execute": execute, "reversal_operations": len(reversals)})
    return report.run_dir
