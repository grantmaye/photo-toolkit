# Event date fix

```bash
photo move-prefix --from /path/to/staging/2014 --to /path/to/staging/event --prefix 20140101
photo fix-date /path/to/staging/event --date 20200101
photo fix-date /path/to/staging/event --date 20200101 --execute
```
