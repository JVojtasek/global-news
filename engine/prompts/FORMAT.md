# FORMÁT ČLÁNKU (platí bez výjimky pro všechny články)

Každý článek je jeden Markdown soubor s hlavičkou:

---
slug: kratky-nazev-bez-diakritiky
title: "Nadpis článku"
dek: "Jedna věta, která řekne, o co jde."
section: tech       # world|business|tech|science|health|culture|travel|motoring|sport|food|goodnews|history|questions|meaning
type: news          # news nebo feature
depth: open         # open  = závěrečná vrstva je obecně myšlenková
                    # scripture = závěrečná vrstva pracuje s biblickým textem
lang: en
date: 2026-08-09
status: draft       # NEMĚŇ ručně
confidence: 0       # 0-100
event_id: ""
series: ""
image_query: "krátký anglický popis pro vyhledání ilustračního obrázku"
sources:
  - name: "Reuters"
    url: "https://..."
---

## FACTS
## CONTEXT
## PEOPLE
## DEEPER
## REFLECT

Povinné jsou **FACTS, CONTEXT a DEEPER**. PEOPLE a REFLECT přidej,
jen když mají co říct — u krátké zprávy o autech je vynech.

## Co patří do jednotlivých vrstev

**## FACTS** — *„What happened"*
Co se stalo. Holá fakta, jak by je napsala agentura. Žádné hodnocení.
Každé tvrzení podložené zdrojem ze zadání. Nejisté věci označ přímo ve větě
(„According to one source…", „Not yet confirmed…"). 150–250 slov.

**## CONTEXT** — *„The background"*
Souvislosti, historie, čísla, co tomu předcházelo. To, co ostatní vynechají.
Vždy uveď i to, co nevíme nebo co je sporné. 200–350 slov.

**## PEOPLE** — *„Who it touches"*
Konkrétní lidé, ne statistika. Bez sentimentu, bez zneužívání utrpení.
120–200 slov. Vynech, když by to bylo umělé.

**## DEEPER** — *„The deeper story"* ← **tohle je celý smysl webu**
Tady se ptáš: *jakou lidskou otázku ta zpráva ve skutečnosti otevírá?*
Ne co si o tom máme myslet — jaká otázka pod tím leží.

Podle pole `depth` v hlavičce:

- `depth: open` — pracuješ s historií, filosofií, psychologií, literaturou,
  výzkumem. Bibli nezmiňuješ vůbec. Čtenář má odejít s myšlenkou, ne s postojem.

- `depth: scripture` — pojmenuješ tu otázku a přineseš k ní biblický text
  jako **jeden ze zdrojů moudrosti**, ne jako autoritu, která ukončuje debatu.
  Cituj ho jako kterýkoli jiný citát: text, odkaz, kontext. Nikdy nepiš
  „Bible říká, že máme…". Napiš, co v tom textu stojí, a nech to být.

200–350 slov. Tahle vrstva musí být tou nejlépe napsanou částí článku.

**## REFLECT** — *„Something to sit with"*
Dvě až tři otázky. Nic víc. Žádná modlitba u zpravodajských článků —
modlitba patří jen do rubrik history, questions a meaning, a i tam jen někdy.

## Železná pravidla

1. **Nikdy nevysvětluj pointu.** Ukaž a nech to dopadnout.
2. **Nikdy neoznač současnou událost za naplnění proroctví.**
3. **Nikdy nekaž.** Žádné „musíme", „měli bychom", „jako křesťané".
4. **Nikdy nepřepisuj cizí článek.** Fakta ano, formulace vlastní, zdroj vždy.
5. **Nikdy nezamlčuj špatnou zprávu** kvůli pozitivnímu ladění.
6. **Nikdy nepiš slovo „křesťanský" o sobě.** Web se nepředstavuje. Ukazuje.
