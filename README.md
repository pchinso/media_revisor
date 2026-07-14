# Media Revisor

Media Revisor is a local desktop tool for reviewing multimedia files quickly.
The left arrow moves the current file to a timestamped purge folder; the right
arrow keeps it in its original location.

## Current Status

Version 0.1.0 is the first implementation slice. The core scanner and
reversible purge service are tested. The PySide6 interface provides folder
selection, background scanning, image preview, basic audio/video playback,
keyboard classification, theme switching, and session restoration.

## Requirements

- Python 3.11 or newer.
- Windows or Linux.
- PySide6 6.7 or newer.

Install the project and its test dependencies in a virtual environment:

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[test]"
```

On Linux, activate the environment with `source .venv/bin/activate`.

## Run

On Windows, double-click `run_media_revisor.bat` in the project root.

```text
python -m media_revisor
```

Choose a root folder. Media Revisor scans supported files recursively and
creates `_purge_YYYYMMDD_HHMMSS` inside that root for the current session.
The purge directory is excluded from scanning and relative subdirectories are
preserved.

## Supported Formats

The current scanner recognises common images, video, audio, and selected RAW
formats:

- Images: BMP, GIF, JPEG, PNG, TIFF, and WEBP.
- Video: AVI, MKV, MOV, MP4, and WEBM.
- Audio: FLAC, M4A, MP3, OGG, and WAV.
- RAW: ARW, CR2, CR3, DNG, NEF, and RAF.

PDF, text, and office documents are outside the current scope.

## Keyboard Actions

| Key | Action |
| --- | --- |
| Left arrow | Move the current file to the purge directory |
| Right arrow | Keep the current file in its original location |

The buttons provide the same actions. `Undo last` restores the latest purge;
`Restore session` restores all successful purges made during the session.
Existing destination files are never overwritten.

## Development

Run the tests with:

```text
python -m pytest -q
```

Compile-check the package with:

```text
python -m compileall -q media_revisor tests
```

The planned executable packaging uses a platform-specific PyInstaller build.
That build configuration will be added after the first UI review.

## Documentation

- [User guide](docs/usuario/README.md)
- [Technical guide](docs/tecnica/README.md)
- [Product and architecture specification](spec.md)

This V1 does not implement license activation or machine binding. External
distribution should therefore be treated as an explicit release risk.
