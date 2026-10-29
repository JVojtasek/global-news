import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup

from engine import build, config, radar
from tools.preview_radar import context, environment


class RadarTests(unittest.TestCase):
    def setUp(self):
        self.pages = {}
        for lang in ("en", "cs"):
            self.pages.update(radar.pages(environment(), context(lang), config.site()))

    def test_bilingual_routes_metadata_and_sample_date(self):
        self.assertEqual(4, len(self.pages))
        for path, html in self.pages.items():
            soup = BeautifulSoup(html, "html.parser")
            self.assertEqual(1, len(soup.find_all("h1")))
            self.assertEqual("true", soup.body.get("data-skip-onboarding"))
            self.assertLessEqual(len(soup.select("nav.sections a")), 5)
            expected_alt = "/en/ai-radar/sample/" if "/sample/" in path else "/en/ai-radar/"
            self.assertEqual(expected_alt, soup.select_one(".langs a")["href"])
            self.assertEqual(f"{config.origin()}{config.base_path()}/{path[:-10]}",
                             soup.find("link", rel="canonical")["href"])
            self.assertEqual({"en", "cs", "x-default"},
                             {x["hreflang"] for x in soup.select("link[hreflang]")})
            self.assertTrue(soup.find("meta", attrs={"name": "description"})["content"])
            ld = json.loads(soup.find("script", type="application/ld+json").string)
            self.assertNotIn("offers", ld)
            if "/sample/" in path:
                self.assertEqual("2026-10-29", ld["datePublished"])
                self.assertEqual(3, len(soup.select(".radar-sources li a")))

    def test_enquiry_never_claims_to_collect_a_subscription_or_payment(self):
        for path, html in self.pages.items():
            soup = BeautifulSoup(html, "html.parser")
            main = soup.find("main")
            self.assertFalse(main.find("form"))
            self.assertFalse(main.find("input"))
            self.assertIsNone(soup.find(id="newsletter"))
            self.assertIsNone(soup.find(id="nl-thanks"))
            if "/sample/" not in path:
                link = main.select_one("#pilot a.radar-button")["href"]
                parts = urlsplit(link)
                self.assertEqual("mailto", parts.scheme)
                self.assertEqual("hello@mypaper.news", parts.path)
                self.assertTrue(parse_qs(parts.query)["body"])
                self.assertIn("249", main.get_text())
                self.assertIn("1 490", main.get_text())

    def test_no_analytics_without_real_token_and_single_provider_when_enabled(self):
        ctx = context("cs")
        ctx["analytics"] = {}
        html = radar.pages(environment(), ctx, config.site())["cs/ai-radar/index.html"]
        self.assertNotIn("beacon.min.js", html)
        self.assertNotIn("plausible.io/js", html)
        ctx["analytics"] = {"cloudflare_token": "fixture-only", "plausible_domain": "example.test"}
        html = radar.pages(environment(), ctx, config.site())["cs/ai-radar/index.html"]
        soup = BeautifulSoup(html, "html.parser")
        beacon = soup.find("script", src="https://static.cloudflareinsights.com/beacon.min.js")
        self.assertEqual({"token": "fixture-only"}, json.loads(beacon["data-cf-beacon"]))
        self.assertNotIn("plausible.io/js", html)

    def test_routes_enter_the_existing_sitemap(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for path, html in self.pages.items():
                p = out / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(html, encoding="utf-8")
            sitemap = build._sitemap(out, "https://mypaper.news")
            for path in self.pages:
                self.assertIn("https://mypaper.news/" + path[:-10], sitemap)

    def test_disabled_pilot_has_no_pages(self):
        with patch("engine.radar.load", return_value={"enabled": False}):
            self.assertEqual({}, radar.pages(environment(), context("cs"), config.site()))


if __name__ == "__main__":
    unittest.main()
