"""Offline media integration using FFmpeg tools extracted from the release EXE.

Uses synthetic media and a loopback HTTP server; never contacts YouTube.
yt-dlp runs in the build environment, using the release's actual FFmpeg binaries.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import tempfile
import threading

from PyInstaller.archive.readers import CArchiveReader
import yt_dlp
from yt_dlp.postprocessor.ffmpeg import FFmpegMergerPP


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    archive = CArchiveReader("dist/StreamSave.exe")
    with tempfile.TemporaryDirectory(prefix="StreamSave media ") as directory:
        root = Path(directory)
        for name in ("ffmpeg.exe", "ffprobe.exe"):
            entry = next(key for key in archive.toc if key.replace("\\", "/") == "vendor/" + name)
            (root / name).write_bytes(archive.extract(entry))
        ffmpeg = str(root / "ffmpeg.exe")

        def create(*args):
            subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *args],
                           check=True, timeout=30, capture_output=True)

        create("-f", "lavfi", "-i", "color=c=blue:s=128x72:d=1", "-an", "-c:v", "libx264", str(root / "video.mp4"))
        create("-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-c:a", "aac", str(root / "audio.m4a"))
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=directory))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            options = {"quiet": True, "ffmpeg_location": directory,
                       "outtmpl": str(root / "downloaded.%(ext)s"),
                       "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]}
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([f"http://127.0.0.1:{server.server_port}/audio.m4a"])
            assert (root / "downloaded.mp3").stat().st_size > 0
            with yt_dlp.YoutubeDL({"quiet": True, "ffmpeg_location": directory}) as ydl:
                FFmpegMergerPP(ydl).run({"filepath": str(root / "merged.mp4"), "ext": "mp4",
                    "__files_to_merge": [str(root / "video.mp4"), str(root / "audio.m4a")],
                    "requested_formats": [{"vcodec": "h264", "acodec": "none", "protocol": "http"},
                                          {"vcodec": "none", "acodec": "aac", "protocol": "http"}]})
            result = subprocess.run([str(root / "ffprobe.exe"), "-v", "error", "-show_entries", "stream=codec_type",
                                     "-of", "csv=p=0", str(root / "merged.mp4")],
                                    capture_output=True, text=True, check=True, timeout=30)
            assert set(result.stdout.split()) == {"video", "audio"}, result.stdout
            print("PASS: loopback HTTP download, MP3 extraction, MP4 merge and ffprobe using EXE's binaries")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    main()
