import unittest

from engine import build


class AssetCacheTests(unittest.TestCase):
    def test_asset_version_is_a_short_content_hash(self):
        version = build._asset_version()

        self.assertEqual(12, len(version))
        self.assertTrue(all(char in "0123456789abcdef" for char in version))


if __name__ == "__main__":
    unittest.main()
