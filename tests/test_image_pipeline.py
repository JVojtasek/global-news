import os
import unittest
from pathlib import Path
from unittest import mock

from engine import imagebank, images


class ImagePipelineTests(unittest.TestCase):
    def test_github_pages_caps_remote_image_attempts(self):
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            self.assertEqual(12, images._attempt_limit({"max_per_run": 90}))
            self.assertEqual(6, images._attempt_limit({"max_per_run": 6}))

    @mock.patch("engine.imagebank.time.sleep")
    @mock.patch("engine.imagebank.requests.get")
    def test_rate_limit_does_not_retry_inside_deployment(self, get, sleep):
        get.return_value.status_code = 429
        get.return_value.content = b""

        result = imagebank.download(
            {"url": "https://example.com/rate-limited.jpg"},
            Path("unused.jpg"),
        )

        self.assertFalse(result)
        get.assert_called_once()
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
