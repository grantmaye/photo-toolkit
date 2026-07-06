# Safety

`photo-toolkit` is dry-run by default. Commands that move files, rename files, update metadata, remove GPS, convert files, or remove duplicates require `--execute`.

The tool refuses broad root paths unless `--allow-root-path` is passed. Back up your photo library before metadata-changing operations.
