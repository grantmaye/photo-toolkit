from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from photo.commands import (
    convert_heic,
    fix_date,
    fix_year,
    hash as hash_command,
    move_prefix,
    remove_duplicates,
    rename_from_exif,
    report as report_command,
    strip_gps,
    verify as verify_command,
)
from photo.core.safety import SafetyError

app = typer.Typer(help="Safe-by-default photo and video library toolkit.")
console = Console()


def _done(run_dir: Path) -> None:
    console.print(f"Run log: {run_dir}")


def _handle(func, *args, **kwargs) -> None:
    try:
        _done(func(*args, **kwargs))
    except SafetyError as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.command("move-prefix")
def move_prefix_cmd(
    source: Path = typer.Option(..., "--from", help="Folder to move files from."),
    destination: Path = typer.Option(..., "--to", help="Folder to move files into."),
    prefix: str = typer.Option(..., "--prefix", help="Filename prefix to match."),
    execute: bool = typer.Option(False, "--execute", help="Actually move files."),
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(move_prefix.run, source, destination, prefix, execute, allow_root_path)


@app.command("fix-date")
def fix_date_cmd(
    folder: Path,
    date: str = typer.Option(..., "--date", help="Capture date as YYYYMMDD."),
    execute: bool = typer.Option(False, "--execute", help="Actually update metadata and rename files."),
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(fix_date.run, folder, date, execute, allow_root_path)


@app.command("fix-year")
def fix_year_cmd(
    folder: Path,
    year: int = typer.Option(..., "--year", help="Replacement capture year."),
    execute: bool = typer.Option(False, "--execute", help="Actually update metadata and rename files."),
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(fix_year.run, folder, year, execute, allow_root_path)


@app.command("rename-from-exif")
def rename_from_exif_cmd(
    folder: Path,
    execute: bool = typer.Option(False, "--execute", help="Actually rename files."),
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(rename_from_exif.run, folder, execute, allow_root_path)


@app.command("verify")
def verify_cmd(
    folder: Path,
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(verify_command.run, folder, allow_root_path)


@app.command("hash")
def hash_cmd(
    folder: Path,
    output: Path = typer.Option(Path("hashes.csv"), "--output", help="CSV manifest path."),
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(hash_command.run, folder, output, allow_root_path)


@app.command("remove-duplicates")
def remove_duplicates_cmd(
    folder: Path,
    move_to: Path | None = typer.Option(None, "--move-to", help="Move duplicates here."),
    delete: bool = typer.Option(False, "--delete", help="Delete duplicates. Never default."),
    execute: bool = typer.Option(False, "--execute", help="Actually move or delete duplicates."),
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(remove_duplicates.run, folder, move_to, delete, execute, allow_root_path)


@app.command("report")
def report_cmd(
    folder: Path,
    output: Path = typer.Option(Path("photo-report"), "--output", help="Report output folder."),
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(report_command.run, folder, output, allow_root_path)


@app.command("strip-gps")
def strip_gps_cmd(
    folder: Path,
    execute: bool = typer.Option(False, "--execute", help="Actually remove GPS metadata."),
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(strip_gps.run, folder, execute, allow_root_path)


@app.command("convert-heic")
def convert_heic_cmd(
    folder: Path,
    output: Path = typer.Option(..., "--output", help="Converted JPEG output folder."),
    execute: bool = typer.Option(False, "--execute", help="Actually convert files."),
    allow_root_path: bool = typer.Option(False, "--allow-root-path", help="Allow dangerous root paths."),
) -> None:
    _handle(convert_heic.run, folder, output, execute, allow_root_path)


if __name__ == "__main__":
    app()
