from __future__ import annotations

from pathlib import Path

from photo.core.filesystem import HEIC_EXTENSIONS, media_files, unique_destination
from photo.core.reports import RunReport
from photo.core.safety import assert_distinct_paths, assert_safe_source


def run(folder: Path, output: Path, execute: bool, allow_root_path: bool = False) -> Path:
    assert_safe_source(folder, allow_root_path)
    assert_distinct_paths(folder, output)
    report = RunReport("convert-heic")
    files = [path for path in media_files(folder) if path.suffix.lower() in HEIC_EXTENSIONS]
    if execute:
        output.mkdir(parents=True, exist_ok=True)
    for path in files:
        target = unique_destination(output / f"{path.stem}.jpg")
        report.operation(action="convert-heic", source=str(path), destination=str(target), executed=execute)
        if execute:
            try:
                from PIL import Image
                import pillow_heif

                pillow_heif.register_heif_opener()
                with Image.open(path) as image:
                    image.convert("RGB").save(target, "JPEG", quality=95)
            except ImportError as exc:
                report.error(path, "Install HEIC support with `pip install photo-toolkit[heic]`.")
                break
            except Exception as exc:
                report.error(path, str(exc))
    report.finish({"execute": execute, "output": str(output)})
    return report.run_dir
