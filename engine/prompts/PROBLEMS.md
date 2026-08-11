# Formát stránky velkého problému

Soubor: `content/problems/<id>.<lang>.md` — jen hlavička (YAML) a pod ní krátký úvod.
Všechny tři sloupce jsou v hlavičce, aby vypadaly na všech deseti stránkách stejně
a aby šlo doplnit jedenáctý problém bez sahání do kódu.

```yaml
---
id: housing                 # stejné ve všech jazycích, je z něj adresa /problems/housing/
lang: en
title: "Housing: what has actually worked, and where"
dek: "Jedna věta, o čem stránka je."
status: published
date: 2026-08-11
updated: 2026-08-11         # datum, kdy někdo naposled ověřil čísla

measure:                    # JEDNO číslo, proti kterému se poměřuje celá stránka
  name: "Median rent as a share of median disposable income"
  unit: "%"
  better: low               # low | high — kterým směrem je to lepší
  source: "OECD Affordable Housing Database HC1.2, 2025"
  url: "https://..."

board:                      # žebříček — 5 až 8 zemí, seřazené od nejlepší
  - country: at             # kód z data/countries.yml (kvůli prokliku na stránku země)
    value: "21.6 %"         # hotový text i s jednotkou
    note: "Jedna věta: čím to je."

tried:                      # 3 až 5 skutečných pokusů, včetně jednoho, který nevyšel
  - country: at
    what: "Co konkrétně udělali. 2–3 věty. Konkrétní roky a čísla."
    result: "Co pak udělala čísla. Musí obsahovat aspoň jedno měřené číslo."
    caveat: "Háček. Co se za to zaplatilo, nebo proč to jinde nepůjde."
    source: "Jméno zdroje"
    url: "https://..."

machine:                    # počet, ne rada
  optimise: "Jedna věta: které jediné číslo se vyhání nahoru."
  moves:                    # 3 až 4 kroky, které z toho počtu vyplývají
    - "Konkrétní krok. Ne obecnost."
  arithmetic: "Číslo, na kterém to stojí, aby si to čtenář mohl přepočítat."

blind:                      # 3 body, tohle je nejdůležitější část stránky
  - point: "Kdo to zaplatí"
    text: "2–3 věty, konkrétně kdo a kolik."
  - point: "Co se v tom čísle ztratí"
    text: "..."
  - point: "Co tabulka nevidí"
    text: "..."

sources:                    # všechny zdroje pohromadě, kvůli ověřitelnosti
  - name: "OECD Affordable Housing Database"
    url: "https://..."
---

Dva až tři odstavce úvodu. Co ten problém je, proč se ho nedaří vyřešit,
a jedno číslo, které to postaví do měřítka. Bez patosu, bez „musíme".
