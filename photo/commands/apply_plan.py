from __future__ import annotations

from pathlib import Path

from photo.core.operations import apply_file_operation, read_plan
from photo.core.reports import RunReport
from photo.core.safety import SafetyError


def run(plan_file: Path, execute: bool, collision: str = "suffix") -> Path:
    report = RunReport("apply-plan")
    operations = read_plan(plan_file)
    for operation in operations:
        if operation.get("skipped") in {True, "True", "true"}:
            report.operation(**operation, executed=False, skipped=True)
            continue
        report.operation(**operation, executed=execute)
        if execute:
            ok, message = apply_file_operation(operation, collision)
            if not ok:
                report.error(operation.get("source", ""), message)
    if not execute:
        report.finish({"execute": execute, "warning": "Dry-run only. Re-run with --execute to apply the plan."})
        return report.run_dir
    report.finish({"execute": execute})
    return report.run_dir
