# voice-cli

Convert voice files to text.

```sh
Usage: v [OPTIONS]

Options:
  -d, --directory TEXT    Directory to iterate
  --start TEXT            Filter files since date in format YYYY-MM-
                          DD[THH:MM:SS]
  --end TEXT              Filter files until date in format YYYY-MM-
                          DD[THH:MM:SS]
  -o, --output-file TEXT  Output file to write to
  --dry-run               Run in dry-run mode without transcribing
  --help                  Show this message and exit.
```

Example output:

```md
## 2024-01-01 00:14:00

Test 2

## 2022-01-01 00:16:00

Test 1
```
