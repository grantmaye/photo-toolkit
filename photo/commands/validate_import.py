from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import MEDIA_EXTENSIONS, inspect_file, iter_files, live_photo_partner, media_files
from photo.core.hashing import duplicate_groups
from photo.core.metadata import capture_datetime
from photo.core.reports import RunReport, write_csv
from photo.core.safety import assert_safe_source

TARGETS = {"immich", "photoprism", "apple", "synology", "vault"}


def run(folder: Path, target: str, output: Path = Path("import-validation.csv"), allow_root_path: bool = False) -> Path:
    if target not in TARGETS:
        raise ValueError(f"Unsupported target: {target}")
    assert_safe_source(folder, allow_root_path)
    report = RunReport("validate-import")
    rows = []
    files = list(iter_files(folder))
    supported = media_files(folder)
    duplicates = duplicate_groups(supported)
    duplicate_paths = {str(path) for group in duplicates.values() for path in group[1:]}
    for path in files:
        info = inspect_file(path)
        captured, source = capture_datetime(path) if info.supported and not info.zero_byte else (None, "missing")
        warnings = []
        if not info.supported and info.extension not in {".xmp", ".aae", ".json", ".dop", ".pp3"}:
            warnings.append("unsupported")
        if info.zero_byte:
            warnings.append("zero-byte")
        if info.supported and not captured:
            warnings.append("missing-date")
        if str(path) in duplicate_paths:
            warnings.append("duplicate")
        if target == "immich" and info.extension == ".mov" and not live_photo_partner(path):
            warnings.append("possible-orphan-live-photo-video")
        if target == "apple" and info.extension in {".heic", ".mov"} and not live_photo_partner(path):
            warnings.append("check-live-photo-pair")
        row = {
            "path": str(path),
            "target": target,
            "supported": info.supported or info.extension in {".xmp", ".aae", ".json", ".dop", ".pp3"},
            "date_source": source,
            "warnings": ";".join(warnings),
        }
        rows.append(row)
        report.operation(**row)
    write_csv(output, rows)
    report.finish({"output": str(output), "target": target, "warnings": sum(1 for row in rows if row["warnings"])})
    return report.run_dir
