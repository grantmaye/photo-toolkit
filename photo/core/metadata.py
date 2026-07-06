from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, time
from pathlib import Path

from photo.core.filesystem import VIDEO_EXTENSIONS

DATE_PREFIX_RE = re.compile(r"^(?P<date>\d{8})(?:[_-]?(?P<time>\d{6}))?")


def exiftool_path() -> str | None:
    return shutil.which("exiftool")


def require_exiftool() -> str:
    tool = exiftool_path()
    if tool:
        return tool
    raise RuntimeError(
        "ExifTool is required for metadata writes. Install it with "
        "`brew install exiftool`, `sudo apt install libimage-exiftool-perl`, "
        "or from https://exiftool.org/."
    )


def read_metadata(path: Path) -> dict[str, object]:
    tool = exiftool_path()
    if not tool:
        return {}
    result = subprocess.run(
        [tool, "-json", "-DateTimeOriginal", "-CreateDate", "-ModifyDate", "-MediaCreateDate", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {}
    data = json.loads(result.stdout or "[]")
    return data[0] if data else {}


def parse_exif_datetime(value: object) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y:%m:%d %H:%M:%S%z"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def filename_datetime(path: Path) -> datetime | None:
    match = DATE_PREFIX_RE.match(path.stem)
    if not match:
        return None
    date_part = match.group("date")
    time_part = match.group("time") or "120000"
    try:
        return datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S")
    except ValueError:
        return None


def capture_datetime(path: Path) -> tuple[datetime | None, str]:
    from_name = filename_datetime(path)
    if from_name:
        return from_name, "filename"
    metadata = read_metadata(path)
    for key in ("DateTimeOriginal", "CreateDate", "MediaCreateDate", "ModifyDate"):
        parsed = parse_exif_datetime(metadata.get(key))
        if parsed:
            return parsed, key
    return None, "missing"


def build_fixed_date(path: Path, yyyymmdd: str) -> datetime:
    base = datetime.strptime(yyyymmdd, "%Y%m%d")
    existing, _ = capture_datetime(path)
    existing_time = existing.time() if existing else time(12, 0, 0)
    return datetime.combine(base.date(), existing_time)


def build_fixed_year(path: Path, year: int) -> datetime:
    existing, _ = capture_datetime(path)
    if existing:
        return existing.replace(year=year)
    return datetime(year, 1, 1, 12, 0, 0)


def filename_with_datetime(path: Path, captured: datetime, include_original: bool = True) -> str:
    stamp = captured.strftime("%Y%m%d_%H%M%S")
    original = DATE_PREFIX_RE.sub("", path.stem).lstrip("_- ") or path.stem
    if include_original:
        return f"{stamp}_{original}{path.suffix.lower()}"
    return f"{stamp}{path.suffix.lower()}"


def update_metadata(path: Path, captured: datetime) -> None:
    tool = require_exiftool()
    value = captured.strftime("%Y:%m:%d %H:%M:%S")
    args = [tool, "-overwrite_original"]
    if path.suffix.lower() in VIDEO_EXTENSIONS:
        args.extend([f"-QuickTime:CreateDate={value}", f"-QuickTime:ModifyDate={value}"])
    args.extend([f"-DateTimeOriginal={value}", f"-CreateDate={value}", f"-ModifyDate={value}", str(path)])
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "ExifTool metadata update failed")


def strip_gps_metadata(path: Path) -> None:
    tool = require_exiftool()
    result = subprocess.run(
        [tool, "-overwrite_original", "-gps:all=", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "ExifTool GPS removal failed")
