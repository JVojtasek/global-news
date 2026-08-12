"""Postaví statický web ze složky content/ do složky public/.

Nepotřebuje server, databázi ani Node.js. Výsledek se dá nahrát kamkoli
(Cloudflare Pages, GitHub Pages, obyčejný webhosting).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html as _html_mod
import json
import re
import shutil
import urllib.parse
import xml.sax.saxutils as sx

import markdown as md
from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import analyst, article, config, countries, images, impact, interests, members, morning, quizzes
from . import problems, quotes, reader
from . import weekend
from . import seo as indexnow          # `seo` je uvnitř run() nastavení z site.yml

# Jazyk stránky pro sdílení na sítích. Web píše britskou angličtinou,
# proto en_GB — Facebook a spol. z toho vybírají správnou verzi náhledu.
LOCALES = {"en": "en_GB", "cs": "cs_CZ", "sk": "sk_SK"}

STRINGS = {
    "en": {
        "briefing_title": "Today in five minutes",
        "brief_nav": "Briefing",
        "brief_page_title": "Your morning briefing",
        "brief_page_intro": "The world first, then your country, what could change your day and one calm step that makes a household more resilient. A finite edition—not an endless feed.",
        "brief_world": "The world now",
        "brief_world_help": "Fresh global signals in publisher time order. Links open the original reporting; this is the map before My Paper analysis.",
        "brief_local": "Your country",
        "brief_local_help": "Local reporting and official information for the country saved on this device. Choose a country above to make this section yours.",
        "brief_practical": "What changes for you",
        "brief_practical_help": "A decision layer for money, health, daily life and safety. We separate what to know, watch, prepare and act on—and cite the source.",
        "brief_action": "Practical step",
        "brief_trigger": "Only if",
        "brief_empty_practical": "No source-backed practical action is justified today. That is useful information too.",
        "brief_ready": "Ready, not afraid",
        "brief_ready_help": "One low-cost household task a day, based on official preparedness guidance—not disaster theatre or shopping lists.",
        "brief_ready_rule": "A headline alone never triggers stockpiling, a financial trade, a medication change or evacuation. Consequential advice must name an official source, geography, trigger and expiry.",
        "brief_durable": "Keep beyond today",
        "brief_durable_help": "Explanations and practical guides selected for usefulness after the headline has expired.",
        "brief_live": "Right now",
        "brief_live_help": "Fresh event signals from the newsroom collector. These link to the original publisher and are not presented as finished My Paper analysis.",
        "brief_recent": "The last 24 hours",
        "brief_recent_help": "My Paper reporting and analysis, newest first.",
        "brief_watch": "What to watch today",
        "brief_watch_help": "Time-bound events verified by the research desk, or explicit signals our articles say could change the picture.",
        "brief_scope": "Edition scope",
        "brief_scope_home": "My country",
        "brief_scope_mix": "My country + world",
        "brief_scope_world": "World",
        "brief_country": "Home country",
        "brief_country_pick": "Choose a country",
        "brief_settings": "Edit interests and reading balance",
        "brief_private": "Your country and interests stay on this device.",
        "brief_country_mark": "Relevant to your country",
        "brief_empty_live": "No reliably timed live signals are available in this window.",
        "brief_empty_recent": "No My Paper article was published in the last 24 hours.",
        "brief_empty_watch": "No adequately sourced watch item is available yet.",
        "brief_empty_country": "Nothing in this edition is specifically tied to the selected country. Switch to Country + world to keep the full picture.",
        "brief_source": "Original source",
        "brief_sources": "sources in cluster",
        "brief_calendar": "Verified calendar",
        "brief_signals": "Editorial watch signals",
        "brief_done": "You’re caught up",
        "brief_done_help": "The briefing ends here. Return later for genuinely new information—not recycled headlines.",
        "brief_open": "Open the full morning briefing",
        "quiz_nav": "Quizzes",
        "quiz_hub_title": "Find out something useful about yourself",
        "quiz_hub_intro": "One short, evidence-aware quiz a day: understand a pattern, test a practical skill and leave with one realistic next step.",
        "quiz_daily": "Quiz of the day",
        "quiz_start": "Take today’s quiz",
        "quiz_archive": "Earlier quizzes",
        "quiz_empty": "Today’s quiz is still being checked.",
        "quiz_minutes": "min",
        "quiz_questions": "questions",
        "quiz_method_title": "Useful, private and honest",
        "quiz_method_text": "My Paper quizzes are designed for reflection and learning—not labels, diagnoses or false certainty.",
        "quiz_method_private": "Answers and results are calculated on this device and are not sent to My Paper.",
        "quiz_method_honest": "Evidence-based instruments are cited; original self-checks say exactly what they can and cannot measure.",
        "quiz_method_action": "Every result gives a practical next step, not merely a flattering personality label.",
        "quiz_all": "All quizzes",
        "quiz_private": "Private by design: your answers stay in this browser.",
        "quiz_answer_all": "Please answer every question to see a meaningful result.",
        "quiz_result_button": "Show my result",
        "quiz_your_result": "Your result",
        "quiz_strength": "A strength to keep",
        "quiz_next": "Best next step",
        "quiz_watchout": "A blind spot to watch",
        "quiz_reset": "Take it again",
        "quiz_more": "Explore more quizzes",
        "quiz_what_means": "What this result does—and does not—mean",
        "quiz_home_cta": "A few minutes, a personal result and one useful next step. No sign-up.",
        "section": "Section",
        "sources": "Sources",
        "sources_word": "sources",
        "sources_note": "We report facts from the sources above in our own words and link to the originals. "
                        "Interpretation is ours, not theirs.",
        "confidence": "Confidence",
        "confidence_help": "How strongly this piece is supported by independent sources and passed our review.",
        "nextstep_q": "Every headline has a deeper story. This is ours.",
        "nextstep_cta": "What we are doing here",
        "about": "About us",
        "empty": "Nothing here yet.",
        "footer_note": "Facts first, context second, meaning last — in that order, always. "
                       "We tell you what we know, what we do not, and where the line between them runs.",
        "forecasts_title": "Our forecasts, scored",
        "forecasts_intro": "We publish specific predictions with a probability and a deadline, "
                           "then grade ourselves in public — including when we were wrong.",
        "fc_resolved": "forecasts settled", "fc_brier": "Brier score", "fc_verdict": "verdict",
        "fc_explain": "The Brier score measures calibration. 0.00 is perfect, 0.25 is what you get "
                      "by saying 50% to everything, and anything above 0.30 means we are guessing. "
                      "Nothing is ever deleted from this page.",
        "v_none": "not yet scored", "v_strong": "clearly better than chance",
        "v_good": "better than a coin flip", "v_chance": "no better than chance",
        "v_poor": "worse than chance",
        "fc_open": "Open", "fc_done": "Settled", "fc_void": "Voided — could not be judged fairly",
        "fc_by": "resolves by", "fc_outcome": "Outcome", "fc_yes": "happened", "fc_no": "did not happen",
        "forecasts_link": "Forecasts",
        "republish_title": "Republish our work — free",
        "republish_body": """Our reporting is free to republish under a
[{license}]({license_url}) licence. We would rather our work reached your readers
than sat behind our own logo.

## What you may do

Take any article marked *Free to republish* — the block at the bottom of the page
gives you the full HTML, ready to paste. Print, online, newsletter, all fine, and
you may run advertising alongside it.

## What we ask

**Credit us and link back.** Keep the line at the bottom of the article that says
where it came from, with a working link. That line is the entire price.

**Do not edit the substance.** You may change a headline for your house style and
adjust wording for relative time and place ("yesterday" becomes "last week").
You may not add material, cut the qualifications, or change what a sentence claims.

**Do not sell the article on its own** or place it behind a paywall as a standalone
product.

**Keep the pixel.** The one-pixel image at the end of the block tells us how many
people read it. It collects no personal data and does not track anyone.

**Photographs are not included** unless we say so on the page. Most of our images
are licensed from third parties and you need your own rights to them.

## Translations

Ask us first. We will usually say yes, but we want to see the translated text
before it runs — a bad translation of a careful sentence is worse than no
translation at all.

## Anything else

Write to {email}. We answer.""",
        "today": "",
        "theme": "Light / dark",
        "weather_title": "Weather",
        "weather_intro": "Pick your place once and it stays. Seven-day forecast and live rain radar.",
        "weather_ph": "Town or city…",
        "weather_find": "Find",
        "weather_here": "Use my location",
        "weather_hint": "Type a place, or let the browser find you. Your choice is stored on this device only.",
        "weather_radar": "Rain radar — where the storm is heading",
        "weather_credit": "Forecast: Open-Meteo · Radar: RainViewer · Air and pollen: Open-Meteo · Map: OpenStreetMap contributors",
        "weather_feels": "Feels like",
        "weather_wind": "Wind",
        "weather_hum": "Humidity",
        "weather_rainc": "Rain",
        "weather_now": "Now",
        "weather_play": "Play",
        "weather_pause": "Pause",
        "weather_past": "Past two hours",
        "weather_soon": "Next 30 minutes",
        "weather_nowcast_dry": "No rain expected in the next two hours.",
        "weather_nowcast_start": "Rain starts in about %d min",
        "weather_nowcast_stop": "Rain should stop in about %d min",
        "weather_nowcast_now": "It is raining now",
        "weather_hours": "Next 24 hours",
        "weather_best": "Best window today",
        "weather_best_none": "No clearly better window today — it looks much the same all day.",
        "weather_best_txt": "%s to %s looks driest and calmest.",
        "weather_air": "Air and pollen",
        "weather_aqi": "Air quality",
        "weather_pollen": "Pollen",
        "weather_uv": "UV",
        "weather_sun": "Sun",
        "weather_aqi_labels": ["Good", "Fair", "Moderate", "Poor", "Very poor", "Extremely poor"],
        "weather_low": "low", "weather_med": "moderate", "weather_high": "high",
        "weather_days": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "weather_codes": {"0": "Clear sky", "1": "Mainly clear", "2": "Partly cloudy", "3": "Overcast", "45": "Fog", "48": "Freezing fog", "51": "Light drizzle", "53": "Drizzle", "55": "Heavy drizzle", "61": "Light rain", "63": "Rain", "65": "Heavy rain", "66": "Freezing rain", "67": "Heavy freezing rain", "71": "Light snow", "73": "Snow", "75": "Heavy snow", "77": "Snow grains", "80": "Rain showers", "81": "Heavy showers", "82": "Violent showers", "85": "Snow showers", "86": "Heavy snow showers", "95": "Thunderstorm", "96": "Thunderstorm with hail", "99": "Severe thunderstorm"},
        "thought_title": "Thought for the day",
        "wit_title": "Last word",
        "ticker_title": "Live now",
        "ticker_note": "Checked every five minutes. Times come from the publisher; links open the original reporting.",
        "ticker_all": "All",
        "ticker_updated": "Feed checked",
        "ticker_stale": "The feed is delayed",
        "ticker_loading": "Loading the latest verified headlines…",
        "ticker_empty": "No verified headline is available in this desk yet.",
        "ticker_new": "New",
        "ticker_ago_now": "just now",
        "ticker_ago_min": "%d min ago",
        "ticker_ago_hour": "%dh ago",
        "ticker_ago_day": "%dd ago",
        "ticker_brief_cta": "Open the finite morning briefing",
        "ticker_email_cta": "Get the morning edition by e-mail",
        "reader_open": "Reading balance",
        "reader_title": "Your reading balance",
        "reader_intro": "You decide how much news you get and how hard it lands. Nothing is deleted — heavy stories are shortened to a calm summary you can open in full whenever you want.",
        "reader_amount": "How much",
        "reader_amount_1": "Overview only",
        "reader_amount_2": "Balanced",
        "reader_amount_3": "Everything",
        "reader_amount_help": "Overview keeps you in the picture with about a dozen stories a day.",
        "reader_tone": "How hard it lands",
        "reader_tone_1": "Gentle",
        "reader_tone_2": "Balanced",
        "reader_tone_3": "Unfiltered",
        "reader_tone_help": "Gentle shows heavy stories as a summary — what happened, what it means, what the risks are, what can be done.",
        "reader_mute": "Keep these out",
        "reader_brake": "Remind me to take a break",
        "reader_brake_msg": "That is five heavy stories in a row. The world will still be there in ten minutes.",
        "reader_brake_ok": "Carry on",
        "reader_brake_alt": "Show me something good",
        "reader_topics": {"war": "War and conflict", "crime": "Crime and courts",
                          "disaster": "Disasters", "politics": "Politics",
                          "health": "Illness and medicine", "money": "Money and markets",
                          "tech": "Technology"},
        "reader_full": "Read the whole article",
        "reader_calm": "Shown as a summary because of your reading settings.",
        "reader_hidden_1": "1 story is hidden by your settings.",
        "reader_hidden_n": "%d stories are hidden by your settings.",
        "reader_show": "Show them anyway",
        "reader_privacy": "Saved on this device only. We do not profile you and nothing is sent anywhere.",
        "reader_save": "Save",
        "reader_reset": "Reset",
        "ob_title": "Make this your paper",
        "ob_intro": "Thirty seconds, and the front page starts with what matters to you. You can change it any time, and you can skip this entirely.",
        "ob_skip": "Skip",
        "ob_next": "Next",
        "ob_back": "Back",
        "ob_done": "Done",
        "ob_step": "Step %d of 3",
        "ob_sections": "Which sections should come first?",
        "ob_interests": "And more precisely?",
        "ob_balance": "How much, and how hard?",
        "ob_privacy": "Everything you tick stays in this browser. There is no account, nothing is sent anywhere, and we cannot see it. Clearing your browser data clears this too.",
        "ob_own": "Your own topics",
        "ob_own_ph": "beekeeping",
        "ob_own_add": "Add",
        "ob_own_help": "We look for what you type in headlines and summaries, so a plain word works best — beekeeping, diabetes, Formula 1 — rather than a whole sentence.",
        "foryou": "For you",
        "foryou_title": "Chosen for you",
        "foryou_intro": "Ranked in your browser from your own settings. We never see them.",
        "foryou_empty": "Tell us what interests you and this page fills up.",
        "foryou_setup": "Set up my paper",
        "foryou_outside": "Outside your circle — on purpose",
        "foryou_outside_help": "A newspaper that only ever agreed with you would be a mirror, not a newspaper. These are picked from everything else.",
        "foryou_health_note": "Health is a topic here, not advice. We report what research shows, name the source, and say what is still unknown. For anything about your own health, ask a doctor.",
        "picked": "Picked for you",
        "imp_link": "What it means for you",
        "imp_title": "What this means for you",
        "imp_intro": "The news, turned into the only question that matters at your kitchen table: does this touch my money, my health, my everyday life or my safety — and what can I actually do about it?",
        "imp_rail": "What it means for you",
        "imp_more": "All practical impacts",
        "imp_todo": "What you can do",
        "imp_none": "Nothing here yet. A story appears here only once we can say honestly what it changes for a reader.",
        "imp_areas": {"money": "Money", "health": "Health", "life": "Everyday life", "safety": "Safety"},
        "imp_filter": "Show only",
        "imp_all": "Everything",
        # --- sobotní vydání (engine/weekend.py) ---
        # --- velké problémy (engine/problems.py) ---
        "pr_nav": "Big problems",
        "pr_title": "The big problems",
        "pr_intro": "Ten problems the whole world has, and one page each. Not opinions: "
                    "what a country actually tried, what the numbers did afterwards, and "
                    "who is genuinely ahead. Then the part nobody else prints — what a "
                    "machine would do with the same problem, and what a machine would miss.",
        "pr_measure": "How this is measured",
        "pr_measure_help": "One number, named and sourced. Everything on this page is "
                           "argued against it, so you can check us.",
        "pr_board": "Who is actually ahead",
        "pr_board_help": "Ranked on the number above — not on reputation.",
        "pr_board_country": "Country",
        "pr_board_value": "Result",
        "pr_board_note": "Why",
        "pr_tried": "What has actually been tried",
        "pr_tried_help": "Real countries, real policies, and what the numbers did afterwards "
                         "— including where it went wrong.",
        "pr_result": "What happened",
        "pr_caveat": "The catch",
        "pr_machine": "What a machine would optimise for",
        "pr_machine_help": "This is arithmetic, not advice and not a prediction. We name the "
                           "single number being maximised and follow it wherever it goes. "
                           "The point is to see the shape of the answer a calculator gives.",
        "pr_optimise": "The number being maximised",
        "pr_arith": "The arithmetic",
        "pr_blind": "What the machine would miss",
        "pr_blind_help": "The most important part of this page. A number that goes up can "
                         "still be paid for by somebody, and some things never make it into "
                         "the number at all.",
        "pr_yours": "Where does your country stand?",
        "pr_yours_cta": "Open my country",
        "pr_sources": "Where the numbers come from",
        "pr_updated": "Checked on",
        "pr_all": "All ten problems",
        "pr_none": "Nothing here yet.",
        "pr_read": "Read the page",
        "pr_disclaimer": "We are a newspaper, not a government and not an adviser. Nothing "
                         "on this page is a recommendation to you or to anyone in office. "
                         "It is what was tried, what it measured, and what a calculator "
                         "would say if you let it loose on the same problem.",
        # --- co to znamená pro mou zemi (engine/countries.py) ---
        "co_nav": "My country",
        "co_link": "What it means for my country",
        "co_title": "What it means for %s",
        "co_pick_title": "What it means for my country",
        "co_intro": "Pick the country you live in. You get the last two weeks of "
                    "news that actually reaches it — what it changes for money, "
                    "health, everyday life and safety, and what you can do about it.",
        "co_pick": "Choose your country",
        "co_pick_help": "Your choice stays in this browser. We never learn it.",
        "co_change": "Change country",
        "co_window": "Stories from %s",
        "co_direct": "Named directly",
        "co_direct_help": "These stories are about this country.",
        "co_ripple": "Reaches you from outside",
        "co_ripple_help": "Not about this country, but it lands here anyway — through "
                          "the EU, a trading partner, or simply because it is worldwide.",
        "co_why": "Why this reaches you",
        "co_todo": "What you can do",
        "co_none": "Nothing from the last two weeks touches this country yet. "
                   "That happens, and we would rather say so than pad the page.",
        "co_thin": "Only a few stories so far. The page fills up as the fortnight goes on.",
        "co_all": "All countries",
        "co_all_help": "Every country we watch. The number says how many stories from the last two weeks reach it — a nought means nothing did, and the page says so plainly.",
        "co_areas_here": "What it touches here",
        "co_saved": "Saved on this device",
        "co_no_impact": "Also from here",
        "co_no_impact_help": "We could not honestly say what these change for you, "
                             "so we say nothing and let you read them yourself.",
        "co_eu": "European Union",
        "co_reason_eu": "an EU-wide decision",
        "co_reason_global": "a worldwide story",
        "co_reason_partner": "a close trading partner",
        "co_reason_named": "this country is named in it",
        "wk_nav": "Saturday edition",
        "wk_kicker": "Saturday edition",
        "wk_title": "The Saturday edition",
        "wk_intro": "The week, finished. Read it with your coffee and you are done — "
                    "there is nothing underneath.",
        "wk_issue": "Issue %d",
        "wk_print": "Print this edition",
        "wk_past": "Past editions",
        "wk_open": "This issue is still being set. It closes on %s — everything already "
                   "on this page is finished and will not change.",
        "wk_five": "The week in five minutes",
        "wk_five_help": "Every summary here was written to stand on its own. Read only "
                        "these and you are still in the picture.",
        "wk_long": "The long read",
        "wk_long_more": "Read the whole piece",
        "wk_impact": "What it meant for you",
        "wk_impact_help": "Not what happened — what it changed, and what you can do about it.",
        "wk_good": "Good news",
        "wk_sit": "Something to sit with",
        "wk_sit_from": "The questions come from",
        "wk_read": "Read in full",
        "wk_end": "That is the end of the edition.",
        "wk_end_body": "Nothing follows this line. No more to scroll, nothing else to open. "
                       "You have read the week, and that was the whole idea.",
        "wk_next": "The next edition comes out on %s. Until then the paper comes out every "
                   "morning, as it always does.",
        "wk_next_open": "This issue closes on %s. Until then the paper comes out every "
                        "morning, as it always does.",
        "wk_join": "There is no advertising here and there never will be. If you would like "
                   "the paper to carry on, you can become a member.",
        "wk_archive_title": "Every Saturday edition",
        "wk_archive_intro": "Each issue is finished and stays exactly as it was. Nothing is "
                            "ever added to an old edition.",
        "wk_redirect": "Opening the newest edition…",
        "partners_title": "Worth reading",
        "archive_title": "Everything we have published",
        "archive_intro": "Every article, oldest kept as carefully as newest. Nothing here is ever quietly deleted — if we correct something, the correction stays visible on the piece itself.",
        "archive_search": "Search the archive…",
        "archive_note": "Search runs inside your browser over the list on this page. We do not log what you look for.",
        "archive_link": "Archive",
        "sec_sort": "Sort",
        "sec_sort_new": "Newest",
        "sec_sort_deep": "Longest reads",
        "sec_sort_light": "Lightest first",
        "sec_count": "%d articles",
        "sec_calm": "A quiet section. No news ticker here on purpose.",
        "privacy_link": "Privacy",
        "related": "Keep reading",
        "newsletter_soon": "The newsletter opens shortly.",
        "nl_sub_subject": "Newsletter sign-up",
        "nl_sub_thanks": "Your mail app should be open. Send the message and you are on the list.",
        "nl_privacy": "One click to leave. We never sell or share your address.",
        "republish_offer": "Free to republish",
        "republish_help": "Copy this HTML into your CMS. Credit line and licence are included.",
        "mem_link": "Membership",
        "mem_title": "Become a member",
        "mem_intro": "Almost everything here is free to read and stays that way. Membership is for readers "
                     "who want the long pieces first, want the ones that only go out by e-mail, and want "
                     "this to keep existing without advertising.",
        "mem_honest": "One thing we would rather say ourselves than have you find out: this site is a set "
                      "of plain files with no server behind it, so we cannot lock a page and we are not "
                      "going to pretend otherwise. What we can honestly do is give members a head start "
                      "and send them things by e-mail. That is the whole of it.",
        "mem_tiers": "What you can join",
        "mem_free": "Free",
        "mem_price": "€%s a month",
        "mem_join_head": "Join, and read the long pieces a week early",
        "mem_join_why": "One e-mail address is all it takes. No account, no password, and one click to leave.",
        "mem_join": "Join",
        "mem_email_ph": "your@email.com",
        "mem_soon": "Membership opens shortly. Nothing is being taken yet.",
        "mem_early_badge": "Early access · members",
        "mem_early_lead": "Members are reading this in full today. Here is the summary, so you know what is in it.",
        "mem_opens_on": "It opens to everyone on %s, in full and unchanged.",
        "mem_opens_tomorrow": "It opens to everyone tomorrow, in full and unchanged.",
        "mem_opens_today": "It opens to everyone later today, in full and unchanged.",
        "mem_early_list": "In early access right now",
        "mem_early_note": "Members have these in full today. Everyone else gets the same text on the date "
                          "shown — nothing cut, nothing rewritten.",
        "mem_only_list": "Sent to members by e-mail",
        "mem_only_note": "These are not published on the site at all. Members get them in full in their "
                         "inbox. They are listed here so you can see what you would be getting.",
        "mem_none": "Nothing is in early access at the moment.",
        "mem_ads": "No advertising, and no selling you on",
        "mem_ads_note": "We do not run advertising and we never sell, rent or share reader data. Your "
                        "e-mail address is used to send you what you signed up for and nothing else. "
                        "What you tick in your reading settings stays in your browser and never reaches us.",
        "mem_terms": "Membership terms",
        # --- rozcestníky podle témat ---------------------------------
        # počet článků skloňovaný: 1 / 2-4 / 5 a víc (čeština to potřebuje)
        "count_one": "%d article",
        "count_few": "%d articles",
        "count_many": "%d articles",
        "hub_more": "More on this",
        "hub_intro": "Everything we have published on %s, newest first. Background, research "
                     "and plain explanation — not only the headline of the day.",
        "hub_back": "Browse the whole %s section",
        # --- tichá pozvánka na konci článku ---------------------------
        "nl_inline_cta": "How to get it by e-mail",
        # --- stránka 404 ----------------------------------------------
        "e404_title": "That page is not here",
        "e404_line": "Sorry about that — the address may have a typo, or we may have moved the piece.",
        "e404_go": "Search",
        "e404_secs": "Or start from a section",
        # --- doplněk stránky o soukromí, když se zapne měření ----------
        "priv_analytics": "## Counting visits\n\n"
                          "This site counts how often each page is opened, using %s — a service "
                          "that sets no cookies, stores no identifier and builds no profile. It "
                          "tells us which articles are worth reading, never who read them. What "
                          "you tick in your reading settings and in your interests never reaches "
                          "it: that stays in your browser, exactly as described above.",
    },
    "cs": {
        "briefing_title": "Svět dnes za pět minut",
        "brief_nav": "Briefing",
        "brief_page_title": "Váš ranní briefing",
        "brief_page_intro": "Nejdřív svět, potom vaše země, co může změnit váš den a jeden klidný krok k odolnější domácnosti. Konečné vydání, ne nekonečný proud.",
        "brief_world": "Svět právě teď",
        "brief_world_help": "Čerstvé světové signály seřazené podle času vydavatele. Odkazy vedou k původní zprávě; nejdřív mapa, potom analýza My Paper.",
        "brief_local": "Vaše země",
        "brief_local_help": "Místní zpravodajství a oficiální informace pro zemi uloženou v tomto zařízení. Vyberte ji nahoře a tahle část bude vaše.",
        "brief_practical": "Co se mění pro vás",
        "brief_practical_help": "Rozhodovací vrstva pro peníze, zdraví, běžný život a bezpečí. Oddělujeme, co vědět, sledovat, připravit a kdy jednat—vždy se zdrojem.",
        "brief_action": "Praktický krok",
        "brief_trigger": "Jen pokud",
        "brief_empty_practical": "Dnes není doložený důvod k praktickému zásahu. I to je užitečná informace.",
        "brief_ready": "Připraveni, ne vystrašeni",
        "brief_ready_help": "Jeden levný krok pro domácnost denně podle oficiálních doporučení—bez katastrofického divadla a nákupních seznamů.",
        "brief_ready_rule": "Samotný titulek nikdy nespouští předzásobení, finanční obchod, změnu léků ani evakuaci. Závažná rada musí uvést oficiální zdroj, území, podmínku a konec platnosti.",
        "brief_durable": "Nechte si i na později",
        "brief_durable_help": "Vysvětlení a praktické návody vybrané tak, aby byly užitečné i po vypršení titulku.",
        "brief_live": "Právě teď",
        "brief_live_help": "Čerstvé signály ze sběru redakce. Vedou přímo k původnímu vydavateli a nevydáváme je za hotovou analýzu My Paper.",
        "brief_recent": "Posledních 24 hodin",
        "brief_recent_help": "Články a analýzy My Paper, od nejnovějších.",
        "brief_watch": "Co dnes sledovat",
        "brief_watch_help": "Časově určené události ověřené rešeršní redakcí, případně výslovné signály z našich článků, které mohou změnit situaci.",
        "brief_scope": "Rozsah vydání",
        "brief_scope_home": "Moje země",
        "brief_scope_mix": "Moje země + svět",
        "brief_scope_world": "Svět",
        "brief_country": "Domovská země",
        "brief_country_pick": "Vyberte zemi",
        "brief_settings": "Upravit zájmy a rovnováhu čtení",
        "brief_private": "Vaše země a zájmy zůstávají jen v tomto zařízení.",
        "brief_country_mark": "Týká se vaší země",
        "brief_empty_live": "V tomto okně nejsou dostupné žádné spolehlivě časované živé signály.",
        "brief_empty_recent": "Za posledních 24 hodin nevyšel žádný článek My Paper.",
        "brief_empty_watch": "Zatím nemáme dostatečně doložený bod ke sledování.",
        "brief_empty_country": "V tomto vydání není nic přímo svázáno se zvolenou zemí. Přepněte na Moje země + svět, ať vám neunikne širší obraz.",
        "brief_source": "Původní zdroj",
        "brief_sources": "zdrojů v události",
        "brief_calendar": "Ověřený kalendář",
        "brief_signals": "Redakční signály",
        "brief_done": "Máte přečteno",
        "brief_done_help": "Briefing tady končí. Vraťte se později pro skutečně nové informace, ne pro recyklované titulky.",
        "brief_open": "Otevřít celý ranní briefing",
        "quiz_nav": "Kvízy",
        "quiz_hub_title": "Zjistěte o sobě něco užitečného",
        "quiz_hub_intro": "Každý den jeden krátký a poctivý kvíz: pochopíte svůj vzorec, prověříte praktickou dovednost a odnesete si jeden realistický další krok.",
        "quiz_daily": "Kvíz dne",
        "quiz_start": "Spustit dnešní kvíz",
        "quiz_archive": "Předchozí kvízy",
        "quiz_empty": "Dnešní kvíz ještě prochází kontrolou.",
        "quiz_minutes": "min",
        "quiz_questions": "otázek",
        "quiz_method_title": "Užitečně, soukromě a poctivě",
        "quiz_method_text": "Kvízy My Paper slouží k zamyšlení a vzdělávání — ne k nálepkování, diagnózám nebo falešné jistotě.",
        "quiz_method_private": "Odpovědi i výsledek se počítají v tomto zařízení a My Paper je neodesílá.",
        "quiz_method_honest": "U ověřených metod uvádíme zdroje; u vlastních sebehodnocení přesně říkáme, co mohou a nemohou změřit.",
        "quiz_method_action": "Každý výsledek nabídne praktický krok, ne pouze líbivou osobnostní nálepku.",
        "quiz_all": "Všechny kvízy",
        "quiz_private": "Soukromí už v návrhu: vaše odpovědi zůstávají v tomto prohlížeči.",
        "quiz_answer_all": "Pro smysluplný výsledek prosím odpovězte na všechny otázky.",
        "quiz_result_button": "Ukázat můj výsledek",
        "quiz_your_result": "Váš výsledek",
        "quiz_strength": "Silná stránka, kterou si udržet",
        "quiz_next": "Nejlepší další krok",
        "quiz_watchout": "Slepé místo, na které pozor",
        "quiz_reset": "Vyplnit znovu",
        "quiz_more": "Další kvízy",
        "quiz_what_means": "Co tento výsledek znamená — a co ne",
        "quiz_home_cta": "Pár minut, osobní výsledek a jeden užitečný krok. Bez registrace.",
        "section": "Rubrika",
        "sources": "Zdroje",
        "sources_word": "zdrojů",
        "sources_note": "Fakta přebíráme z uvedených zdrojů vlastními slovy a odkazujeme na originály. "
                        "Výklad je náš, ne jejich.",
        "confidence": "Jistota",
        "confidence_help": "Nakolik je text podložen nezávislými zdroji a prošel naší kontrolou.",
        "nextstep_q": "Za každým titulkem je hlubší příběh. Tohle je ten náš.",
        "nextstep_cta": "Co tady vlastně děláme",
        "about": "O nás",
        "empty": "Tady zatím nic není.",
        "footer_note": "Nejdřív fakta, pak souvislosti, teprve pak smysl — v tomhle pořadí, vždycky. "
                       "Říkáme, co víme, co nevíme, a kde mezi tím vede hranice.",
        "forecasts_title": "Naše předpovědi a jak dopadly",
        "forecasts_intro": "Vydáváme konkrétní předpovědi s pravděpodobností a termínem "
                           "a pak si sami veřejně spočítáme, jak jsme dopadli — i když špatně.",
        "fc_resolved": "vyhodnocených", "fc_brier": "Brierovo skóre", "fc_verdict": "hodnocení",
        "fc_explain": "Brierovo skóre měří, jak dobře odhadujeme. 0,00 je dokonalé, 0,25 dostane ten, "
                      "kdo na všechno řekne 50 %, a cokoli nad 0,30 znamená, že hádáme. "
                      "Z téhle stránky se nikdy nic nemaže.",
        "v_none": "zatím nevyhodnoceno", "v_strong": "výrazně lepší než náhoda",
        "v_good": "lepší než hod mincí", "v_chance": "na úrovni náhody",
        "v_poor": "horší než náhoda",
        "fc_open": "Otevřené", "fc_done": "Vyhodnocené", "fc_void": "Zrušené — nešlo poctivě rozhodnout",
        "fc_by": "rozhodne se do", "fc_outcome": "Výsledek", "fc_yes": "stalo se", "fc_no": "nestalo se",
        "forecasts_link": "Předpovědi",
        "republish_title": "Převezměte naše články — zdarma",
        "republish_body": """Naše články jsou volně k převzetí pod licencí
[{license}]({license_url}). Radši budeme, když se dostanou k vašim čtenářům,
než aby zůstaly jen pod naším logem.

## Co smíte

Vzít kterýkoli článek označený *Volně k převzetí* — pod textem najdete blok
s hotovým HTML k vložení. Tisk, web, newsletter, všechno je v pořádku a vedle
článku můžete mít reklamu.

## Co za to chceme

**Uveďte nás a odkažte zpět.** Nechte pod článkem řádek s tím, odkud pochází,
i s funkčním odkazem. Ten řádek je celá cena.

**Neměňte obsah.** Titulek si klidně upravte do svého stylu a přepište údaje
o čase a místě („včera" na „minulý týden"). Nepřidávejte text, nevyhazujte
výhrady a neměňte, co která věta tvrdí.

**Neprodávejte článek samostatně** ani ho nedávejte za placenou zeď jako
samostatný produkt.

**Nechte tam ten pixel.** Jednopixelový obrázek na konci bloku nám říká, kolik
lidí článek četlo. Nesbírá žádné osobní údaje a nikoho nesleduje.

**Fotografie součástí nejsou**, pokud u nich nepíšeme jinak. Většina obrázků je
licencovaná od třetích stran a potřebujete k nim vlastní práva.

## Překlady

Napište nám předem. Většinou souhlasíme, ale chceme text vidět — špatný překlad
pečlivě napsané věty je horší než žádný.

## Cokoli dalšího

Pište na {email}. Odpovídáme.""",
        "today": "",
        "theme": "Světlý / tmavý režim",
        "weather_title": "Počasí",
        "weather_intro": "Vyber si místo jednou a zůstane ti. Předpověď na sedm dní a živý srážkový radar.",
        "weather_ph": "Město nebo obec…",
        "weather_find": "Najít",
        "weather_here": "Moje poloha",
        "weather_hint": "Napiš místo, nebo nech prohlížeč, ať tě najde. Volba se ukládá jen do tvého zařízení.",
        "weather_radar": "Srážkový radar — kam se bouřka posouvá",
        "weather_credit": "Předpověď: Open-Meteo · Radar: RainViewer · Ovzduší a pyl: Open-Meteo · Mapa: přispěvatelé OpenStreetMap",
        "weather_feels": "Pocitově",
        "weather_wind": "Vítr",
        "weather_hum": "Vlhkost",
        "weather_rainc": "Déšť",
        "weather_now": "Teď",
        "weather_play": "Přehrát",
        "weather_pause": "Pauza",
        "weather_past": "Poslední dvě hodiny",
        "weather_soon": "Nejbližší půlhodina",
        "weather_nowcast_dry": "V nejbližších dvou hodinách se déšť nečeká.",
        "weather_nowcast_start": "Déšť začne asi za %d min",
        "weather_nowcast_stop": "Déšť by měl ustat asi za %d min",
        "weather_nowcast_now": "Právě prší",
        "weather_hours": "Nejbližších 24 hodin",
        "weather_best": "Nejlepší okno dne",
        "weather_best_txt": "Nejsušeji a nejklidněji bude mezi %s a %s.",
        "weather_best_none": "Dnes není výrazně lepší okno — celý den vypadá podobně.",
        "weather_air": "Ovzduší a pyl",
        "weather_aqi": "Kvalita ovzduší",
        "weather_pollen": "Pyl",
        "weather_uv": "UV",
        "weather_sun": "Slunce",
        "weather_aqi_labels": ["Dobrá", "Slušná", "Střední", "Špatná", "Velmi špatná", "Extrémně špatná"],
        "weather_low": "nízký", "weather_med": "střední", "weather_high": "vysoký",
        "weather_days": ["Ne", "Po", "Út", "St", "Čt", "Pá", "So"],
        "weather_codes": {"0": "Jasno", "1": "Skoro jasno", "2": "Polojasno", "3": "Zataženo", "45": "Mlha", "48": "Mrznoucí mlha", "51": "Slabé mrholení", "53": "Mrholení", "55": "Silné mrholení", "61": "Slabý déšť", "63": "Déšť", "65": "Silný déšť", "66": "Mrznoucí déšť", "67": "Silný mrznoucí déšť", "71": "Slabé sněžení", "73": "Sněžení", "75": "Silné sněžení", "77": "Sněhová zrna", "80": "Přeháňky", "81": "Silné přeháňky", "82": "Prudké přeháňky", "85": "Sněhové přeháňky", "86": "Silné sněhové přeháňky", "95": "Bouřka", "96": "Bouřka s krupobitím", "99": "Silná bouřka"},
        "thought_title": "Myšlenka dne",
        "wit_title": "Poslední slovo",
        "ticker_title": "Právě se děje",
        "ticker_note": "Kontrola každých pět minut. Čas přebíráme od vydavatele; odkaz vede na původní zprávu.",
        "ticker_all": "Vše",
        "ticker_updated": "Feed zkontrolován",
        "ticker_stale": "Feed má zpoždění",
        "ticker_loading": "Načítám nejnovější ověřené titulky…",
        "ticker_empty": "V této rubrice zatím není ověřený čerstvý titulek.",
        "ticker_new": "Nové",
        "ticker_ago_now": "právě teď",
        "ticker_ago_min": "před %d min",
        "ticker_ago_hour": "před %d h",
        "ticker_ago_day": "před %d d",
        "ticker_brief_cta": "Otevřít konečný ranní briefing",
        "ticker_email_cta": "Dostávat ranní vydání e-mailem",
        "reader_open": "Nastavení čtení",
        "reader_title": "Kolik toho na tebe má web pustit",
        "reader_intro": "Ty rozhoduješ, kolik zpráv dostaneš a jak natvrdo. Nic se nemaže — těžké zprávy se zkrátí na klidné shrnutí, které si kdykoli rozklikneš celé.",
        "reader_amount": "Kolik toho",
        "reader_amount_1": "Jen přehled",
        "reader_amount_2": "Vyváženě",
        "reader_amount_3": "Všechno",
        "reader_amount_help": "Přehled ti nechá zhruba tucet zpráv denně, ale o nic důležitého nepřijdeš.",
        "reader_tone": "Jak natvrdo",
        "reader_tone_1": "Šetrně",
        "reader_tone_2": "Vyváženě",
        "reader_tone_3": "Bez filtru",
        "reader_tone_help": "Šetrný režim ukáže u těžkých zpráv jen shrnutí: co se stalo, co to znamená, jaká jsou rizika a co se s tím dá dělat.",
        "reader_mute": "Tohle mi sem nedávej",
        "reader_brake": "Připomeň mi pauzu",
        "reader_brake_msg": "To je pět těžkých zpráv za sebou. Svět tu za deset minut pořád bude.",
        "reader_brake_ok": "Pokračovat",
        "reader_brake_alt": "Ukaž mi něco dobrého",
        "reader_topics": {"war": "Válka a konflikty", "crime": "Kriminalita a soudy",
                          "disaster": "Katastrofy", "politics": "Politika",
                          "health": "Nemoci a medicína", "money": "Peníze a trhy",
                          "tech": "Technologie"},
        "reader_full": "Číst celý článek",
        "reader_calm": "Zobrazeno jako shrnutí podle tvého nastavení čtení.",
        "reader_hidden_1": "Podle tvého nastavení je skrytá 1 zpráva.",
        "reader_hidden_n": "Podle tvého nastavení jsou skryté %d zprávy.",
        "reader_show": "Přesto zobrazit",
        "reader_privacy": "Uloženo jen v tomhle zařízení. Nesledujeme tě a nikam se nic neposílá.",
        "reader_save": "Uložit",
        "reader_reset": "Zpět na výchozí",
        "ob_title": "Udělej si z toho svoje noviny",
        "ob_intro": "Třicet vteřin a titulní strana začne tím, co zajímá tebe. Kdykoli to změníš a klidně to celé přeskoč.",
        "ob_skip": "Přeskočit",
        "ob_next": "Dál",
        "ob_back": "Zpět",
        "ob_done": "Hotovo",
        "ob_step": "Krok %d ze 3",
        "ob_sections": "Které rubriky mají být první?",
        "ob_interests": "A přesněji?",
        "ob_balance": "Kolik toho a jak natvrdo?",
        "ob_privacy": "Všechno, co zaškrtneš, zůstane v tomhle prohlížeči. Žádný účet, nic se nikam neposílá a my se to nedozvíme. Když si smažeš data prohlížeče, smaže se i tohle.",
        "ob_own": "Vlastní témata",
        "ob_own_ph": "včelaření",
        "ob_own_add": "Přidat",
        "ob_own_help": "Co sem napíšeš, hledáme v titulcích a perexech. Nejlíp proto funguje jedno slovo — včelaření, cukrovka, formule 1 — ne celá věta.",
        "foryou": "Pro tebe",
        "foryou_title": "Vybráno pro tebe",
        "foryou_intro": "Seřazeno přímo v tvém prohlížeči podle tvého nastavení. My ho nevidíme.",
        "foryou_empty": "Řekni nám, co tě zajímá, a tahle stránka se naplní.",
        "foryou_setup": "Nastavit si noviny",
        "foryou_outside": "Mimo tvůj okruh — schválně",
        "foryou_outside_help": "Noviny, které by ti jen přitakávaly, jsou zrcadlo, ne noviny. Tohle je vybrané ze všeho ostatního.",
        "foryou_health_note": "Zdraví je tady téma, ne rada. Píšeme, co ukazuje výzkum, uvádíme zdroj a říkáme, co se zatím neví. Na cokoli ohledně svého zdraví se ptej lékaře.",
        "picked": "Vybráno pro tebe",
        "imp_link": "Co to znamená pro tebe",
        "imp_title": "Co to pro tebe znamená",
        "imp_intro": "Zprávy převedené na jedinou otázku, která vás doopravdy zajímá u kuchyňského stolu: sáhne mi to na peníze, na zdraví, na běžný život nebo na bezpečí — a co s tím můžu udělat?",
        "imp_rail": "Co to znamená pro tebe",
        "imp_more": "Všechny praktické dopady",
        "imp_todo": "Co s tím můžeš udělat",
        "imp_none": "Zatím tu nic není. Zpráva se sem dostane, teprve když umíme poctivě říct, co konkrétně mění.",
        "imp_areas": {"money": "Peníze", "health": "Zdraví", "life": "Běžný život", "safety": "Bezpečí"},
        "imp_filter": "Zobrazit jen",
        "imp_all": "Všechno",
        # --- sobotní vydání (engine/weekend.py) ---
        # --- velké problémy (engine/problems.py) ---
        "pr_nav": "Velké problémy",
        "pr_title": "Velké problémy",
        "pr_intro": "Deset problémů, které má celý svět, a na každý jedna stránka. Ne názory: "
                    "co některá země opravdu zkusila, co pak udělala čísla a kdo je na tom "
                    "vážně nejlíp. A pak to, co jinde nenajdeš — co by se stejným problémem "
                    "udělal stroj a co by mu uniklo.",
        "pr_measure": "Čím se to měří",
        "pr_measure_help": "Jedno číslo, pojmenované a se zdrojem. Všechno na téhle stránce "
                           "se poměřuje proti němu, abys nás mohl zkontrolovat.",
        "pr_board": "Kdo je na tom vážně nejlíp",
        "pr_board_help": "Řazeno podle čísla nahoře — ne podle pověsti.",
        "pr_board_country": "Země",
        "pr_board_value": "Výsledek",
        "pr_board_note": "Proč",
        "pr_tried": "Co se opravdu zkusilo",
        "pr_tried_help": "Skutečné země, skutečná opatření a co pak udělala čísla — včetně "
                         "toho, kde se to nepovedlo.",
        "pr_result": "Jak to dopadlo",
        "pr_caveat": "Háček",
        "pr_machine": "Co by optimalizoval stroj",
        "pr_machine_help": "Tohle je počet, ne rada a ne předpověď. Pojmenujeme jedno číslo, "
                           "které se má vyhnat co nejvýš, a jdeme za ním, ať to dopadne "
                           "jakkoli. Jde o to vidět, jaký tvar má odpověď kalkulačky.",
        "pr_optimise": "Číslo, které se vyhání nahoru",
        "pr_arith": "Počet",
        "pr_blind": "Co by stroji uniklo",
        "pr_blind_help": "Nejdůležitější část téhle stránky. I číslo, které roste, někdo "
                         "zaplatí — a některé věci se do čísla nedostanou vůbec.",
        "pr_yours": "Jak je na tom tvoje země?",
        "pr_yours_cta": "Otevřít moji zemi",
        "pr_sources": "Odkud jsou čísla",
        "pr_updated": "Ověřeno",
        "pr_all": "Všech deset problémů",
        "pr_none": "Zatím tu nic není.",
        "pr_read": "Otevřít stránku",
        "pr_disclaimer": "Jsme noviny, ne vláda a ne poradce. Nic na téhle stránce není "
                         "doporučení tobě ani nikomu, kdo rozhoduje. Je to, co se zkusilo, "
                         "co to naměřilo a co by řekla kalkulačka, kdyby se pustila na "
                         "stejný problém.",
        # --- co to znamená pro mou zemi (engine/countries.py) ---
        "co_nav": "Moje země",
        "co_link": "Co to znamená pro mou zemi",
        "co_title": "Co to znamená pro %s",
        "co_pick_title": "Co to znamená pro mou zemi",
        "co_intro": "Vyber zemi, ve které žiješ. Dostaneš poslední dva týdny zpráv, "
                    "které se jí opravdu týkají — co mění pro peníze, zdraví, běžný "
                    "život a bezpečí a co se s tím dá dělat.",
        "co_pick": "Vyber si zemi",
        "co_pick_help": "Výběr zůstane v tomhle prohlížeči. My se ho nedozvíme.",
        "co_change": "Změnit zemi",
        "co_window": "Zprávy z období %s",
        "co_direct": "Přímo o téhle zemi",
        "co_direct_help": "Tyhle zprávy jsou o téhle zemi.",
        "co_ripple": "Dolehne to sem zvenčí",
        "co_ripple_help": "Není to o téhle zemi, ale stejně to sem dopadne — přes "
                          "Evropskou unii, obchodního partnera, nebo prostě proto, "
                          "že jde o celosvětovou věc.",
        "co_why": "Proč se to týká i tebe",
        "co_todo": "Co s tím můžeš udělat",
        "co_none": "Za poslední dva týdny se téhle země nedotklo nic. Stává se to "
                   "a radši to řekneme, než abychom stránku něčím vycpali.",
        "co_thin": "Zatím jen pár zpráv. Stránka se plní, jak dva týdny ubíhají.",
        "co_all": "Všechny země",
        "co_all_help": "Všechny země, které sledujeme. Číslo říká, kolik zpráv z posledních dvou týdnů se jí týká — nula znamená, že žádná, a stránka to rovnou napíše.",
        "co_areas_here": "Čeho se to tady dotýká",
        "co_saved": "Uloženo v tomhle zařízení",
        "co_no_impact": "Taky odtud",
        "co_no_impact_help": "U těchhle zpráv neumíme poctivě říct, co mění pro tebe. "
                             "Tak radši nic nepíšeme a necháme je na tobě.",
        "co_eu": "Evropská unie",
        "co_reason_eu": "rozhodnutí pro celou Evropskou unii",
        "co_reason_global": "celosvětová věc",
        "co_reason_partner": "blízký obchodní partner",
        "co_reason_named": "je v ní ta země přímo jmenovaná",
        "wk_nav": "Sobotní vydání",
        "wk_kicker": "Sobotní vydání",
        "wk_title": "Sobotní vydání",
        "wk_intro": "Týden, který skončil. Přečteš u kávy a máš hotovo — pod tím už nic není.",
        "wk_issue": "Číslo %d",
        "wk_print": "Vytisknout vydání",
        "wk_past": "Starší vydání",
        "wk_open": "Tohle číslo se ještě sází. Uzavře se %s — co už na stránce je, "
                   "je hotové a měnit se nebude.",
        "wk_five": "Týden v pěti minutách",
        "wk_five_help": "Každé shrnutí je psané tak, aby obstálo samo za sebe. Když přečteš "
                        "jenom je, pořád víš, co se dělo.",
        "wk_long": "Dlouhé čtení",
        "wk_long_more": "Přečíst celý článek",
        "wk_impact": "Co to znamenalo pro tebe",
        "wk_impact_help": "Ne co se stalo, ale co se tím mění a co s tím můžeš udělat.",
        "wk_good": "Dobré zprávy",
        "wk_sit": "K zamyšlení",
        "wk_sit_from": "Otázky jsou z článku",
        "wk_read": "Číst celé",
        "wk_end": "A to je konec vydání.",
        "wk_end_body": "Pod tímhle řádkem už nic není. Není kam rolovat ani na co kliknout. "
                       "Přečetl jsi celý týden a přesně o to šlo.",
        "wk_next": "Příští vydání vyjde %s. Do té doby vycházejí noviny každé ráno jako vždycky.",
        "wk_next_open": "Tohle číslo se uzavře %s. Do té doby vycházejí noviny každé ráno "
                        "jako vždycky.",
        "wk_join": "Reklama tu není a nebude. Jestli chceš, aby noviny mohly vycházet dál, "
                   "můžeš se stát členem.",
        "wk_archive_title": "Všechna sobotní vydání",
        "wk_archive_intro": "Každé číslo je hotové a zůstává přesně takové, jaké bylo. "
                            "Do starého vydání se nikdy nic nedopisuje.",
        "wk_redirect": "Otevírám nejnovější vydání…",
        "partners_title": "Stojí za přečtení",
        "archive_title": "Všechno, co jsme vydali",
        "archive_intro": "Každý článek, o ty starší se staráme stejně jako o nové. Nic tady potichu nemizí — když něco opravíme, oprava zůstane vidět přímo u textu.",
        "archive_search": "Hledat v archivu…",
        "archive_note": "Hledá se přímo ve tvém prohlížeči v seznamu na téhle stránce. Nezaznamenáváme, co hledáš.",
        "archive_link": "Archiv",
        "sec_sort": "Řadit",
        "sec_sort_new": "Nejnovější",
        "sec_sort_deep": "Nejdelší čtení",
        "sec_sort_light": "Nejlehčí nahoře",
        "sec_count": "%d článků",
        "sec_calm": "Klidná rubrika. Proužek zpráv tu schválně není.",
        "privacy_link": "Soukromí",
        "related": "Čtěte dál",
        "newsletter_soon": "Odběr spouštíme zanedlouho.",
        "nl_sub_subject": "Přihlášení k odběru",
        "nl_sub_thanks": "Poštovní aplikace by se měla otevřít. Odešli zprávu a jsi na seznamu.",
        "nl_privacy": "Odhlášení jedním kliknutím. Adresu nikdy neprodáváme ani nepředáváme.",
        "republish_offer": "Volně k převzetí",
        "republish_help": "Zkopírujte HTML do svého systému. Uvedení zdroje i licence je součástí.",
        "mem_link": "Členství",
        "mem_title": "Staň se členem",
        "mem_intro": "Skoro všechno je tu ke čtení zadarmo a tak to zůstane. Členství je pro ty, kdo chtějí "
                     "dlouhé texty dřív, chtějí i ty, které vycházejí jen e-mailem, a chtějí, aby tenhle web "
                     "mohl existovat dál bez reklamy.",
        "mem_honest": "Jednu věc radši řekneme sami, než abys na ni přišel: tenhle web jsou obyčejné soubory "
                      "bez serveru za zády. Stránku tady nejde zamknout a nebudeme dělat, že jde. Co umíme "
                      "poctivě nabídnout, je náskok a e-mail. Nic víc v tom není.",
        "mem_tiers": "Z čeho si vybrat",
        "mem_free": "Zdarma",
        "mem_price": "%s € měsíčně",
        "mem_join_head": "Přidej se a čti dlouhé texty o týden dřív",
        "mem_join_why": "Stačí e-mailová adresa. Žádný účet, žádné heslo a odhlášení jedním kliknutím.",
        "mem_join": "Chci se přidat",
        "mem_email_ph": "tvuj@email.cz",
        "mem_soon": "Členství spouštíme zanedlouho. Zatím se nic neplatí.",
        "mem_early_badge": "Předčasný přístup · pro členy",
        "mem_early_lead": "Členové ho dnes čtou celý. Tady je shrnutí, ať víš, o čem to je.",
        "mem_opens_on": "Všem se otevře %s, celý a beze změn.",
        "mem_opens_tomorrow": "Všem se otevře zítra, celý a beze změn.",
        "mem_opens_today": "Všem se otevře ještě dnes, celý a beze změn.",
        "mem_early_list": "Právě teď v předčasném přístupu",
        "mem_early_note": "Členové je dnes mají celé. Ostatní dostanou přesně stejný text v uvedený den — "
                          "nic se nekrátí a nic nepřepisuje.",
        "mem_only_list": "Posíláme jen členům e-mailem",
        "mem_only_note": "Tyhle texty na web nejdou vůbec. Členové je dostanou celé do schránky. Tady jsou "
                         "vypsané, abys viděl, o co jde.",
        "mem_none": "V předčasném přístupu teď nic není.",
        "mem_ads": "Žádná reklama a žádné prodávání čtenářů",
        "mem_ads_note": "Nemáme reklamu a nikdy neprodáváme, nepronajímáme ani nesdílíme data o čtenářích. "
                        "E-mailová adresa slouží k tomu, co sis objednal, a k ničemu jinému. Co si "
                        "zaškrtneš v nastavení čtení, zůstane v tvém prohlížeči a k nám se nedostane.",
        "mem_terms": "Podmínky členství",
        # --- rozcestníky podle témat ---------------------------------
        # počet článků skloňovaný: 1 / 2-4 / 5 a víc
        "count_one": "%d článek",
        "count_few": "%d články",
        "count_many": "%d článků",
        "hub_more": "Víc k tématu",
        "hub_intro": "Všechno, co jsme vydali k tématu %s, od nejnovějšího. Souvislosti, výzkum "
                     "a srozumitelné vysvětlení — ne jenom titulek dne.",
        "hub_back": "Prohlédnout celou rubriku %s",
        # --- tichá pozvánka na konci článku ---------------------------
        "nl_inline_cta": "Jak to dostat e-mailem",
        # --- stránka 404 ----------------------------------------------
        "e404_title": "Tahle stránka tu není",
        "e404_line": "Omlouváme se — buď je v adrese překlep, nebo jsme text přesunuli jinam.",
        "e404_go": "Hledat",
        "e404_secs": "Nebo začni od rubriky",
        # --- doplněk stránky o soukromí, když se zapne měření ----------
        "priv_analytics": "## Počítání návštěv\n\n"
                          "Web počítá, kolikrát se která stránka otevřela. Používá k tomu %s — "
                          "službu, která nenastavuje cookies, neukládá žádný identifikátor "
                          "a nevytváří profily. Říká nám, které články stojí za přečtení, nikdy "
                          "ne, kdo je četl. Co si zaškrtneš v nastavení čtení a v zájmech, se "
                          "k ní nedostane: zůstává to v tvém prohlížeči přesně tak, jak je psáno výš.",
    },
}
STRINGS.setdefault("sk", STRINGS["cs"])

MD = md.Markdown(extensions=["extra", "sane_lists", "smarty"])


def _html(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def _url(meta: dict) -> str:
    return f"{config.base_path()}/{meta['lang']}/{meta['section']}/{meta['slug']}/"


def _published_iso(meta: dict, path=None) -> str:
    """Přesný čas vydání. V hlavičce vyhrává `published_at`, jinak se
    bere čas, kdy soubor poprvé přistál v repozitáři."""
    v = meta.get("published_at")
    if isinstance(v, str) and len(v) >= 16:
        return v
    if path is not None:
        got = config.first_commit_iso(path)
        if got:
            return got
    return f"{meta.get('date', '')}T00:00:00+00:00"


_CS_MONTH = ["", "ledna", "února", "března", "dubna", "května", "června",
             "července", "srpna", "září", "října", "listopadu", "prosince"]


def _published_label(meta: dict, path=None, lang: str = "en") -> str:
    iso = _published_iso(meta, path)
    try:
        d = dt.datetime.fromisoformat(iso)
    except Exception:
        return meta.get("date", "")
    if lang == "cs":
        return f"{d.day}. {_CS_MONTH[d.month]} {d.year}, {d:%H:%M}"
    return f"{d.day} {d:%B %Y}, {d:%H:%M}"


def _img_size(slug: str) -> tuple:
    """Skutečné rozměry obálky. Bez nich stránka při načtení poskočí.

    Čte se přímo ze souboru, který právě vznikl v public/img — hádat
    se to nedá, obrázky přicházejí z různých zdrojů. Když soubor není,
    vrátí se (None, None) a šablona atributy prostě nevypíše.
    """
    p = config.PUBLIC / "img" / f"{slug}.jpg"
    try:
        from PIL import Image
        with Image.open(p) as im:      # rozměry se čtou z hlavičky, ne z pixelů
            w, h = im.size
        return (int(w), int(h)) if w and h else (None, None)
    except Exception:  # noqa: BLE001
        return (None, None)


# Počítadla a sledovací pixely v převzatých článcích. Připojení k nim
# nikdy nepředpřipravujeme — zrychlovat sledování čtenáře není naše práce.
_NO_PRECONNECT = ("counter", "gravatar", "pixel", "analytic", "stats.", "track")


def _remote_img_host(body_html: str) -> str:
    """Cizí server, ze kterého se v převzatém článku tahají obrázky.

    Vrátí nejčastější takový server, aby se na něj dalo navázat spojení
    dopředu (`preconnect`) a velký obrázek se objevil dřív. Naše vlastní
    obálky jsou na stejné doméně, takže u běžného článku nevrátí nic.
    """
    import re as _re
    from urllib.parse import urlparse as _up
    hosts: dict = {}
    for src in _re.findall(r'<img[^>]+src="(https?://[^"]+)"', body_html or ""):
        host = _up(src).netloc
        if not host or any(bad in host for bad in _NO_PRECONNECT):
            continue
        hosts[host] = hosts.get(host, 0) + 1
    return max(hosts, key=hosts.get) if hosts else ""


def _clean_quiz(meta: dict) -> dict | None:
    q = meta.get("quiz")
    if not isinstance(q, dict):
        return None
    options = q.get("options")
    try:
        answer = int(q.get("answer"))
    except (TypeError, ValueError):
        return None
    if (not isinstance(options, list) or len(options) != 3 or answer not in range(3)
            or not str(q.get("question") or "").strip()
            or not str(q.get("explanation") or "").strip()):
        return None
    return {
        "question": str(q["question"]).strip(),
        "options": [str(x).strip() for x in options],
        "answer": answer,
        "explanation": str(q["explanation"]).strip(),
    }


def _qma_target(meta: dict, lens: dict) -> dict | None:
    """Bezpečný tematický odkaz do QMA s měřitelnou atribucí."""
    qma = (lens or {}).get("qma") or {}
    if not qma.get("enabled") or meta.get("section") not in qma.get("sections", []):
        return None

    base = "https://quantummarketanalyzer.com"
    path = ""
    explicit = str(meta.get("qma_path") or "").strip()
    if explicit.startswith("/") and not explicit.startswith("//"):
        path = explicit

    if not path:
        tickers = meta.get("tickers") or []
        if isinstance(tickers, str):
            tickers = [tickers]
        for ticker in tickers:
            symbol = str(ticker).upper().strip()
            if re.fullmatch(r"[A-Z][A-Z0-9.-]{0,9}", symbol):
                path = f"/stocks/{symbol}"
                break

    haystack = " ".join(str(meta.get(k) or "") for k in ("title", "dek", "topics")).lower()
    if not path:
        for route in qma.get("topic_paths", []):
            if any(str(k).lower() in haystack for k in route.get("keywords", [])):
                candidate = str(route.get("path") or "")
                if candidate.startswith("/") and not candidate.startswith("//"):
                    path = candidate
                    break

    if not path:
        path = str((qma.get("section_paths") or {}).get(meta.get("section")) or "")
    if not path.startswith("/") or path.startswith("//"):
        return None

    query = urllib.parse.urlencode({
        "utm_source": "mypaper",
        "utm_medium": "editorial",
        "utm_campaign": "wider_lens",
        "utm_content": str(meta.get("slug") or "article")[:80],
    })
    return {"url": f"{base}{path}?{query}", "path": path}


def _view(meta: dict, body: str, path=None) -> dict:
    lang = meta["lang"]
    labels = article.LAYER_LABELS.get(lang, article.LAYER_LABELS["en"])
    secs = article.sections(body)
    layers = []
    for lid in article.LAYERS:
        if lid in secs and secs[lid].strip():
            label, icon = labels[lid]
            layers.append({"id": lid, "label": label, "icon": icon, "html": _html(secs[lid])})
    layer_ids = {layer["id"] for layer in layers}
    section_label = next(
        (s.get(lang) or s["en"] for s in config.site()["sections"] if s["id"] == meta["section"]),
        meta["section"],
    )
    # převzaté texty občas nesou HTML entity (&#160;, &amp;) — v perexu
    # by se pak ukázaly jako text
    for _k in ("title", "dek"):
        if isinstance(meta.get(_k), str) and "&" in meta[_k]:
            meta[_k] = _html_mod.unescape(meta[_k])
    words = len(body.split())
    w = reader.weigh(meta, body)
    body_html = _html(body) if not layers else ""
    # obrázek musí být na disku dřív, než se z něj čtou rozměry
    img = images.ensure(meta)
    img_w, img_h = _img_size(meta.get("slug", "")) if img.get("src") else (None, None)
    is_wider_lens = (
        meta.get("type") in {"daily", "feature", "analysis"}
        and {"EVIDENCE", "PERSPECTIVES"}.issubset(layer_ids)
    )
    lens = config.site().get("wider_lens") or {}
    return {
        **meta,
        "url": _url(meta),
        "words": words,
        "reading_time": max(1, round(words / 220)),
        "layers": layers,
        "has_brief": any(l["id"] == "BRIEFLY" for l in layers),
        # The Wider Lens is a verifiable article format, not just a visual badge.
        # Older deep articles keep their original presentation until they contain
        # both of the new editorial layers.
        "is_wider_lens": is_wider_lens,
        "qma_target": _qma_target(meta, lens) if is_wider_lens else None,
        "quiz": _clean_quiz(meta),
        "load": w["load"],
        "band": reader.band(w["load"]),
        "topics_csv": ",".join(w["topics"]),
        "tags_csv": ",".join(interests.tags(meta, body)),
        "impact": impact.read(meta, body),
        # Které země se v textu jmenují a jak daleko ta zpráva dosáhne.
        # Počítá se tady, protože jinde už není po ruce celý text.
        "countries": countries.detect(meta, body),
        "published_iso": _published_iso(meta, path),
        "published_label": _published_label(meta, path, lang),
        "body_html": body_html,
        "image": img["src"], "credit": img["credit"],
        # rozměry obálky do šablony, ať stránka při načtení neposkočí
        "img_w": img_w, "img_h": img_h,
        # cizí server s obrázky (jen u převzatých textů) — kvůli preconnect
        "img_host": _remote_img_host(body_html or " ".join(l["html"] for l in layers)),
        "section_label": section_label,
        # public = běžný článek, early = zatím jen shrnutí a nabídka členství,
        # members = na web se nevydá vůbec (viz engine/members.py)
        "access_state": members.state(meta),
        "days_left": members.days_left(meta),
        "opens_label": _date_words(members.opens_on(meta), lang),
    }


def _ticker_time(value, lang: str) -> tuple[str, str]:
    """Absolutní místní čas a relativní stáří pro pravý sloupec."""
    try:
        stamp = dt.datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=dt.timezone.utc)
        stamp = stamp.astimezone(morning.PRAGUE)
    except (TypeError, ValueError):
        return "", ""
    now = dt.datetime.now(dt.timezone.utc).astimezone(morning.PRAGUE)
    mins = max(0, int((now - stamp).total_seconds() // 60))
    if lang == "cs":
        exact = f"{stamp.day}. {stamp.month}. · {stamp:%H:%M}"
        age = "právě teď" if mins < 1 else (f"před {mins} min" if mins < 60 else
              (f"před {mins // 60} h" if mins < 1440 else f"před {mins // 1440} d"))
    else:
        exact = stamp.strftime("%-d %b · %H:%M")
        age = "just now" if mins < 1 else (f"{mins} min ago" if mins < 60 else
              (f"{mins // 60}h ago" if mins < 1440 else f"{mins // 1440}d ago"))
    return exact, age


def _ticker(site: dict, lang: str, limit: int = 14, preferred_section: str = "") -> dict:
    """Rychlé zprávy do postranního sloupce.

    Systém posbírá 300 událostí denně, ale článků napíše pár. Zbytek
    by se jinak zahodil — tady z něj děláme živý proužek toho, co se
    právě děje, s odkazem vždy na původní zdroj.
    """
    p = config.DATA / "events.json"
    if not p.exists():
        return {"items": [], "updated_iso": "", "filters": [], "preferred": preferred_section}
    try:
        events = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"items": [], "updated_iso": "", "filters": [], "preferred": preferred_section}

    labels = {s["id"]: (s.get(lang) or s["en"]) for s in site["sections"]}
    # Skóre určuje redakční význam, ne čerstvost. V živém proudu proto
    # vyhrává skutečný čas publikace; při shodě teprve skóre.
    events = sorted(events, key=lambda e: (e.get("event_time") or e.get("created", ""),
                                           e.get("score", 0)), reverse=True)
    selected = [e for e in events if e.get("section") == preferred_section] if preferred_section else events
    if preferred_section and not selected:
        selected = events
    out, seen = [], set()
    for e in selected:
        head = e.get("headline", "").strip()
        key = head.lower()[:60]
        if not head or key in seen or len(head) < 25:
            continue
        item = (e.get("items") or [{}])[0]
        if not item.get("url"):
            continue
        seen.add(key)
        # Starší události znají jen okamžik našeho stažení. Ten nesmíme
        # vydávat za čas publikace. Jakmile proběhne nový sběr, dostanou se
        # sem jen položky s časem skutečně dodaným původním vydavatelem.
        published_iso = item.get("published_at") or (
            e.get("event_time", "") if e.get("time_kind") == "published" else ""
        )
        if not published_iso:
            continue
        exact, age = _ticker_time(published_iso, lang)
        out.append({
            "headline": head[:130],
            "url": item["url"],
            "source": item.get("source", ""),
            "section": labels.get(e.get("section", ""), ""),
            "section_id": e.get("section", "world"),
            "sources_count": e.get("sources_count", 1),
            "hot": e.get("score", 0) >= 70,
            "published_iso": published_iso,
            "published_label": exact,
            "age_label": age,
        })
        if len(out) >= limit:
            break
    core = ["world", "tech", "ai", "science"]
    if preferred_section and preferred_section not in core:
        core.insert(0, preferred_section)
    present = {e.get("section") for e in events}
    filters = [{"id": sec, "label": labels.get(sec, sec)} for sec in core if sec in present]
    updated = max((e.get("created", "") for e in events), default="")
    return {"items": out, "updated_iso": updated, "filters": filters,
            "preferred": preferred_section, "limit": limit}


def _related(a: dict, pool: list, n: int) -> list:
    """Vybere související články: nejdřív stejná rubrika, pak společná slova."""
    import re as _re
    words = set(_re.findall(r"[a-z]{5,}", (a.get("title", "") + " " + a.get("dek", "")).lower()))
    scored = []
    for other in pool:
        if other["slug"] == a["slug"]:
            continue
        w = set(_re.findall(r"[a-z]{5,}", (other.get("title", "") + " " + other.get("dek", "")).lower()))
        score = len(words & w) * 3
        if other["section"] == a["section"]:
            score += 5
        if other.get("type") in ("daily", "feature", "demand"):
            score += 2      # hlubší články drží čtenáře déle
        if score > 0:
            scored.append((score, other))
    scored.sort(key=lambda t: (-t[0], t[1]["date"]))
    return [o for _, o in scored[:n]]


def _faq_jsonld(a: dict) -> str:
    """Otázky a odpovědi pro bohatý výsledek ve vyhledávači."""
    import re as _re
    if a.get("type") not in ("demand", "daily"):
        return ""
    qa = []
    for layer in a.get("layers", []):
        text = _re.sub(r"<[^>]+>", " ", layer["html"])
        parts = _re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
        for i, sent in enumerate(parts):
            if sent.strip().endswith("?") and 20 < len(sent) < 160 and i + 1 < len(parts):
                answer = " ".join(parts[i + 1:i + 3])[:600]
                if len(answer) > 60:
                    qa.append({"@type": "Question", "name": sent.strip(),
                               "acceptedAnswer": {"@type": "Answer", "text": answer}})
        if len(qa) >= 4:
            break
    if len(qa) < 2:
        return ""
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": qa[:5]}, ensure_ascii=False)


def _breadcrumbs(a: dict, site: dict) -> str:
    base = config.origin() + config.base_path() + "/"
    return json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": site["brand"]["name_en"],
             "item": f"{base}{a['lang']}/"},
            {"@type": "ListItem", "position": 2, "name": a.get("section_label", ""),
             "item": f"{base}{a['lang']}/{a['section']}/"},
            {"@type": "ListItem", "position": 3, "name": a.get("title", "")},
        ]}, ensure_ascii=False)


def _jsonld(a: dict, site: dict) -> str:
    brand = site["brand"]
    data = {
        "@context": "https://schema.org", "@type": "NewsArticle",
        "headline": a.get("title", "")[:110],
        "description": a.get("dek", ""),
        # přesný čas vydání, ne jen den — vyhledávače podle něj řadí
        "datePublished": a.get("published_iso") or a.get("date", ""),
        "dateModified": (a.get("updated_at") or a.get("published_iso")
                         or a.get("date", "")),
        "articleSection": a.get("section_label", ""),
        "inLanguage": a.get("lang", "en"),
        "mainEntityOfPage": {"@type": "WebPage", "@id": config.origin() + a["url"]},
        **({"image": [config.origin() + a["image"]]} if a.get("image") else {}),
        "author": {"@type": "Organization", "name": brand["name_en"], "url": brand["url"]},
        "publisher": {"@type": "Organization", "name": brand["name_en"], "url": brand["url"]},
        # U článku v předčasném přístupu je na stránce jen shrnutí, takže
        # se tvrdit, že je volně dostupný celý, nebude. Za pár dní se to
        # samo přepne zpátky.
        "isAccessibleForFree": a.get("access_state") != "early",
    }
    if a.get("origin"):
        data["mainEntityOfPage"] = {"@type": "WebPage", "@id": a["origin"]["url"]}
    elif a.get("syndicated"):
        original_author = a["syndicated"].get("author") or a["syndicated"].get("source")
        if original_author:
            data["author"] = {"@type": "Person", "name": original_author}
        data["mainEntityOfPage"] = {"@type": "WebPage", "@id": a["syndicated"]["url"]}
    return json.dumps(data, ensure_ascii=False)


# Jak se která služba pro měření návštěvnosti jmenuje na stránce
# o soukromí. Odkaz míří na to, co o sobě sama píše.
_ANALYTICS_NAMES = {
    "cloudflare": "[Cloudflare Web Analytics](https://www.cloudflare.com/web-analytics/)",
    "plausible": "[Plausible](https://plausible.io/privacy-focused-web-analytics)",
}


def _e404_html(t: dict, nav: list, lang: str) -> str:
    """Tělo stránky 404: omluva, hledání a rozcestí do rubrik.

    Hledání je obyčejný formulář `GET` do archivu — ten si parametr
    `?q=` přečte sám. Bez javascriptu, bez přesměrování, bez měření.
    """
    esc, bp = _html_mod.escape, config.base_path()
    links = " · ".join(
        f'<a href="{bp}/{lang}/{s["id"]}/">{esc(s.get(lang) or s["en"])}</a>' for s in nav)
    return (
        f'<p class="dek">{esc(t["e404_line"])}</p>'
        f'<form class="e404-find" role="search" method="get" action="{bp}/{lang}/archive/">'
        f'<input type="search" name="q" autocomplete="off" '
        f'placeholder="{esc(t["archive_search"])}" aria-label="{esc(t["archive_search"])}">'
        f'<button type="submit">{esc(t["e404_go"])}</button>'
        f'</form>'
        f'<h2>{esc(t["e404_secs"])}</h2>'
        f'<p class="e404-secs">{links}</p>'
    )


def _privacy_note(text: str, site: dict, t: dict) -> str:
    """Dopíše do stránky o soukromí odstavec o měření — jen když běží."""
    cfg = site.get("analytics") or {}
    which = ("cloudflare" if cfg.get("cloudflare_token")
             else "plausible" if cfg.get("plausible_domain") else "")
    if not which:
        return text
    note = t["priv_analytics"] % _ANALYTICS_NAMES[which]
    # radši před závěrečné „napište nám" než úplně na konec stránky
    for anchor in ("## Ask us anything", "## Zeptejte se nás na cokoli"):
        if anchor in text:
            return text.replace(anchor, f"{note}\n\n{anchor}", 1)
    return f"{text}\n\n{note}\n"


_ABC = {"á": "a", "č": "c", "ď": "d", "é": "e", "ě": "e", "í": "i", "ň": "n",
        "ó": "o", "ř": "r", "š": "s", "ť": "t", "ú": "u", "ů": "u", "ý": "y",
        "ž": "z", "ä": "a", "ö": "o", "ü": "u", "ß": "ss", "å": "a", "ø": "o",
        "æ": "ae", "ł": "l", "ç": "c", "ñ": "n", "ğ": "g", "ı": "i", "ş": "s"}


def _abc(name: str) -> str:
    """Řadicí klíč pro jména zemí — háčky a čárky se pro řazení sundají.

    Čeština by chtěla vlastní abecedu (ch mezi h a i), ale na seznam
    padesáti zemí stačí tohle: Česko před Čínou, Řecko u R, Švédsko u S.
    """
    return "".join(_ABC.get(ch, ch) for ch in name.lower())


def _count_label(n: int, t: dict) -> str:
    """„7 článků", ale „3 články" a „1 článek". Angličtina má tvary dva."""
    key = "count_one" if n == 1 else "count_few" if 2 <= n <= 4 else "count_many"
    return t[key] % n


def _weekend_archive_html(issues: list, t: dict, lang: str) -> str:
    """Přehled sobotních vydání — od nejnovějšího po první číslo.

    Je to obyčejný seznam, ne další noviny: čtenář sem chodí najít jedno
    konkrétní vydání a odejít. Proto tady nejsou perexy ani obrázky.
    """
    esc, bp = _html_mod.escape, config.base_path()
    rows = []
    for ed in issues:
        rows.append(
            f'<li><a href="{bp}/{lang}/weekend/{ed["no"]}/">'
            f'{esc(t["wk_issue"] % ed["no"])}</a> '
            f'<span class="wk-arch-range">{esc(_range_words(ed["start"], ed["end"], lang))}</span> '
            f'<span class="wk-arch-count">{esc(_count_label(ed["count"], t))}</span></li>'
        )
    return (f'<p class="dek">{esc(t["wk_archive_intro"])}</p>'
            f'<ol class="wk-arch">{"".join(rows)}</ol>')


HUB_MIN = 3          # míň než tři články rozcestník nepotřebuje


def _hubs(arts: list, lang: str, site: dict) -> list:
    """Rozcestníky podle zájmů z data/interests.yml.

    Štítky u článku počítá engine/interests.py při stavbě webu, takže
    rozcestník je jen jiný pohled na tentýž veřejný seznam — nic se
    neodvozuje z chování čtenáře a nic se nikam neposílá.

    Zdravotní skupina má vlastní příznak: na takové stránce se pak
    ukáže stálá poznámka, že zdraví je tady téma, ne rada
    (EDITORIAL-CODE, oddíl 5).
    """
    meta: dict = {}
    for g in interests.catalogue():
        for it in g.get("items", []):
            meta[it["id"]] = (it.get(lang) or it.get("en") or it["id"], g.get("id") == "health")

    buckets: dict = {}
    for a in arts:
        for tag in (a.get("tags_csv") or "").split(","):
            if tag in meta:
                buckets.setdefault(tag, []).append(a)

    order = [s["id"] for s in site["sections"]]
    sec_label = {s["id"]: (s.get(lang) or s["en"]) for s in site["sections"]}
    hubs = []
    for tag, (label, is_health) in meta.items():          # pořadí z katalogu
        group = buckets.get(tag, [])
        if len(group) < HUB_MIN:
            continue
        # Odkaz zpátky do rubriky, ze které je téma nejvíc doma. U shody
        # rozhoduje pořadí rubrik v site.yml, ať se stránka mezi stavbami
        # nepřehazuje. Zdravotní téma patří do Zdraví, i když zrovna víc
        # článků vyšlo jinde — jinak by to čtenáři nedávalo smysl.
        counts: dict = {}
        for a in group:
            counts[a["section"]] = counts.get(a["section"], 0) + 1
        top = min(counts, key=lambda sec: (-counts[sec], order.index(sec)
                                           if sec in order else len(order)))
        if is_health and "health" in order:
            top = "health"
        hubs.append({
            "id": tag, "label": label, "health": is_health,
            "count_label": _count_label(len(group), STRINGS.get(lang, STRINGS["en"])),
            "url": f"{config.base_path()}/{lang}/topic/{tag}/",
            "articles": group,
            "section": top, "section_label": sec_label.get(top, top),
        })
    return hubs


def _site_jsonld(site: dict, lang: str) -> str:
    """Kdo web vydává a kde se v něm hledá — jen na titulní straně.

    `SearchAction` míří do archivu: ten má vlastní hledání a rozumí
    parametru `?q=`. Hledá se přímo v prohlížeči a nikam se neodesílá,
    takže se tím o čtenáři nic nedozvíme ani my, ani vyhledávač.
    """
    brand = site["brand"]
    name = brand["name_cs"] if lang == "cs" else brand["name_en"]
    tagline = brand["tagline_cs"] if lang == "cs" else brand["tagline_en"]
    base = config.origin() + config.base_path()
    home = f"{base}/{lang}/"
    org = {
        "@type": "Organization",
        "@id": f"{base}/#organization",
        "name": brand["name_en"],
        "alternateName": brand["name_cs"],
        "url": brand["url"],
        "email": brand.get("email", ""),
        "description": tagline,
        "contactPoint": {
            "@type": "ContactPoint",
            "email": brand.get("email", ""),
            "contactType": "editorial",
            "availableLanguage": ["en", "cs"],
        },
    }
    website = {
        "@type": "WebSite",
        "@id": f"{home}#website",
        "url": home,
        "name": name,
        "description": tagline,
        "inLanguage": lang,
        "publisher": {"@id": org["@id"]},
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{home}archive/?q={{search_term_string}}",
            },
            "query-input": "required name=search_term_string",
        },
    }
    return json.dumps({"@context": "https://schema.org", "@graph": [website, org]},
                      ensure_ascii=False)


def _republish_html(a: dict, site: dict) -> str:
    """Hotový kus HTML, který si jiné médium jen zkopíruje."""
    r = site.get("republish", {})
    brand, url = site["brand"], config.origin() + a["url"]
    parts = [f"<h1>{a['title']}</h1>", f"<p><em>{a.get('dek', '')}</em></p>"]
    for layer in a.get("layers", []):
        parts.append(f"<h2>{layer['label']}</h2>")
        parts.append(layer["html"])
    if a.get("body_html"):
        parts.append(a["body_html"])
    parts.append(
        f'<p><em>This article was originally published by '
        f'<a href="{url}">{brand["name_en"]}</a> and is republished under a '
        f'<a href="{r.get("license_url", "")}">{r.get("license", "")}</a> licence.</em></p>'
    )
    parts.append(f'<img src="{config.origin()}{config.base_path()}/px.gif?a={a["slug"]}" alt="" width="1" height="1">')
    return "\n".join(parts)


MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "cs": ["ledna", "února", "března", "dubna", "května", "června", "července",
           "srpna", "září", "října", "listopadu", "prosince"],
}
DAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "cs": ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"],
}


def _date_words(iso: str, lang: str) -> str:
    """'2026-08-17' → '17 August' / '17. srpna'. Prázdné vstupu nevadí."""
    try:
        d = dt.date.fromisoformat(str(iso)[:10])
    except (TypeError, ValueError):
        return ""
    months = MONTHS.get(lang, MONTHS["en"])
    if lang == "cs":
        return f"{d.day}. {months[d.month - 1]}"
    return f"{d.day} {months[d.month - 1]}"


def _date_label(lang: str) -> str:
    d = dt.date.today()
    days, months = DAYS.get(lang, DAYS["en"]), MONTHS.get(lang, MONTHS["en"])
    if lang == "cs":
        return f"{days[d.weekday()]} {d.day}. {months[d.month - 1]} {d.year}"
    return f"{days[d.weekday()]}, {d.day} {months[d.month - 1]} {d.year}"


# „v sobotu", ne „Sobota". Čeština má u dne v týdnu po předložce jiný
# tvar a věta „Příští vydání vyjde Sobota 22. srpna" by byla patvar.
_CS_DAY_IN = ["v pondělí", "v úterý", "ve středu", "ve čtvrtek",
              "v pátek", "v sobotu", "v neděli"]


def _day_words(iso: str, lang: str) -> str:
    """'2026-08-22' → 'Saturday, 22 August' / 'v sobotu 22. srpna'."""
    try:
        d = dt.date.fromisoformat(str(iso)[:10])
    except (TypeError, ValueError):
        return ""
    if lang == "cs":
        return f"{_CS_DAY_IN[d.weekday()]} {_date_words(iso, lang)}"
    days = DAYS.get(lang, DAYS["en"])
    return f"{days[d.weekday()]}, {_date_words(iso, lang)}"


def _range_words(start: str, end: str, lang: str) -> str:
    """Rozsah dnů, který vydání pokrývá — tak, jak by ho napsal člověk.

    '9–15 August 2026', přes přelom měsíce '28 July – 3 August 2026'.
    Česky '9.–15. srpna 2026' a '28. července – 3. srpna 2026'.
    """
    try:
        a = dt.date.fromisoformat(str(start)[:10])
        b = dt.date.fromisoformat(str(end)[:10])
    except (TypeError, ValueError):
        return ""
    months = MONTHS.get(lang, MONTHS["en"])
    if a.year == b.year and a.month == b.month:
        if lang == "cs":
            return f"{a.day}.–{b.day}. {months[b.month - 1]} {b.year}"
        return f"{a.day}–{b.day} {months[b.month - 1]} {b.year}"
    left = _date_words(a.isoformat(), lang)
    if a.year != b.year:
        left = f"{left} {a.year}"
    return f"{left} – {_date_words(b.isoformat(), lang)} {b.year}"


def _write(path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _asset_version() -> str:
    """Short content hash used to invalidate cached CSS and JavaScript."""
    digest = hashlib.sha256()
    for name in ("style.css", "reader.js", "live.js", "quiz.js"):
        path = config.STATIC / name
        digest.update(name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def run() -> None:
    site = config.site()
    brand_key = "name_cs"
    out = config.PUBLIC
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    env = Environment(
        loader=FileSystemLoader(str(config.TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )
    # '2026-08-10'|datewords('cs') → '10. srpna'. V sobotním vydání se
    # datum píše slovy: '2026-08-10' vypadá jako výpis z databáze.
    env.filters["datewords"] = _date_words

    langs = [site["languages"]["master"], *site["languages"]["translations"]]
    today = dt.date.today().isoformat()
    asset_version = _asset_version()
    daily_quizzes = quizzes.load_all(today)

    # --- nejdřív se načtou všechny jazyky, teprve pak se staví ---------
    # Kvůli odkazům `hreflang`: aby se dalo poctivě napsat, ve kterých
    # jazycích ta stránka opravdu existuje. Půlka anglických článků
    # česky nevyšla a odkaz na nepřeloženou verzi vede na 404.
    everything: dict = {}
    for lang in langs:
        published = [
            (m, b, members.state(m, today), pth)
            for m, b, pth in article.load_all(lang)
            if m.get("status") == "published" and m.get("date", "9999") <= today
        ]
        # Text psaný jen pro členy se na web nevydá vůbec: nemá stránku,
        # není v sitemapě, ve zdroji RSS, v articles.json ani v žádném
        # výpisu. Na stránce pro členy je z něj vidět titulek a perex,
        # aby bylo poznat, co se posílá e-mailem.
        arts = [_view(m, b, pth) for m, b, st, pth in published if st != "members"]
        arts.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)
        hubs = _hubs(arts, lang, site) if (site.get("seo_plus") or {}).get("topic_hubs") else []
        # Sobotní vydání — týden složený z toho, co už vyšlo. Skládá se
        # tady, ještě před stavbou stránek, protože z něj vede odkaz
        # v menu a hlavička každé stránky potřebuje vědět, jestli vůbec
        # nějaké vydání existuje. Podrobně: engine/weekend.py.
        issues = weekend.plan(arts, lang=lang, today=today)
        everything[lang] = {
            "published": published, "arts": arts, "hubs": hubs,
            "slugs": {f"{a['section']}/{a['slug']}/" for a in arts},
            "hub_ids": {h["id"] for h in hubs},
            "issues": issues, "issue_nos": {i["no"] for i in issues},
        }

    def langs_with_article(a: dict) -> list:
        """Jazyky, ve kterých ten článek opravdu vyšel."""
        path = f"{a['section']}/{a['slug']}/"
        return [l for l in langs if path in everything[l]["slugs"]] or [a["lang"]]

    def langs_with_hub(hub_id: str) -> list:
        """Jazyky, ve kterých má rozcestník dost článků, aby vznikl."""
        return [l for l in langs if hub_id in everything[l]["hub_ids"]]

    def langs_with_issue(no: int) -> list:
        """Jazyky, ve kterých se to číslo sobotního vydání postavilo.

        Česká verze se skládá výhradně z českých článků. Když jich za ten
        týden nebylo dost, číslo česky prostě nevyjde — a odkaz na
        neexistující stránku se do hlavičky nedostane.
        """
        return [l for l in langs if no in everything[l]["issue_nos"]]

    for lang in langs:
        t = STRINGS.get(lang, STRINGS["en"])
        brand = site["brand"]["name_cs"] if lang == "cs" else site["brand"]["name_en"]
        tagline = site["brand"]["tagline_cs"] if lang == "cs" else site["brand"]["tagline_en"]

        published = everything[lang]["published"]
        arts = everything[lang]["arts"]
        quiz_views = [quizzes.view(item, lang, config.base_path()) for item in daily_quizzes]

        by_mail = sorted(
            ({"title": m.get("title", ""), "dek": m.get("dek", ""),
              "date": m.get("date", ""), "section": m.get("section", ""),
              "tier": m.get("tier", "")}
             for m, _, st, _p in published if st == "members"),
            key=lambda a: a["date"], reverse=True,
        )
        in_early = [a for a in arts if a["access_state"] == "early"]

        filled = {a["section"] for a in arts}
        nav = [s for s in site["sections"] if s.get("primary") or s["id"] in filled]

        # Sobotní vydání jako první položka menu — je to to jediné na
        # webu, co má konec, a stojí za to, aby ho čtenář našel hned.
        # Odkaz míří rovnou na aktuální číslo, ne na /weekend/: ta adresa
        # jen přesměrovává a čtenář by čekal na jedno načtení navíc.
        # Když se ten týden vydání nepostavilo, není v menu vůbec nic.
        issues = everything[lang]["issues"]
        if issues:
            nav = [{"id": f"weekend/{issues[0]['no']}",
                    "en": STRINGS["en"]["wk_nav"], "cs": STRINGS["cs"]["wk_nav"]}, *nav]

        common = dict(
            lang=lang, brand=brand, tagline=tagline, t=t,
            sections=nav, all_sections=site["sections"], all_langs=langs,
            site_url=config.origin(), base=config.base_path(), current_section=None,
            asset_version=asset_version,
            seo=site.get("seo", {}), newsletter=site.get("newsletter", {}),
            wider_lens=site.get("wider_lens", {}),
            wit=quotes.wit(),
            interest_groups=interests.catalogue(),
            partners=site.get("partners", []),
            brand_email=site["brand"].get("email", ""),
            today_label=_date_label(lang),
            nl_headline=(site.get("newsletter", {}).get(f"headline_{lang}")
                         or site.get("newsletter", {}).get("headline_en", "")),
            nl_text=(site.get("newsletter", {}).get(f"text_{lang}")
                     or site.get("newsletter", {}).get("text_en", "")),
            nl_button=(site.get("newsletter", {}).get(f"button_{lang}")
                       or site.get("newsletter", {}).get("button_en", "")),
            mem=members.cfg(),
            # Měření návštěvnosti. Dokud jsou obě políčka v site.yml
            # prázdná, nevloží se do stránky vůbec nic — ani komentář.
            analytics=site.get("analytics") or {},
            og_locale=LOCALES.get(lang, "en_GB"), og_locales=LOCALES,
            # výchozí hodnoty, které si každá stránka přepíše přes page()
            canonical="", alt_path="", page_type="page", home_jsonld="", noindex=False,
            alt_langs=langs,
        )

        def page(path: str = "", ptype: str = "page", **extra) -> dict:
            """Kontext jedné stránky: kanonická adresa, jazykové varianty, typ.

            `path` je cesta za jazykem ('world/', 'topic/space/', '' pro
            titulní stranu). Je stejná pro všechny jazyky, takže z ní jde
            odvodit i `hreflang`.
            """
            return {**common, "page_type": ptype, "alt_path": path,
                    "canonical": f"{config.origin()}{config.base_path()}/{lang}/{path}",
                    **extra}

        # --- rozcestníky podle témat ----------------------------------
        # Člověk hledá „výzkum cukrovky", ne titulek. Rozcestník je
        # stránka, která na takový dotaz odpovídá — a zároveň drží
        # pohromadě, co jsme k tématu za měsíce napsali.
        hubs = everything[lang]["hubs"]
        hub_by_id = {h["id"]: h for h in hubs}

        # --- článek ---
        rep_cfg = site.get("republish", {})
        seo = site.get("seo", {})
        for a in arts:
            early = a["access_state"] == "early"
            a["jsonld"] = _jsonld(a, site)
            # Otázky a odpovědi pro vyhledávač i hotové HTML k převzetí
            # se skládají z vrstev článku. U předčasného přístupu by tím
            # celý text propadl do stránky zadními dveřmi.
            a["faq"] = "" if early else _faq_jsonld(a)
            a["crumbs"] = _breadcrumbs(a, site)
            a["related"] = _related(a, arts, int(seo.get("related_count", 3)))
            # Rozcestníky, do kterých článek patří — řádek „Víc k tématu"
            # pod textem. Bere se ze štítků článku, ne z nastavení čtenáře.
            a["hubs"] = [
                {"id": h["id"], "label": h["label"], "url": h["url"]}
                for tag in (a.get("tags_csv") or "").split(",")
                if (h := hub_by_id.get(tag))
            ][:4]
            a["republish"] = (
                _republish_html(a, site)
                if not early and rep_cfg.get("enabled")
                and a.get("type") in rep_cfg.get("types", [])
                and not a.get("syndicated")
                else ""
            )
            # kanonickou adresu si článek řeší sám (převzatý text míří
            # na originál), proto se tu z page() nebere
            _write(out / lang / a["section"] / a["slug"] / "index.html",
                   env.get_template("article.html").render(
                       a=a, **{**common, "page_type": "article",
                               "alt_langs": langs_with_article(a)}))

        # --- rozcestníky podle témat ---
        for h in hubs:
            _write(out / lang / "topic" / h["id"] / "index.html",
                   env.get_template("hub.html").render(
                       **page(f"topic/{h['id']}/", "hub", hub=h,
                              alt_langs=langs_with_hub(h["id"]))))

        # --- titulní strana ---
        briefing = [a for a in arts if a["type"] in ("news", "daily", "demand")][:7]
        # v čele webu má stát náš vlastní článek dne, ne převzatý text
        prio = {"daily": 0, "feature": 1, "demand": 2, "analysis": 3, "news": 4,
                "syndicated": 8, "imported": 9}
        lead = min(
            arts,
            key=lambda a: (a["date"] < today, prio.get(a.get("type"), 5), -a.get("words", 0)),
        ) if arts else None
        used = {lead["slug"]} if lead else set()
        rows = []
        for sec in nav:
            sub = [a for a in arts if a["section"] == sec["id"] and a["slug"] not in used][:4]
            if len(sub) >= 1:
                rows.append({
                    "id": sec["id"],
                    "label": sec.get(lang) or sec["en"], "articles": sub,
                })
        _write(out / lang / "index.html",
               env.get_template("index.html").render(
                   impact_rail=[a for a in arts if a.get("impact")][:4],
                   briefing=briefing, lead=lead, articles=arts[1:9],
                   daily_quiz=(quiz_views[0] if quiz_views else None),
                   rows=rows, ticker=_ticker(site, lang),
                   thought=quotes.thought(),
                   **page("", "home", home_jsonld=_site_jsonld(site, lang))))

        # --- ranní briefing -------------------------------------------
        # Jedna konečná stránka: živé signály s přímým zdrojem, naše
        # ověřené články za přesných 24 hodin a dnešní body ke sledování.
        # Výběr země si až v prohlížeči aplikuje reader.js, takže se
        # osobní nastavení nikdy nedostane do buildu ani do analytiky.
        _write(out / lang / "briefing" / "index.html",
               env.get_template("briefing.html").render(
                   briefing=morning.edition(arts, site, lang),
                   daily_quiz=(quiz_views[0] if quiz_views else None),
                   country_catalogue=countries.catalogue(),
                   **page("briefing/", "briefing", current_section="briefing")))

        # --- samostatné denní kvízy ----------------------------------
        # Výsledek se počítá v prohlížeči. Build dostane jen deklarativní
        # data, nikdy kód z automaticky vytvořeného kvízu.
        _write(out / lang / "quizzes" / "index.html",
               env.get_template("quizzes.html").render(
                   quizzes=quiz_views,
                   **page("quizzes/", "quizzes", current_section="quizzes")))
        quiz_labels = {
            "score": ("Your result score: {score}" if lang == "en" else "Vaše výsledné skóre: {score}"),
            "correct": ("{score} of {total} correct" if lang == "en" else "Správně {score} z {total}"),
            "profile": ("Your strongest current pattern" if lang == "en" else "Váš nejsilnější současný vzorec"),
            "next_title": ("A useful experiment" if lang == "en" else "Užitečný pokus"),
            "watch_title": ("Keep this in perspective" if lang == "en" else "Zachovejte si odstup"),
        }
        for quiz in quiz_views:
            canonical = f"{config.origin()}{quiz['url']}"
            quiz_jsonld = json.dumps({
                "@context": "https://schema.org", "@type": "Quiz",
                "name": quiz["title"], "description": quiz["dek"],
                "datePublished": quiz["date"], "inLanguage": lang,
                "educationalUse": "self assessment", "isAccessibleForFree": True,
                "url": canonical, "provider": {"@type": "Organization", "name": brand},
            }, ensure_ascii=False).replace("</", "<\\/")
            _write(out / lang / "quizzes" / quiz["slug"] / "index.html",
                   env.get_template("quiz.html").render(
                       quiz=quiz, quiz_labels=quiz_labels, quiz_jsonld=quiz_jsonld,
                       **page(f"quizzes/{quiz['slug']}/", "quiz", current_section="quizzes")))

        # --- rubriky ---
        # Proužek rychlých zpráv patří všude, kde čtenář chce vědět, co se
        # děje. V klidných rubrikách (`calm: true` v data/site.yml) by ale
        # rušil — tam je člověk kvůli něčemu jinému.
        for s in site["sections"]:
            sub = [a for a in arts if a["section"] == s["id"]]
            _write(out / lang / s["id"] / "index.html",
                   env.get_template("section.html").render(
                       articles=sub, section_label=s.get(lang) or s["en"],
                       section_calm=bool(s.get("calm")),
                       ticker=({"items": []} if s.get("calm") else
                               _ticker(site, lang, preferred_section=s["id"])),
                       thought=quotes.thought(),
                       **page(f"{s['id']}/", "section", current_section=s["id"])))

        # --- sobotní vydání ---------------------------------------------
        # Poskládané je už z první části běhu (engine/weekend.py), tady
        # se z něj dělají stránky. Každé číslo má vlastní trvalou adresu
        # /weekend/<číslo>/ a stará čísla se staví znovu při každé stavbě
        # webu — vždycky vyjdou stejně, protože se skládají z článků,
        # které se nemění.
        for ed in issues:
            _write(out / lang / "weekend" / str(ed["no"]) / "index.html",
                   env.get_template("weekend.html").render(
                       ed=ed,
                       ed_range=_range_words(ed["start"], ed["end"], lang),
                       ed_close=_day_words(ed["date"], lang),
                       ed_next=_day_words(ed["next"], lang),
                       thought=quotes.thought(),
                       **page(f"weekend/{ed['no']}/", "weekend",
                              current_section=f"weekend/{ed['no']}",
                              alt_langs=langs_with_issue(ed["no"]))))
        if issues:
            # Přehled starších čísel. Každé z nich je hotové a zůstává,
            # jaké bylo — tohle je jediné místo, odkud se k nim dá dostat.
            _write(out / lang / "weekend" / "archive" / "index.html",
                   env.get_template("page.html").render(
                       page_title=t["wk_archive_title"],
                       page_html=_weekend_archive_html(issues, t, lang),
                       **page("weekend/archive/", "page",
                              alt_langs=[l for l in langs if everything[l]["issues"]])))
            # Prostá adresa /weekend/ vede vždycky na nejnovější číslo.
            # Statický web neumí přesměrovat na serveru, takže je to
            # stejná stránka s odkazem, jakou má kořen webu.
            newest = f"{config.base_path()}/{lang}/weekend/{issues[0]['no']}/"
            _write(out / lang / "weekend" / "index.html",
                   f'<!doctype html><html lang="{lang}"><meta charset="utf-8">'
                   f'<meta http-equiv="refresh" content="0; url={newest}">'
                   f'<link rel="canonical" href="{newest}">'
                   f'<meta name="robots" content="noindex,follow">'
                   f'<title>{_html_mod.escape(t["wk_title"])} — {_html_mod.escape(brand)}</title>'
                   f'<p>{_html_mod.escape(t["wk_redirect"])} '
                   f'<a href="{newest}">{_html_mod.escape(t["wk_title"])}</a></p>')

        # --- archiv: všechno, co kdy vyšlo, na jedné stránce ------------
        # Kvůli vyhledávačům i kvůli čtenáři. Statický web nemá databázi,
        # ale tohle je to, co databáze v praxi nahrazuje: jeden trvalý
        # rozcestník, ze kterého vede odkaz na každý článek.
        by_year: dict = {}
        for a in arts:
            by_year.setdefault(a["date"][:4], []).append(a)
        years = [{"year": y, "articles": sorted(v, key=lambda x: x["date"], reverse=True)}
                 for y, v in sorted(by_year.items(), reverse=True)]
        _write(out / lang / "archive" / "index.html",
               env.get_template("archive.html").render(
                   years=years, total=len(arts), **page("archive/", "archive")))

        # --- The Wider Lens: jen články, které skutečně obsahují audit
        # důkazů i doložené různé perspektivy. Značka není ruční štítek.
        lens_articles = [a for a in arts if a.get("is_wider_lens")]
        _write(out / lang / "wider-lens" / "index.html",
               env.get_template("lens.html").render(
                   articles=lens_articles,
                   **page("wider-lens/", "archive", current_section="wider-lens")))

        # --- stránka pro média, která chtějí naše články převzít ---
        if site.get("republish", {}).get("enabled"):
            _write(out / lang / "republish" / "index.html",
                   env.get_template("page.html").render(
                       page_title=t["republish_title"],
                       page_html=_html(t["republish_body"].format(
                           license=site["republish"]["license"],
                           license_url=site["republish"]["license_url"],
                           email=site["brand"]["email"])),
                       **page("republish/", "page")))

        # --- počasí ---
        # výchozí místo, dokud si čtenář nevybere svoje
        wx_default = {"cs": {"name": "Praha", "country": "", "admin": "", "lat": 50.08, "lon": 14.44}}.get(
            lang, {"name": "London", "country": "", "admin": "", "lat": 51.51, "lon": -0.13})
        _write(out / lang / "weather" / "index.html",
               env.get_template("weather.html").render(
                   weather_default=json.dumps(wx_default, ensure_ascii=False),
                   **page("weather/", "weather")))

        # --- seznam všech článků pro prohlížeč ------------------------
        # Web nemá server ani databázi, takže osobní výběr musí sestavit
        # prohlížeč sám. Dostane k tomu tenhle seznam — je pro všechny
        # stejný, nikdo se z něj nedozví, co koho zajímá.
        index = [{
            "u": a["url"], "t": a["title"], "d": (a.get("dek") or "")[:180],
            "s": a["section"], "sl": a["section_label"], "dt": a["date"],
            "g": a.get("tags_csv", ""), "p": a.get("topics_csv", ""),
            "l": a.get("load", 0), "b": a.get("band", "mid"),
            "i": a.get("image") or "", "y": a.get("type", ""),
            "im": (a.get("impact") or {}).get("line", ""),
            "ia": ",".join((a.get("impact") or {}).get("areas", [])),
            "it": (a.get("impact") or {}).get("todo", ""),
            "c": ",".join((a.get("countries") or {}).get("direct", [])),
            "cr": (a.get("countries") or {}).get("scope", "none"),
        } for a in arts]
        _write(out / lang / "articles.json",
               json.dumps(index, ensure_ascii=False, separators=(",", ":")))

        # --- co to znamená pro tebe ------------------------------------
        with_impact = [a for a in arts if a.get("impact")]
        _write(out / lang / "impact" / "index.html",
               env.get_template("impact.html").render(
                   articles=with_impact, areas=impact.AREAS, **page("impact/", "page")))

        # --- velké problémy -------------------------------------------
        # Deset problémů, které má celý svět. Na každý jedna stránka a na
        # ní tři sloupce: co se opravdu zkusilo (skutečná země, měřený
        # výsledek, zdroj), co by optimalizoval stroj (počet, ne rada) —
        # a co by stroji uniklo. Ten třetí sloupec je důvod, proč tahle
        # rubrika existuje. Bez něj by to byly chytré rady od stroje,
        # a to je přesně to, co dělat nechceme.
        probs = problems.load(lang)
        for pr in probs:
            _write(out / lang / "problems" / pr["id"] / "index.html",
                   env.get_template("problem.html").render(
                       page=pr, **page(f"problems/{pr['id']}/", "page")))
        if probs:
            _write(out / lang / "problems" / "index.html",
                   env.get_template("problems.html").render(
                       pages=probs, **page("problems/", "page")))

        # --- co to znamená pro mou zemi -------------------------------
        # Stejná zpráva dopadá jinak v Irsku a jinak v Polsku. Tahle
        # stránka bere posledních čtrnáct dní a ptá se za čtenáře:
        # co z toho doopravdy doletí až ke mně a co s tím můžu dělat.
        #
        # Stránka vzniká pro každou zemi ze seznamu, i pro tu, ke které
        # zrovna nic nevyšlo — čtenářova volba je uložená v prohlížeči
        # a nesmí skončit na chybě 404. Zemím s méně než dvěma zprávami
        # se nastaví `noindex`: prázdnou stránku nemá cenu nabízet
        # vyhledávači, ale čtenáři ano.
        lands = countries.pages(arts, lang=lang, today=today)
        # Seznam v rozcestníku se řadí podle jména, které čtenář vidí —
        # v české verzi tedy česky, včetně háčků a čárek (Česko patří
        # před Čínu, ne za ni).
        lands.sort(key=lambda c: _abc(c["label"]))
        land_list = [{"code": c["code"], "label": c["label"], "count": c["count"]}
                     for c in lands]
        for c in lands:
            _write(out / lang / "country" / c["code"] / "index.html",
                   env.get_template("country.html").render(
                       country=c, countries=land_list,
                       window_label=_range_words(c["from"], c["to"], lang),
                       # „1 zpráva", „3 zprávy", „7 zpráv" — čeština má tři tvary
                       count_label=_count_label(c["count"], t),
                       **page(f"country/{c['code']}/", "country",
                              noindex=c["thin"])))
        # rozcestník: mapa všech zemí, odtud si čtenář vybírá
        _write(out / lang / "country" / "index.html",
               env.get_template("country.html").render(
                   country=None, countries=land_list, window_label="",
                   **page("country/", "page")))

        # --- osobní výběr ---------------------------------------------
        _write(out / lang / "foryou" / "index.html",
               env.get_template("foryou.html").render(**page("foryou/", "page")))

        # --- členství -------------------------------------------------
        # Jediná stránka, kde je vidět, co členství je: úrovně, co se
        # právě drží v předčasném přístupu a co vychází jen e-mailem.
        if members.enabled():
            _write(out / lang / "members" / "index.html",
                   env.get_template("members.html").render(
                       tiers=members.tiers(lang), early=in_early,
                       by_mail=by_mail, **page("members/", "page")))

        # --- statické stránky ---
        for name in ("about", "start", "privacy", "terms"):
            src = config.DATA / "pages" / f"{name}.{lang}.md"
            page_lang = lang
            if not src.exists():
                src = config.DATA / "pages" / f"{name}.en.md"
                page_lang = "en"
            if src.exists():
                raw = src.read_text(encoding="utf-8").replace("{email}", site["brand"]["email"])
                title = raw.splitlines()[0].lstrip("# ").strip()
                text = "\n".join(raw.splitlines()[1:])
                # Stránka o soukromí musí zůstat pravdivá i potom, co
                # majitel zapne měření návštěvnosti. Odstavec o něm se
                # proto dopíše sám — a zase sám zmizí, když se vypne.
                if name == "privacy":
                    text = _privacy_note(text, site, STRINGS.get(page_lang, STRINGS["en"]))
                _write(out / lang / name / "index.html",
                       env.get_template("page.html").render(
                           page_title=title, page_html=_html(text),
                           **page(f"{name}/", "page")))

        # --- předpovědi ---
        fc = analyst.load_forecasts()["forecasts"]
        _write(out / lang / "forecasts" / "index.html",
               env.get_template("forecasts.html").render(
                   score={**(_sc := analyst.scoreboard()),
                          "verdict": t.get("v_" + _sc["verdict"], _sc["verdict"])},
                   open=[f for f in fc if f["status"] == "open"],
                   resolved=sorted([f for f in fc if f["status"] == "resolved"],
                                   key=lambda f: f.get("resolved_on", ""), reverse=True),
                   void=[f for f in fc if f["status"] == "void"],
                   **page("forecasts/", "page")))

        # --- RSS ---
        _write(out / lang / "feed.xml", _feed(arts[:30], brand, tagline, site["brand"]["url"], lang))

        # --- stránka 404 ----------------------------------------------
        # GitHub Pages ji nabídne sám, kdykoli adresa nikam nevede.
        # Staví se v hlavním jazyce — ze špatné adresy se jazyk poznat nedá.
        if lang == site["languages"]["master"]:
            _write(out / "404.html",
                   env.get_template("page.html").render(
                       page_title=t["e404_title"],
                       page_html=_e404_html(t, nav, lang),
                       **page("", "404", canonical="")))

    # --- kořen webu ---
    master = site["languages"]["master"]
    bp = config.base_path()
    _write(out / "index.html",
           f'<!doctype html><meta charset="utf-8">'
           f'<meta http-equiv="refresh" content="0; url={bp}/{master}/briefing/">'
           f'<link rel="canonical" href="{bp}/{master}/briefing/">'
           f'<title>{site["brand"]["name_en"]}</title>'
           f'<p>→ <a href="{bp}/{master}/briefing/">{site["brand"]["name_en"]} Briefing</a></p>')
    # robots.txt — co smí robot vyhledávače a kde najde mapu webu.
    # SeznamBot a Googlebot-News uvádíme zvlášť, ať je to jednoznačné;
    # roboty, které jen odsávají obsah na trénink, sem nepatří.
    _write(out / "robots.txt", "\n".join([
        "User-agent: *",
        "Allow: /",
        f"Disallow: {config.base_path()}/admin/",
        "",
        "User-agent: SeznamBot",
        "Allow: /",
        "",
        "User-agent: Googlebot-News",
        "Allow: /",
        "",
        f"Sitemap: {site['brand']['url']}/sitemap.xml",
        f"Sitemap: {site['brand']['url']}/sitemap-news.xml",
        "",
    ]))

    # Klíč pro IndexNow. Vyhledávač si tímhle souborem ověří, že adresy
    # hlásí opravdu majitel webu. Bez něj by se ohlášení zahodilo.
    if indexnow.write_key_file(out):
        config.log(f"IndexNow: klíč vystaven na {indexnow.key_location()}")

    # admin sekce — bez tokenu je to prázdná stránka, proto může být veřejně
    admin_src = config.ROOT / "admin"
    if admin_src.exists():
        shutil.copytree(admin_src, out / "admin")
    _write(out / "sitemap-pages.xml", _sitemap(out, config.origin() + config.base_path()))
    _write(out / "sitemap-news.xml", _news_sitemap(site))
    base = config.origin() + config.base_path()
    _write(out / "sitemap.xml",
           '<?xml version="1.0" encoding="UTF-8"?>'
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           f"<sitemap><loc>{base}/sitemap-pages.xml</loc></sitemap>"
           f"<sitemap><loc>{base}/sitemap-news.xml</loc></sitemap>"
           "</sitemapindex>")

    for item in config.STATIC.iterdir():
        if item.name == "covers":
            continue
        (shutil.copytree if item.is_dir() else shutil.copy2)(item, out / item.name)

    # rejstřík pro admin — díky němu si admin nemusí stahovat všechny články
    index = []
    for lang in langs:
        for m, _, path in article.load_all(lang):
            st = members.state(m)
            index.append({
                "lang": lang, "slug": m.get("slug", ""), "title": m.get("title", ""),
                "dek": m.get("dek", ""), "date": m.get("date", ""),
                "status": m.get("status", ""), "section": m.get("section", ""),
                "type": m.get("type", ""), "depth": m.get("depth", ""),
                "confidence": m.get("confidence", 0),
                "path": f"content/{lang}/{path.name}",
                "access": st,
                # text jen pro členy nemá na webu stránku, tak ať se na
                # ni z adminu neodkazuje
                "url": _url(m) if m.get("status") == "published" and st != "members" else "",
                "review": m.get("review", {}), "problems": m.get("problems", []),
            })
    index.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)
    (config.DATA / "admin-index.json").write_text(
        json.dumps({"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                    "articles": index}, ensure_ascii=False, indent=1), encoding="utf-8")

    n = sum(1 for _ in out.rglob("index.html"))
    config.log(f"Web postaven: {n} stránek → {out}")


def _feed(arts: list, brand: str, tagline: str, url: str, lang: str) -> str:
    items = "".join(
        f"<item><title>{sx.escape(a['title'])}</title>"
        f"<link>{url}{a['url']}</link><guid>{url}{a['url']}</guid>"
        f"<pubDate>{a['date']}</pubDate>"
        f"<description>{sx.escape(a.get('dek', ''))}</description></item>"
        for a in arts
    )
    return (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
            f"<title>{sx.escape(brand)}</title><link>{url}/{lang}/</link>"
            f"<description>{sx.escape(tagline)}</description>{items}</channel></rss>")


def _news_sitemap(site: dict) -> str:
    """Sitemap pro Google News — bere jen články z posledních dvou dnů."""
    cutoff = (dt.date.today() - dt.timedelta(days=2)).isoformat()
    brand = site["brand"]
    rows = []
    for lang in [site["languages"]["master"], *site["languages"]["translations"]]:
        for m, _, _ in article.load_all(lang):
            if m.get("status") != "published" or m.get("date", "") < cutoff:
                continue
            # Text jen pro členy tady nemá co dělat — nemá stránku.
            # Článek v předčasném přístupu má `noindex`, takže by bylo
            # rovnou proti sobě hlásit ho do zpravodajské sitemapy.
            if members.state(m) != "public":
                continue
            loc = f"{config.origin()}{config.base_path()}/{lang}/{m['section']}/{m['slug']}/"
            rows.append(
                f"<url><loc>{loc}</loc><news:news>"
                f"<news:publication><news:name>{sx.escape(brand['name_en'])}</news:name>"
                f"<news:language>{lang}</news:language></news:publication>"
                f"<news:publication_date>{m['date']}</news:publication_date>"
                f"<news:title>{sx.escape(m.get('title', ''))}</news:title>"
                f"</news:news></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
            + "".join(rows) + "</urlset>")


def _sitemap(out, url: str) -> str:
    urls = []
    for p in sorted(out.rglob("index.html")):
        rel = str(p.parent.relative_to(out)).replace("\\", "/")
        if rel.startswith("admin"):
            continue
        # /weekend/ je jen přesměrování na nejnovější číslo. Do mapy webu
        # patří samo číslo (/weekend/3/), ne rozcestí k němu.
        if rel.endswith("/weekend"):
            continue
        # Stránka označená `noindex` do mapy webu nepatří — poslat ji tam
        # znamená říct vyhledávači dvě opačné věci najednou. Týká se to
        # zemí, ke kterým zrovna skoro nic nevyšlo.
        if 'content="noindex"' in p.read_text(encoding="utf-8"):
            continue
        loc = f"{url}/" if rel == "." else f"{url}/{rel}/"
        urls.append(f"<url><loc>{loc}</loc></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(urls) + "</urlset>")


if __name__ == "__main__":
    run()
