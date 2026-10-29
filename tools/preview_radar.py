"""Render only the radar pages, without images, article processing or state writes.

Usage: python -m tools.preview_radar --out C:/Users/Admin/AppData/Local/Temp/mypaper-radar
"""
from __future__ import annotations

import argparse
import pathlib
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape

from engine import build, config, interests, members, radar


def environment():
    env = Environment(loader=FileSystemLoader(str(config.TEMPLATES)),
                      autoescape=select_autoescape(["html"]))
    env.filters["metadesc"] = build._meta_desc
    return env


def context(lang: str) -> dict:
    site = config.site()
    return dict(
        lang=lang, brand=site["brand"]["name_cs" if lang == "cs" else "name_en"],
        tagline=site["brand"]["tagline_cs" if lang == "cs" else "tagline_en"],
        t=build.STRINGS[lang], sections=site["sections"], all_sections=site["sections"],
        all_langs=["en", "cs"], site_url=config.origin(), base=config.base_path(),
        current_section=None, asset_version=build._asset_version(), seo=site.get("seo", {}),
        newsletter=site.get("newsletter", {}), wider_lens=site.get("wider_lens", {}),
        interest_groups=interests.catalogue(), partners=[], mem=members.cfg(),
        analytics=site.get("analytics") or {}, brand_email=site["brand"]["email"],
        today_label=build._date_label(lang), og_locale=build.LOCALES[lang],
        og_locales=build.LOCALES, share_image=build._share_image({}, site),
        canonical="", alt_path="", page_type="page", page_jsonld="", noindex=False,
        alt_langs=["en", "cs"], radar=radar.load(),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = pathlib.Path(args.out).resolve()
    # Refuse to mistake the checkout for a preview destination.
    if out == config.ROOT.resolve() or out in config.ROOT.resolve().parents:
        parser.error("The output must be a separate preview directory.")
    out.mkdir(parents=True, exist_ok=True)
    for name in ("style.css", "radar.css", "reader.js", "live.js"):
        shutil.copy2(config.STATIC / name, out / name)
    for lang in ("en", "cs"):
        for path, html in radar.pages(environment(), context(lang), config.site()).items():
            target = out / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            print(target)
    # This sitemap is useful for verifying the production sitemap rules too.
    (out / "sitemap-pages.xml").write_text(
        build._sitemap(out, config.origin() + config.base_path()), encoding="utf-8")


if __name__ == "__main__":
    main()
