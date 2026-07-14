# Media Revisor Technical Guide

## Architecture

The application uses a modular desktop architecture built with Python and
PySide6. The GUI coordinates the domain services directly; there is no server,
database, CLI engine, or network dependency.

```text
QMainWindow
    |
    +-- ScanWorker -> scanner.scan_media -> MediaFile queue
    |
    +-- preview/player -> current MediaFile
    |
    +-- classification action -> PurgeSession -> MoveRecord history
    |
    +-- theme tokens -> Qt palette and stylesheet
```

## Modules

| Module | Responsibility |
| --- | --- |
| `models.py` | Immutable media and move records. |
| `scanner.py` | Recursive extension filtering and non-fatal warnings. |
| `file_operations.py` | Timestamped purge folders, collision handling, and restoration. |
| `theme.py` | Cox color tokens, palettes, and Qt stylesheet rules. |
| `main_window.py` | User interface, worker lifecycle, preview, and commands. |
| `__main__.py` | Qt application startup. |

## File operation contract

`scan_media(root)` returns `(list[MediaFile], list[str])`. It rejects a root
that is not a directory. Hidden entries, symbolic links, unsupported files,
and `_purge_*` directories are excluded.

`PurgeSession.purge(path)` records the original absolute path and the actual
destination. The destination preserves the path relative to the review root.
If it already exists, a timestamped suffix is generated. Restoration uses the
record rather than reconstructing a path from a filename.

## Concurrency

Folder scanning runs in a `QThread` through `ScanWorker`, so directory walking
does not block the event loop. File moves are short local filesystem actions
and currently run on the GUI thread. A future implementation should move bulk
restoration to a worker if large sessions show measurable UI stalls.

## Theme and UI

`theme.py` is the single source for functional colors. Components use the
active palette and stylesheet rather than individual color literals. The
interface has light and dark modes, with Cox Planet Blue, Water Turquoise, and
Energy Coral as invariant brand colors.

## Testing

The current unit tests cover supported-file filtering, purge-directory
exclusion, relative-path preservation, restoration, and collision safety:

```text
python -m pytest -q
```

The next test layer should use an offscreen Qt platform to cover keyboard
actions, scan-worker signals, preview transitions, and theme changes.

## Packaging

The project is configured as a Python package and exposes the
`media-revisor` console entry point. A platform-specific PyInstaller
configuration is intentionally deferred until the first GUI review confirms
the multimedia backend requirements on Windows and Linux.