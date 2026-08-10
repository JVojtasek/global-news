# FORMÁT ČLÁNKU (platí bez výjimky pro všechny články)

## 0. TEST, KTERÝM MUSÍ PROJÍT KAŽDÝ ČLÁNEK

Než článek uložíš, projdi těchhle pět otázek. Když u kterékoli
odpovíš „ne", článek neukládej — přepiš ho, nebo ho zahoď.

1. **Přidaná hodnota.** Odchází čtenář s něčím, co před čtením neměl?
   Převyprávěná agenturní zpráva bez vlastního vkladu není článek.
2. **Praktičnost.** Je v textu aspoň jedna věc, kterou může čtenář
   dnes použít, ověřit si, nebo podle ní něco rozhodnout?
3. **Zábavnost.** Dočte to člověk, který si ten text neotevřel z povinnosti?
   Aspoň jeden obraz, příběh, přirovnání nebo detail, který si zapamatuje.
4. **Edukativnost.** Vysvětluje článek, *jak to funguje* — ne jen *co se stalo*?
   Po přečtení má čtenář rozumět i příští podobné zprávě.
5. **Čtivost.** Krátké věty. Odstavce do 120 slov. Žádný odborný žargon
   bez okamžitého vysvětlení. Piš, jako bys to vyprávěl chytrému
   kamarádovi, který o tématu nic neví — nikdy blahosklonně.

Radši tři takové články než deset odbytých. Tohle pravidlo je nadřazené
kvótám: když nemáš čím naplnit rubriku, nech ji ten den prázdnou.

---

Každý článek je jeden Markdown soubor s hlavičkou:

---
slug: kratky-nazev-bez-diakritiky
title: "Nadpis článku"
dek: "Jedna věta, která řekne, o co jde."
section: tech       # world|business|tech|science|health|culture|travel|motoring|sport|food|goodnews|history|questions|meaning
type: news          # news | daily (článek dne) | demand | feature | analysis
depth: open         # open  = závěrečná vrstva je obecně myšlenková
                    # scripture = závěrečná vrstva pracuje s biblickým textem
lang: en
date: 2026-08-09
status: draft       # NEMĚŇ ručně
confidence: 0       # 0-100
load: 0             # 0-100, psychická zátěž článku. Nech 0 a systém si ji spočítá sám;
                    # vyplň jen tehdy, když se výpočet zjevně mýlí
topics: []          # štítky pro filtr čtenáře: war, crime, disaster, politics,
                    # health, money, tech. Nech prázdné a systém je doplní
event_id: ""
series: ""
image_query: "krátký anglický popis pro vyhledání ilustračního obrázku"
sources:
  - name: "Reuters"
    url: "https://..."
---

## BRIEFLY
## FACTS
## CONTEXT
## PEOPLE
## DEEPER
## REFLECT

Povinné jsou **FACTS, CONTEXT a DEEPER**. **BRIEFLY** je povinné
u `type: news` a u `type: analysis` — všude jinde ho piš, kdykoli to jde,
čtenář ho ocení i u dlouhého textu. PEOPLE a REFLECT přidej, jen když
mají co říct — u krátké zprávy o autech je vynech.

## Zátěž a štítky (load, topics)

Čtenář si na webu sám nastaví, kolik toho na něj má web pustit, jak
natvrdo a která témata mu sem nemáme dávat. Aby to šlo, potřebuje web
u každého článku vědět dvě věci: jak je ten text těžký (`load`) a čeho
se týká (`topics`). Obojí si spočítá sám z textu, takže je nech tak, jak
jsou, a sáhni na ně jen tehdy, když se výpočet zjevně mýlí. Nic se tím
nemaže ani neschovává: v šetrném režimu se u těžkého článku ukáže jen
vrstva BRIEFLY a zbytek si čtenář kdykoli rozklikne.

## Co patří do jednotlivých vrstev

**## BRIEFLY** — *„In short"* ← **tohle přečte i ten, kdo dál nepokračuje**
Klidné shrnutí celého článku v pěti řádcích. Je tady kvůli lidem, kteří
chtějí vědět, co se děje, ale nechtějí se tím nechat rozhodit. Kdo si
v nastavení čtení zvolí šetrný režim, uvidí u těžkého článku **jenom
tuhle vrstvu** — zbytek si rozklikne, až bude chtít, nebo taky nikdy.
Proto musí obstát úplně sama za sebe.

Přesný tvar — pět řádků uvozených tučným popiskem, nic víc, žádné odrážky:

```
## BRIEFLY

**What happened.** Jedna věta. Bez přídavných jmen.

**What it means.** Nejvýš dvě věty. Proč na tom záleží i po dnešku.

**Risks and impact.** Koho se to doopravdy týká a jak. Konkrétně
a přiměřeně — nic nenafukuj a nic nezlehčuj.

**What can be done.** Co se s tím dělá a co s tím může udělat, ověřit si
nebo rozhodnout běžný čtenář. Když je poctivá odpověď „nic, jen o tom
vědět", napiš to.

**What to watch.** Ta jedna věc, podle které se pozná, jestli se to
lepší, nebo horší — a zhruba kdy.
```

V českých článcích jsou popisky takhle: **Co se stalo.** / **Co to
znamená.** / **Rizika a dopady.** / **Co se s tím dá dělat.** /
**Na co se dívat dál.**

Pravidla, která u téhle vrstvy platí bez výjimky:

- 120–180 slov za celou vrstvu. Když je delší, není to shrnutí.
- Musí být čitelná úplně sama o sobě, pro člověka, který zbytek nepřečte.
  Žádné „jak jsme psali výše".
- Nikdy sem nedávej číslo, které není i ve FACTS a tam se zdrojem.
- Nikdy sem nedávej tvrzení, které článek nepodkládá.
- Žádná citově zabarvená přídavná jména. Tahle vrstva je přesně pro lidi,
  kteří nechtějí být vybuzení.
- „What can be done" nikdy nesmí být rada, kterou má dát lékař, právník
  nebo finanční poradce. Je to: co si ověřit, koho se zeptat, kde jsou
  oficiální informace.

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
