"""Standalone Windows bundle; build.ps1 performs discovery and validation."""
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

root = Path(SPECPATH)
binaries, datas, hiddenimports = [], [], []
for name in ("ffmpeg.exe", "ffprobe.exe", "deno.exe"):
    tool = root / "vendor" / name
    if not tool.is_file():
        raise SystemExit(f"Missing {tool}. Run build.ps1; see README.md.")
    binaries.append((str(tool), "vendor"))
for package in ("customtkinter", "yt_dlp", "yt_dlp_ejs"):
    data, binary, hidden = collect_all(package)
    datas += data
    binaries += binary
    hiddenimports += hidden
notices = root / "vendor" / "licenses"
if not notices.is_dir():
    raise SystemExit("Missing vendor/licenses. Supply redistribution notices before building.")
datas.append((str(notices), "vendor/licenses"))
a = Analysis([str(root / "main.py")], pathex=[str(root)], binaries=binaries,
             datas=datas, hiddenimports=hiddenimports, excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="StreamSave",
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, version=str(root / "packaging" / "version_info.txt"))
