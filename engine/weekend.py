"""Sobotní vydání — jediné noviny, které jednou skončí.

Všechno ostatní na internetu je nekonečný proud: dočteš jednu věc a máš
pod ní tři další. Tohle ne. Jednou týdně se z toho, co už během týdne
vyšlo, poskládá vydání, které má začátek, prostředek a konec. Čtenář ho
v sobotu u kávy dočte — a je hotový. Přesně kvůli tomu se web jmenuje
Moje noviny.

Tenhle soubor **nic nepíše a nic si nevymýšlí**. Umí jedinou věc: vybrat
z článků, které už týden prošly redakcí, faktcheckem i kontrolou, ty,
které vydání unesou, a poskládat je do pořadí. Text se nikde nemění ani
nekrátí — bere se přesně tak, jak vyšel.

Z čeho se vydání skládá a proč zrovna z toho:

  * **Týden v pěti minutách** — vrstva `BRIEFLY` pěti nejdůležitějších
    článků. Ta vrstva je psaná tak, aby obstála úplně sama za sebe
    (FORMAT.md, oddíl BRIEFLY), takže se dá bez rozpaků přenést sem.
  * **Dlouhé čtení** — nejlepší `daily` nebo `feature` týdne a jeho
    vrstva `DEEPER` celá, s odkazem na celý článek.
  * **Co to znamenalo pro tebe** — bloky `impact:` seskupené podle toho,
    čeho se týkají: peníze, zdraví, běžný život, bezpečí.
  * **Dobré zprávy**, **k zamyšlení** (vrstva `REFLECT`), citáty
    a závěrečné slovo.

Tři pravidla, která se tady neporušují:

1. **Každý článek je ve vydání nejvýš jednou.** Sekce si ho zabírají
    v tom pořadí, ve kterém je čtenář potká. Vydání, ve kterém se jedna
    zpráva opakuje třikrát, není vydání, je to výpis z databáze.
2. **Prázdná sekce se vynechá.** Nikdy se nedoplňuje výplní a nikdy se
    nenapíše „tento týden nic". Radši kratší vydání.
3. **Do vydání jde jen text, který je venku celý.** Článek v předčasném
    přístupu (`access: early`) má na svojí stránce zatím jen shrnutí —
    kdyby se sem přenesla jeho vrstva DEEPER, obešli bychom sami sebe.

Nastavení je v `data/site.yml` → `weekend`.
"""
from __future__ import annotations

import datetime as dt

from . import config, impact

# Zkratky dnů tak, jak se píšou v data/site.yml.
DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

# Míň článků než tohle za celý týden a vydání ten týden nevyjde vůbec.
# Vydání složené ze tří textů není vydání a čtenáře by jen zklamalo.
MIN_ARTICLES = 4

# Kolik praktických dopadů se vejde do jedné oblasti. Je to schválně
# málo: tahle sekce má být přehled, ne seznam všeho, co jsme napsali.
IMPACT_PER_AREA = 3

# Kolik dobrých zpráv. „Jedna dvě" znamená jedna dvě.
GOOD_MAX = 2

# Pořadí, ve kterém se články poměřují. Nižší číslo = důležitější.
# Vlastní práce jde před převzatým textem — vydání má být obrazem toho,
# co jsme ten týden udělali my.
TYPE_RANK = {"daily": 0, "feature": 1, "demand": 2, "analysis": 3, "news": 4,
             "imported": 7, "syndicated": 8}

# Naše vlastní texty. Jen ty mají vrstvy (BRIEFLY, DEEPER, REFLECT) —
# převzatý článek je jeden kus textu pod cizí licencí a nic z něj sem
# nepřenášíme než titulek a odkaz.
OWN_TYPES = ("daily", "feature", "demand", "analysis", "news")

# Typy, ze kterých se vybírá dlouhé čtení.
LONG_TYPES = ("daily", "feature")


# ------------------------------------------------------------------ nastavení
def cfg() -> dict:
    return config.site().get("weekend") or {}


def enabled() -> bool:
    return bool(cfg().get("enabled"))


def window_days() -> int:
    """Kolik dní vydání pokrývá. Nesmysl v nastavení = týden."""
    try:
        return max(1, int(cfg().get("window_days", 7)))
    except (TypeError, ValueError):
        return 7


def briefly_count() -> int:
    """Kolik shrnutí se vejde do „týdne v pěti minutách"."""
    try:
        return max(1, int(cfg().get("briefly_count", 5)))
    except (TypeError, ValueError):
        return 5


def _day_index() -> int:
    """Den v týdnu, kdy vydání vychází. Nesmysl v nastavení = sobota."""
    return DAYS.get(str(cfg().get("day", "sat")).strip().lower()[:3], 5)


def _as_date(value) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _snap(day: dt.date) -> dt.date:
    """Nejbližší den vydání od zadaného data dopředu (včetně něj)."""
    return day + dt.timedelta(days=(_day_index() - day.weekday()) % 7)


def first_issue(today=None) -> dt.date:
    """Datum prvního čísla. Podle něj se čísluje všechno ostatní.

    Když v nastavení chybí nebo je v něm nesmysl, bere se tenhle týden —
    web se tím nezastaví, jen se začne počítat od jedničky teď.
    """
    d = _as_date(cfg().get("first_issue"))
    if d is None:
        d = _as_date(today) or dt.date.today()
    return _snap(d)


def current_edition(today=None) -> dt.date:
    """Které číslo se právě má ukazovat.

    Je to poslední den vydání, který už nastal — díky tomu se vydání
    během týdne nemění. Sobotní noviny mají v úterý vypadat úplně stejně
    jako v sobotu; kdyby se přeskládaly každý den, nekončily by.

    Než vyjde první číslo, ukazuje se to, které se právě sází: tentýž
    týden, totéž číslo, jen ještě není uzavřené. V sobotu se z něj beze
    změny adresy i čísla stane hotové vydání.
    """
    day = _as_date(today) or dt.date.today()
    last = day - dt.timedelta(days=(day.weekday() - _day_index()) % 7)
    return max(last, first_issue(today))


def edition_dates(today=None) -> list[dt.date]:
    """Data všech vydání od prvního čísla po to současné, nejnovější první."""
    first, cur = first_issue(today), current_edition(today)
    weeks = max(0, (cur - first).days // 7)
    return [cur - dt.timedelta(days=7 * i) for i in range(weeks + 1)]


def issue_number(edition: dt.date, today=None) -> int:
    """Kolikáté je to číslo. První vydání je číslo 1."""
    return max(1, (edition - first_issue(today)).days // 7 + 1)


def window(edition: dt.date) -> tuple[dt.date, dt.date]:
    """Od kdy do kdy vydání sahá. Poslední den je den vydání."""
    return edition - dt.timedelta(days=window_days() - 1), edition


# ------------------------------------------------------------------ výběr
def _layer(a: dict, name: str) -> str:
    """Hotové HTML jedné vrstvy článku, nebo prázdno."""
    for layer in a.get("layers") or []:
        if layer.get("id") == name and (layer.get("html") or "").strip():
            return layer["html"]
    return ""


def _rank(a: dict) -> tuple:
    """Jak moc článek do vydání patří. Menší je lepší.

    Nejdřív rozhoduje typ (vlastní práce před převzatou), pak jistota,
    se kterou jsme text vydali, pak počet nezávislých zdrojů a délka.
    Slug je na konci jen proto, aby stejně silné články vycházely při
    každé stavbě webu ve stejném pořadí.
    """
    return (
        TYPE_RANK.get(a.get("type"), 5),
        -int(a.get("confidence") or 0),
        -len(a.get("sources") or []),
        -int(a.get("words") or 0),
        a.get("slug", ""),
    )


def _in_window(arts: list, start: dt.date, end: dt.date) -> list:
    """Články vydané v tom týdnu — a jen ty, které jsou venku celé.

    Text v předčasném přístupu má zatím veřejné jen shrnutí. Do vydání
    proto nejde: nechceme dvěma cestami vydat to, co jsme jednou cestou
    vydat nechtěli.
    """
    lo, hi = start.isoformat(), end.isoformat()
    return [a for a in arts
            if lo <= str(a.get("date", "")) <= hi
            and a.get("access_state", "public") == "public"]


def _pick_briefly(pool: list, used: set, limit: int) -> list:
    """Týden v pěti minutách: vrstva BRIEFLY nejdůležitějších článků.

    Bere se jen z vlastních textů — jen ty tu vrstvu mají a jen u nich
    víme, že prošla faktcheckem.
    """
    out = []
    for a in sorted(pool, key=_rank):
        if a["slug"] in used or a.get("type") not in OWN_TYPES:
            continue
        html = _layer(a, "BRIEFLY")
        if not html:
            continue
        used.add(a["slug"])
        out.append({"a": a, "html": html})
        if len(out) >= limit:
            break
    return out


def _pick_long(pool: list, used: set) -> dict | None:
    """Dlouhé čtení: nejlepší článek dne nebo feature a jeho vrstva DEEPER."""
    for a in sorted(pool, key=_rank):
        if a["slug"] in used or a.get("type") not in LONG_TYPES:
            continue
        html = _layer(a, "DEEPER")
        if not html:
            continue
        used.add(a["slug"])
        return {"a": a, "html": html}
    return None


def _pick_impact(pool: list, used: set) -> list:
    """Praktické dopady seskupené podle oblasti.

    Článek se počítá do té oblasti, která u něj vyšla jako první —
    jinak by se tentýž text objevil ve třech skupinách pod sebou.
    """
    groups: dict = {area: [] for area in impact.AREAS}
    for a in sorted(pool, key=_rank):
        block = a.get("impact")
        if a["slug"] in used or not block or not block.get("areas"):
            continue
        area = block["areas"][0]
        if area not in groups or len(groups[area]) >= IMPACT_PER_AREA:
            continue
        used.add(a["slug"])
        groups[area].append(a)
    # Klíč se schválně nejmenuje „items": v šabloně by `g.items` sáhlo
    # na metodu slovníku, ne na náš seznam.
    return [{"area": area, "articles": arts} for area, arts in groups.items() if arts]


def _pick_good(pool: list, used: set) -> list:
    """Dobré zprávy. Jen z rubriky, která je na to určená."""
    out = []
    for a in sorted(pool, key=_rank):
        if a["slug"] in used or a.get("section") != "goodnews":
            continue
        used.add(a["slug"])
        out.append(a)
        if len(out) >= GOOD_MAX:
            break
    return out


def _pick_reflect(pool: list, long_read: dict | None) -> dict | None:
    """Otázky na konec. Nejraději z dlouhého čtení — vydání tím drží
    pohromadě: čtenář se ptá na to, co právě přečetl."""
    if long_read:
        html = _layer(long_read["a"], "REFLECT")
        if html:
            return {"a": long_read["a"], "html": html}
    for a in sorted(pool, key=_rank):
        html = _layer(a, "REFLECT")
        if html:
            return {"a": a, "html": html}
    return None


# ------------------------------------------------------------------ složení
def compose(arts: list, edition: dt.date, *, lang: str = "", today=None) -> dict | None:
    """Poskládá jedno číslo. Vrátí None, když ten týden nebylo z čeho."""
    start, end = window(edition)
    pool = _in_window(arts, start, end)
    number = issue_number(edition, today)
    if len(pool) < MIN_ARTICLES:
        config.log(
            f"Sobotní vydání {lang} č. {number} ({start} – {end}) se nestaví: "
            f"článků za ten týden {len(pool)}, potřeba je aspoň {MIN_ARTICLES}."
        )
        return None

    # Pořadí, ve kterém si sekce zabírají články, je skoro totéž jako
    # pořadí, ve kterém je čtenář potká. Jediná odchylka: dobré zprávy
    # si berou dřív než praktické dopady. Dopadů bývá dvacet a o jeden
    # nepřijdou, dobré zprávy jsou v týdnu jedna dvě — kdyby je předběhly
    # dopady, zmizela by celá sekce kvůli jednomu řádku jinde.
    used: set = set()
    briefly = _pick_briefly(pool, used, briefly_count())
    long_read = _pick_long(pool, used)
    good = _pick_good(pool, used)
    impacts = _pick_impact(pool, used)
    reflect = _pick_reflect(pool, long_read)

    return {
        "no": number,
        "date": edition.isoformat(),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "next": (edition + dt.timedelta(days=7)).isoformat(),
        # Uzavřené číslo je hotové a už se nemění. Neuzavřené je to,
        # které se právě sází — v sobotu se uzavře samo.
        "closed": edition <= (_as_date(today) or dt.date.today()),
        "count": len(pool),
        "briefly": briefly,
        "long": long_read,
        "impact": impacts,
        "good": good,
        "reflect": reflect,
    }


def plan(arts: list, *, lang: str = "", today=None) -> list[dict]:
    """Všechna čísla, která se dají postavit. Nejnovější první."""
    if not enabled():
        return []
    out = [compose(arts, day, lang=lang, today=today) for day in edition_dates(today)]
    return [issue for issue in out if issue]
