import base64
from io import BytesIO
from pathlib import Path
from queue import Empty
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image
from .manager import DownloadManager
from .utils import QUALITIES, FORMATS, normalize_url, duration_text, ffmpeg_directory


class Application(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title("StreamSave • YouTube Downloader")
        self.geometry("900x780")
        self.minsize(740, 700)
        self.configure(fg_color="#10141c")
        self.manager = DownloadManager()
        self.closing = False
        self.preview_url = None
        self.photo = None
        self.url = tk.StringVar()
        default = Path.home() / "Downloads"
        self.folder = tk.StringVar(value=str(default if default.is_dir() else Path.home()))
        self.quality = tk.StringVar(value="Best Available")
        self.media_format = tk.StringVar(value=FORMATS[0])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        body.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(body, text="StreamSave", font=ctk.CTkFont(size=30, weight="bold"), anchor="w").grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(body, text="Your videos. Ready when you are.", text_color="#99a8bd", anchor="w").grid(row=1, column=0, sticky="ew", pady=(0, 22))
        link = self.card(body, 2)
        self.label(link, "01   VIDEO LINK", 0)
        line = ctk.CTkFrame(link, fg_color="transparent")
        line.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        line.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(line, textvariable=self.url, placeholder_text="https://www.youtube.com/watch?v=…", height=42)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.paste = ctk.CTkButton(line, text="Paste", width=74, height=42, command=self.paste_url)
        self.paste.grid(row=0, column=1, padx=(0, 8))
        self.preview_button = ctk.CTkButton(line, text="Preview", width=90, height=42, command=self.preview)
        self.preview_button.grid(row=0, column=2)
        self.entry.bind("<Return>", lambda event: self.preview())
        preview = self.card(body, 3)
        preview.grid_columnconfigure(1, weight=1)
        self.thumbnail = ctk.CTkLabel(preview, text="VIDEO PREVIEW", width=190, height=108, fg_color="#111824", corner_radius=8, text_color="#71829b")
        self.thumbnail.grid(row=0, column=0, rowspan=2, padx=18, pady=18)
        self.video_title = ctk.CTkLabel(preview, text="Add a video to get started", font=ctk.CTkFont(size=17, weight="bold"), anchor="w", justify="left", wraplength=390)
        self.video_title.grid(row=0, column=1, sticky="sew", padx=(0, 18), pady=(18, 4))
        self.duration = ctk.CTkLabel(preview, text="Title, thumbnail and duration appear here", text_color="#99a8bd", anchor="w")
        self.duration.grid(row=1, column=1, sticky="new", padx=(0, 18), pady=(0, 18))
        settings = self.card(body, 4)
        self.label(settings, "02   DOWNLOAD OPTIONS", 0)
        options = ctk.CTkFrame(settings, fg_color="transparent")
        options.grid(row=1, column=0, sticky="ew", padx=18)
        options.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(options, text="Format", anchor="w").grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(options, text="Video quality", anchor="w").grid(row=0, column=1, sticky="ew", padx=(14, 0))
        self.format_menu = ctk.CTkOptionMenu(options, values=list(FORMATS), variable=self.media_format, command=self.format_changed, height=38)
        self.format_menu.grid(row=1, column=0, sticky="ew")
        self.quality_menu = ctk.CTkOptionMenu(options, values=list(QUALITIES), variable=self.quality, height=38)
        self.quality_menu.grid(row=1, column=1, sticky="ew", padx=(14, 0))
        ctk.CTkLabel(settings, text="Save to", anchor="w").grid(row=2, column=0, sticky="ew", padx=18, pady=(12, 0))
        destination = ctk.CTkFrame(settings, fg_color="transparent")
        destination.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))
        destination.grid_columnconfigure(0, weight=1)
        self.folder_entry = ctk.CTkEntry(destination, textvariable=self.folder, height=38)
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.browse = ctk.CTkButton(destination, text="Browse…", width=100, height=38, command=self.choose_folder)
        self.browse.grid(row=0, column=1)
        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.grid(row=5, column=0, sticky="ew", pady=(12, 12))
        actions.grid_columnconfigure(0, weight=1)
        self.download = ctk.CTkButton(actions, text="Download", height=46, font=ctk.CTkFont(size=16, weight="bold"), command=self.start_download)
        self.download.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.cancel = ctk.CTkButton(actions, text="Cancel", height=46, width=100, fg_color="#354155", hover_color="#46546a", state="disabled", command=self.cancel_download)
        self.cancel.grid(row=0, column=1)
        self.progress = ctk.CTkProgressBar(body, height=8)
        self.progress.grid(row=6, column=0, sticky="ew")
        self.progress.set(0)
        self.stats = ctk.CTkLabel(body, text="0%   •   Ready", anchor="w", text_color="#99a8bd")
        self.stats.grid(row=7, column=0, sticky="ew", pady=(4, 0))
        self.notice = ctk.CTkLabel(body, text="Paste a YouTube link, choose your options, then download.", anchor="w", justify="left", wraplength=740)
        self.notice.grid(row=8, column=0, sticky="ew", pady=(8, 0))
        ctk.CTkLabel(body, text="Download only content you own or have permission to save.", text_color="#71829b", anchor="w").grid(row=9, column=0, sticky="ew", pady=(14, 0))
        if not ffmpeg_directory():
            self.notify("FFmpeg / ffprobe not found. Install them or add them to vendor (see README).", error=True)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(100, self.poll)

    @staticmethod
    def card(parent, row):
        frame = ctk.CTkFrame(parent, fg_color="#1b2330", corner_radius=12)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        frame.grid_columnconfigure(0, weight=1)
        return frame

    @staticmethod
    def label(parent, text, row):
        ctk.CTkLabel(parent, text=text, anchor="w", text_color="#a5b6cf", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="ew", padx=18, pady=(12, 8))

    def notify(self, text, error=False):
        self.notice.configure(text=text, text_color="#ff9393" if error else "#8ddcc4")

    def paste_url(self):
        try:
            self.url.set(self.clipboard_get().strip())
        except tk.TclError:
            self.notify("The clipboard does not contain text.", error=True)

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder.get() if Path(self.folder.get()).is_dir() else str(Path.home()))
        if folder:
            self.folder.set(folder)

    def format_changed(self, value=None):
        self.quality_menu.configure(state="disabled" if self.manager.busy or self.media_format.get() == "MP3 Audio" else "normal")

    def set_busy(self, busy):
        for widget in (self.entry, self.paste, self.preview_button, self.download, self.format_menu, self.folder_entry, self.browse):
            widget.configure(state="disabled" if busy else "normal")
        self.cancel.configure(state="normal" if busy else "disabled")
        self.format_changed()

    def begin(self, request):
        try:
            if self.manager.start(request):
                self.progress.stop()
                self.progress.set(0)
                self.set_busy(True)
                self.notify("Fetching video information…" if request["action"] == "preview" else "Connecting to YouTube…")
        except (OSError, ValueError) as exc:
            self.notify(str(exc), error=True)

    def preview(self):
        if self.manager.busy:
            return
        try:
            self.preview_url = normalize_url(self.url.get())
        except ValueError as exc:
            self.notify(str(exc), error=True)
            return
        self.video_title.configure(text="Loading video…")
        self.duration.configure(text="")
        self.thumbnail.configure(image=None, text="VIDEO PREVIEW")
        self.begin({"action": "preview", "url": self.preview_url})

    def start_download(self):
        if self.manager.busy:
            return
        try:
            from .config import DownloadConfig
            url = normalize_url(self.url.get())
            config = DownloadConfig(url, self.folder.get().strip(), self.quality.get(), self.media_format.get())
            config.options(ffmpeg_directory())
            # Verify write access without leaving a probe file behind.
            import tempfile
            with tempfile.TemporaryFile(dir=config.folder):
                pass
        except (ValueError, OSError) as exc:
            self.notify(str(exc), error=True)
            return
        self.begin({"action": "download", "url": url, "folder": config.folder,
                    "quality": config.quality, "media_format": config.media_format})

    def cancel_download(self):
        self.manager.cancel()
        self.cancel.configure(state="disabled")
        self.notify("Cancelling…")

    def handle(self, event):
        kind = event["type"]
        if self.manager.cancelled and kind != "idle":
            return
        if kind == "preview":
            self.video_title.configure(text=event["title"])
            self.duration.configure(text=duration_text(event["duration"]))
            if event.get("thumbnail"):
                with Image.open(BytesIO(base64.b64decode(event["thumbnail"]))) as img:
                    self.photo = ctk.CTkImage(light_image=img.copy(), dark_image=img.copy(), size=(190, 107))
                self.thumbnail.configure(image=self.photo, text="")
            self.notify("Video information loaded. Choose your download options.")
        elif kind == "progress":
            self.progress.stop()
            percent = event.get("percent")
            if percent is not None:
                self.progress.set(percent / 100)
            speed = event.get("speed")
            eta = event.get("eta")
            parts = [f"{percent:.0f}%" if percent is not None else "Downloading…"]
            if speed:
                parts.append(f"{speed / 1048576:.2f} MB/s")
            if eta is not None:
                parts.append(f"{duration_text(eta)} remaining")
            self.stats.configure(text="   •   ".join(parts))
            if event.get("status") == "finished":
                self.stats.configure(text="Stream downloaded • Preparing final file…")
        elif kind == "processing":
            self.stats.configure(text=event["message"])
        elif kind == "success":
            self.progress.set(1)
            self.stats.configure(text="100%   •   Complete")
            self.notify(event["message"])
        elif kind == "error":
            self.stats.configure(text="Operation failed")
            self.notify(event["message"], error=True)
        elif kind == "warning":
            self.notify(event["message"], error=True)
        elif kind == "idle":
            self.manager.busy = False
            self.set_busy(False)
            if event.get("cancelled"):
                self.stats.configure(text="Cancelled")
                self.notify("Cancelled. Partial files are kept so a later download can resume.")
            if self.closing:
                self.destroy()

    def poll(self):
        try:
            for _ in range(150):
                self.handle(self.manager.events.get_nowait())
        except Empty:
            pass
        if self.closing and not self.manager.busy:
            return
        if self.winfo_exists():
            self.after(100, self.poll)

    def close(self):
        if self.manager.busy:
            self.closing = True
            self.cancel_download()
        else:
            self.destroy()
