from dataclasses import dataclass
from pathlib import Path
from .utils import QUALITIES, FORMATS, normalize_url


@dataclass(frozen=True)
class DownloadConfig:
    url: str
    folder: str
    quality: str = "Best Available"
    media_format: str = "MP4 Video"

    def options(self, ffmpeg: str) -> dict:
        normalize_url(self.url)
        if self.quality not in QUALITIES or self.media_format not in FORMATS:
            raise ValueError("Unsupported quality or format.")
        if not self.folder.strip() or not Path(self.folder).is_dir():
            raise ValueError("Choose an existing output folder.")
        if not ffmpeg:
            raise ValueError("FFmpeg and ffprobe are required. See README installation instructions.")
        options = {
            "noplaylist": True, "ffmpeg_location": ffmpeg,
            "outtmpl": str(Path(self.folder) / "%(title).150B [%(id)s].%(ext)s"),
            "windowsfilenames": True, "overwrites": False,
            "continuedl": True, "socket_timeout": 20, "retries": 3,
            "fragment_retries": 3, "concurrent_fragment_downloads": 1,
        }
        if self.media_format == "MP3 Audio":
            options.update(format="bestaudio/best", postprocessors=[{
                "key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}])
        else:
            cap = "" if self.quality == "Best Available" else f"[height<={self.quality[:-1]}]"
            options.update(format=f"bestvideo[ext=mp4]{cap}+bestaudio[ext=m4a]/best[ext=mp4]{cap}",
                           merge_output_format="mp4")
        return options
