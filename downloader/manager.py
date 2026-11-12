"""A reader thread transports worker events; it never calls Tkinter."""
import json
from pathlib import Path
from queue import Queue
import subprocess
import sys
import threading


class DownloadManager:
    def __init__(self):
        self.events = Queue()
        self.process = None
        self.busy = False
        self.cancelled = False

    def start(self, request):
        if self.busy:
            return False
        command = [sys.executable]
        if not getattr(sys, "frozen", False):
            command.append(str(Path(__file__).resolve().parent.parent / "main.py"))
        command.append("--worker")
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
                                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.close()
        except OSError:
            self.process.kill()
            self.process.wait()
            self.process.stdout.close()
            raise
        self.busy, self.cancelled = True, False
        threading.Thread(target=self._read, args=(self.process,), daemon=True).start()
        return True

    def _read(self, process):
        terminal = False
        for line in process.stdout:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            terminal |= event.get("type") in ("success", "preview", "error")
            self.events.put(event)
        process.stdout.close()
        code = process.wait()
        if not terminal and not self.cancelled:
            self.events.put({"type": "error", "message": f"Worker stopped unexpectedly (exit {code})."})
        self.events.put({"type": "idle", "cancelled": self.cancelled})

    def cancel(self):
        if self.busy and self.process and self.process.poll() is None:
            self.cancelled = True
            threading.Thread(target=self._terminate, daemon=True).start()

    def _terminate(self):
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(self.process.pid), "/T", "/F"],
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            self.process.terminate()
