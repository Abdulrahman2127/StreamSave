from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import re
import shutil
import sys

QUALITIES = ("360p", "480p", "720p", "1080p", "Best Available")
FORMATS = ("MP4 Video", "MP3 Audio")


def normalize_url(value: str) -> str:
    """Accept single YouTube video URLs and discard playlist/tracking arguments."""
    try:
        url = urlsplit(value.strip())
        if url.scheme not in ("http", "https") or url.username or url.password or url.port:
            raise ValueError
        host = (url.hostname or "").lower()
        parts = url.path.strip("/").split("/")
        if host == "youtu.be" and len(parts) == 1:
            video_id = parts[0]
        elif host in ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"):
            if url.path == "/watch":
                video_id = parse_qs(url.query).get("v", [""])[0]
            elif len(parts) == 2 and parts[0] in ("shorts", "embed", "live"):
                video_id = parts[1]
            else:
                raise ValueError
        else:
            raise ValueError
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise ValueError
        return f"https://www.youtube.com/watch?v={video_id}"
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Enter a valid YouTube video URL (watch, Shorts, or youtu.be).") from None


def ffmpeg_directory() -> str | None:
    roots = [Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)) / "vendor",
             Path(sys.executable).parent / "vendor"]
    suffix = ".exe" if sys.platform == "win32" else ""
    for root in roots:
        if all((root / (name + suffix)).is_file() for name in ("ffmpeg", "ffprobe")):
            return str(root)
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if ffmpeg and ffprobe and Path(ffmpeg).parent == Path(ffprobe).parent:
        return str(Path(ffmpeg).parent)
    return None


def duration_text(seconds) -> str:
    if seconds is None:
        return "Unknown duration"
    seconds = max(0, int(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"


def javascript_runtimes() -> dict:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    bundled = root / "vendor" / ("deno.exe" if sys.platform == "win32" else "deno")
    return {"deno": {"path": str(bundled)}} if bundled.is_file() else {"deno": {}}
