"""Qt tests for keyboard classification shortcuts."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton

from media_revisor.main_window import MainWindow
from media_revisor.models import MediaFile
from media_revisor.file_operations import PurgeSession


def test_right_arrow_classifies_even_when_keep_button_has_focus(tmp_path: Path) -> None:
    """The right arrow action is not reduced to button-focus navigation."""

    application = QApplication.instance() or QApplication([])
    source = tmp_path / "image.jpg"
    source.write_bytes(b"image")
    window = MainWindow()
    window.review_root = tmp_path
    window.session = PurgeSession(tmp_path)
    window.files = [MediaFile(source, "image")]
    window._show_current()
    window.show()
    window.activateWindow()
    application.processEvents()
    keep_button = next(
        button for button in window.findChildren(QPushButton)
        if button.text().startswith("Keep")
    )
    keep_button.setFocus()

    QTest.keyClick(keep_button, Qt.Key.Key_Right)
    application.processEvents()

    assert window.current_index == 1
    window.close()