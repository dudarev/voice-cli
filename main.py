"""
A CLI tool to transcribe audio files in a directory.
"""
import io
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


import click
import whisper


MODEL_NAME = "medium.en"
SOUND_EXTENSIONS = (".mp3", ".wav", ".ogg", ".m4a", ".flac", "")
CACHE_DIR = Path.home() / ("cache/voice-cli/")
TIMESTAMP_FORMAT = "## %Y-%m-%d %H:%M:%S"


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

    def transcribe(self, path: Path):
        cache_path = CACHE_DIR / f"{generate_path_hash(path)}.json"
        if cache_path.exists():
            # check that cache is not older than the file
            if cache_path.stat().st_mtime < path.stat().st_mtime:
                cache_path.unlink()
            else:
                cache_data = json.loads(cache_path.read_text())
                return cache_data["text"].strip()

        result = self.model.transcribe(str(path), fp16=False)

        with open(cache_path, "w") as f:
            json.dump(result, f, indent=2)

        return result["text"].strip()


transcriber = Transcriber()


def echo(message: str, f_out: Optional[io.TextIOWrapper] = None):
    click.echo(message)
    if f_out:
        click.echo(message, f_out)


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
            and is_between(
                start_dt, end_dt, datetime.fromtimestamp(path.stat().st_mtime)
            )
            and not path.stem.startswith(".")
        ):
            sound_files.append(path)

    sorted_sound_files: list[Path] = sorted(
        sound_files, key=lambda x: x.stat().st_mtime, reverse=True
    )

    timestamp_texts = {}
    for f in sorted_sound_files:
        t = f.stat().st_mtime
        if dry_run:
            echo(datetime.fromtimestamp(t).strftime(TIMESTAMP_FORMAT))
            click.echo("\n")
            continue
        result = transcriber.transcribe(f)
        timestamp_texts[t] = result

    if dry_run:
        return

    f_out = open(output_file, "w") if output_file else None
    for t in timestamp_texts:
        echo(datetime.fromtimestamp(t).strftime(TIMESTAMP_FORMAT), f_out)
        echo(timestamp_texts[t], f_out)
        echo("\n", f_out)
    if f_out:
        f_out.close()


if __name__ == "__main__":
    cli()
