"""Build on Windows with matching-architecture FFmpeg binaries in vendor/."""
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

root = Path(SPECPATH)
binaries = []
for name in ("ffmpeg.exe", "ffprobe.exe"):
    path = root / "vendor" / name
    if not path.is_file():
        raise SystemExit(f"Missing {path}. See README: install FFmpeg before building.")
    binaries.append((str(path), "vendor"))
if (root / "vendor" / "deno.exe").is_file():
    binaries.append((str(root / "vendor" / "deno.exe"), "vendor"))
datas, extra_binaries, hiddenimports = [], [], []
for package in ("customtkinter", "yt_dlp", "yt_dlp_ejs"):
    data, binary, hidden = collect_all(package)
    datas += data
    extra_binaries += binary
    hiddenimports += hidden
analysis = Analysis([str(root / "main.py")], pathex=[str(root)],
                    binaries=binaries + extra_binaries, datas=datas,
                    hiddenimports=hiddenimports, excludes=[], noarchive=False)
pyz = PYZ(analysis.pure)
exe = EXE(pyz, analysis.scripts, [], exclude_binaries=True, name="StreamSave",
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False, console=False)
coll = COLLECT(exe, analysis.binaries, analysis.datas, strip=False, upx=False, name="StreamSave")
