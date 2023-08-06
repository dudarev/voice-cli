from pathlib import Path
from click.testing import CliRunner

from main import cli

from conftest import DATA_DIRECTORY


# TODO: replace this tests with more unit specific tests
def test_dir(cli_runner: CliRunner, reverse_sorted_test_data_files: list[Path]) -> None:
    result = cli_runner.invoke(cli, f"-d {DATA_DIRECTORY} --dry-run")
    assert result.exit_code == 0
    assert (
        result.output == "Files to transcribe:\n"
        "tests/data/test-2.m4a (2024-01-01 00:14:00)\n"
        "tests/data/subfolder/test-1.m4a (2022-01-01 00:16:00)\n"
        "## 2024-01-01 00:14:00\n\n\n"
        "## 2022-01-01 00:16:00\n\n\n"
    )


def test_dir_single(
    cli_runner: CliRunner, reverse_sorted_test_data_files: list[Path]
) -> None:
    result = cli_runner.invoke(cli, f"-d {DATA_DIRECTORY}/subfolder --dry-run")
    assert result.exit_code == 0
    assert (
        result.output == "Files to transcribe:\n"
        "tests/data/subfolder/test-1.m4a (2022-01-01 00:16:00)\n"
        "## 2022-01-01 00:16:00\n\n\n"
    )


def test_start(
    cli_runner: CliRunner, reverse_sorted_test_data_files: list[Path]
) -> None:
    result = cli_runner.invoke(cli, "-d tests/data --start 2023-01-01 --dry-run")
    assert result.exit_code == 0
    assert (
        result.output == "Files to transcribe:\n"
        "tests/data/test-2.m4a (2024-01-01 00:14:00)\n"
        "## 2024-01-01 00:14:00\n\n\n"
    )


def test_model(
    cli_runner: CliRunner,
    reverse_sorted_test_data_files: list[Path],
    tmp_path: Path,
    output_file: Path,
) -> None:
    result = cli_runner.invoke(
        cli, f"-d tests/data --start 2023-01-01 -o {output_file}"
    )
    assert result.exit_code == 0
    assert "## 2024-01-01 00:14:00\nTest 2\n\n\n" == output_file.read_text()
