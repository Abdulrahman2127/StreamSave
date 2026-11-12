# StreamSave v1.0.0 verification

Verified on 2026-11-12, Windows 11 build 26200 x64, Python 3.13.7, CustomTkinter 5.2.2, Pillow 12.3.0, yt-dlp 2026.10.26, yt-dlp-ejs 0.8.0, PyInstaller 6.22.3, FFmpeg/ffprobe 9.0.2 Gyan essentials static build, and Deno 2.9.8.

## Final artifact

- `dist/StreamSave.exe`: 152,552,677 bytes; Windows file/product version 1.0.0; one-file, windowed, unsigned x64 executable.
- SHA-256: `d6089581fceb81d4ac5debfb9318b06bfc72ffaba3b6f8dfd36662ba9c270cc0`.
- `dist/SHA256SUMS.txt`, `dist/build-environment.txt`, `dist/THIRD-PARTY-NOTICES.zip` accompany the executable.
- `dist/diagnostics.json` is a local verification report containing temporary/local paths; it is not intended as a public release asset.

## Passed

- All 11 unittest cases, including existing URL/configuration/worker tests and new bundled-tool priority and incomplete-pair tests.
- Python compilation of the entry point, application, tests, and packaging helper; `pip check` passed.
- Real source GUI startup and close with `main.py --smoke-test` on the normal Windows desktop.
- Successful build through build.ps1 with CustomTkinter assets, yt-dlp/EJS, Python/Tcl/Tk, FFmpeg, ffprobe, Deno and collected dependency notices.
- `tests/verify_release.py` against the final EXE: bundled FFmpeg, ffprobe and Deno executed successfully from `_MEIPASS/vendor`; yt-dlp reported both FFmpeg tools available; CustomTkinter assets present; real packaged GUI opened and closed automatically; windowed worker returned the expected JSON error for invalid input.
- `tests/verify_media.py` against the final EXE: extracted its actual FFmpeg/ffprobe binaries, generated synthetic media, downloaded audio over a loopback HTTP server using installed yt-dlp, converted it to MP3, merged separate video/audio into MP4 with yt-dlp's merger, and verified both merged streams with ffprobe. This exercises real download/postprocessing without third-party media or external network access. It uses the build environment's yt-dlp, rather than the packaged worker, for this integration check.
- Windows file version and generated checksum checked. No executable/DLL, secret-key or environment files are tracked by Git.

The first restricted-environment build omitted Tcl/Tk because its installed files were inaccessible. That artifact was replaced by the successful normal-desktop build. The build script now checks real Tcl/Tk startup before packaging and fails clearly when it is inaccessible.

## Not verified / publication considerations

- Public metadata retrieval for yt-dlp's standard test URL `https://www.youtube.com/watch?v=BaW_jenozKc` returned “This video is unavailable.” No successful external YouTube download, thumbnail fetch, or full GUI-to-YouTube MP4/MP3 workflow was verified. A permitted, accessible test URL is still needed; run `tests/verify_release.py --url URL` for packaged MP4/MP3 download checks.
- Clean Windows 10/11 machines without developer dependencies, non-ASCII user/output paths, display scaling/accessibility, download resume, and cancellation of real transfers/conversions remain untested. The final EXE was tested on this Windows 11 development machine.
- The EXE is unsigned. SmartScreen behavior and code signing were not tested.
- Dependency notices are bundled and supplied separately. Complete any required corresponding-source/build-material distribution for the selected third-party binaries before public upload, as described in RELEASE.md; automated collection is not a license audit.
- No release was published, no Git remote was modified, and no commits or pushes were issued by this work.
