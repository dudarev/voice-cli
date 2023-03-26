import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


import click
import whisper


MODEL_NAME = 'medium.en'
SOUND_EXTENSIONS = (".mp3", ".wav", ".ogg", ".m4a", ".flac", "")
CACHE_DIR = Path.home() / ("cache/voice-cli/")
Path(CACHE_DIR).mkdir(exist_ok=True, parents=True)

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"


def round_to_nearest_half_hour(dt: datetime) -> datetime:
    rounded_minute = round(dt.minute / 30) * 30
    if rounded_minute == 60:
        dt += timedelta(hours=1)
        rounded_minute = 0
    return dt.replace(minute=rounded_minute, second=0, microsecond=0)


def generate_path_hash(path: Path) -> str:
    """
    Generates a unique hash for a Path object using the SHA-256 hashing algorithm.
    """
    hasher = hashlib.sha256()
    hasher.update(str(path).encode("utf-8"))
    return hasher.hexdigest()


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
        cache_path = Path(CACHE_DIR) / f"{generate_path_hash(path)}.json"
        if cache_path.exists():
            cache_data = json.loads(cache_path.read_text())
            return cache_data["text"].strip()

        result = self.model.transcribe(str(path), fp16=False)

        with open(cache_path, "w") as f:
            json.dump(result, f, indent=2)

        return result["text"].strip()


transcriber = Transcriber()


@click.command()
@click.option("-d", "--directory", help="Directory to iterate")
@click.option("--since", help="Filter files since date in format YYYY-MM-DD")
@click.option(
    "--dry-run", help="Run in dry-run mode without transcribing", is_flag=True
)
def cli(
    directory: Optional[str] = None, since: Optional[str] = None, dry_run: bool = False
):
    since_timestamp = datetime.fromisoformat(since).timestamp() if since else 0
    directory = directory if directory else "."

    sound_files = []
    directory = Path(directory)
    for path in directory.glob("**/*"):
        if (
            path.is_file()
            and path.suffix.lower() in SOUND_EXTENSIONS
            and path.stat().st_mtime > since_timestamp
            and not path.stem.startswith(".")
        ):
            sound_files.append(path)

    sorted_sound_files: list[Path] = sorted(
        sound_files, key=lambda x: x.stat().st_mtime, reverse=True
    )
    for f in sorted_sound_files:
        click.echo(f.name)
        click.echo(
            round_to_nearest_half_hour(
                datetime.fromtimestamp(f.stat().st_mtime)
            ).strftime(TIMESTAMP_FORMAT)
        )
        if dry_run:
            click.echo("\n")
            continue
        result = transcriber.transcribe(f)
        click.echo(result)
        click.echo("\n")
