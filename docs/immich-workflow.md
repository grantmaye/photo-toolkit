# Immich workflow

Use a staging folder before importing into Immich.

```bash
photo verify /path/to/staging
photo report /path/to/staging --output ./photo-report
photo fix-date /path/to/staging/event --date 20220716
photo fix-date /path/to/staging/event --date 20220716 --execute
photo rename-from-exif /path/to/staging --execute
photo hash /path/to/staging
```

Import only after reviewing run reports.
