"""AI router: zkusí Anthropic, pak OpenAI, pak se vzdá elegantně.

Klíčové vlastnosti:
  * fallback mezi poskytovateli (když jeden vypadne, jede druhý)
  * automatické opakování při dočasné chybě
  * denní strop útraty (data/state.json -> spend)
  * mock režim (AI_MOCK=1) pro testování bez klíče a bez peněz
"""
from __future__ import annotations

import json
import os
import re
import time

import requests

from . import config

MOCK = os.environ.get("AI_MOCK") == "1"


class AIUnavailable(RuntimeError):
    pass


class BudgetExceeded(RuntimeError):
    pass


# hrubý odhad ceny, jen aby existoval strop; skutečné ceny se liší podle modelu
_PRICE_PER_1K = {"anthropic": 0.006, "openai": 0.002}


def _budget_check(provider: str, tokens: int) -> None:
    st = config.load_state()
    day = config.today()
    spent = st.setdefault("spend", {}).get(day, 0.0)
    cap = config.site()["ai"]["max_usd_per_day"]
    if spent >= cap:
        raise BudgetExceeded(f"Denní strop {cap} USD vyčerpán ({spent:.2f}).")
    st["spend"][day] = round(spent + tokens / 1000 * _PRICE_PER_1K.get(provider, 0.004), 4)
    st["spend"] = {k: v for k, v in sorted(st["spend"].items())[-40:]}
    config.save_state(st)


# ------------------------------------------------------------ providers
def _anthropic(system: str, user: str, max_tokens: int, temperature: float) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise AIUnavailable("chybí ANTHROPIC_API_KEY")
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": config.site()["ai"]["anthropic_model"],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        timeout=300,
    )
    if r.status_code != 200:
        raise AIUnavailable(f"anthropic {r.status_code}: {r.text[:300]}")
    data = r.json()
    _budget_check("anthropic", data.get("usage", {}).get("output_tokens", max_tokens))
    return "".join(b.get("text", "") for b in data.get("content", []))


def _openai(system: str, user: str, max_tokens: int, temperature: float) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise AIUnavailable("chybí OPENAI_API_KEY")
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
        json={
            "model": config.site()["ai"]["openai_model"],
            "max_completion_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=300,
    )
    if r.status_code != 200:
        raise AIUnavailable(f"openai {r.status_code}: {r.text[:300]}")
    data = r.json()
    _budget_check("openai", data.get("usage", {}).get("completion_tokens", max_tokens))
    return data["choices"][0]["message"]["content"]


_PROVIDERS = {"anthropic": _anthropic, "openai": _openai}


def ask(system: str, user: str, max_tokens: int = 6000, temperature: float = 0.4) -> str:
    if MOCK:
        from .mock import mock_answer

        return mock_answer(system, user)

    errors = []
    for name in config.site()["ai"]["providers"]:
        fn = _PROVIDERS.get(name)
        if not fn:
            continue
        for attempt in range(3):
            try:
                return fn(system, user, max_tokens, temperature)
            except BudgetExceeded:
                raise
            except Exception as e:  # noqa: BLE001
                errors.append(f"{name}#{attempt}: {e}")
                config.log(f"  ! {name} pokus {attempt + 1} selhal: {str(e)[:160]}")
                time.sleep(4 * (attempt + 1))
    raise AIUnavailable("Žádný AI poskytovatel nefunguje.\n" + "\n".join(errors[-4:]))


def ask_json(system: str, user: str, **kw) -> dict:
    """Jako ask(), ale vynutí a vyparsuje JSON odpověď."""
    system = system + "\n\nOdpověz VÝHRADNĚ platným JSON objektem. Žádný text okolo, žádné ```."
    raw = ask(system, user, **kw)
    return _parse_json(raw)


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise
