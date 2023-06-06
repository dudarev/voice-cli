# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## How-to

Hint: Use `git diff > out.diff` to generate the diff and ask one of the LLM bots
(ChatGPT, Bard, Claude-Instant, etc.) to describe it.

Example prompts:

```
Describe this diff:
Summarize the diff:
```

## [0.0.2] - 2023-06-06

### Added

#### Functionality

- `--start` and `--end` options to filter files by date
- `--dry-run` option to run without transcribing
- `--output-file` option to write to file instead of stdout
- Adds type hints and function documentation

#### Files

- `CHANGELOG.md` to track changes
- `Makefile` to run tests
- `requirements.txt` to track dependencies
- `setup.py` and `pyproject.toml` to package the project
- `README.md` to describe the project
- `/tests` directory with `pytest` tests:

  - `/data` directory with test data
  - `test_cli.py` to test the CLI
  - `test_time.py` to test the time parsing

### Changed

- Only re-transcribes files if the cache is older than the actual file
- Improves the ISO 8601 date parsing to handle more granular timestamps
- Printing timestamps before each transcription
- Formatting timestamps in a consistent format

### Removed

- The rounding of timestamps to half hours
- `--since` option
