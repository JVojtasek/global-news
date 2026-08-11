"""Velké problémy — co se opravdu zkusilo, co by počítal stroj a co by mu uniklo.

Zpravodajství umí den. Umí říct, co se stalo včera a kdo na to co řekl.
Neumí ale odpovědět na otázku, kterou má člověk v hlavě, když noviny
zavře: *a dá se s tím vůbec něco dělat?* Bydlení je drahé deset let,
čekárny u lékařů jsou plné deset let, a přesto se o tom pokaždé píše,
jako by to začalo v úterý. O tom, že jedna země přesně tohle před
dvanácti lety zkusila a naměřila si výsledek, se čtenář nedozví.

Tahle rubrika je pokus o opak. Deset problémů, které má celý svět,
a na každý jedna stránka, která se skoro nemění. Nejsou to komentáře:
na stránce jsou tři sloupce a každý dělá něco jiného.

  * **co se opravdu zkusilo** — skutečná země, skutečné opatření,
    naměřený výsledek a zdroj, ve kterém si to čtenář ověří. Ne úmysly
    a ne plány: čísla z doby potom. Mezi pokusy patří schválně i ten,
    který nevyšel — bez něj by to byl katalog úspěchů, ne poctivý přehled.
  * **co by optimalizoval stroj** — otevřeně jako počet. Pojmenuje se
    jedno jediné číslo, které se má vyhnat co nejvýš, a jde se za ním
    až do konce. Není to rada, není to předpověď a není to politika.
    Je to ukázka, jaký tvar má odpověď kalkulačky, když se pustí
    na lidskou věc.
  * **co by stroji uniklo** — kdo to zaplatí, co se v tom čísle ztratí
    a co tabulka nevidí vůbec. Tenhle sloupec je na celé stránce ten
    nejdůležitější a je to jediný důvod, proč smí předchozí sloupec
    existovat. Proto se taky nikdy netiskne sám: šablona ho drží
    ve dvojici a bez něj se počet stroje nezobrazí.

Čtvrtá věc na stránce je žebříček — kdo je na tom podle toho jednoho
čísla vážně nejlíp. Odkazuje rovnou na stránky zemí, které web už má
(`engine/countries.py`), takže se čtenář ze světového průměru dostane
na jedno kliknutí k tomu, jak je na tom on sám.

Proč to takhle složitě: **kontrola `check()` je celý smysl tohohle
modulu.** Text o velkém problému se strašně snadno sveze do dojmů —
jedna nedoložená věta, jeden výsledek bez čísla, jeden odbytý bod
v nejdůležitějším bloku a je z toho úvodník. Síto proto trvá na tom,
co se ověřit dá: měřítko musí mít jméno, zdroj i odkaz; každý pokus
zdroj nebo odkaz; každý výsledek aspoň jedno číslo; blok „co by stroji
uniklo" aspoň tři body a každý pořádně dlouhý. A ve sloupci stroje se
hlídají slova „musíme", „mělo by se" a „should" — stroj počítá, nikomu
nic nedoporučuje. Kdo si chce stránky projít, spustí:

    python -m engine.problems

Formát souboru je popsaný v `engine/prompts/PROBLEMS.md` a je závazný.
Stránky bydlí v `content/problems/<id>.<lang>.md`, hlavička se čte
stejnou čtečkou jako u článků (`engine.article.parse`) — druhý rozdělovač
YAML by se dřív nebo později rozešel s tím prvním. Pořadí rubriky je
v `data/site.yml`, ne v kódu: který problém je první, je redakční
rozhodnutí, a kvůli němu se nemá sahat do Pythonu.
"""
from __future__ import annotations

import re
import unicodedata

import markdown as md

from . import article, config, countries

# Složka se stránkami. Jméno souboru je `<id>.<lang>.md`, takže je
# ve všech jazycích stejné id a z něj i stejná adresa.
DIR = "problems"

# Kolik nejmíň. Čísla jsou schválně tady nahoře a ne schovaná v kódu,
# aby šla najít a případně změnit jedním řádkem.
BLIND_MIN_POINTS = 3      # kolik bodů má mít blok „co by stroji uniklo"
BLIND_MIN_CHARS = 120     # a jak dlouhý má být každý z nich
BOARD_MIN_ROWS = 3        # žebříček ze dvou zemí není žebříček

# Kázání ve sloupci stroje. Ta slova jsou jediné, co ten sloupec
# rozděluje na počet a na názor: „když zvýšíš X o deset procent, vyjde
# ti Y" je počet, „měli bychom zvýšit X" je rada. Rady tenhle web
# nedává (CLAUDE.md, oddíl o tom, že nikdy nekážeme).
PREACH_RX = re.compile(
    r"\b(?:should|must|ought to|we need to|governments need|"
    r"je třeba|musíme|měli bychom|mělo by se)\b",
    re.I,
)

# Markdown se převádí tady, ne v šabloně. Převod žije v engine/build.py,
# jenže build.py si tenhle modul sám načítá — a kdyby si ho tenhle modul
# zavolal zpátky, Python by se zacyklil a nepostavilo by se nic.
# Rozšíření jsou proto schválně přesně ta samá jako v build.py; kdyby se
# tam někdy měnila, změň je i tady.
_MD = md.Markdown(extensions=["extra", "sane_lists", "smarty"])

_cache: dict = {}


# ------------------------------------------------------------------ drobnosti
def _html(text: str) -> str:
    _MD.reset()
    return _MD.convert(str(text or ""))


def _str(value) -> str:
    """Text z hlavičky. Chybějící i prázdná hodnota je prázdný řetězec.

    YAML dovolí napsat `note:` a nechat za tím prázdno. V Pythonu je
    z toho `None` a v šabloně by se vypsalo slovo „None" — čtenář by
    v novinách četl hlášku z programu. Tady se to sjednotí hned na
    vstupu, takže se to dál nemůže stát nikde.
    """
    return "" if value is None else str(value).strip()


def _code(value) -> str:
    """Kód země z YAML. Pozor na Norsko — stejná past jako v countries.py:
    `no` bez uvozovek přečte YAML jako „ne" a země by se tiše ztratila."""
    if value is False:
        return "no"
    if value is True:
        return "yes"
    return _str(value).lower()


def _dict(value) -> dict:
    return dict(value) if isinstance(value, dict) else {}


def _list(value) -> list:
    """Seznam z hlavičky. Jedna hodnota napsaná bez pomlčky je seznam
    o jednom prvku — psaná chyba nemá stát celý blok."""
    if isinstance(value, list):
        return list(value)
    return [] if value is None or value == "" else [value]


def _abc(name: str) -> str:
    """Řadicí klíč pro titulky — háčky a čárky se pro řazení sundají.

    Stejný trik jako u zemí v engine/build.py: na deset stránek nemá
    cenu tahat celou českou abecedu, tohle stačí, aby „Čistá voda"
    nespadla za „Zdraví".
    """
    stripped = unicodedata.normalize("NFKD", str(name or "").lower())
    return "".join(ch for ch in stripped if not unicodedata.combining(ch))


def _many(n: int, one: str, few: str, many: str) -> str:
    """„1 bod", „3 body", „5 bodů" — čeština má tři tvary a hlášení,
    které je nedodrží, vypadá jako z automatu. Stejná pomůcka jako
    `_count_label` v engine/build.py."""
    return f"{n} {one if n == 1 else few if 2 <= n <= 4 else many}"


def _known() -> set:
    """Kódy zemí, které web opravdu má. Katalog se čte jednou."""
    if "known" not in _cache:
        _cache["known"] = {c["code"] for c in countries.catalogue()}
    return _cache["known"]


def _country(row: dict, lang: str) -> dict:
    """Doplní k řádku jméno země a odkaz na její stránku.

    Když kód v katalogu není, zůstane v popisku holý kód a odkaz je
    prázdný. Řádek se ale nikdy nezahodí: chybějící země v seznamu je
    naše chyba, ne důvod zatajit čtenáři celý pokus. Prázdný odkaz
    šablona pozná a jméno pak nikam neodkazuje.
    """
    code = _code(row.get("country"))
    row["country"] = code
    if code and code in _known():
        row["country_label"] = countries.label(code, lang)
        row["country_url"] = f"country/{code}/"
    else:
        row["country_label"] = code
        row["country_url"] = ""
    return row


# ------------------------------------------------------------------ hlavička
def _measure(value) -> dict:
    """Jedno číslo, proti kterému se poměřuje celá stránka."""
    out = _dict(value)
    for key in ("name", "unit", "better", "source", "url"):
        out[key] = _str(out.get(key))
    return out


def _board(value, lang: str) -> list:
    """Žebříček. Řádek, který není slovník, je chyba v souboru — text
    se přesto neztratí, přečte se aspoň jako poznámka a check() to řekne."""
    out = []
    for row in _list(value):
        row = dict(row) if isinstance(row, dict) else {"note": _str(row)}
        for key in ("value", "note"):
            row[key] = _str(row.get(key))
        out.append(_country(row, lang))
    return out


def _tried(value, lang: str) -> list:
    """Skutečné pokusy. Totéž pravidlo: nic se nezahazuje."""
    out = []
    for row in _list(value):
        row = dict(row) if isinstance(row, dict) else {"what": _str(row)}
        for key in ("what", "result", "caveat", "source", "url"):
            row[key] = _str(row.get(key))
        out.append(_country(row, lang))
    return out


def _machine(value) -> dict:
    out = _dict(value)
    out["optimise"] = _str(out.get("optimise"))
    out["arithmetic"] = _str(out.get("arithmetic"))
    out["moves"] = [_str(x) for x in _list(out.get("moves")) if _str(x)]
    return out


def _blind(value) -> list:
    out = []
    for row in _list(value):
        row = dict(row) if isinstance(row, dict) else {"text": _str(row)}
        row["point"] = _str(row.get("point"))
        row["text"] = _str(row.get("text"))
        out.append(row)
    return out


def _sources(value) -> list:
    """Zdroje pohromadě. Zdroj napsaný jedním řádkem se přečte taky:
    když to vypadá jako adresa, je to adresa, jinak je to jméno."""
    out = []
    for row in _list(value):
        if isinstance(row, dict):
            row = dict(row)
        else:
            text = _str(row)
            row = {"url": text, "name": text} if text.startswith("http") else {"name": text}
        row["url"] = _str(row.get("url"))
        # Aby v seznamu nikdy nebyla prázdná odrážka, je jménem odkazu
        # aspoň sama adresa.
        row["name"] = _str(row.get("name")) or row["url"]
        if row["name"] or row["url"]:
            out.append(row)
    return out


def _page(meta: dict, body: str, lang: str, pid: str) -> dict:
    """Hotová stránka pro šablonu: hlavička srovnaná do textů a doplněná
    o adresu, jména zemí a převedený úvod."""
    page = dict(meta)
    page["id"] = _str(meta.get("id")) or pid
    page["lang"] = lang
    page["title"] = _str(meta.get("title"))
    page["dek"] = _str(meta.get("dek"))
    page["status"] = _str(meta.get("status"))
    page["date"] = _str(meta.get("date"))
    # Datum, kdy někdo naposled ověřil čísla. Když chybí, platí datum
    # vzniku — v `<time>` nikdy nesmí zůstat prázdno.
    page["updated"] = _str(meta.get("updated")) or page["date"]
    # Jen cesta za jazykem, zbytek si doplní šablona. Stejně jako u zemí.
    page["url"] = f"problems/{page['id']}/"
    page["measure"] = _measure(meta.get("measure"))
    page["board"] = _board(meta.get("board"), lang)
    page["tried"] = _tried(meta.get("tried"), lang)
    page["machine"] = _machine(meta.get("machine"))
    page["blind"] = _blind(meta.get("blind"))
    page["sources"] = _sources(meta.get("sources"))
    # Úvod pod hlavičkou. `body` je markdown tak, jak ho někdo napsal,
    # `body_html` je hotový k vypsání — šablona si bere to druhé.
    page["body"] = str(body or "").strip()
    page["body_html"] = _html(page["body"]) if page["body"] else ""
    return page


# ------------------------------------------------------------------ čtení
def _order() -> list:
    """Pořadí stránek z data/site.yml. Zapisuje se takhle:

        problems:
          order: [housing, health, water]

    Který problém stojí první, je redakční rozhodnutí, ne věc abecedy.
    Když v nastavení nic není, řadí se všechno podle titulku a nic se
    nerozbije.
    """
    block = config.site().get("problems")
    if isinstance(block, dict):
        block = block.get("order")
    return [_str(x) for x in _list(block) if _str(x)]


def _everything(lang: str) -> list:
    """Všechny soubory v jazyce, i nehotové. Pro kontrolu, ne pro web.

    Soubor bez hlavičky se nepřeskočí, jen projde dál prázdný —
    v kontrole je pak vidět, že je rozbitý. Na web se stejně nedostane,
    protože nemá `status: published`.
    """
    folder = config.CONTENT / DIR
    if not folder.exists():
        return []
    tail = f".{lang}.md"
    out = []
    for path in sorted(folder.glob(f"*{tail}")):
        raw = path.read_text(encoding="utf-8")
        meta, body = article.parse(raw)
        page = _page(meta or {}, body, lang, path.name[: -len(tail)])
        # Rozbitá hlavička se pozná takhle: v souboru mezi `---` něco je,
        # ale nepřečetlo se z toho nic. Bez tohohle příznaku by kontrola
        # jen vysypala deset hlášek „chybí" a nebylo by poznat proč.
        page["_head_ok"] = bool(meta) or not raw.lstrip().startswith("---")
        page["_file"] = path.name
        out.append(page)
    return out


def load(lang: str) -> list[dict]:
    """Všechny stránky problémů v daném jazyce, seřazené podle `order`
    v data/site.yml, jinak podle titulku. Nehotové (status != published)
    se vynechají."""
    order = _order()
    pages = [p for p in _everything(lang) if p["status"] == "published"]
    # Co v pořadí není, jde za tím podle abecedy. Řazení je stabilní,
    # takže web vypadá při každé stavbě stejně.
    pages.sort(key=lambda p: (
        order.index(p["id"]) if p["id"] in order else len(order),
        _abc(p["title"]),
        p["id"],
    ))
    return pages


def one(pid: str, lang: str) -> dict | None:
    """Jedna stránka podle jejího id, nebo None, když taková není.

    Nehotová stránka se nevrací. Kdyby se vracela, stačilo by na ni
    jednou odkázat a rozepsaný text by se tiše ocitl na webu.
    """
    pid = _str(pid)
    for page in load(lang):
        if page["id"] == pid:
            return page
    return None


# ------------------------------------------------------------------ kontrola
def check(page: dict) -> list[str]:
    """Seznam výhrad — prázdný seznam znamená v pořádku.

    Tohle je to hlavní, co modul umí. Nekontroluje se sloh, kontroluje
    se jen to, co se ověřit dá: jestli je čím měřit, jestli je co
    doložit a jestli nejdůležitější blok stránky někdo neodbyl.
    """
    # Když se hlavička vůbec nepřečetla, nemá cenu vypisovat, co v ní
    # chybí — chybí všechno. Nejčastější příčina je obyčejná uvozovka
    # uvnitř textu v uvozovkách: česká zavírací je „takhle“, ne "takhle".
    if not page.get("_head_ok", True):
        return [f'hlavička se nedá přečíst ({page.get("_file", "?")}) — '
                'nejspíš je uvnitř textu v uvozovkách obyčejná uvozovka ("), '
                'která YAML předčasně ukončí. Česká zavírací uvozovka je “.']

    out: list[str] = []
    measure = _dict(page.get("measure"))
    machine = _dict(page.get("machine"))

    # Stránka bez pojmenovaného a doloženého čísla není měření, ale
    # názor. Čtenář musí mít pokaždé co zkontrolovat — jméno čísla,
    # odkud je a kam si pro ně dojít.
    for key, what in (("name", "jméno"), ("source", "zdroj"), ("url", "odkaz")):
        if not _str(measure.get(key)):
            out.append(f"měřítko: chybí {what} (measure.{key})")

    for i, row in enumerate(_list(page.get("tried")), 1):
        row = _dict(row)
        who = _str(row.get("country_label")) or _str(row.get("country")) or "?"
        # Pokus bez zdroje i bez odkazu je vyprávění. Stačí jedno z toho,
        # ale ne nic: cizí opatření si čtenář nemá jak ověřit.
        if not _str(row.get("source")) and not _str(row.get("url")):
            out.append(f"pokus {i} ({who}): není u něj zdroj ani odkaz")
        # Výsledek bez čísla je tvrzení. „Pomohlo to" se nedá zkontrolovat
        # a přesně takové věty dělají z novin úvodník.
        if not re.search(r"\d", _str(row.get("result"))):
            out.append(f"pokus {i} ({who}): výsledek neobsahuje žádné číslo")

    # Blok „co by stroji uniklo" je nejdůležitější část stránky a zároveň
    # ta, na které se nejsnáz šetří: tři odbyté věty a je z toho poznámka
    # pod čarou. Proto se počítají body i znaky.
    blind = _list(page.get("blind"))
    if len(blind) < BLIND_MIN_POINTS:
        out.append(f"co by stroji uniklo: jen {_many(len(blind), 'bod', 'body', 'bodů')}, "
                   f"mají být aspoň {BLIND_MIN_POINTS}")
    for i, row in enumerate(blind, 1):
        text = _str(_dict(row).get("text"))
        if len(text) < BLIND_MIN_CHARS:
            out.append(f"co by stroji uniklo, bod {i}: text má "
                       f"{_many(len(text), 'znak', 'znaky', 'znaků')}, "
                       f"má mít aspoň {BLIND_MIN_CHARS}")

    # Bez pojmenovaného čísla a bez počtu není sloupec stroje počet,
    # ale úvaha — a úvahu na tomhle místě stránka nesnese.
    for key, what in (("optimise", "co se vyhání nahoru"), ("arithmetic", "počet")):
        if not _str(machine.get(key)):
            out.append(f"stroj: chybí {what} (machine.{key})")

    # Stroj počítá, nikomu nic nedoporučuje. Jedno „měli bychom" a je
    # z celého sloupce názor redakce — přesně to, čemu se rubrika vyhýbá.
    for key in ("optimise", "arithmetic"):
        found = PREACH_RX.search(_str(machine.get(key)))
        if found:
            out.append(f'stroj: kázání ve `machine.{key}` — „{found.group(0)}"')
    for i, move in enumerate(_list(machine.get("moves")), 1):
        found = PREACH_RX.search(_str(move))
        if found:
            out.append(f'stroj: kázání v kroku {i} — „{found.group(0)}"')

    # Žebříček ze dvou zemí není žebříček, je to příklad. Pod třemi
    # řádky se nedá poznat, jestli je první země výjimka, nebo pravidlo.
    board = _list(page.get("board"))
    if len(board) < BOARD_MIN_ROWS:
        out.append(f"žebříček: jen {_many(len(board), 'řádek', 'řádky', 'řádků')}, "
                   f"mají být aspoň {BOARD_MIN_ROWS}")

    return out


# ------------------------------------------------------------------ report
if __name__ == "__main__":
    # Rychlá zkouška bez stavby webu: python -m engine.problems
    # Projde všechny soubory ve všech jazycích, i nehotové, a vypíše,
    # co je na kterém špatně. Když je něco špatně, skončí kódem 1 —
    # ať to pozná i hlídač v GitHub Actions.
    _site = config.site()
    _langs = [_site["languages"]["master"], *_site["languages"]["translations"]]

    print("=" * 64)
    print("  VELKÉ PROBLÉMY — kontrola stránek")
    print("=" * 64)

    _total = _bad = 0
    for _lang in _langs:
        _pages = _everything(_lang)
        if not _pages:
            print(f"{_lang}: zatím tu žádné stránky nejsou")
            continue
        for _p in _pages:
            _total += 1
            _issues = check(_p)
            _state = "hotová" if _p["status"] == "published" else (_p["status"] or "?")
            _head = f"{_lang}  {_p['id'][:22]:<24}{_state:<12}"
            if _issues:
                _bad += 1
                print(f"{_head}{_many(len(_issues), 'výhrada', 'výhrady', 'výhrad')}")
                for _issue in _issues:
                    print(f"      - {_issue}")
            else:
                print(f"{_head}v pořádku")

    print("-" * 64)
    if not _total:
        print("Zatím tu nejsou žádné stránky. Formát souboru je "
              "v engine/prompts/PROBLEMS.md.")
    else:
        print(f"Stránek: {_total}, v pořádku: {_total - _bad}, s výhradami: {_bad}.")
    if _bad:
        raise SystemExit(1)
