from datetime import datetime
import os
from pathlib import Path
import pytest

from click.testing import CliRunner


DATA_DIRECTORY = "tests/data"


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def reverse_sorted_test_data_files() -> list[Path]:
    modified_time_0 = datetime(2022, 1, 1, 0, 16, 0).timestamp()
    modified_time_1 = datetime(2024, 1, 1, 0, 14, 0).timestamp()

    path_0 = Path(DATA_DIRECTORY) / "subfolder/test-1.m4a"
    path_1 = Path(DATA_DIRECTORY) / "test-2.m4a"

    os.utime(path_0, (modified_time_0, modified_time_0))
    os.utime(path_1, (modified_time_1, modified_time_1))

    # file modified later comes first
    return path_1, path_0


@pytest.fixture
def output_file(tmp_path: Path) -> Path:
    return tmp_path / "output.txt"
