# Media Revisor - Product and Architecture Specification (v0.1)

**Media Revisor** is an offline desktop application for quickly deciding which
multimedia files should be kept or moved to a purge folder.

| Field | Value |
| --- | --- |
| Document | `spec.md` - first implementation slice |
| Date | 2026-07-14 |
| Platforms | Windows and Linux |
| Status | In development |
| Stack | Python 3.11+, PySide6, Qt Multimedia |

## 1. Vision and objective

The application helps one user review a large folder of multimedia files while
viewing or playing each item. A single keyboard decision is enough to keep the
file in place or move it into a timestamped purge folder. The user can undo the
last purge or restore all purges from the current session.

Core capabilities:

- Recursively discover supported multimedia files.
- Preview images and play audio/video with basic controls.
- Classify with the left and right arrow keys.
- Preserve relative paths when moving files to purge.
- Restore file movements without overwriting existing files.
- Provide clear red/green visual feedback and light/dark modes.

### 1.1 Architectural principle

Use a modular local desktop application. The file rules remain independent of
the GUI, while PySide6 coordinates scanning, preview, classification, and
restoration. A CLI engine, service, or web application would add deployment
and orchestration cost without a current multi-user or remote requirement.

```text
User -> PySide6 window -> scanner -> media queue
                    |             |
                    +-> preview  +-> PurgeSession -> local filesystem
                    +-> theme tokens
```

## 2. V1 scope

### 2.1 Included

| ID | Capability | Status |
| --- | --- | --- |
| V1-1 | Recursive scan of images, video, audio, and selected RAW formats | Implemented |
| V1-2 | Image preview and basic Qt audio/video playback | Implemented in UI slice |
| V1-3 | Left arrow purge and right arrow keep actions | Implemented in UI slice |
| V1-4 | `_purge_YYYYMMDD_HHMMSS` session folder with relative paths | Implemented |
| V1-5 | Last-action undo and restore-all session action | Implemented |
| V1-6 | Cox light/dark tokenized theme | Implemented in UI slice |

### 2.2 Excluded

- PDF, text, office-document, and document preview.
- Editing, tagging, batch rules, or cloud synchronization.
- Additional classification folders for up/down keys.
- Persistent session history or a database.
- License activation and machine binding in V1.

## 3. Visual identity

The UI follows the Cox visual identity with Planet Blue (`#283198`), Water
Turquoise (`#2CB8C7`), and Energy Coral (`#ED696A`). Functional colors are
centralized in `media_revisor/theme.py`. Light and dark palettes use the same
token names. Red Hat Display is the intended bundled font with Segoe UI as a
fallback. Purge and keep feedback must remain distinguishable by color and
text, not color alone.

## 4. Application architecture

Pattern A, modular desktop monolith, is selected because one offline user needs
a single executable and the logic is lightweight local filesystem work. Pattern
B is rejected because there are no independent calculation engines. Patterns C
and D are rejected because there is no shared service, collaboration, or remote
access. Pattern E is rejected because the target user needs a GUI.

Proposed structure:

```text
media_revisor/
  media_revisor/
    __main__.py
    main_window.py
    scanner.py
    file_operations.py
    models.py
    theme.py
  tests/
  docs/
  pyproject.toml
```

Scanning runs in a `QThread`. The session history is in memory and contains
source/destination pairs for exact restoration. The selected root and theme
preference may later use `QSettings`; they are not review history.

The project is packaged as a platform-specific PyInstaller executable after
the Qt Multimedia backend is verified on Windows and Linux. Tests include pure
Python unit tests first, followed by offscreen Qt tests and packaged smoke
tests.

## 5. Components

### 5.1 Scanner

`scan_media(root)` returns supported `MediaFile` records in case-insensitive
relative-path order and warning strings for non-fatal filesystem failures. It
skips hidden entries, symbolic links, inaccessible directories, and any
directory beginning with `_purge_`.

### 5.2 Purge session

`PurgeSession` creates a timestamped folder at session start. `purge()` uses a
recorded source and destination, preserves relative directories, and generates
a timestamped name on collision. `undo_last()` and `restore_all()` reverse
successful moves in memory.

### 5.3 GUI and preview

The main window provides folder selection, progress feedback, a preview area,
metadata, keyboard actions, undo controls, restore-all, and theme switching.
Images use `QPixmap`; audio and video use `QMediaPlayer` and
`QVideoWidget`.

## 6. Functional GUI specification

The primary preview occupies most of the window, targeting about 70% of the
available area. The header identifies the app and opens a folder. The footer
shows queue position and current path. Purge produces coral feedback and Keep
produces turquoise feedback; both actions advance the queue.

## 7. Non-functional requirements

| Topic | Requirement |
| --- | --- |
| Performance | Scanning must not block the Qt event loop; local actions should feel immediate. |
| Robustness | Do not overwrite existing files; show actionable filesystem errors. |
| Privacy | Files remain local; no network service is required. |
| Quality | Pure Python tests, offscreen Qt tests, and packaged smoke tests. |
| Language | UI and user guide in English; code and technical docs in English. |
| Identity | Follow the Cox tokens and light/dark rules. |
| Delivery | Comments and public docstrings in English; Markdown passes markdownlint. |
| Numbers | Decimal values display with two decimals and adjacent units; counters are integers. |

External distribution is a known risk because V1 deliberately has no license
activation or machine binding. The licensing template is not active for this
implementation slice.

## 8. Data model

The runtime model contains `MediaFile(path, kind)` and
`MoveRecord(source, destination)`. There is no database. Session history is
discarded when the application closes. The purge folder and moved files remain
on disk until restored or manually removed.

## 9. Roadmap

| Version | Content |
| --- | --- |
| V1.0 | Stabilize preview, keyboard flow, collision handling, restoration, and packaging. |
| V2.0 | Configurable extra destination folders and up/down classifications. |
| V2.1 | PDF/document preview and richer playback controls. |
| V3.0 | Optional persistent projects and an explicit distribution protection decision. |

## 10. Acceptance criteria

1. Selecting a readable root scans nested supported files without blocking the window.
2. Hidden entries, symbolic links, and `_purge_*` directories do not enter the queue.
3. The left arrow moves the current file to the current session purge folder.
4. The right arrow leaves the current file at its original path and advances.
5. A collision never overwrites an existing destination file.
6. Undo restores the most recent purge and makes the original content readable.
7. Restore session returns every successful purge without losing file content.
8. Images render in the preview and audio/video are passed to Qt Multimedia.
9. Light/dark mode changes functional UI tokens without hardcoded panel colors.
10. Invalid roots and filesystem failures produce an actionable status or dialog.

## 11. Risks and open decisions

| Risk or decision | Mitigation or proposal |
| --- | --- |
| Codec availability differs by operating system. | Verify Qt Multimedia backends and document unsupported codecs. |
| A user may distribute the executable externally without protection. | Decide on licensing before a public release; V1 states the limitation clearly. |
| Large restore batches may take time. | Move bulk restoration to a worker if profiling shows UI stalls. |
| RAW preview support varies by Qt. | Keep RAW files classifiable and add a dedicated decoder in the roadmap. |
