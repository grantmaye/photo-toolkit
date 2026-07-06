# photo-toolkit v0.2.0

This is the first polished alpha release of `photo-toolkit`.

## Highlights

- Safe, reviewable operation planning with `photo plan`.
- Plan execution with `photo apply-plan`.
- Undo support for move and rename operations.
- Sidecar and Live Photo pairing during move/rename/date-fix workflows.
- Date auditing and import validation reports for staging folders.
- GitHub Actions tests and open-source project docs.

## Install

```bash
pipx install git+https://github.com/grantmaye/photo-toolkit.git
```

For metadata writes, install ExifTool:

```bash
brew install exiftool
```

## Safety

`photo-toolkit` is dry-run by default. Commands that change files or metadata require `--execute`. Back up media libraries before metadata-changing operations.
