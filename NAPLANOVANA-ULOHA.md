# Naplánovaná redakce ChatGPT Work — bez API klíče

Závazná pravidla jsou v
[`engine/prompts/SCHEDULED-NEWSROOM.md`](engine/prompts/SCHEDULED-NEWSROOM.md).
Nepoužívej starý postup s osobním GitHub tokenem vloženým do promptu.
ChatGPT Work používá připojený GitHub a žádné tajemství se nezapisuje do
konverzace ani repozitáře.

## Denní sestava

| Úloha | Výstup |
| --- | --- |
| Evergreen Value Scout | `data/daily-agenda/YYYY-MM-DD.md` se skóre poptávky, užitku, trvanlivosti, důkazů a originality |
| Sloty 1–4 | čtyři nové anglické hodnotové stránky: cornerstone, practical, science-to-life a interactive |
| Sloty 5–6 | dvě úplné a podstatné aktualizace existujících článků bez změny jejich URL |
| Slot 7 | jeden delší anglický článek se stavem `reserve` |
| GitHub Actions | kontrola hodnotových metadat, zdrojů, citlivých témat, duplicit a bezpečnosti aktualizace; potom vydání a nasazení |

Každý slot je samostatná naplánovaná úloha. Selhání jednoho výstupu proto
nezruší ostatních pět. Sloty 1–4 vytvoří jeden nový soubor v `content/inbox/`;
sloty 5–6 úplný návrh náhrady v `content/refresh-inbox/`. Žádná úloha nesmí
měnit živý článek přímo, slučovat větev ani obejít redakční kontrolu.

Pilíře, clustery a role pro konkrétní den určuje `data/edition-plan.json`,
který zdarma vytváří `python -m engine.edition`. Šest pilířů se každý den
posune, takže se dlouhodobě střídá duševní odolnost, zdraví, vztahy, příroda,
věda a smysl.

## Bezpečné první spuštění

1. V ChatGPT připoj GitHub a povol jen repozitář `JVojtasek/global-news`.
2. Nech ručně proběhnout scouta a jeden nový slot.
3. Zkontroluj nový soubor v `content/inbox/` a spusť workflow `2 · Redakce`.
4. Teprve po úspěšném průchodu testy nech běžet celou denní sestavu.

`OPENAI_API_KEY` ani `ANTHROPIC_API_KEY` nejsou pro tuto cestu potřeba.
Klíč v GitHub Secrets zůstává pouze volitelnou zálohou pro starý generátor.
