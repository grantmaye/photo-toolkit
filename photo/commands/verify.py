from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import inspect_file, iter_files
from photo.core.metadata import capture_datetime
from photo.core.reports import RunReport
from photo.core.safety import assert_safe_source


def run(folder: Path, allow_root_path: bool = False) -> Path:
    assert_safe_source(folder, allow_root_path)
    report = RunReport("verify")
    for path in iter_files(folder):
        info = inspect_file(path)
        captured, source = capture_datetime(path) if info.supported and not info.zero_byte else (None, "missing")
        report.operation(
            path=str(path),
            size=info.size,
            extension=info.extension,
            supported=info.supported,
            zero_byte=info.zero_byte,
            readable=True,
            date_source=source,
            capture_datetime=captured.isoformat(sep=" ") if captured else "",
        )
    report.finish()
    return report.run_dir
