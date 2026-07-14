"""Main PySide6 window for reviewing and classifying media files."""

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .file_operations import FileOperationError, PurgeSession
from .models import MediaFile
from .scanner import scan_media
from .theme import build_palette, stylesheet


class ScanWorker(QObject):
    """Run recursive discovery outside the GUI thread."""

    finished = Signal(list, list)
    failed = Signal(str)

    def __init__(self, root: Path) -> None:
        """Store the root to scan."""

        super().__init__()
        self.root = root

    @Slot()
    def run(self) -> None:
        """Scan media and emit either results or an actionable error."""

        try:
            files, warnings = scan_media(self.root)
        except (OSError, ValueError) as error:
            self.failed.emit(str(error))
            return
        self.finished.emit(files, warnings)


class MainWindow(QMainWindow):
    """Present the review queue and coordinate user classification actions."""

    def __init__(self) -> None:
        """Build the initial empty review window."""

        super().__init__()
        self.setWindowTitle("Media Revisor")
        self.resize(1200, 780)
        self.files: list[MediaFile] = []
        self.review_root: Path | None = None
        self.current_index = 0
        self.session: PurgeSession | None = None
        self.mode = "light"
        self.thread: QThread | None = None
        self.worker: ScanWorker | None = None
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        self._build_ui()
        self._apply_theme()

    def _build_ui(self) -> None:
        header = QFrame(objectName="header")
        header_layout = QHBoxLayout(header)
        brand = QLabel("MEDIA REVISOR", objectName="brand")
        header_layout.addWidget(brand)
        header_layout.addStretch()
        choose = QPushButton("Open folder")
        choose.clicked.connect(self.choose_folder)
        header_layout.addWidget(choose)
        theme_action = QAction("Toggle theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        toolbar = QToolBar()
        toolbar.addAction(theme_action)
        self.addToolBar(toolbar)

        self.media_panel = QFrame(objectName="mediaPanel")
        media_layout = QVBoxLayout(self.media_panel)
        self.preview = QLabel(
            "Open a folder to start reviewing",
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        self.preview.setMinimumSize(640, 440)
        self.preview.setScaledContents(False)
        media_layout.addWidget(self.preview, stretch=1)
        self.video_widget.hide()
        media_layout.addWidget(self.video_widget, stretch=1)
        self.details = QLabel("No media selected", objectName="hint")
        media_layout.addWidget(self.details)

        self.status = QLabel("Choose a root folder to create a review session.")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        purge = QPushButton("Purge  ←", objectName="purgeButton")
        purge.clicked.connect(self.purge_current)
        keep = QPushButton("Keep  →", objectName="keepButton")
        keep.clicked.connect(self.keep_current)
        undo = QPushButton("Undo last")
        undo.clicked.connect(self.undo_last)
        restore = QPushButton("Restore session")
        restore.clicked.connect(self.restore_session)
        controls = QHBoxLayout()
        controls.addWidget(purge)
        controls.addWidget(keep)
        controls.addWidget(undo)
        controls.addWidget(restore)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(header)
        layout.addWidget(self.media_panel, stretch=1)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)
        layout.addLayout(controls)
        self.setCentralWidget(central)

    def _apply_theme(self) -> None:
        """Apply the active palette and token-based stylesheet."""

        self.setPalette(build_palette(self.mode))
        self.setStyleSheet(stylesheet(self.mode))

    @Slot()
    def choose_folder(self) -> None:
        """Select a root folder and start a background scan."""

        selected = QFileDialog.getExistingDirectory(self, "Choose media folder")
        if not selected:
            return
        self.review_root = Path(selected).expanduser().resolve()
        self.progress.show()
        self.status.setText("Scanning media files...")
        self.thread = QThread(self)
        self.worker = ScanWorker(Path(selected))
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._scan_finished)
        self.worker.failed.connect(self._scan_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self._clear_worker)
        self.thread.start()

    @Slot(list, list)
    def _scan_finished(self, files: list[MediaFile], warnings: list[str]) -> None:
        """Create a purge session and display the first discovered file."""

        self.progress.hide()
        self.files = files
        self.current_index = 0
        if files:
            self.session = PurgeSession(self.review_root) if self.review_root else None
            self._show_current()
            message = f"{len(files)} media files ready"
            if warnings:
                message += f" ({len(warnings)} warnings)"
            self.status.setText(message)
        else:
            self.session = None
            self.status.setText("No supported media files found.")

    @Slot(str)
    def _scan_failed(self, message: str) -> None:
        """Show a scan error without crashing the application."""

        self.progress.hide()
        self.status.setText(f"Scan failed: {message}")

    @Slot()
    def _clear_worker(self) -> None:
        """Release the completed scan worker and thread."""

        self.worker = None
        self.thread = None

    def _show_current(self) -> None:
        """Render the current queue item using its media family."""

        if not self.files or self.current_index >= len(self.files):
            self.preview.setText("Review complete")
            self.details.setText("No remaining media files")
            self.video_widget.hide()
            self.player.stop()
            return
        item = self.files[self.current_index]
        self.details.setText(f"{self.current_index + 1} / {len(self.files)}    {item.path}")
        if item.kind in {"image", "raw"}:
            self.player.stop()
            self.video_widget.hide()
            pixmap = QPixmap(str(item.path))
            self.preview.setPixmap(pixmap.scaled(
                self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
            self.preview.show()
        else:
            self.preview.hide()
            self.video_widget.show()
            self.player.setSource(item.path.as_uri())
            self.player.play()

    def _advance(self) -> None:
        """Move to the next queue item and update the preview."""

        self.current_index += 1
        self._show_current()

    def purge_current(self) -> None:
        """Move the current item to the session purge folder."""

        if not self.session or not self.files or self.current_index >= len(self.files):
            return
        try:
            self.session.purge(self.files[self.current_index].path)
        except FileOperationError as error:
            QMessageBox.warning(self, "Could not purge file", str(error))
            return
        self.status.setText("Purged")
        self._advance()

    def keep_current(self) -> None:
        """Keep the current item in its original location and advance."""

        if self.files and self.current_index < len(self.files):
            self.status.setText("Kept")
            self._advance()

    def undo_last(self) -> None:
        """Restore the last purged file and move the queue back to it."""

        if not self.session or not self.session.history:
            return
        try:
            self.session.undo_last()
        except FileOperationError as error:
            QMessageBox.warning(self, "Could not undo", str(error))
            return
        self.current_index = max(0, self.current_index - 1)
        self._show_current()
        self.status.setText("Last purge restored")

    def restore_session(self) -> None:
        """Restore all purged files in the current session."""

        if not self.session:
            return
        try:
            restored = self.session.restore_all()
        except FileOperationError as error:
            QMessageBox.warning(self, "Could not restore session", str(error))
            return
        self.status.setText(f"Restored {len(restored)} file(s)")

    def toggle_theme(self) -> None:
        """Switch between the light and dark token palettes."""

        self.mode = "dark" if self.mode == "light" else "light"
        self._apply_theme()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        """Map left and right arrows to purge and keep decisions."""

        if event.key() == Qt.Key.Key_Left:
            self.purge_current()
        elif event.key() == Qt.Key.Key_Right:
            self.keep_current()
        else:
            super().keyPressEvent(event)