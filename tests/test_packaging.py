"""Exercise resource discovery without depending on a developer's installed tools."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from downloader.utils import ffmpeg_directory, javascript_runtimes


class BundledToolTests(unittest.TestCase):
    def test_extracted_tools_take_priority_over_path(self):
        with tempfile.TemporaryDirectory() as directory:
            vendor = Path(directory) / "vendor"
            vendor.mkdir()
            suffix = ".exe" if sys.platform == "win32" else ""
            for name in ("ffmpeg", "ffprobe", "deno"):
                (vendor / (name + suffix)).touch()
            with patch.object(sys, "_MEIPASS", directory, create=True), patch("shutil.which") as which:
                self.assertEqual(ffmpeg_directory(), str(vendor))
                self.assertEqual(javascript_runtimes()["deno"]["path"], str(vendor / ("deno" + suffix)))
                which.assert_not_called()

    def test_incomplete_pair_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            vendor = Path(directory) / "vendor"
            vendor.mkdir()
            (vendor / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")).touch()
            with patch.object(sys, "_MEIPASS", directory, create=True), patch.object(sys, "executable", str(Path(directory) / "app.exe")), patch("shutil.which", return_value=None):
                self.assertIsNone(ffmpeg_directory())
