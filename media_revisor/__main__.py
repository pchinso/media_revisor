"""Application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .theme import build_palette


def main() -> int:
    """Create the Qt application and run the main window."""

    application = QApplication(sys.argv)
    application.setApplicationName("Media Revisor")
    application.setPalette(build_palette("light"))
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())