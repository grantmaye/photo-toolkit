from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

MEDIA_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".heic",
    ".heif",
    ".mov",
    ".mp4",
    ".m4v",
    ".dng",
    ".cr2",
    ".nef",
    ".arw",
    ".raf",
    ".tiff",
    ".tif",
}

VIDEO_EXTENSIONS = {".mov", ".mp4", ".m4v"}
HEIC_EXTENSIONS = {".heic", ".heif"}


@dataclass(frozen=True)
class FileInfo:
    path: Path
    size: int
    extension: str
    supported: bool
    zero_byte: bool


def iter_files(root: Path, recursive: bool = True) -> Iterable[Path]:
    root = Path(root)
    if root.is_file():
        yield root
        return
    pattern = "**/*" if recursive else "*"
    for path in root.glob(pattern):
        if path.is_file():
            yield path


def media_files(root: Path, recursive: bool = True) -> list[Path]:
    return [p for p in iter_files(root, recursive) if p.suffix.lower() in MEDIA_EXTENSIONS]


def inspect_file(path: Path) -> FileInfo:
    stat = path.stat()
    ext = path.suffix.lower()
    return FileInfo(
        path=path,
        size=stat.st_size,
        extension=ext,
        supported=ext in MEDIA_EXTENSIONS,
        zero_byte=stat.st_size == 0,
    )


def unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    index = 1
    while True:
        candidate = parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def same_path(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except FileNotFoundError:
        return a.absolute() == b.absolute()
