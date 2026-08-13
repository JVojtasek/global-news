# Naplánovaná redakce ChatGPT Work — bez API klíče

Závazná pravidla jsou v
[`engine/prompts/SCHEDULED-NEWSROOM.md`](engine/prompts/SCHEDULED-NEWSROOM.md).
Nepoužívej starý postup s osobním GitHub tokenem vloženým do promptu.
ChatGPT Work používá připojený GitHub a žádné tajemství se nezapisuje do
konverzace ani repozitáře.

## Denní sestava

| Úloha | Výstup |
| --- | --- |
| Research desk | `data/daily-agenda/YYYY-MM-DD.md` se sedmi různými tématy a zdroji |
| Sloty 1–6 | šest původních anglických článků či analýz v šesti různých rubrikách |
| Slot 7 | jeden delší anglický článek se stavem `reserve` |
| GitHub Actions | kontrola formátu, rozsahu, zdrojů, citlivých témat a duplicit; potom vydání a nasazení |

Všechny autorské úlohy navíc čtou `engine/prompts/VOICE.md`. Přesnost,
lidský hlas, praktičnost a čtivost jsou společný standard pro GPT i Claude.

## Redakce během dne

Ranní vydání zůstává konečné a klidné. Vedle něj mohou tři naplánované
kontroly v 12:30, 17:30 a 22:30 Europe/Prague reagovat na skutečně významnou
změnu. Každá kontrola se řídí `engine/prompts/INTRADAY-DESK.md`, smí vytvořit
nejvýš jeden nový text a při absenci významné změny nevytvoří nic.

Intradenní text má `automation_role: intraday`, `edition_slot: 0`,
`type: analysis` a `format: roundtable`. Formát „The Newsroom Table“ používá
transparentní AI role KAI (moderátor), MIRA (důkazy) a ORIN (rizika). Nikdy
nezabírá ranní slot 1–7 a nikdy nepřepisuje již vydaný článek.
Commit takového souboru spouští samostatnou bezplatnou bránu
`.github/workflows/2b-intraday.yml`, takže nemusí čekat na další ranní vydání.

Každý autorský slot je samostatná naplánovaná úloha. Selhání jednoho textu
proto nezruší ostatních pět. Autorská úloha smí vytvořit právě jeden nový
soubor `content/inbox/YYYY-MM-DD-slot-N-slug.md`; nesmí slučovat větev,
měnit workflow ani obejít redakční kontrolu.

Rubriky a role pro konkrétní den určuje `data/edition-plan.json`, který zdarma
vytváří `python -m engine.edition`. Rubriky se každý den posunou a v jednom
vydání se neopakují.

## Bezpečné první spuštění

1. V ChatGPT připoj GitHub a povol jen repozitář `JVojtasek/global-news`.
2. Nech ručně proběhnout research desk a jeden veřejný slot.
3. Zkontroluj nový soubor v `content/inbox/` a spusť workflow `2 · Redakce`.
4. Teprve po úspěšném průchodu testy nech běžet celou denní sestavu.

`OPENAI_API_KEY` ani `ANTHROPIC_API_KEY` nejsou pro tuto cestu potřeba.
Klíč v GitHub Secrets zůstává pouze volitelnou zálohou pro starý generátor.
