# photo-toolkit

[![tests](https://github.com/grantmaye/photo-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/grantmaye/photo-toolkit/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#project-status)

`photo-toolkit` is a reusable open-source command-line toolkit for preparing photo and video libraries before importing them into Immich, PhotoPrism, Synology Photos, Apple Photos, or long-term vault/archive folders.

The CLI command is named `photo`.

## Project status

`photo-toolkit` is alpha software. It is designed around conservative dry-runs, reviewable reports, and explicit execution flags, but you should still test it on copies first and back up important media before metadata-changing commands.

Current release: `v0.2.0`

## Why it exists

Large personal media libraries are often messy: mixed camera exports, scanned archives, wrong years, duplicated folders, HEIC/JPEG pairs, zero-byte files, and files with missing or inconsistent metadata. `photo-toolkit` gives self-hosters, family archivists, NAS users, and Immich users a safe way to inspect and prepare those libraries before import.

## Safety guarantees

- Dry-run by default.
- File-changing commands require `--execute`.
- Originals are never modified unless `--execute` is explicitly passed.
- Commands write logs and reports under `./photo-toolkit-runs/<timestamp>/`.
- Every run writes `summary.txt`, `summary.json`, `operations.csv`, and `errors.csv`.
- Duplicate removal never deletes by default; moving duplicates is preferred.
- Dangerous paths such as `/`, `/home`, `/mnt`, and drive roots are refused unless `--allow-root-path` is passed.
- Back up your photos before running metadata-changing commands.

## Install

Recommended for now, directly from GitHub:

```bash
pipx install git+https://github.com/grantmaye/photo-toolkit.git
```

From a local checkout:

```bash
pip install -e .
```

For HEIC conversion support:

```bash
pip install -e ".[heic]"
```

For best metadata support, install ExifTool:

```bash
brew install exiftool
# or
sudo apt install libimage-exiftool-perl
```

If ExifTool is missing, metadata-writing commands fail gracefully with install instructions.

## Packages and releases

GitHub Releases are the right fit while the project is alpha. PyPI packaging can come after a little more real-world testing and API/CLI stabilization.

For now:

- Use GitHub Releases for tagged versions and release notes.
- Install with `pipx` from GitHub or `pip install -e .` from a checkout.
- Defer PyPI until the CLI has a stable `v0.3` or `v1.0` command contract.

## Quick start

```bash
photo verify /path/to/staging
photo date-audit /path/to/staging --output date-audit.csv
photo validate-import /path/to/staging --target immich
photo report /path/to/staging --output ./photo-report
photo hash /path/to/staging --output hashes.csv
photo plan /path/to/staging --mode rename-from-exif --output photo-plan.json
photo apply-plan photo-plan.json
photo apply-plan photo-plan.json --execute
photo rename-from-exif /path/to/staging
photo rename-from-exif /path/to/staging --execute
```

## Common workflows

Move files with a known filename prefix:

```bash
photo move-prefix --from /path/to/staging/2014 --to /path/to/staging/wedding --prefix 20140101
photo move-prefix --from /path/to/staging/2014 --to /path/to/staging/wedding --prefix 20140101 --execute
```

Fix an event date:

```bash
photo fix-date /path/to/staging/wedding --date 20220716
photo fix-date /path/to/staging/wedding --date 20220716 --execute
```

Create, review, and apply a plan:

```bash
photo plan /path/to/staging/wedding --mode fix-date --date 20220716 --output wedding-plan.json
photo apply-plan wedding-plan.json
photo apply-plan wedding-plan.json --execute
```

Undo supported move/rename operations from a previous run:

```bash
photo undo photo-toolkit-runs/20260706-120000
photo undo photo-toolkit-runs/20260706-120000 --execute
```

Fix only the year while preserving month, day, and time where possible:

```bash
photo fix-year /path/to/staging/to2018 --year 2018
photo fix-year /path/to/staging/to2018 --year 2018 --execute
```

Find and move duplicates:

```bash
photo remove-duplicates /path/to/staging
photo remove-duplicates /path/to/staging --move-to /path/to/duplicates --execute
```

Commands that move or rename files also handle common sidecars (`.xmp`, `.aae`, `.json`, `.dop`, `.pp3`) and Live Photo image/video partners by default. Use `--no-sidecars` or `--no-live-photos` to disable that behavior.

## Immich workflow

1. Copy media into a staging folder.
2. Run `photo verify /path/to/staging`.
3. Run `photo report /path/to/staging`.
4. Fix known date/year problems with dry-runs first.
5. Rename consistently with `photo rename-from-exif`.
6. Generate `hashes.csv`.
7. Import the cleaned staging folder into Immich.

## NAS workflow

Use `photo report`, `photo hash`, and `photo remove-duplicates --move-to` before copying into NAS import folders. Keep the run reports alongside archive manifests.

## Vault/private photo workflow

Prepare a copy of the vault import folder, then run:

```bash
photo strip-gps /path/to/vault-import
photo strip-gps /path/to/vault-import --execute
```

GPS removal changes metadata. Always keep a backup.

## Supported media

JPG, JPEG, PNG, HEIC, HEIF, MOV, MP4, M4V, DNG, CR2, NEF, ARW, RAF, TIFF, and TIF.

## License

MIT
