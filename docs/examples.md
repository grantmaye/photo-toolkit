# Examples

```bash
photo move-prefix --from /path/to/staging/2014 --to /path/to/staging/wedding --prefix 20140101
photo plan /path/to/staging/wedding --mode fix-date --date 20220716 --output wedding-plan.json
photo apply-plan wedding-plan.json --execute
photo date-audit /path/to/staging --output date-audit.csv
photo validate-import /path/to/staging --target immich
photo fix-year /path/to/staging/to2018 --year 2018
photo remove-duplicates /path/to/staging --move-to /path/to/duplicates --execute
photo convert-heic /path/to/input --output /path/to/converted --execute
```
