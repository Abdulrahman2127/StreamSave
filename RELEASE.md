# StreamSave v1.1.0 release procedure

StreamSave v1.1.0 targets Windows x64 and supports YouTube and TikTok, including TikTok short links. The build script produces local release artifacts.

## Build inputs

Install `requirements-build.txt` in a Windows Python 3.11+ environment. It includes the pinned yt-dlp nightly with EJS and curl_cffi for browser impersonation. Provide standalone x64 `ffmpeg.exe`, `ffprobe.exe` and `deno.exe` in `vendor`, on PATH, or through the script's explicit path parameters. The build script uses `StreamSave.spec` to package the staged tools and installed dependencies.

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

Diagnostics executes the bundled FFmpeg, ffprobe and Deno. It checks yt-dlp's FFmpeg discovery and verifies that yt-dlp can use curl_cffi for browser impersonation. The report includes dependency versions and should identify version 1.1.0. Tool paths should be under the temporary `_MEI.../vendor` directory. `customtkinter_assets` should be true. The smoke test opens the GUI briefly and closes it.

Run `.\.venv\Scripts\python tests/verify_release.py` for the packaged checks. Add `--url YOUR_PERMITTED_YOUTUBE_URL` to test YouTube MP4 and MP3 downloads and `--tiktok-url YOUR_PERMITTED_TIKTOK_URL` to test TikTok MP4. Each platform uses a separate temporary output folder.

Run `.\.venv\Scripts\python tests/verify_media.py` for a loopback HTTP download, MP3 conversion, MP4 merge and ffprobe check using synthetic media and binaries extracted from the EXE. This runs yt-dlp in the developer environment. Use the optional platform checks to verify live downloads.

Test on a clean Windows 10/11 x64 machine without Python, FFmpeg or Deno on PATH. Check MP4 merging, MP3 conversion, preview, cancellation, resume, non-ASCII output paths, and normal-user permissions using media you own or have permission to download. See VERIFICATION.md for actual results and limitations. Sign the EXE if desired, then regenerate SHA256SUMS.txt after signing.

## Manual GitHub Releases upload

1. Review the source changes and verification limitations. Commit the intended source changes yourself. Push only after approving that action; the assistant has not pushed anything.
2. In the existing GitHub repository, open **Releases > Draft a new release**.
3. Select or create tag **v1.1.0** on the reviewed commit and title the release **StreamSave v1.1.0**.
4. Attach `dist/StreamSave.exe`, `dist/SHA256SUMS.txt`, `dist/THIRD-PARTY-NOTICES.zip`, and any required corresponding-source/build archives. Optionally attach `dist/build-environment.txt` for reproducibility. Diagnostics contains local paths and is for local verification.
5. Describe Windows x64 support, portable operation, bundled tools, the unsigned status, and any remaining validation limits from VERIFICATION.md. Review all assets and the checksum, then publish manually when ready.

Suggested description

> StreamSave v1.1.0 downloads YouTube and TikTok videos on Windows x64. Download `StreamSave.exe` from Assets and verify it using `SHA256SUMS.txt`. The executable includes Python, FFmpeg, and Deno. Download only media you own or have permission to save.
