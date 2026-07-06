# Immich workflow

Use a staging folder before importing into Immich.

```bash
photo verify /path/to/staging
photo validate-import /path/to/staging --target immich
photo date-audit /path/to/staging --output date-audit.csv
photo report /path/to/staging --output ./photo-report
photo plan /path/to/staging/event --mode fix-date --date 20220716 --output event-plan.json
photo apply-plan event-plan.json --execute
photo fix-date /path/to/staging/event --date 20220716
photo fix-date /path/to/staging/event --date 20220716 --execute
photo rename-from-exif /path/to/staging --execute
photo hash /path/to/staging
```

Import only after reviewing run reports.
