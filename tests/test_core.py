import tempfile
import unittest
from downloader.config import DownloadConfig
from downloader.utils import normalize_url, duration_text


class URLTests(unittest.TestCase):
    def test_supported_links(self):
        for url in ("https://youtu.be/dQw4w9WgXcQ?t=10", "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=abc", "https://m.youtube.com/shorts/dQw4w9WgXcQ", "https://youtube.com/live/dQw4w9WgXcQ"):
            with self.subTest(url=url):
                self.assertEqual(normalize_url(url), "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_invalid_links(self):
        for url in ("", "hello", "ftp://youtu.be/dQw4w9WgXcQ", "https://youtube.com.evil.org/watch?v=dQw4w9WgXcQ", "https://youtube.com@evil.org/watch?v=dQw4w9WgXcQ", "https://youtube.com/playlist?list=abc", "https://youtu.be/short", "https://youtu.be/dQw4w9WgXcQ/extra", "https://youtu.be:8080/dQw4w9WgXcQ", "https://youtu.be:bad/dQw4w9WgXcQ"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                normalize_url(url)

    def test_duration(self):
        self.assertEqual(duration_text(3661), "1:01:01")
        self.assertEqual(duration_text(None), "Unknown duration")


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def options(self, quality="720p", media_format="MP4 Video"):
        return DownloadConfig("https://youtu.be/dQw4w9WgXcQ", self.temp.name, quality, media_format).options("ffmpeg-bin")

    def test_video_cap_and_container(self):
        for quality in ("360p", "480p", "720p", "1080p"):
            options = self.options(quality)
            self.assertIn(f"[height<={quality[:-1]}]", options["format"])
            self.assertIn("[ext=mp4]", options["format"])
            self.assertEqual(options["merge_output_format"], "mp4")
            self.assertFalse(options["overwrites"])
            self.assertTrue(options["noplaylist"])

    def test_best_and_audio(self):
        self.assertNotIn("height", self.options("Best Available")["format"])
        options = self.options(media_format="MP3 Audio")
        self.assertEqual(options["postprocessors"][0]["preferredcodec"], "mp3")
        self.assertEqual(options["format"], "bestaudio/best")

    def test_reject_invalid_configuration(self):
        for quality, media_format in (("4K", "MP4 Video"), ("720p", "WAV")):
            with self.assertRaises(ValueError):
                self.options(quality, media_format)
        with self.assertRaises(ValueError):
            DownloadConfig("https://youtu.be/dQw4w9WgXcQ", "").options("bin")
        with self.assertRaises(ValueError):
            DownloadConfig("https://youtu.be/dQw4w9WgXcQ", self.temp.name).options(None)


if __name__ == "__main__":
    unittest.main()

