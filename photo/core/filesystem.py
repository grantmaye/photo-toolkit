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
SIDECAR_EXTENSIONS = {".xmp", ".aae", ".json", ".dop", ".pp3"}
COLLISION_POLICIES = {"skip", "suffix", "error", "replace-never"}


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


def resolve_destination(source: Path, target: Path, collision: str = "suffix") -> Path | None:
    if collision not in COLLISION_POLICIES:
        raise ValueError(f"Unsupported collision policy: {collision}")
    if same_path(source, target):
        return source
    if not target.exists():
        return target
    if collision == "skip":
        return None
    if collision == "suffix":
        return unique_destination(target)
    raise FileExistsError(f"Destination already exists: {target}")


def sidecar_files(path: Path) -> list[Path]:
    candidates = []
    for ext in SIDECAR_EXTENSIONS:
        candidates.extend(path.parent.glob(f"{path.name}{ext}"))
        candidates.extend(path.parent.glob(f"{path.stem}{ext}"))
    return sorted({candidate for candidate in candidates if candidate.exists() and candidate.is_file()})


def live_photo_partner(path: Path) -> Path | None:
    ext = path.suffix.lower()
    if ext == ".mov":
        for image_ext in (".heic", ".jpg", ".jpeg"):
            candidate = path.with_suffix(image_ext)
            if candidate.exists():
                return candidate
    if ext in {".heic", ".jpg", ".jpeg"}:
        candidate = path.with_suffix(".mov")
        if candidate.exists():
            return candidate
    return None


def associated_files(path: Path, include_sidecars: bool = True, include_live_photo: bool = True) -> list[Path]:
    files = [path]
    if include_sidecars:
        files.extend(sidecar_files(path))
    if include_live_photo:
        partner = live_photo_partner(path)
        if partner:
            files.append(partner)
            if include_sidecars:
                files.extend(sidecar_files(partner))
    return sorted({file for file in files if file.exists() and file.is_file()})


def retarget_associated_file(source: Path, target: Path, associated: Path) -> Path:
    if associated == source:
        return target
    if associated.stem == source.stem:
        return target.with_name(f"{target.stem}{associated.suffix}")
    if associated.name.startswith(f"{source.name}."):
        return target.with_name(f"{target.name}{associated.name[len(source.name):]}")
    return target.parent / associated.name
