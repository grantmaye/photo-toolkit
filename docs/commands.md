# Commands

- `move-prefix`: move files whose names start with a prefix.
- `fix-date`: set a full capture date and update filename prefixes.
- `fix-year`: change only the year where possible.
- `rename-from-exif`: rename from capture date.
- `verify`: inspect metadata, hashes, readability, zero-byte files, and unsupported files.
- `hash`: write a SHA256 manifest.
- `remove-duplicates`: detect duplicates by hash and move or explicitly delete them.
- `report`: generate CSV and HTML reports.
- `strip-gps`: remove GPS metadata when executed.
- `convert-heic`: convert HEIC/HEIF to JPEG output copies.
- `plan`: write a reviewable JSON plan for rename, date-fix, year-fix, or prefix-move operations.
- `apply-plan`: apply supported operations from a reviewed plan. Dry-run by default.
- `undo`: reverse supported move/rename operations from a previous `operations.csv`.
- `date-audit`: compare filename dates and metadata dates.
- `validate-import`: validate a staging folder for Immich, PhotoPrism, Apple Photos, Synology Photos, or vault imports.

Move and rename commands support `--on-conflict skip|suffix|error|replace-never`, `--no-sidecars`, and `--no-live-photos`.
