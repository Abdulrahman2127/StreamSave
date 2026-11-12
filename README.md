# StreamSave

A modern YouTube downloader for Windows 10 and Windows 11, built with Python 3.11+, CustomTkinter, yt-dlp and FFmpeg. No API keys, advertisements, analytics or account login.

## Features

- Dark, resizable interface with video title, thumbnail and duration preview.
- MP4 video at 360p, 480p, 720p, 1080p or the best available MP4 quality.
- MP3 audio extraction at 192 kbps.
- Output folder picker, transfer percentage, speed, ETA and in-app notifications.
- Background worker with a reader thread; all widget updates run on Tkinter's main thread.
- Cancel metadata retrieval, downloads and FFmpeg processing. Closing the app stops its active worker tree.
- Single video downloads only. Playlist and tracking parameters are removed.
- Existing files are not overwritten; partial downloads can resume.

Download only videos you own or have permission to save. This application does not supply cookies, bypass authentication, defeat DRM, or circumvent access controls. Unavailable, restricted and private videos may fail normally.

## Install and run (PowerShell)

Install 64-bit Python 3.11 or newer from [python.org](https://www.python.org/downloads/windows/), including Tcl/Tk support. From this project folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py
```

Activation is optional; these commands work without changing PowerShell's execution policy.

### FFmpeg (required for downloads)

Get a Windows build using the links on the [official FFmpeg download page](https://ffmpeg.org/download.html). Extract the archive. Either copy **both** `ffmpeg.exe` and `ffprobe.exe` into this project's `vendor` folder, or add the directory containing both programs to your user `PATH` and restart the app.

```text
vendor/
  ffmpeg.exe
  ffprobe.exe
```

Use a self-contained/static build matching your target architecture. If using a shared build, its required DLLs must also be deployed; the supplied packaging configuration expects standalone executables. Do not install a Python package named ffmpeg as a substitute for the binaries.

### YouTube JavaScript runtime

Current yt-dlp needs an external JavaScript runtime for full YouTube support; the `yt-dlp[default]` dependency installs its EJS scripts, but does not install the runtime. Install [Deno](https://docs.deno.com/runtime/getting_started/installation/) and ensure `deno --version` works in a new terminal. Alternatively, place `deno.exe` in `vendor`; the app detects it and the build bundles it automatically. Without a runtime, some videos or formats can be unavailable. No remote component downloads are enabled by the app.

## Use

1. Paste a YouTube watch, Shorts, live-video archive or youtu.be URL.
2. Click **Preview** to fetch the title, artwork and duration. Preview is optional before downloading.
3. Choose **MP4 Video** and a quality, or **MP3 Audio**. The quality menu is disabled for audio.
4. Select an existing writable folder and click **Download**.
5. Use **Cancel** to stop the active operation. Files already downloaded and partial files are retained.

A video quality is an upper bound: when that resolution is unavailable, yt-dlp selects the best available MP4 stream below it. MP4-compatible sources are preferred for predictable merging without slow video transcoding. If no suitable MP4 source exists, the app reports a format error. Best Available means best available **MP4**, and may exceed 1080p. Audio uses the best available audio source before conversion.

Progress describes the current stream, so it can restart when switching from video to audio. Estimated sizes and ETA can change. Merging/conversion has a separate status and no invented percentage. Live broadcasts are rejected; completed archives are supported when YouTube makes them available.

## Build a standalone Windows application

Build on Windows with Python and FFmpeg binaries matching the target architecture. Put `ffmpeg.exe` and `ffprobe.exe` in `vendor` even if they are on PATH. For self-contained YouTube runtime support, also put `deno.exe` there.

```powershell
.\.venv\Scripts\python -m pip install -r requirements-build.txt
.\.venv\Scripts\python -m PyInstaller --noconfirm --clean StreamSave.spec
.\dist\StreamSave\StreamSave.exe
```

Distribute the **entire `dist\StreamSave` folder**, for example as a ZIP. It contains the EXE, Python runtime, CustomTkinter theme/font assets, yt-dlp extractors/EJS scripts, and FFmpeg tools. End users do not need Python installed. The spec intentionally uses a directory bundle to simplify asset loading and diagnostics. Missing FFmpeg binaries cause an explicit build failure. A Deno installation on PATH remains necessary if it was not bundled.

Before release, test on clean Windows 10 and 11 machines, with non-ASCII paths and an account without administrator privileges. Validate actual MP4 merging, MP3 extraction, cancellation during transfer and conversion, network failures, and runtime discovery. Unsigned executables can trigger Windows SmartScreen; signing is a separate release step. Review and include the licenses and notices required by Python, dependencies, your FFmpeg build and Deno when redistributing them.

## Development and verification

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python -m compileall -q main.py downloader tests
.\.venv\Scripts\python -m pip check
.\.venv\Scripts\python main.py --smoke-test
```

The smoke test creates the real GUI and closes it automatically; it requires an interactive desktop. Unit tests do not access YouTube. See `VERIFICATION.md` for what was actually checked in the implementation environment.

```text
main.py                 GUI entry point and isolated worker dispatch
StreamSave.spec         Windows PyInstaller bundle configuration
downloader/
  gui.py                CustomTkinter view and main-thread event handling
  manager.py            Process lifecycle and background event reader
  worker.py             Metadata, thumbnail, download and conversion work
  config.py             Validated yt-dlp download settings
  utils.py              URL validation, tool discovery and formatting
tests/                  Standard-library unittest suite
vendor/                 Local FFmpeg and optional Deno binaries (not committed)
```

## Troubleshooting

- **FFmpeg not found:** ensure both tools are in `vendor`, or in the same directory on PATH. Restart after changing PATH.
- **Network / unavailable / sign-in error:** check your connection and whether the video is publicly accessible. Restricted content is not bypassed.
- **YouTube extractor / JavaScript error:** check Deno, then update yt-dlp with `.\.venv\Scripts\python -m pip install --upgrade "yt-dlp[default]"`. Rebuild the EXE to incorporate updates. YouTube changes can require a newer extractor.
- **Format unavailable:** try Best Available, another lower resolution, or MP3. Not all videos offer every format.
- **Permission denied:** choose a folder you can write to and ensure the output file is not open in another application.
- **Cancelled download:** retry the same video, format and folder to reuse partial data. Delete unwanted `.part`, fragment and `.ytdl` files manually when no operation is running.

The API and packaging approach follow the [yt-dlp embedding documentation](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp) and [CustomTkinter packaging documentation](https://customtkinter.tomschimansky.com/documentation/packaging/).
