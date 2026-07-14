"""Filesystem operations for purging and restoring reviewed media."""

from datetime import datetime
from pathlib import Path

from .models import MoveRecord


class FileOperationError(RuntimeError):
    """Report an operation that could not be completed safely."""


class PurgeSession:
    """Move reviewed files into a timestamped purge folder and restore them."""

    def __init__(self, root: Path, started_at: datetime | None = None) -> None:
        """Create a session rooted at ``root`` without moving any files."""

        self.root = root.expanduser().resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(self.root)
        timestamp = (started_at or datetime.now()).strftime("%Y%m%d_%H%M%S")
        self.purge_directory = self.root / f"_purge_{timestamp}"
        self.purge_directory.mkdir(exist_ok=True)
        self.history: list[MoveRecord] = []

    def purge(self, source: Path) -> MoveRecord:
        """Move ``source`` into purge while preserving its relative path."""

        source = source.expanduser().resolve()
        if not source.is_file():
            raise FileOperationError(f"Source file does not exist: {source}")
        try:
            relative = source.relative_to(self.root)
        except ValueError as error:
            raise FileOperationError("Source file must be inside the review root") from error

        destination = self.purge_directory / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination = self._unique_destination(destination)
        try:
            source.rename(destination)
        except OSError as error:
            raise FileOperationError(f"Could not move {source}: {error}") from error
        record = MoveRecord(source=source, destination=destination)
        self.history.append(record)
        return record

    def undo_last(self) -> MoveRecord | None:
        """Restore and remove the most recent purge operation, if present."""

        if not self.history:
            return None
        record = self.history[-1]
        self._restore(record)
        self.history.pop()
        return record

    def restore_all(self) -> list[MoveRecord]:
        """Restore every successful move in reverse order."""

        restored: list[MoveRecord] = []
        while self.history:
            record = self.undo_last()
            if record is not None:
                restored.append(record)
        return restored

    def _restore(self, record: MoveRecord) -> None:
        if not record.destination.is_file():
            raise FileOperationError(f"Purged file is missing: {record.destination}")
        record.source.parent.mkdir(parents=True, exist_ok=True)
        destination = self._unique_destination(record.source)
        try:
            record.destination.rename(destination)
        except OSError as error:
            raise FileOperationError(f"Could not restore {record.source}: {error}") from error

    @staticmethod
    def _unique_destination(path: Path) -> Path:
        """Return ``path`` or a timestamped variant that does not overwrite."""

        if not path.exists():
            return path
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        candidate = path.with_name(f"{path.stem}_{stamp}{path.suffix}")
        counter = 2
        while candidate.exists():
            candidate = path.with_name(f"{path.stem}_{stamp}_{counter}{path.suffix}")
            counter += 1
        return candidate