from __future__ import annotations

from pathlib import Path

from photo.core.operations import read_plan, run_operations
from photo.core.reports import RunReport


def run(plan_file: Path, execute: bool, collision: str = "suffix") -> Path:
    operations = read_plan(plan_file)
    report = RunReport("apply-plan")
    run_operations(operations, report, execute, collision)
    report.finish({"execute": execute})
    return report.run_dir
