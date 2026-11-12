# StreamSave v1.0.0 release procedure

Build target: Windows x64, version 1.0.0. The existing GUI and worker architecture are preserved. No release, tag, push, or remote change is performed by build.ps1.

## Build inputs

Install requirements-build.txt in a Windows Python 3.11+ environment. Provide standalone x64 ffmpeg.exe and ffprobe.exe together, and deno.exe. Use `vendor`, PATH, or the script's explicit path parameters. The build does not download or update dependencies automatically.

FFmpeg Windows builds are linked from [FFmpeg](https://ffmpeg.org/download.html); the build used here comes from [Gyan's builds](https://www.gyan.dev/ffmpeg/builds/). Deno binaries come from [Deno releases](https://github.com/denoland/deno/releases). Keep exact versions and provenance for each release.

Place FFmpeg's LICENSE and build README plus Deno's license and applicable third-party notices in `vendor/licenses`. The script also collects installed Python dependency licenses and the Python license. Notices are embedded in the executable; distribute a readable copy alongside it as `THIRD-PARTY-NOTICES.zip`.

Before public upload, satisfy the redistribution terms for the actual binaries, including corresponding source and build information for GPL/LGPL components where required. The supplied Gyan build reports GPL v3 and identifies its FFmpeg source revision in its README; its external libraries also need consideration. Retain and provide the matching source/build materials with the release as required; links to upstream projects alone do not establish that all redistribution obligations have been met. Do not claim a completed license audit from the automated notice collection.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

Outputs are ignored by Git. Never add EXEs, DLLs, archives, credentials, downloaded media, or the local environment to source control. Keep build.ps1, StreamSave.spec, packaging/, requirements files, tests and documentation tracked.

## Validate the artifact

```powershell
$app = Start-Process .\dist\StreamSave.exe -ArgumentList '--smoke-test' -PassThru -Wait
if ($app.ExitCode -ne 0) { throw 'GUI smoke test failed' }
$report = Join-Path $PWD 'dist\diagnostics.json'
$app = Start-Process .\dist\StreamSave.exe -ArgumentList @('--diagnostics', ('"' + $report + '"')) -PassThru -Wait
if ($app.ExitCode -ne 0) { throw 'Bundled tools check failed' }
Get-Content $report
Get-FileHash .\dist\StreamSave.exe -Algorithm SHA256
Compress-Archive -Path .\vendor\licenses\* -DestinationPath .\dist\THIRD-PARTY-NOTICES.zip -Force
```

Diagnostics executes the bundled FFmpeg, ffprobe and Deno, and checks yt-dlp's FFmpeg discovery. Paths in the report should be under the temporary `_MEI.../vendor` directory; that directory is removed when the process exits. `customtkinter_assets` should be true in the packaged report. The smoke test opens the real GUI briefly and closes it.

The repeatable artifact check is `.\.venv\Scripts\python tests/verify_release.py`. Add `--url YOUR_PERMITTED_YOUTUBE_URL` to also attempt real MP4 and MP3 downloads into a temporary folder. This check downloads nothing by default.

Run `.\.venv\Scripts\python tests/verify_media.py` for a loopback HTTP download, MP3 conversion, MP4 merge and ffprobe check using synthetic media and binaries extracted from the EXE. This runs yt-dlp in the developer environment; it complements the packaged-worker checks and does not establish YouTube availability.

Test on a clean Windows 10/11 x64 machine without Python, FFmpeg or Deno on PATH. Check MP4 merging, MP3 conversion, preview, cancellation, resume, non-ASCII output paths, and normal-user permissions using media you own or have permission to download. See VERIFICATION.md for actual results and limitations. Sign the EXE if desired, then regenerate SHA256SUMS.txt after signing.

## Manual GitHub Releases upload

1. Review the source changes and verification limitations. Commit the intended source changes yourself. Push only after approving that action; the assistant has not pushed anything.
2. In the existing GitHub repository, open **Releases > Draft a new release**.
3. Select/create tag **v1.0.0** on the reviewed commit, and title the release **StreamSave v1.0.0**.
4. Attach `dist/StreamSave.exe`, `dist/SHA256SUMS.txt`, `dist/THIRD-PARTY-NOTICES.zip`, and any required corresponding-source/build archives. Optionally attach `dist/build-environment.txt` for reproducibility. Diagnostics contains local paths and is for local verification.
5. Describe Windows x64 support, portable operation, bundled tools, the unsigned status, and any remaining validation limits from VERIFICATION.md. Review all assets and the checksum, then publish manually when ready.

Suggested description: "StreamSave v1.0.0 for Windows x64. Download StreamSave.exe from Assets and run it; no Python, FFmpeg, or Deno installation is needed. Verify it using SHA256SUMS.txt. Download only media you own or have permission to save."
