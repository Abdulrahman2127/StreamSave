"""Offline release diagnostics; no GUI or network access required."""
import json
from pathlib import Path
import subprocess
import sys

from .utils import ffmpeg_directory, javascript_runtimes


def write_report(destination):
    from yt_dlp.postprocessor.ffmpeg import FFmpegPostProcessor

    directory = ffmpeg_directory()
    if not directory:
        raise RuntimeError("FFmpeg and ffprobe were not found.")
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    tools = {name: Path(directory) / (name + ".exe" if sys.platform == "win32" else name)
             for name in ("ffmpeg", "ffprobe")}
    tools["deno"] = Path(javascript_runtimes()["deno"].get("path", "deno"))
    versions = {}
    for name, path in tools.items():
        result = subprocess.run([str(path), "--version" if name == "deno" else "-version"],
                                capture_output=True, text=True, timeout=30, check=True,
                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        versions[name] = {"path": str(path), "version": result.stdout.splitlines()[0]}
    import yt_dlp
    with yt_dlp.YoutubeDL({"ffmpeg_location": directory, "quiet": True}) as ydl:
        processor = FFmpegPostProcessor(ydl)
        if not processor.available or not processor.probe_available:
            raise RuntimeError("yt-dlp could not use FFmpeg and ffprobe.")
    report = {"version": "1.0.0", "frozen": bool(getattr(sys, "frozen", False)),
              "resource_root": str(root), "tools": versions, "yt_dlp_ffmpeg": True,
              "customtkinter_assets": (root / "customtkinter" / "assets").is_dir()}
    Path(destination).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0
