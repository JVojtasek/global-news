"""Public, non-transactional AI radar pilot and its dated sample issue."""
from __future__ import annotations

import json
from urllib.parse import quote, urlencode

import markdown
import yaml

from . import config


def load() -> dict:
    path = config.DATA / "radar.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def pages(env, common: dict, site: dict) -> dict[str, str]:
    """Production and preview share a renderer. An enquiry is not consent.

    No form provider or payment URL is accepted in this pre-launch phase.
    """
    cfg = load()
    if not cfg.get("enabled"):
        return {}
    lang = common["lang"]
    copy = cfg[lang]
    base = common.get("base", "")
    origin = common.get("site_url", site["brand"]["url"]).rstrip("/")
    email_url = "mailto:" + cfg["contact_email"] + "?" + urlencode({
        "subject": copy["email_subject"], "body": copy["email_body"],
    }, quote_via=quote)
    sample = (config.DATA / "radar" / f"sample.{lang}.md").read_text(encoding="utf-8")
    result = {}
    for is_sample, path in ((False, "ai-radar/"), (True, "ai-radar/sample/")):
        title = copy["sample_title"] if is_sample else copy["name"]
        description = copy["sample_description"] if is_sample else copy["description"]
        canonical = f"{origin}{base}/{lang}/{path}"
        structured = {
            "@context": "https://schema.org", "@type": "WebPage",
            "name": title, "description": description, "url": canonical,
            "inLanguage": lang,
        }
        if is_sample:
            structured["datePublished"] = str(cfg["sample_date"])
        context = {
            **common, "page_type": "ai-radar-sample" if is_sample else "ai-radar",
            "canonical": canonical, "alt_path": path,
            "alt_langs": ["en", "cs"], "noindex": False,
            "page_jsonld": json.dumps(structured, ensure_ascii=False).replace("<", "\\u003c"),
            "newsletter": {"enabled": False},
            "radar": cfg, "r": copy, "is_sample": is_sample,
            "radar_email_url": email_url,
            "sample_html": markdown.markdown(sample, extensions=["extra", "sane_lists"]),
        }
        result[f"{lang}/{path}index.html"] = env.get_template("radar.html").render(**context)
    return result
