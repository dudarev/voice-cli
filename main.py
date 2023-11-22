"""
A CLI tool to transcribe audio files in a directory.
"""
import io
import json
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from typing import Optional


import click
import whisper
from dateutil.parser import parse, ParserError


MODEL_NAME = "medium.en"
SOUND_EXTENSIONS = (".mp3", ".wav", ".ogg", ".m4a", ".flac", "", ".webm")
CACHE_DIR = Path.home() / ("cache/voice-cli/")
TIMESTAMP_FORMAT = "## %Y-%m-%d %H:%M:%S"
CACHE_DELTA_MINUTES = 5


Path(CACHE_DIR).mkdir(exist_ok=True, parents=True)


def generate_path_hash(path: Path) -> str:
    """
    Generates a unique hash for a Path object using the SHA-256 hashing algorithm.
    """
    hasher = hashlib.sha256()
    hasher.update(str(path).encode("utf-8"))
    return hasher.hexdigest()


def fromisoformat(iso_str: str, end_of_date_for_date: bool = False) -> datetime:
    """
    Converts an ISO 8601 string to a datetime object.
    `end_of_date_for_date` flag is used to determine if the end of the day should be used
    when `iso_str` is a date.
    """
    dt = datetime.fromisoformat(iso_str)
    if end_of_date_for_date and (
        dt.second == 0 and dt.minute == 0 and dt.hour == 0 and dt.microsecond == 0
    ):
        return dt + timedelta(days=1)
    return dt


def is_between(
    start: Optional[datetime], end: Optional[datetime], timestamp: datetime
) -> bool:
    """
    Checks if a timestamp is between two dates.
    """
    if start is None and end is None:
        return True
    if start is not None and timestamp < start:
        return False
    if end is not None and timestamp > end:
        return False
    return True


def get_modified_time_utc(path: Path) -> datetime:
    """
    Returns the modified time of a file in timezone-aware format in UTC timezone.
    """
    timestamp = path.stat().st_mtime
    dt = datetime.fromtimestamp(timestamp, tz=datetime.now().astimezone().tzinfo)
    return dt.astimezone(timezone.utc)


def get_utcnow_with_timezone() -> datetime:
    """
    Returns the current UTC datetime in timezone-aware format.
    """
    return datetime.utcnow().replace(tzinfo=timezone.utc)


class Transcriber:
    model_name = MODEL_NAME
    _model = None

    def __init__(self, model_name=None):
        if model_name is not None:
            self.model_name = model_name

    @property
    def model(self):
        if not self._model:
            self._model = whisper.load_model(self.model_name)
        return self._model

    def get_cache_path(self, path) -> Path:
        return CACHE_DIR / f"{generate_path_hash(path)}.json"

    def get_cache(self, path: Path):
        cache_path = self.get_cache_path(path)
        if cache_path.exists():
            cache_data = json.loads(cache_path.read_text())
            if "transcribe_started_at_utc" not in cache_data:
                cache_path.unlink()
                return None
            else:
                transcribe_started_at_utc = fromisoformat(
                    cache_data["transcribe_started_at_utc"]
                )
                modified_time_utc = get_modified_time_utc(path)
                if transcribe_started_at_utc < modified_time_utc + timedelta(
                    minutes=CACHE_DELTA_MINUTES
                ):
                    cache_path.unlink()
                    return None
            cache_data = json.loads(cache_path.read_text())
            return cache_data["text"].strip()
        return None

    def save_cache(self, path: Path, result):
        with open(self.get_cache_path(path), "w") as f:
            json.dump(result, f, indent=2)

    def transcribe(self, path: Path):
        echo(f"Transcribing {path}")

        cache = self.get_cache(path)
        if cache is not None:
            return cache

        transcribe_started_at_utc = get_utcnow_with_timezone()
        result = self.model.transcribe(str(path), fp16=False)
        result["transcribe_started_at_utc"] = transcribe_started_at_utc.isoformat()

        self.save_cache(path, result)

        echo(result["text"].strip())

        return result["text"].strip()


transcriber = Transcriber()


def echo(message: str, f_out: Optional[io.TextIOWrapper] = None):
    click.echo(message)
    if f_out:
        click.echo(message, f_out)


def get_file_timestamp(path: Path) -> datetime:
    """
    Try to extract timestamp from file name.
    If not found, use modified time of file.

    Examples of file names:
    Voice 1571_W_20230806_020851.mp3
    20230804 214200.m4a
    """
    try:
        elements = re.split(r"[_\.]", path.name)
        timestamp_elements = [e for e in elements if len(e) >= 6 and e.isdigit()]
        return parse(" ".join(timestamp_elements))
    except ParserError:
        pass

    try:
        # split on white space
        elements = re.split(r"[\s\.]", path.name)
        timestamp_elements = [e for e in elements if len(e) >= 6 and e.isdigit()]
        return parse(" ".join(timestamp_elements))
    except ParserError:
        pass

    return datetime.fromtimestamp(path.stat().st_mtime)


@click.command()
@click.option("-d", "--directory", help="Directory to iterate")
@click.option("--start", help="Filter files since date in format YYYY-MM-DD[THH:MM:SS]")
@click.option("--end", help="Filter files until date in format YYYY-MM-DD[THH:MM:SS]")
@click.option("-o", "--output-file", help="Output file to write to")
@click.option(
    "--dry-run", help="Run in dry-run mode without transcribing", is_flag=True
)
def cli(
    directory: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    output_file: Optional[click.Path] = None,
    dry_run: bool = False,
):
    directory = directory if directory else "."

    start_dt = fromisoformat(start) if start else None
    end_dt = fromisoformat(end, end_of_date_for_date=True) if end else None

    sound_files = []
    directory = Path(directory)
    for path in directory.glob("**/*"):
        if (
            path.is_file()
            and path.suffix.lower() in SOUND_EXTENSIONS
            and is_between(start_dt, end_dt, get_file_timestamp(path))
            and not path.stem.startswith(".")
        ):
            sound_files.append(path)

    sorted_sound_files: list[Path] = sorted(
        sound_files, key=lambda x: get_file_timestamp(x), reverse=True
    )

    echo("Files to transcribe:")
    for f in sorted_sound_files:
        echo(f"{f} ({get_file_timestamp(f).strftime('%Y-%m-%d %H:%M:%S')})")

    timestamp_texts = {}
    existing_timestamp_texts = {}
    if output_file and Path(output_file).exists():
        with open(output_file, "r") as f:
            lines = f.readlines()
        current_timestamp = None
        for line in lines:
            if line.startswith("## "):
                current_timestamp = line.strip()
                existing_timestamp_texts[current_timestamp] = []
            elif current_timestamp:
                existing_timestamp_texts[current_timestamp].append(line)

    for f in sorted_sound_files:
        t = f.stat().st_mtime
        timestamp = datetime.fromtimestamp(t).strftime(TIMESTAMP_FORMAT)
        if dry_run:
            echo(timestamp)
            click.echo("\n")
            continue
        if timestamp in existing_timestamp_texts:
            result = "\n".join(existing_timestamp_texts[timestamp])
        else:
            result = transcriber.transcribe(f)
        timestamp_texts[timestamp] = result

    if dry_run:
        return

    f_out = open(output_file, "w") if output_file else None
    for timestamp, text in timestamp_texts.items():
        echo(timestamp, f_out)
        echo(text, f_out)
        echo("\n", f_out)
    if f_out:
        f_out.close()


if __name__ == "__main__":
    cli()
