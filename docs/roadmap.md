# Roadmap

## v0.3

- RAW+JPEG pairing and policy controls.
- Orphan sidecar reports.
- Album/folder structure reports.
- Manifest verification with `photo verify-manifest hashes.csv`.
- Import-ready copy command for deterministic archive layouts.

## v0.4

- Timezone normalization with `--timezone`, `--assume-timezone`, and offset writing.
- Configurable date source priority.
- Metadata diff reports showing exact ExifTool tag changes.
- Camera/device reports by make, model, lens, phone model, file type, and codec.

## v0.5

- Paranoid copy mode with source hash, destination hash, and manifest comparison.
- Resume interrupted runs.
- SQLite run database for large libraries.
- Checksummed archive export bundles.

## Project Quality

- Ruff formatting and linting.
- CLI snapshot tests.
- Expanded docs for Google Photos Takeout, Synology exports, Immich external libraries, and Apple Photos staging.
- `pipx` and Homebrew installation docs.
