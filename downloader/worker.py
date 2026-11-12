"""Isolated yt-dlp worker. Only JSON events are written to stdout."""
import base64
from io import BytesIO
import json
import sys
import time
from urllib.request import urlopen
from PIL import Image
import yt_dlp
from .config import DownloadConfig
from .utils import normalize_url, ffmpeg_directory, javascript_runtimes


def emit(kind, **data):
    print(json.dumps({"type": kind, **data}), flush=True)


class Logger:
    def debug(self, message):
        pass

    def info(self, message):
        pass

    def warning(self, message):
        emit("warning", message=message)

    def error(self, message):
        pass  # yt-dlp also raises the error; report it once below.


def run():
    try:
        request = json.loads(sys.stdin.readline())
        url = normalize_url(request["url"])
        options = {"quiet": True, "no_warnings": False, "logger": Logger(),
                   "noplaylist": True, "socket_timeout": 20, "retries": 3,
                   "js_runtimes": javascript_runtimes()}
        if request["action"] == "preview":
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
            if not info or info.get("is_live"):
                raise ValueError("Live broadcasts are not supported. Try a completed video.")
            thumbnail = None
            try:
                thumbnail_url = info.get("thumbnail", "")
                if thumbnail_url.startswith("https://"):
                    with urlopen(thumbnail_url, timeout=10) as response:
                        raw = response.read(5_000_001)
                    if len(raw) <= 5_000_000:
                        with Image.open(BytesIO(raw)) as img:
                            img.thumbnail((480, 270))
                            buffer = BytesIO()
                            img.convert("RGB").save(buffer, "PNG")
                            thumbnail = base64.b64encode(buffer.getvalue()).decode("ascii")
            except Exception:
                pass  # Metadata remains useful when artwork is unavailable.
            emit("preview", title=info.get("title", "Untitled"), duration=info.get("duration"),
                 thumbnail=thumbnail)
        else:
            config = DownloadConfig(url, request["folder"], request["quality"], request["media_format"])
            options.update(config.options(ffmpeg_directory()))

            last_update = 0.0

            def progress(data):
                nonlocal last_update
                now = time.monotonic()
                if data["status"] == "downloading" and now - last_update < 0.15:
                    return
                last_update = now
                total = data.get("total_bytes") or data.get("total_bytes_estimate")
                emit("progress", status=data["status"],
                     percent=min(100, 100 * data.get("downloaded_bytes", 0) / total) if total else None,
                     speed=data.get("speed"), eta=data.get("eta"))

            def postprocess(data):
                emit("processing", message="Merging / converting media…")

            options.update(progress_hooks=[progress], postprocessor_hooks=[postprocess],
                           match_filter=lambda info, **kwargs: "Live broadcasts are not supported." if info.get("is_live") else None)
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.extract_info(url, download=True)
            emit("success", message="Download complete. Your file is in the output folder.")
    except Exception as exc:
        emit("error", message=str(exc))
        return 1
    return 0
