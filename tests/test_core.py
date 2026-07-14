"""Tests for media discovery and reversible file operations."""

from datetime import datetime
from pathlib import Path

from media_revisor.file_operations import PurgeSession
from media_revisor.scanner import scan_media


def test_scan_filters_supported_media_and_purge(tmp_path: Path) -> None:
    """The scanner returns supported visible media in deterministic order."""

    (tmp_path / "photos").mkdir()
    (tmp_path / "photos" / "b.JPG").write_bytes(b"image")
    (tmp_path / "photos" / "a.txt").write_text("ignored")
    (tmp_path / ".hidden.jpg").write_bytes(b"ignored")
    (tmp_path / "_purge_20260714_120000").mkdir()
    (tmp_path / "_purge_20260714_120000" / "old.mp4").write_bytes(b"ignored")

    files, warnings = scan_media(tmp_path)

    assert warnings == []
    assert [item.path.name for item in files] == ["b.JPG"]


def test_purge_preserves_relative_path_and_restores(tmp_path: Path) -> None:
    """A moved file can be restored using the recorded source path."""

    source = tmp_path / "photos" / "image.jpg"
    source.parent.mkdir()
    source.write_bytes(b"image")
    session = PurgeSession(tmp_path, datetime(2026, 7, 14, 12, 0, 0))

    record = session.purge(source)

    assert record.destination == tmp_path / "_purge_20260714_120000" / "photos" / "image.jpg"
    assert not source.exists()
    assert record.destination.exists()
    session.undo_last()
    assert source.read_bytes() == b"image"


def test_purge_renames_collisions_without_overwriting(tmp_path: Path) -> None:
    """A collision creates a new destination and retains both files."""

    source = tmp_path / "image.jpg"
    source.write_bytes(b"new")
    session = PurgeSession(tmp_path, datetime(2026, 7, 14, 12, 0, 0))
    destination = session.purge_directory / "image.jpg"
    destination.write_bytes(b"old")

    record = session.purge(source)

    assert record.destination != destination
    assert destination.read_bytes() == b"old"
    assert record.destination.read_bytes() == b"new"