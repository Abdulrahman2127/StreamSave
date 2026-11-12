"""Real worker protocol checks; no network requests are made."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from downloader.manager import DownloadManager


class WorkerTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows redirected handles")
    def test_windowed_worker_stream_restoration(self):
        script = (
            "import sys, main; sys.stdin = None; sys.stdout = None; sys.stderr = None; "
            "sys.argv = ['main.py', '--worker']; raise SystemExit(main.main())"
        )
        result = subprocess.run([sys.executable, "-c", script],
                                cwd=Path(__file__).resolve().parents[1],
                                input=json.dumps({"action": "preview", "url": "invalid"}) + "\n",
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["type"], "error")

    def test_invalid_url_returns_structured_error(self):
        result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / "main.py"), "--worker"],
                                input=json.dumps({"action": "preview", "url": "invalid"}) + "\n",
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["type"], "error")

    def test_manager_rejects_duplicate_and_delivers_idle(self):
        manager = DownloadManager()
        self.assertTrue(manager.start({"action": "preview", "url": "invalid"}))
        self.assertFalse(manager.start({"action": "preview", "url": "invalid"}))
        events = []
        while not events or events[-1]["type"] != "idle":
            events.append(manager.events.get(timeout=20))
        self.assertEqual(events[0]["type"], "error")
        self.assertFalse(events[-1]["cancelled"])
        self.assertIsNotNone(manager.process.poll())


if __name__ == "__main__":
    unittest.main()
