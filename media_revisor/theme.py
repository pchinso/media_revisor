"""Cox-inspired theme tokens and Qt palette construction."""

from PySide6.QtGui import QColor, QPalette

TOKENS = {
    "light": {
        "BG_APP": "#EAEDED",
        "BG_PANEL": "#FFFFFF",
        "TEXT_MAIN": "#17191F",
        "TEXT_SOFT": "#43464F",
        "BORDER": "#BDC5E3",
        "BLUE_DEEP": "#283198",
        "BLUE_DARKER": "#171D69",
        "TURQUOISE": "#2CB8C7",
        "CORAL": "#ED696A",
    },
    "dark": {
        "BG_APP": "#17191F",
        "BG_PANEL": "#252830",
        "TEXT_MAIN": "#FFFFFF",
        "TEXT_SOFT": "#BDC5E3",
        "BORDER": "#43464F",
        "BLUE_DEEP": "#283198",
        "BLUE_DARKER": "#171D69",
        "TURQUOISE": "#2CB8C7",
        "CORAL": "#ED696A",
    },
}


def build_palette(mode: str) -> QPalette:
    """Build a Qt palette from the selected light or dark token set."""

    colors = TOKENS[mode]
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(colors["BG_APP"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors["BG_PANEL"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["BG_APP"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors["TEXT_MAIN"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["TEXT_MAIN"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors["BLUE_DEEP"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["TURQUOISE"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#17191F"))
    return palette


def stylesheet(mode: str) -> str:
    """Return the small set of Qt rules that use the active theme tokens."""

    colors = TOKENS[mode]
    return f"""
        QWidget {{ background: {colors['BG_APP']}; color: {colors['TEXT_MAIN']};
            font-family: 'Red Hat Display', 'Segoe UI'; }}
        QMainWindow {{ background: {colors['BG_APP']}; }}
        QFrame#header {{ background: {colors['BLUE_DEEP']}; }}
        QLabel#brand {{ color: #FFFFFF; font-size: 22px; font-weight: 700; }}
        QLabel#hint {{ color: {colors['TEXT_SOFT']}; }}
        QFrame#mediaPanel {{ background: {colors['BG_PANEL']};
            border: 1px solid {colors['BORDER']}; border-radius: 8px; }}
        QPushButton {{ min-height: 34px; padding: 0 14px; border: 0;
            border-radius: 4px; background: {colors['BLUE_DEEP']}; color: #FFFFFF; }}
        QPushButton:hover {{ background: {colors['TURQUOISE']}; color: #17191F; }}
        QPushButton#purgeButton {{ background: {colors['CORAL']}; }}
        QPushButton#keepButton {{ background: {colors['TURQUOISE']}; color: #17191F; }}
        QProgressBar {{ border: 0; background: {colors['BORDER']}; height: 6px; }}
        QProgressBar::chunk {{ background: {colors['TURQUOISE']}; }}
    """