from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import media_files
from photo.core.metadata import filename_datetime, parse_exif_datetime, read_metadata
from photo.core.reports import RunReport, write_csv
from photo.core.safety import assert_safe_source


def run(folder: Path, output: Path = Path("date-audit.csv"), allow_root_path: bool = False) -> Path:
    assert_safe_source(folder, allow_root_path)
    report = RunReport("date-audit")
    rows = []
    for path in media_files(folder):
        metadata = read_metadata(path)
        filename_date = filename_datetime(path)
        metadata_dates = {
            key: parse_exif_datetime(metadata.get(key))
            for key in ("DateTimeOriginal", "CreateDate", "MediaCreateDate", "ModifyDate")
        }
        present = {key: value for key, value in metadata_dates.items() if value}
        unique_values = {value.isoformat(sep=" ") for value in present.values()}
        mismatch = bool(filename_date and unique_values and filename_date.isoformat(sep=" ") not in unique_values)
        mismatch = mismatch or len(unique_values) > 1
        row = {
            "path": str(path),
            "filename_datetime": filename_date.isoformat(sep=" ") if filename_date else "",
            "datetime_original": metadata_dates["DateTimeOriginal"].isoformat(sep=" ") if metadata_dates["DateTimeOriginal"] else "",
            "create_date": metadata_dates["CreateDate"].isoformat(sep=" ") if metadata_dates["CreateDate"] else "",
            "media_create_date": metadata_dates["MediaCreateDate"].isoformat(sep=" ") if metadata_dates["MediaCreateDate"] else "",
            "modify_date": metadata_dates["ModifyDate"].isoformat(sep=" ") if metadata_dates["ModifyDate"] else "",
            "mismatch": mismatch,
            "missing_metadata": not bool(present),
        }
        rows.append(row)
        report.operation(**row)
    write_csv(output, rows)
    report.finish({"output": str(output), "mismatches": sum(1 for row in rows if row["mismatch"])})
    return report.run_dir
