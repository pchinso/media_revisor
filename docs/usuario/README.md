# Media Revisor User Guide

## Start the application

Install Python 3.11 or newer and the application dependencies, then run:

```text
python -m media_revisor
```

The application works locally on Windows and Linux. It does not upload files.

## Review a folder

1. Select **Open folder**.
2. Choose the root folder that contains the files to review.
3. Wait for the scan to finish.
4. Review the displayed file.
5. Press the left arrow to purge it or the right arrow to keep it.

Media Revisor scans subfolders, ignores hidden entries and symbolic links, and
skips folders whose name starts with `_purge_`.

## Purge and restore

At the beginning of a session, the application creates a folder named
`_purge_YYYYMMDD_HHMMSS` in the selected root. Purged files keep their
relative folder structure. The application never overwrites an existing file;
it creates a timestamped alternative name when necessary.

Use **Undo last** to restore the most recent purged file. Use **Restore
session** to restore every purged file from the current session.

## Preview

Images are fitted into the preview area. Video and audio files use the basic
Qt media player. Advanced playback, editing, and document preview are not part
of this version.

## Common problems

| Problem | Action |
| --- | --- |
| No files appear | Check the extension and confirm the folder is readable. |
| A file cannot be purged | Close other applications using it and check permissions. |
| A file cannot be restored | Check that the purge folder and its contents still exist. |
| Video or audio does not play | Confirm that the local Qt multimedia backend supports its codec. |

## Support and release scope

This first implementation does not include license activation. It is intended
for local development and review while packaging and external distribution
decisions are completed.