from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

import pytest

from photo.commands import apply_plan, date_audit, fix_date, fix_year, move_prefix, plan, rename_from_exif, report, undo, validate_import, verify
from photo.core.hashing import duplicate_groups
from photo.core.metadata import build_fixed_date, build_fixed_year, filename_with_datetime
from photo.core.safety import SafetyError, assert_safe_source


@pytest.fixture(autouse=True)
def isolated_working_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)


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

    captured = build_fixed_date(path, "20200101")
    new_name = filename_with_datetime(path, captured)

    assert captured.strftime("%Y%m%d_%H%M%S") == "20200101_091011"
    assert new_name == "20200101_091011_camera.jpg"


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
        lambda p: (datetime(2020, 1, 1, 9, 10, 11), "DateTimeOriginal"),
    )
    run_dir = rename_from_exif.run(folder, execute=False)

    rows = read_operations(run_dir)
    assert rows[0]["destination"].endswith("20200101_091011_camera.jpg")
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
    (folder / "20200101_091011_a.jpg").write_bytes(b"a")

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

    run_dir = fix_date.run(folder, "20200101", execute=False)

    rows = read_operations(run_dir)
    assert rows[0]["destination"].endswith("20200101_091011_a.jpg")


def test_fix_year_dry_run_writes_plan(tmp_path: Path) -> None:
    folder = tmp_path / "photos"
    folder.mkdir()
    (folder / "20140101_091011_a.jpg").write_bytes(b"a")

    run_dir = fix_year.run(folder, 2018, execute=False)

    rows = read_operations(run_dir)
    assert rows[0]["destination"].endswith("20180101_091011_a.jpg")


def test_sidecar_is_planned_with_rename(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    folder = tmp_path / "photos"
    folder.mkdir()
    (folder / "camera.jpg").write_bytes(b"image")
    (folder / "camera.xmp").write_text("sidecar", encoding="utf-8")
    monkeypatch.setattr(
        "photo.commands.rename_from_exif.capture_datetime",
        lambda p: (datetime(2020, 1, 1, 9, 10, 11), "DateTimeOriginal"),
    )

    run_dir = rename_from_exif.run(folder, execute=False)

    rows = read_operations(run_dir)
    assert {row["action"] for row in rows} == {"rename", "sidecar-rename"}
    assert any(row["destination"].endswith("20200101_091011_camera.xmp") for row in rows)


def test_collision_skip_marks_operation_skipped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    folder = tmp_path / "photos"
    folder.mkdir()
    (folder / "camera.jpg").write_bytes(b"image")
    (folder / "20200101_091011_camera.jpg").write_bytes(b"existing")
    monkeypatch.setattr(
        "photo.commands.rename_from_exif.capture_datetime",
        lambda p: (datetime(2020, 1, 1, 9, 10, 11), "DateTimeOriginal"),
    )

    run_dir = rename_from_exif.run(folder, execute=False, collision="skip")

    rows = read_operations(run_dir)
    camera_row = next(row for row in rows if Path(row["source"]).name == "camera.jpg")
    assert camera_row["skipped"] == "True"


def test_plan_writes_json_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    folder = tmp_path / "photos"
    output = tmp_path / "photo-plan.json"
    folder.mkdir()
    (folder / "camera.jpg").write_bytes(b"image")
    monkeypatch.setattr(
        "photo.commands.plan.capture_datetime",
        lambda p: (datetime(2020, 1, 1, 9, 10, 11), "DateTimeOriginal"),
    )

    plan.run(folder, output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["version"] == 1
    assert payload["operations"][0]["destination"].endswith("20200101_091011_camera.jpg")


def test_apply_plan_dry_run_does_not_move(tmp_path: Path) -> None:
    source = tmp_path / "a.jpg"
    destination = tmp_path / "b.jpg"
    source.write_bytes(b"image")
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(
        json.dumps({"version": 1, "operations": [{"action": "rename", "source": str(source), "destination": str(destination)}]}),
        encoding="utf-8",
    )

    apply_plan.run(plan_file, execute=False)

    assert source.exists()
    assert not destination.exists()


def test_apply_plan_execute_moves_file(tmp_path: Path) -> None:
    source = tmp_path / "a.jpg"
    destination = tmp_path / "b.jpg"
    source.write_bytes(b"image")
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(
        json.dumps({"version": 1, "operations": [{"action": "rename", "source": str(source), "destination": str(destination)}]}),
        encoding="utf-8",
    )

    apply_plan.run(plan_file, execute=True)

    assert not source.exists()
    assert destination.exists()


def test_undo_dry_run_plans_reversal(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    operations = run_dir / "operations.csv"
    operations.write_text(
        "action,source,destination,executed\nrename,/tmp/source.jpg,/tmp/destination.jpg,True\n",
        encoding="utf-8",
    )

    undo_run = undo.run(run_dir, execute=False)

    rows = read_operations(undo_run)
    assert rows[0]["source"] == "/tmp/destination.jpg"
    assert rows[0]["destination"] == "/tmp/source.jpg"


def test_date_audit_generates_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    folder = tmp_path / "photos"
    output = tmp_path / "audit.csv"
    folder.mkdir()
    (folder / "20200101_091011_a.jpg").write_bytes(b"a")
    monkeypatch.setattr("photo.commands.date_audit.read_metadata", lambda p: {"DateTimeOriginal": "2020:01:01 09:10:11"})

    date_audit.run(folder, output)

    assert output.exists()
    rows = list(csv.DictReader(output.open(newline="", encoding="utf-8")))
    assert rows[0]["mismatch"] == "False"


def test_validate_import_flags_zero_byte(tmp_path: Path) -> None:
    folder = tmp_path / "photos"
    output = tmp_path / "validation.csv"
    folder.mkdir()
    (folder / "empty.jpg").write_bytes(b"")

    validate_import.run(folder, "immich", output)

    rows = list(csv.DictReader(output.open(newline="", encoding="utf-8")))
    assert "zero-byte" in rows[0]["warnings"]


def test_undo_refuses_dry_run_and_skipped_records(tmp_path: Path) -> None:
    from photo.core.operations import reverse_operations
    rows = [{"action": "rename", "source": "a", "destination": "b", "executed": value} for value in ("False", "", "false")]
    rows.append({"action": "move", "source": "a", "destination": "b", "executed": "True", "skipped": "True"})
    assert reverse_operations(rows) == []


def test_apply_logs_collision_destination_and_undo_restores(tmp_path: Path) -> None:
    source, target = tmp_path / "a.jpg", tmp_path / "b.jpg"
    source.write_bytes(b"original")
    target.write_bytes(b"unrelated")
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps({"version": 1, "operations": [{"action": "rename", "source": str(source), "destination": str(target)}]}))
    run_dir = apply_plan.run(plan_file, execute=True)
    rows = read_operations(run_dir)
    assert rows[0]["destination"] == str(tmp_path / "b_1.jpg")
    assert rows[0]["executed"] == "True"
    undo_dir = undo.run(run_dir, execute=True)
    assert source.read_bytes() == b"original"
    assert target.read_bytes() == b"unrelated"
    assert read_operations(undo_dir)[0]["executed"] == "True"
    assert run_dir != undo_dir


def test_skipped_plan_is_safe_and_failed_move_is_not_undoable(tmp_path: Path) -> None:
    from photo.core.operations import reverse_operations
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps({"version": 1, "operations": [
        {"action": "rename", "source": "missing.jpg", "destination": "b.jpg", "skipped": True},
        {"action": "rename", "source": "missing.jpg", "destination": "b.jpg"},
    ]}))
    run_dir = apply_plan.run(plan_file, execute=True)
    assert reverse_operations(read_operations(run_dir)) == []
    assert json.loads((run_dir / "summary.json").read_text())["errors"] == 1


@pytest.mark.parametrize("payload", [[], {"version": 2, "operations": []}, {"version": 1, "operations": ["bad"]}])
def test_invalid_plan_schema_rejected(tmp_path: Path, payload) -> None:
    from photo.core.operations import read_plan
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        read_plan(path)


def test_plan_does_not_move_directories_or_symlinks(tmp_path: Path) -> None:
    from photo.core.operations import apply_file_operation
    folder = tmp_path / "folder"
    folder.mkdir()
    assert not apply_file_operation({"action": "move", "source": str(folder), "destination": str(tmp_path / "other")})[0]
    source = tmp_path / "file.jpg"
    source.write_bytes(b"image")
    link = tmp_path / "link.jpg"
    link.symlink_to(source)
    assert not apply_file_operation({"action": "move", "source": str(link), "destination": str(tmp_path / "other")})[0]
    assert source.read_bytes() == b"image"


def test_written_plan_paths_survive_working_directory_change(tmp_path: Path, monkeypatch) -> None:
    from photo.core.operations import write_plan
    Path("a.jpg").write_bytes(b"image")
    plan_file = tmp_path / "plan.json"
    write_plan(plan_file, [{"action": "rename", "source": "a.jpg", "destination": "b.jpg"}])
    child = tmp_path / "child"
    child.mkdir()
    monkeypatch.chdir(child)
    apply_plan.run(plan_file, execute=True)
    assert (tmp_path / "b.jpg").read_bytes() == b"image"


def test_html_report_escapes_filenames(tmp_path: Path):
    folder = tmp_path / "photos"
    folder.mkdir()
    (folder / '<img src=x onerror=alert(1)>.jpg').write_bytes(b"fixture")
    output = tmp_path / "report"
    report.run(folder, output)
    html = (output / "report.html").read_text()
    assert "<img" not in html
    assert "&lt;img" in html


def test_cli_returns_failure_for_recorded_operation_error(tmp_path: Path):
    from typer.testing import CliRunner
    from photo.cli import app
    path = tmp_path / "plan.json"
    path.write_text(json.dumps({"version": 1, "operations": [{"action": "rename", "source": "missing.jpg", "destination": "target.jpg"}]}))
    result = CliRunner().invoke(app, ["apply-plan", str(path), "--execute"])
    assert result.exit_code == 1
    assert "errors.csv" in result.stdout
