from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import pytest

from photo.commands import fix_date, fix_year, move_prefix, rename_from_exif, report, verify
from photo.core.hashing import duplicate_groups
from photo.core.metadata import build_fixed_date, build_fixed_year, filename_with_datetime
from photo.core.safety import SafetyError, assert_safe_source


def read_operations(run_dir: Path) -> list[dict[str, str]]:
    with (run_dir / "operations.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_dry_run_does_not_change_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    original = source / "20140101_test.jpg"
    original.write_bytes(b"image")

    run_dir = move_prefix.run(source, destination, "20140101", execute=False)

    assert original.exists()
    assert not destination.exists()
    rows = read_operations(run_dir)
    assert rows[0]["executed"] == "False"


def test_move_prefix_plans_correctly(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    (source / "20140101_a.jpg").write_bytes(b"a")
    (source / "other.jpg").write_bytes(b"b")

    run_dir = move_prefix.run(source, destination, "20140101", execute=False)

    rows = read_operations(run_dir)
    assert len(rows) == 1
    assert rows[0]["source"].endswith("20140101_a.jpg")
    assert rows[0]["destination"].endswith("destination/20140101_a.jpg")


def test_fix_date_builds_correct_new_filename(tmp_path: Path) -> None:
    path = tmp_path / "20140101_091011_camera.jpg"
    path.write_bytes(b"image")

    captured = build_fixed_date(path, "20220716")
    new_name = filename_with_datetime(path, captured)

    assert captured.strftime("%Y%m%d_%H%M%S") == "20220716_091011"
    assert new_name == "20220716_091011_camera.jpg"


def test_fix_year_preserves_month_day_time(tmp_path: Path) -> None:
    path = tmp_path / "20140101_091011_camera.jpg"
    path.write_bytes(b"image")

    captured = build_fixed_year(path, 2018)

    assert captured.strftime("%Y%m%d_%H%M%S") == "20180101_091011"


def test_rename_from_exif_uses_metadata_date(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    folder = tmp_path / "photos"
    folder.mkdir()
    path = folder / "camera.jpg"
    path.write_bytes(b"image")

    monkeypatch.setattr(
        "photo.commands.rename_from_exif.capture_datetime",
        lambda p: (datetime(2022, 7, 16, 9, 10, 11), "DateTimeOriginal"),
    )
    run_dir = rename_from_exif.run(folder, execute=False)

    rows = read_operations(run_dir)
    assert rows[0]["destination"].endswith("20220716_091011_camera.jpg")
    assert rows[0]["date_source"] == "DateTimeOriginal"


def test_duplicate_detection_by_hash(tmp_path: Path) -> None:
    one = tmp_path / "one.jpg"
    two = tmp_path / "two.jpg"
    three = tmp_path / "three.jpg"
    one.write_bytes(b"same")
    two.write_bytes(b"same")
    three.write_bytes(b"different")

    groups = duplicate_groups([one, two, three])

    assert len(groups) == 1
    assert {p.name for group in groups.values() for p in group} == {"one.jpg", "two.jpg"}


def test_zero_byte_detection(tmp_path: Path) -> None:
    folder = tmp_path / "photos"
    folder.mkdir()
    (folder / "empty.jpg").write_bytes(b"")

    run_dir = verify.run(folder)

    rows = read_operations(run_dir)
    assert rows[0]["zero_byte"] == "True"


def test_report_generation(tmp_path: Path) -> None:
    folder = tmp_path / "photos"
    output = tmp_path / "out"
    folder.mkdir()
    (folder / "20220716_091011_a.jpg").write_bytes(b"a")

    report.run(folder, output=output)

    assert (output / "files.csv").exists()
    assert (output / "report.html").exists()


def test_safety_refusal_on_dangerous_paths() -> None:
    with pytest.raises(SafetyError):
        assert_safe_source(Path("/"))


def test_fix_date_dry_run_writes_plan(tmp_path: Path) -> None:
    folder = tmp_path / "photos"
    folder.mkdir()
    (folder / "20140101_091011_a.jpg").write_bytes(b"a")

    run_dir = fix_date.run(folder, "20220716", execute=False)

    rows = read_operations(run_dir)
    assert rows[0]["destination"].endswith("20220716_091011_a.jpg")


def test_fix_year_dry_run_writes_plan(tmp_path: Path) -> None:
    folder = tmp_path / "photos"
    folder.mkdir()
    (folder / "20140101_091011_a.jpg").write_bytes(b"a")

    run_dir = fix_year.run(folder, 2018, execute=False)

    rows = read_operations(run_dir)
    assert rows[0]["destination"].endswith("20180101_091011_a.jpg")
