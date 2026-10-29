"""Local-only draft email rendering; no subscriptions or sending are enabled."""
from __future__ import annotations

import datetime as dt
import html
from urllib.parse import urlsplit

from . import config, interests


def available_topics() -> set[str]:
    return {str(item['id']) for group in interests.catalogue()
            if group.get('id') != 'health' for item in group.get('items', [])}


def select_articles(rows, topics, lang, today, limit=5, sections=()):
    """Select recent public articles; health preferences cannot enter this API."""
    if lang not in ('en', 'cs') or not isinstance(today, dt.date):
        raise ValueError('Invalid language or date')
    selected = set(topics)
    allowed_sections = {str(s['id']) for s in config.site().get('sections', []) if s.get('id') != 'health'}
    chosen_sections = set(sections)
    if (not selected and not chosen_sections) or not selected <= available_topics() or not chosen_sections <= allowed_sections:
        raise ValueError('Choose non-health topics or sections from the public catalogue')
    result, seen = [], set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            day = dt.date.fromisoformat(str(row.get('dt', '')))
        except ValueError:
            continue
        if not 0 <= (today - day).days <= 1:
            continue
        url = str(row.get('u', ''))
        parts = urlsplit(url)
        if (parts.scheme or parts.netloc or not url.startswith('/' + lang + '/')
                or url.startswith('//') or '\\' in url or any(ord(c) < 32 for c in url)):
            continue
        if url in seen or not str(row.get('t', '')).strip():
            continue
        if (row.get('s') not in chosen_sections and
                not selected.intersection(str(row.get('g', '')).split(','))):
            continue
        seen.add(url)
        result.append(row)
        if len(result) >= max(1, min(int(limit), 10)):
            break
    return result


def render_preview(rows, topics, lang, today, sections=()):
    """Render a draft only; this is not a sendable newsletter or opt-in flow."""
    selected = select_articles(rows, topics, lang, today, sections=sections)
    label = 'Ranní briefing — ukázka' if lang == 'cs' else 'Morning briefing — preview'
    empty = 'Pro vybraná témata zatím nemáme nové články.' if lang == 'cs' else 'No recent articles match these topics.'
    lines = ['<!doctype html><html lang="' + lang + '"><meta charset="utf-8"><title>' + label + '</title>',
             '<body><h1>' + label + '</h1>']
    for row in selected:
        url = 'https://mypaper.news' + str(row['u'])
        lines.append('<h2><a href="' + html.escape(url, quote=True) + '">' + html.escape(str(row['t'])) + '</a></h2>')
        lines.append('<p>' + html.escape(str(row.get('d') or '')) + '</p>')
    if not selected:
        lines.append('<p>' + empty + '</p>')
    lines.append('</body></html>')
    return '\n'.join(lines)
