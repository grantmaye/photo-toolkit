# Changelog

## v0.2.0 - 2026-07-06

### Added

- Reviewable JSON plans with `photo plan`.
- Plan execution with `photo apply-plan`.
- Undo planning/execution for supported move and rename operations with `photo undo`.
- Sidecar handling for `.xmp`, `.aae`, `.json`, `.dop`, and `.pp3`.
- Live Photo partner handling for image/video pairs.
- Collision policy options with `--on-conflict skip|suffix|error|replace-never`.
- Date consistency reports with `photo date-audit`.
- Import validation with `photo validate-import --target immich|photoprism|apple|synology|vault`.
- Roadmap document for upcoming archive, manifest, timezone, and packaging work.

### Changed

- Move, rename, and date-fix commands now plan associated sidecar and Live Photo files by default.
- README now documents package/release posture and alpha status.

## v0.1.0 - 2026-07-06

### Added

- Initial `photo` CLI.
- Safe-by-default dry-run behavior.
- Metadata/date repair commands.
- Rename, verify, hash, duplicate, report, GPS stripping, and HEIC conversion commands.
- Tests, docs, MIT license, GitHub Actions, issue templates, and contribution/security docs.
