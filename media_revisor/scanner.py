"""Recursive multimedia discovery with deterministic filtering."""

from pathlib import Path

from .models import MediaFile

IMAGE_EXTENSIONS = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
VIDEO_EXTENSIONS = {".avi", ".mkv", ".mov", ".mp4", ".webm"}
AUDIO_EXTENSIONS = {".flac", ".m4a", ".mp3", ".ogg", ".wav"}
RAW_EXTENSIONS = {".arw", ".cr2", ".cr3", ".dng", ".nef", ".raf"}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | AUDIO_EXTENSIONS | RAW_EXTENSIONS


def media_kind(path: Path) -> str | None:
    """Return the media family for a supported path, or ``None``."""

    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    if suffix in AUDIO_EXTENSIONS:
        return "audio"
    if suffix in RAW_EXTENSIONS:
        return "raw"
    return None


def scan_media(root: Path) -> tuple[list[MediaFile], list[str]]:
    """Scan ``root`` recursively and return files plus non-fatal warnings.

    Hidden entries, symbolic links, and paths below ``_purge_*`` directories
    are skipped. Permission and filesystem errors become warning messages.
    """

    root = root.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)

    files: list[MediaFile] = []
    warnings: list[str] = []

    def visit(directory: Path) -> None:
        try:
            entries = sorted(directory.iterdir(), key=lambda item: item.name.casefold())
        except OSError as error:
            warnings.append(f"Could not read {directory}: {error}")
            return

        for entry in entries:
            if entry.name.startswith(".") or entry.is_symlink():
                continue
            if entry.is_dir():
                if entry.name.startswith("_purge_"):
                    continue
                visit(entry)
                continue
            if not entry.is_file():
                continue
            kind = media_kind(entry)
            if kind is not None:
                files.append(MediaFile(entry, kind))

    visit(root)
    files.sort(key=lambda item: item.path.relative_to(root).as_posix().casefold())
    return files, warnings