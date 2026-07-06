# Releases and packaging

## Current recommendation

Use GitHub Releases while `photo-toolkit` is alpha. Avoid publishing to PyPI until the command contract has had more real-world testing.

## Why releases now

- Users can pin versions.
- Release notes make safety-sensitive changes easy to review.
- Tags give bug reports a stable version reference.
- The project does not need a registry account or package ownership decision yet.

## Why not PyPI yet

- Metadata-writing behavior should be exercised by more users first.
- Command names and report schemas may still change.
- Packaging HEIC extras and ExifTool expectations should be documented more thoroughly before broad distribution.

## Suggested path

1. Publish `v0.2.0` as an alpha GitHub Release.
2. Keep install docs focused on `pipx install git+https://github.com/grantmaye/photo-toolkit.git`.
3. Add Ruff and packaging CI.
4. Publish to PyPI at `v0.3.0` or later if the CLI feels stable.
