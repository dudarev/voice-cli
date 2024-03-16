# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

See [Developement](docs/Development.md) for instructions on how to create a
CHANGELOG entry with AI bots.

## [0.0.5] - 2024-03-16

### Added

- Added a `--force` option to the CLI to force transcribing files even if a cache exists.

### Changed

- Existing text in the output file does not change with new transcription
- Updated the README with information about the new `--force` option.
- Updated the `Development.md` doc to use `main` instead of `master` for the git diff command.
- Updated the `PLAN.md` doc with additional notes and plans.
- Bumped the version in `setup.py` from `0.0.2` to `0.0.5`.
- Added `scratch` to the `.gitignore` file.

### Tests

- Added new tests in `tests/test_cli.py` to cover various scenarios with the output file and the `--force` option.

## [0.0.4] - 2023-08-06

### Added

- Added support for `.webm` sound file extension in `SOUND_EXTENSIONS`.
- Added the `get_file_timestamp` function to extract timestamps from file names or use the modified time if not available.
- Added and modified tests for the new functionalities.
- `test` target in the `Makefile` to run tests with coverage and generate HTML and terminal reports.
- `show-coverage` target in the `Makefile` to open the HTML coverage report in the browser.
- Created a [TODO.md](docs/TODO.md) file to track pending tasks.
- Added a [Development](docs/Development.md) file with instructions for creating a CHANGELOG entry with AI bots.

### Changed

- Updated the sorting of sound files based on their timestamps using `get_file_timestamp`.

## [0.0.3] - 2023-06-18

## Fixed

- Remove outdated cache

## Added

- `get_modified_time_utc()` and `get_utcnow_with_timezone() functions
- `get_cache()`, `save_cache()` and use cache for transcribing

## Changed

- Check cache data to see if file has been modified since transcription started
- Use UTC datetimes for consistency

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
