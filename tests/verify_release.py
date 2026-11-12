"""Explicit artifact checks. Optional --url must identify media you may download."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, default=Path("dist/StreamSave.exe"))
    parser.add_argument("--url", help="Optional permitted YouTube URL for MP4/MP3 download checks")
    args = parser.parse_args()
    exe = str(args.exe.resolve())
    with tempfile.TemporaryDirectory(prefix="StreamSave verification ") as folder:
        report_path = Path(folder) / "diagnostics.json"
        result = subprocess.run([exe, "--diagnostics", str(report_path)], timeout=90)
        assert result.returncode == 0, f"Diagnostics exited {result.returncode}"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["frozen"] and report["yt_dlp_ffmpeg"] and report["customtkinter_assets"], report
        for tool in report["tools"].values():
            assert Path(tool["path"]).parent == Path(report["resource_root"]) / "vendor", tool
        Path("dist/diagnostics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("PASS: bundled FFmpeg, ffprobe, Deno, yt-dlp discovery, GUI assets", flush=True)
        result = subprocess.run([exe, "--smoke-test"], timeout=90)
        assert result.returncode == 0, f"GUI exited {result.returncode}"
        print("PASS: real packaged GUI startup and automatic close", flush=True)

        def worker(request, timeout=90):
            result = subprocess.run([exe, "--worker"], input=json.dumps(request) + "\n",
                                    capture_output=True, text=True, encoding="utf-8", timeout=timeout)
            events = [json.loads(line) for line in result.stdout.splitlines()]
            return result, events

        result, events = worker({"action": "preview", "url": "invalid"})
        assert result.returncode == 1 and events[-1]["type"] == "error", (result, events)
        print("PASS: packaged windowed worker JSON protocol", flush=True)
        if args.url:
            for media_format in ("MP4 Video", "MP3 Audio"):
                result, events = worker({"action": "download", "url": args.url, "folder": folder,
                                         "quality": "360p", "media_format": media_format}, timeout=240)
                assert result.returncode == 0 and events[-1]["type"] == "success", events
                suffix = ".mp4" if media_format == "MP4 Video" else ".mp3"
                assert any(path.stat().st_size > 0 for path in Path(folder).glob("*" + suffix))
                print(f"PASS: permitted {media_format} download", flush=True)


if __name__ == "__main__":
    main()
