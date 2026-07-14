"""Domain models used by the scanner and file operation services."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Decision = Literal["purge", "keep"]


@dataclass(frozen=True)
class MediaFile:
    """Describe a supported file discovered under a review root."""

    path: Path
    kind: str


@dataclass(frozen=True)
class MoveRecord:
    """Record one move so it can be reversed without guessing the source."""

    source: Path
    destination: Path