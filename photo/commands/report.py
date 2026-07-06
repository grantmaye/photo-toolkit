from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from photo.core.filesystem import HEIC_EXTENSIONS, VIDEO_EXTENSIONS, inspect_file, iter_files
from photo.core.hashing import duplicate_groups
from photo.core.metadata import capture_datetime
from photo.core.reports import RunReport, write_csv
from photo.core.safety import assert_safe_source


def run(folder: Path, output: Path = Path("photo-report"), allow_root_path: bool = False) -> Path:
    assert_safe_source(folder, allow_root_path)
    output.mkdir(parents=True, exist_ok=True)
    report = RunReport("report")
    rows = []
    by_year: Counter[str] = Counter()
    by_extension: Counter[str] = Counter()
    date_source: Counter[str] = Counter()
    largest = []
    supported_paths = []
    live_stems = defaultdict(set)
    for path in iter_files(folder):
        info = inspect_file(path)
        captured, source = capture_datetime(path) if info.supported and not info.zero_byte else (None, "missing")
        if info.supported:
            supported_paths.append(path)
        year = str(captured.year) if captured else "missing"
        by_year[year] += 1
        by_extension[info.extension or "[none]"] += 1
        date_source[source] += 1
        largest.append((info.size, path))
        if info.extension in {".jpg", ".jpeg", ".heic", ".mov"}:
            live_stems[path.stem].add(info.extension)
        rows.append(
            {
                "path": str(path),
                "size": info.size,
                "extension": info.extension,
                "supported": info.supported,
                "zero_byte": info.zero_byte,
                "date_source": source,
                "capture_datetime": captured.isoformat(sep=" ") if captured else "",
            }
        )
    duplicates = duplicate_groups(supported_paths)
    write_csv(output / "files.csv", rows)
    summary = {
        "total_files": len(rows),
        "total_size": sum(row["size"] for row in rows),
        "by_year": dict(by_year),
        "by_extension": dict(by_extension),
        "date_source": dict(date_source),
        "missing_metadata": date_source["missing"],
        "duplicate_groups": len(duplicates),
        "zero_byte_files": sum(1 for row in rows if row["zero_byte"]),
        "heic_count": sum(1 for row in rows if row["extension"] in HEIC_EXTENSIONS),
        "jpeg_count": sum(1 for row in rows if row["extension"] in {".jpg", ".jpeg"}),
        "video_count": sum(1 for row in rows if row["extension"] in VIDEO_EXTENSIONS),
        "live_photo_pairs": sum(1 for exts in live_stems.values() if ".mov" in exts and ({".jpg", ".jpeg", ".heic"} & exts)),
        "largest_files": [str(path) for _, path in sorted(largest, reverse=True)[:20]],
    }
    html = "<html><body><h1>Photo Toolkit Report</h1><pre>" + repr(summary) + "</pre></body></html>\n"
    (output / "report.html").write_text(html, encoding="utf-8")
    report.operation(action="report", output=str(output), **summary)
    report.finish(summary)
    return report.run_dir
