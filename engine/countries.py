"""Co to znamená pro mou zemi — které zprávy sem doopravdy dolehnou.

Zpravodajství má jednu tichou vadu: skoro všechno se tváří, jako by se to
týkalo všech stejně. Netýká. Rozhodnutí Evropské komise změní cenu energie
v Irsku i v Česku, ale ne v Kanadě. Clo na dovoz do Spojených států pocítí
Mexiko dřív než Keňa. A spousta zpráv, které vypadají důležitě, se ke
čtenáři nedostane vůbec.

Tahle stránka odpovídá na jednu otázku: **co z posledních dvou týdnů
doléhá sem, kde bydlím** — a co to znamená pro peníze, zdraví, běžný život
a bezpečí. Praktické dopady se nevymýšlejí, berou se hotové z
`engine/impact.py`.

Zpráva se na stránku země dostane třemi cestami:

  * **přímo** — země je v textu jmenovaná a článek má blok `impact`.
    Jen u těch umíme poctivě říct, co konkrétně mění.
  * **doléhá zvenčí** — o téhle zemi to není, ale stejně to sem dopadne.
    Buď je to rozhodnutí pro celou Evropskou unii a země je členem, nebo
    je v textu jmenovaný její blízký obchodní partner, nebo jde prostě
    o celosvětovou věc. U každé takové zprávy se čtenáři napíše, kterou
    z těch tří cest sem přišla — nikdy se netváří, že je to zpráva odsud.
  * **taky odtud** — země je jmenovaná, ale článek blok `impact` nemá.
    Takový text se vypíše holý: titulek, perex a nic víc.

To poslední je tady to hlavní pravidlo a je přímo z redakčního kodexu,
oddílu 0: **dopad se nikdy nedomýšlí.** Když nevíme, co zpráva pro čtenáře
v Irsku mění, napíšeme titulek a mlčíme. Vymyšlený dopad by byl přesně to
odbyté „něco navíc", kvůli kterému čtenář přestane věřit i tomu ostatnímu.

Druhé pravidlo je o rozpoznávání zemí. Země se počítá za jmenovanou, až
když je v textu doopravdy vidět — jednou v titulku, nebo třikrát v textu.
Jedno slovo někde uprostřed nestačí: v převzatých textech bývá v patičce
univerzita autora a „Humboldt-Universität zu Berlin" není zpráva o Německu.
Slovník je v `data/countries.yml` a je psaný tak, aby v něm bylo jen to,
co nemůže znamenat nic jiného. Špatně zařazená zpráva je horší než zpráva,
která nikam nedolehla.

Výběr země zůstává v prohlížeči čtenáře, stejně jako zájmy a rovnováha
čtení (EDITORIAL-CODE, oddíl 5). Web staví stránku pro každou zemi ze
seznamu — i pro tu, ke které zrovna nic není. Uložená volba čtenáře tak
nikdy nespadne na chybějící stránku a my se přitom nedozvíme, kterou si
vybral.
"""
from __future__ import annotations

import datetime as dt
import re

import yaml

from . import config, impact

# Kolik dní zpátky stránka sahá. Čtrnáct dní, ne týden: menší země mívá
# za týden jednu zprávu nebo žádnou a prázdná stránka vypadá jako chyba.
# A na druhou stranu víc než čtrnáct dní už nejsou zprávy, ale archiv.
WINDOW_DAYS = 14

# Kolik znaků těla se prohledává. Země, o kterou v článku jde, je vždycky
# v prvních odstavcích. Dál už bývají patičky, poznámky a licence.
BODY_CHARS = 6000

# Váhy míst, kde se země může objevit. Titulek váží nejvíc, protože do
# titulku se dostane jen to, o čem zpráva doopravdy je.
W_TITLE, W_DEK, W_BODY = 3, 2, 1

# Od kolika bodů se země počítá za jmenovanou. Tři body znamenají:
# jednou v titulku, nebo jednou v perexu a jednou v textu, nebo třikrát
# v textu. Jedna náhodná zmínka nestačí.
DIRECT_SCORE = 3

# Stropy. Stránka má být přehled, ne výpis z databáze.
MAX_DIRECT = 6       # kolik zemí se přiřadí jednomu článku
MAX_RIPPLE = 8       # kolik zpráv „dolehne sem zvenčí"
MAX_PLAIN = 10       # kolik zpráv bez bloku impact
MAX_AREAS = 4        # kolik oblastí se vypíše nad stránkou

# Pořadí, ve kterém se řadí zprávy doléhající zvenčí. Nejdřív to, co je
# pro čtenáře nejzávaznější: rozhodnutí unie platí, ať chce nebo ne.
RIPPLE_ORDER = {"eu": 0, "partner": 1, "global": 2}

# --- co dělá ze zprávy rozhodnutí pro celou Evropskou unii -------------
# Zkratky se hledají s velkými písmeny zvlášť, jinak by „eu" našlo
# každé druhé slovo.
_EU_RX = re.compile(
    r"\b(?:European Union|European Commission|European Parliament|"
    r"European Central Bank|euro area|eurozone|single market|"
    r"Evropsk\w+ uni\w+|Evropsk\w+ komis\w+|Evropsk\w+ parlament\w*|"
    r"Evropsk\w+ centráln\w+ bank\w+|eurozón\w*|jednotn\w+ trh\w*)\b",
    re.I,
)
_EU_ABBR_RX = re.compile(r"\b(?:EU|ECB)\b")

# Brusel sám o sobě je město. Institucí se z něj stává, teprve když je
# poblíž řeč o pravidlech — proto se hledají obě věci najednou.
_BRUSSELS_RX = re.compile(r"\bBrussels\b|\bBrusel\w*")
_EU_ACT_RX = re.compile(
    r"\b(?:directive|regulation|rules?|decision|ban|banned|agreed|"
    r"proposal|law|směrnic\w*|nařízení|pravidl\w*|rozhodnut\w*|"
    r"zákaz\w*|schválil\w*)\b",
    re.I,
)

# --- co dělá ze zprávy celosvětovou věc --------------------------------
# Instituce, které rozhodují za celý svět.
_GLOBAL_RX = re.compile(
    r"\b(?:World Health Organi[sz]ation|United Nations|"
    r"International Monetary Fund|World Bank|World Trade Organi[sz]ation|"
    r"Světov\w+ zdravotnick\w+ organizac\w+|Organizace spojených národů|"
    r"Mezinárodní měnov\w+ fond\w*|Světov\w+ bank\w+)\b",
    re.I,
)
_GLOBAL_ABBR_RX = re.compile(r"\b(?:WHO|UN|IMF|NATO|IPCC|WTO|OSN)\b")

# Slova, která celosvětovost jen naznačují. Jedno „global" nic neznamená,
# globální bývá kdeco — proto mají vlastní, vyšší hranici.
_GLOBAL_SOFT_RX = re.compile(
    r"\b(?:worldwide|globally|global|around the world|across the world|"
    r"celosvětov\w*|po celém světě|na celém světě)\b",
    re.I,
)

# Dvě spojení, ve kterých slovo „global" znamená něco jiného a odečtou se.
# Global Voices je jméno redakce, ze které přebíráme texty, takže se
# v každém takovém článku objeví několikrát. Global South je část světa,
# ne celý svět.
_GLOBAL_SOFT_SKIP_RX = re.compile(r"\bGlobal Voices\b|\bGlobal South\b", re.I)

# Hranice, od kterých se to počítá. Jsou to stejné tři body jako u zemí:
# jednou v titulku, nebo třikrát v textu. U naznačujících slov jsou čtyři,
# protože „global" se v novinářské angličtině říká skoro do věty.
EU_SCORE = 3
GLOBAL_SCORE = 3
GLOBAL_SOFT_SCORE = 4

# Kolik zemí musí článek z rubriky Svět jmenovat, aby se dal považovat za
# zprávu o světě. Když nejmenuje žádnou, neznamená to, že je o celém světě
# — spíš je o zemi, kterou v seznamu nemáme. Mlčet je tam poctivější.
WORLD_MIN_COUNTRIES = 3

_cache: dict = {}


# ------------------------------------------------------------------ seznam
def _code(value) -> str:
    """Kód země z YAML. Pozor na Norsko: `no` bez uvozovek přečte YAML
    jako „ne", a Norsko by se ze seznamu tiše ztratilo. Tady se to vrací
    zpátky, aby jedny chybějící uvozovky nesmazaly celou zemi."""
    if value is False:
        return "no"
    if value is True:
        return "yes"
    return str(value or "").strip().lower()


def _rows() -> list[dict]:
    """Záznamy ze souboru tak, jak jsou, i se slovníky pro hledání."""
    if "rows" not in _cache:
        p = config.DATA / "countries.yml"
        data = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
        out = []
        for row in (data or {}).get("countries", []) or []:
            if not isinstance(row, dict):
                continue
            code = _code(row.get("code"))
            name = str(row.get("en") or "").strip()
            if not code or not name:
                continue
            cs = str(row.get("cs") or name).strip()
            out.append({
                "code": code,
                "en": name,
                "cs": cs,
                # Když chybí tvar do nadpisu, použije se jméno. Nadpis
                # bude česky trochu kostrbatý, ale stránka pojede dál.
                "cs_for": str(row.get("cs_for") or cs).strip(),
                # Anglicky některé země chtějí člen: „the United States".
                "en_the": bool(row.get("en_the")),
                "eu": bool(row.get("eu")),
                "partners": [_code(p) for p in (row.get("partners") or []) if _code(p)],
                "match": row.get("match") or {},
                "avoid": row.get("avoid") or {},
            })
        out.sort(key=lambda c: c["en"])
        _cache["rows"] = out
    return _cache["rows"]


def catalogue() -> list[dict]:
    """Všechny země ze souboru, seřazené podle anglického jména.

    Každá: {"code","en","cs","cs_for","eu":bool,"partners":[...]}
    """
    return [
        {"code": c["code"], "en": c["en"], "cs": c["cs"], "cs_for": c["cs_for"],
         "eu": c["eu"], "partners": list(c["partners"])}
        for c in _rows()
    ]


def label(code: str, lang: str, case: str = "nom") -> str:
    """Jméno země pro daný jazyk. case='for' vrátí tvar do nadpisu.

    Nadpis zní „Co to znamená pro …" a čeština za tím chce čtvrtý pád:
    pro Německo, ale pro Francii. Anglicky je to pořád stejné slovo.
    """
    code = _code(code)
    for c in _rows():
        if c["code"] == code:
            if str(lang).startswith("cs"):
                return c["cs_for"] if case == "for" else c["cs"]
            # Anglicky se jméno nemění, jen některé země chtějí člen:
            # „for the United States", ale „for Ireland".
            return f'the {c["en"]}' if case == "for" and c.get("en_the") else c["en"]
    # Neznámý kód — radši vrátíme aspoň ten kód než prázdno.
    return code.upper()


# ------------------------------------------------------------------ hledání
def _rx_en(word: str, whole: bool = True) -> re.Pattern:
    """Anglicky se hledá celé slovo.

    Velké písmeno v zadání znamená, že se na velikost hledí. Díky tomu
    není „Polish" totéž co „polish" a „US" totéž co „us".

    Hranice slova se hlídá zleva i zprava zvlášť, ne obyčejným `\\b`.
    To by u zkratky „U.S." selhalo: končí tečkou a za tečkou už žádné
    písmeno není, takže by se nenašla nikdy.

    U seznamu `avoid` se konec slova nehlídá (whole=False). Odečítat se
    má celé spojení, ne přesný tvar: „Danish pastry" tak zabere i na
    „Danish pastries" a „US$" na „US$13,000".
    """
    flags = 0 if any(ch.isupper() for ch in word) else re.I
    tail = r"(?!\w)" if whole else ""
    return re.compile(rf"(?<!\w){re.escape(word)}{tail}", flags)


def _rx_cs(word: str) -> re.Pattern:
    """Česky se hledá začátek slova a na velikost písmen se nehledí.

    Čeština skloňuje: „Irsko, Irska, v Irsku, irský" je pořád jedna země.
    Kdyby se hledala celá slova, našla by se sotva polovina.
    """
    return re.compile(rf"(?<!\w){re.escape(word)}", re.I)


def _words(*groups) -> list:
    """Slova z několika seznamů dohromady, bez prázdných a bez opakování.

    Jména zemí se se seznamem `match` často překrývají a u většiny zemí
    je `cs` a `cs_for` totéž slovo. Hledat je dvakrát nemá smysl.
    """
    out, seen = [], set()
    for group in groups:
        for word in group or []:
            word = str(word).strip()
            if word and word.lower() not in seen:
                seen.add(word.lower())
                out.append(word)
    return out


def _patterns() -> dict:
    """Slovník zemí převedený na hotové výrazy. Sestaví se jednou."""
    if "rx" not in _cache:
        out = {}
        for c in _rows():
            match, avoid = c["match"] or {}, c["avoid"] or {}
            # Jméno země se hledá vždycky, i když v `match` není.
            out[c["code"]] = {
                "en": [_rx_en(w) for w in _words([c["en"]], match.get("en"))],
                "cs": [_rx_cs(w) for w in _words([c["cs"], c["cs_for"]], match.get("cs"))],
                "avoid_en": [_rx_en(w, whole=False) for w in _words(avoid.get("en"))],
                "avoid_cs": [_rx_cs(w) for w in _words(avoid.get("cs"))],
            }
        _cache["rx"] = out
    return _cache["rx"]


def _spots(patterns: list, text: str) -> int:
    """Kolik různých míst v textu na seznam sedne.

    Počítají se místa, ne shody. Na totéž slovo často sedne víc výrazů
    najednou — „Izrael" je jméno země i tvar v seznamu a v české větě
    padne obojí na jedno slovo. Kdyby se sčítaly shody, měla by země
    tři body za jedinou zmínku a stačilo by jí to na celou stránku.
    """
    if not text:
        return 0
    return len({m.start() for rx in patterns for m in rx.finditer(text)})


def _score(patterns: list, title: str, dek: str, head: str) -> int:
    """Kolik bodů má země v jednom textu."""
    return (W_TITLE * _spots(patterns, title)
            + W_DEK * _spots(patterns, dek)
            + W_BODY * _spots(patterns, head))


def _dominates(scored: list) -> bool:
    """Je v textu jedna země, o kterou tam očividně jde?

    Slouží jen k jedinému rozhodnutí: článek z rubriky Svět, ve kterém
    jedna země výrazně přebíjí ostatní, není celosvětová zpráva.
    """
    if not scored:
        return False
    if len(scored) == 1:
        return True
    return scored[0][0] >= 2 * scored[1][0]


def _scope(meta: dict, title: str, dek: str, head: str, scored: list) -> str:
    """Jak široce zpráva dopadá: na celou unii, na celý svět, nebo nijak.

    Je to nezávislé na tom, které země jsou v textu jmenované. Zpráva může
    jmenovat Německo a přitom být rozhodnutím, které platí pro všech
    dvacet sedm států.

    Počítá se stejně jako u zemí: jedna zmínka někde uprostřed textu ještě
    nic neznamená. Zpráva, ve které je unie zmíněná jednou v poznámce pod
    čarou, není rozhodnutí unie — a kdyby se za ně vydávala, dolehla by
    na dvacet sedm stránek najednou.
    """
    eu = _score([_EU_RX, _EU_ABBR_RX], title, dek, head)
    if _EU_ACT_RX.search(f"{title} {dek} {head}"):
        eu += _score([_BRUSSELS_RX], title, dek, head)
    if eu >= EU_SCORE:
        return "eu"

    if _score([_GLOBAL_RX, _GLOBAL_ABBR_RX], title, dek, head) >= GLOBAL_SCORE:
        return "global"
    soft = (_score([_GLOBAL_SOFT_RX], title, dek, head)
            - _score([_GLOBAL_SOFT_SKIP_RX], title, dek, head))
    if soft >= GLOBAL_SOFT_SCORE:
        return "global"

    # Článek z rubriky Svět, který jmenuje několik zemí a žádná v něm
    # nepřevažuje, je zpráva o světě.
    if (str(meta.get("section") or "") == "world"
            and len(scored) >= WORLD_MIN_COUNTRIES
            and not _dominates(scored)):
        return "global"
    return "none"


def detect(meta: dict, body: str) -> dict:
    """Které země se v textu opravdu jmenují a jak široký ten dopad je.

    Vrací {"direct": ["ie","gb"], "scope": "eu"|"global"|"none"}
    """
    body = str(body or "")
    if not body.strip():
        # Bez textu se nedá poznat nic. Radši nic než odhad.
        return {"direct": [], "scope": "none"}

    title = str(meta.get("title") or "")
    dek = str(meta.get("dek") or "")
    head = body[:BODY_CHARS]
    # Česká slova se hledají jen v českém textu. V anglickém by „Indie"
    # našlo indie rock a „malt" sladovnu.
    czech = str(meta.get("lang") or "").strip().lower().startswith("cs")

    scored: list = []
    for code, p in _patterns().items():
        found = list(p["en"]) + (list(p["cs"]) if czech else [])
        skip = list(p["avoid_en"]) + (list(p["avoid_cs"]) if czech else [])
        # Spojení ze seznamu `avoid` se odečtou: „Paris Agreement" je
        # o klimatu a „New Mexico" je stát USA.
        points = _score(found, title, dek, head) - _score(skip, title, dek, head)
        if points >= DIRECT_SCORE:
            scored.append((points, code))
    # Nejvíc bodů první; při shodě rozhoduje kód, ať je web pokaždé stejný.
    scored.sort(key=lambda item: (-item[0], item[1]))

    return {
        "direct": [code for _, code in scored[:MAX_DIRECT]],
        "scope": _scope(meta, title, dek, head, scored),
    }


# ------------------------------------------------------------------ stránky
def _as_date(value) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _window(today, window_days: int) -> tuple[str, str]:
    """Od kdy do kdy stránka sahá. Poslední den je dnešek."""
    end = _as_date(today) or dt.date.today()
    days = max(1, int(window_days or WINDOW_DAYS))
    return (end - dt.timedelta(days=days - 1)).isoformat(), end.isoformat()


def _in_window(arts: list, start: str, end: str) -> list:
    """Články z posledních dvou týdnů, nejnovější první.

    Při shodě data rozhoduje adresa. Bez toho by se pořadí měnilo od
    stavby ke stavbě a web by se přepisoval, i když se nic nestalo.
    """
    pool = [a for a in arts if start <= str(a.get("date", ""))[:10] <= end]
    pool.sort(key=lambda a: str(a.get("url", "")))
    pool.sort(key=lambda a: str(a.get("date", ""))[:10], reverse=True)
    return pool


def _named(art: dict) -> list:
    """Země, které článek jmenuje. Doplňuje je stavba webu přes detect()."""
    found = art.get("countries") or {}
    return [str(c) for c in (found.get("direct") or [])]


def _reach(art: dict, country: dict) -> tuple[str, str]:
    """Proč zpráva dolehne do země, která v ní není jmenovaná.

    Pořadí není náhodné: rozhodnutí unie platí pro členský stát, ať chce
    nebo ne, kdežto celosvětová zpráva je z těch tří nejvolnější vazba.
    První, co sedne, vyhrává — čtenář má dostat jeden důvod, ne tři.
    """
    scope = str((art.get("countries") or {}).get("scope") or "none")
    named = _named(art)
    if scope == "eu" and country["eu"]:
        return "eu", ""
    for code in named:
        if code in country["partners"]:
            return "partner", code
    if scope == "global":
        return "global", ""
    return "", ""


def _areas(direct: list, ripple: list) -> list:
    """Čeho se to v téhle zemi dotýká, podle četnosti."""
    counts: dict = {}
    for art in direct + [item["a"] for item in ripple]:
        for area in ((art.get("impact") or {}).get("areas") or []):
            counts[area] = counts.get(area, 0) + 1
    # Při shodě rozhoduje pořadí oblastí z engine/impact.py, aby web
    # vypadal při každé stavbě stejně.
    return sorted(
        counts,
        key=lambda a: (-counts[a], impact.AREAS.index(a) if a in impact.AREAS else 9),
    )[:MAX_AREAS]


def pages(arts: list[dict], lang: str, today: str,
          window_days: int = WINDOW_DAYS) -> list[dict]:
    """Pro každou zemi jedna stránka.

    Stránka se staví i pro zemi, ke které za čtrnáct dní nic nevyšlo.
    Čtenářova volba je uložená v prohlížeči a nikdy nesmí skončit na
    chybějící stránce — prázdná stránka, která to řekne rovnou, je lepší
    než chyba 404 a mnohem lepší než stránka vycpaná nesouvisejícími
    zprávami.
    """
    start, end = _window(today, window_days)
    pool = _in_window(arts, start, end)
    out = []

    for country in _rows():
        code = country["code"]
        direct, plain, ripple = [], [], []

        for art in pool:
            block = art.get("impact")
            if code in _named(art):
                # Země je v textu jmenovaná. S blokem impact umíme říct,
                # co to mění; bez něj se článek vypíše holý a nic se
                # nedomýšlí (EDITORIAL-CODE, oddíl 0).
                (direct if block else plain).append(art)
                continue
            if not block:
                continue
            reason, via = _reach(art, country)
            if reason:
                # `via` je kód partnera, `via_label` jeho jméno rovnou
                # ve správném jazyce — šablona jím doplňuje větu
                # „blízký obchodní partner — Německo".
                ripple.append({"a": art, "reason": reason, "via": via,
                               "via_label": label(via, lang) if via else ""})

        # Řazení je stabilní, takže uvnitř každé skupiny zůstane pořadí
        # z výběru — tedy nejnovější první.
        ripple.sort(key=lambda item: RIPPLE_ORDER.get(item["reason"], 9))
        ripple = ripple[:MAX_RIPPLE]
        plain = plain[:MAX_PLAIN]
        count = len(direct) + len(ripple) + len(plain)

        out.append({
            "code": code,
            "label": label(code, lang),
            "label_for": label(code, lang, "for"),
            # Jen cesta za základem webu, zbytek doplní šablona.
            "url": f"country/{code}/",
            "eu": country["eu"],
            "from": start,
            "to": end,
            "direct": direct,
            "ripple": ripple,
            "plain": plain,
            "areas": _areas(direct, ripple),
            "count": count,
            # Stránka s jedinou zprávou není stránka. Ať ji vyhledávače
            # neindexují, dokud se nenaplní.
            "thin": count < 2,
        })
    return out


# ------------------------------------------------------------------ kontrola
if __name__ == "__main__":
    # Rychlá zkouška bez stavby webu: python -m engine.countries
    # Vypíše, kolik zpráv je za poslední dva týdny na které stránce.
    from . import article

    _lang = config.site()["languages"]["master"]
    _arts = []
    for _meta, _body, _path in article.load_all(_lang):
        if _meta.get("status") != "published":
            continue
        _arts.append({
            "date": str(_meta.get("date", ""))[:10],
            "title": _meta.get("title", ""),
            "dek": _meta.get("dek", ""),
            "url": f"/{_lang}/{_meta.get('section','')}/{_meta.get('slug','')}/",
            "section": _meta.get("section", ""),
            "impact": impact.read(_meta, _body),
            "countries": detect(_meta, _body),
        })

    _today = config.today()
    _rows_out = pages(_arts, _lang, _today)
    _filled = [r for r in _rows_out if r["count"]]
    _filled.sort(key=lambda r: (-r["count"], r["label"]))
    _from, _to = _window(_today, WINDOW_DAYS)
    _pool = _in_window(_arts, _from, _to)
    _with_impact = len([a for a in _pool if a.get("impact")])

    print("=" * 64)
    print(f"  CO TO ZNAMENÁ PRO MOU ZEMI — {_from} až {_to}")
    print(f"  Článků v okně: {len(_pool)} z {len(_arts)} publikovaných, "
          f"z toho {_with_impact} s praktickým dopadem")
    print("=" * 64)
    print(f"{'kód':<5}{'země':<24}{'přímo':>6}{'zvenčí':>8}{'holé':>6}"
          f"{'celkem':>8}  oblasti")
    for _r in _filled:
        print(f"{_r['code']:<5}{_r['label'][:23]:<24}{len(_r['direct']):>6}"
              f"{len(_r['ripple']):>8}{len(_r['plain']):>6}{_r['count']:>8}"
              f"  {', '.join(_r['areas'])}")
    _empty = [r["label"] for r in _rows_out if not r["count"]]
    print("-" * 64)
    print(f"Zemí se zprávami: {len(_filled)} z {len(_rows_out)}. "
          f"Tenkých stránek (míň než dvě zprávy): "
          f"{len([r for r in _rows_out if r['thin']])}.")
    if _empty:
        print("Zatím bez zpráv: " + ", ".join(_empty))
