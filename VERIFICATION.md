# Verification record

Verified on 2026-11-10 using Windows 11 (build 26200), Python 3.13.7, CustomTkinter 5.2.2, Pillow 12.3.0, yt-dlp 2026.10.26 and PyInstaller 6.22.3.

## Passed

- Nine unittest cases: supported and invalid URL forms, duration formatting, quality caps, MP4 and MP3 settings, invalid configurations, real worker JSON error reporting, duplicate-start prevention, and Windows pipe restoration for a windowed worker.
- Python compilation of the entry point, application modules and tests.
- Imports of GUI, worker, CustomTkinter, Pillow, yt-dlp, EJS and PyInstaller.
- `pip check`: no broken requirements.
- Real CustomTkinter GUI startup and automatic close (`main.py --smoke-test`) with normal desktop permissions. The restricted sandbox could not load Tcl; the same command passed outside that restriction.
- Invoked PyInstaller against the supplied spec and confirmed its explicit missing-FFmpeg guard. This is not a successful EXE build.

## Not verified

FFmpeg, ffprobe and Deno were not installed in this environment. No actual YouTube metadata request, thumbnail retrieval, media download, merge, MP3 conversion, download resume, or cancellation of a real transfer/conversion was verified. No complete EXE bundle was generated or run. Windows 10, Python 3.11/3.12, clean-machine distribution, accessibility and visual review across display scales were not tested.

Before distribution, supply the binaries described in README.md, build the EXE, then test these workflows on Windows 10 and 11. The implementation includes them, but passing unit tests and GUI startup does not establish end-to-end media or packaging compatibility.
