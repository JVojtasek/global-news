# My Paper — trvalá pravidla projektu

Tenhle soubor si přečti vždycky, když v tomhle repozitáři něco děláš.
Je to paměť projektu. Jednotlivé prompty se mění, tohle ne.

## Pravidlo číslo jedna — k čemu je článek

**Každý článek musí mít přidanou hodnotu. Musí být praktický, zábavný,
edukativní a napsaný čtivou formou.**

Pět otázek, kterými musí projít každý text, než se uloží:

1. Odchází čtenář s něčím, co před čtením neměl?
2. Je tam aspoň jedna věc, kterou může dnes použít nebo si ověřit?
3. Dočte to i ten, kdo nemusí?
4. Vysvětluje to, *jak to funguje* — ne jen *co se stalo*?
5. Krátké věty, odstavce do 120 slov, žádný žargon bez vysvětlení?

Když u kterékoli odpovíš „ne", článek se nevydá. Prázdná rubrika je
menší škoda než jeden odbytý text.

Delší verze: `engine/prompts/FORMAT.md`, oddíl 0.

## Pravidlo číslo dvě — jakým hlasem píšeme

Závazný hlas všech článků, analýz, kvízů, překladů i oprav je v
`engine/prompts/VOICE.md`. Píšeme s úsudkem přemýšlivého, zkušeného
redaktora kolem padesáti let: lidsky, konkrétně, s klidným humorem,
psychologickým postřehem a respektem ke čtenáři. Není to povolení
předstírat lidský životopis. Umělá inteligence si nikdy nevymýšlí
osobní vzpomínku nebo zkušenost, kterou žádný skutečný autor nedodal.

Přesnost není omluva pro nudu. Text, který je správný, ale zní jako
školní referát, firemní tisková zpráva nebo výstup stroje, se vrací
k přepsání.

## Co je tenhle web

Obecný zpravodajský a magazínový web v angličtině s českou verzí.
Křesťanské pozadí je **nenápadné, ne skryté**: web se nikdy nepředstavuje
jako náboženský, ale závěrečná vrstva článku (`## DEEPER`) se u části
textů ptá po smyslu a někdy sáhne i po biblickém textu — jako po jednom
ze zdrojů moudrosti, nikdy jako po autoritě, která ukončuje debatu.

Nikdy nekážeme. Nikdy nepíšeme „musíme" a „měli bychom".
Nikdy neoznačíme událost za naplnění proroctví.

## Právo a etika

Závazný je `data/EDITORIAL-CODE.md`. Pravidlové síto je `engine/inbox.py`.
Když se ta dvě rozcházejí, platí kodex a síto se opraví.

## Jak se to hýbe samo

**Nulové náklady jsou základní pravidlo.** Za tyhle noviny se neplatí nic:
žádné modelové API, žádný server. Píší je předplacení asistenti, GitHub
Actions je u veřejného repozitáře zdarma a web stojí na GitHub Pages.

- **ranní směna Claude Code** na Jardově počítači (`scripts/redakce.ps1`) —
  hlavní autor. Píše sloty podle `data/edition-plan.json` a sama pushuje.
- **naplánované úlohy ChatGPT Work** — druhý autor slotů 1–6.
- **naplánované úlohy Claude Cowork** — dohled a záskok přes den.
- **GitHub Actions** — sběr zpráv, redakční síto, vydání, publikace, hlídač.
  Články nikdy nepíší, jen je přebírají a kontrolují.
- `2c · Průběžná uzávěrka` běží každé dvě hodiny, takže vydání nestojí
  na jednom přesném čase — co dorazí odpoledne, vyjde odpoledne.
- `engine/autofill.py` je hotová, ale **nečinná** záloha přes placené API.
  Zapnout ji smí jen výslovné rozhodnutí; `tests/test_free_launch.py` hlídá,
  že žádný workflow nenačítá API klíč.

### Pravidlo o slotech (14. 8. 2026 kvůli tomu nevyšlo vydání)

Do slotů 1–7 se počítají **jen** soubory s `automation_generated: true`.
Článek s `automation_generated: false` a `edition_slot: 0` je platný článek,
ale slot NEZAPLNÍ — hlídač ho nevidí a vydání hlásí jako prázdné.
Když píšeš do vydání, ber sekci, typ a rozsah slov z `data/edition-plan.json`
a nastav `edition_slot: N`, `automation_generated: true`,
`automation_role: edition`, `status: draft`.
## Co si čtenář nastavuje sám

Dvě věci, obě čistě v prohlížeči:

- **rovnováha čtení** — kolik zpráv a jak natvrdo, plus ztlumená témata.
  Těžký článek se nikdy nemaže, jen se sbalí do vrstvy BRIEFLY.
- **personalizace** — rubriky a zájmy z `data/interests.yml` (včetně
  skupiny zdraví). Vybrané zájmy posouvají články nahoru.

Architektura: web je statický, nastavení žije v `localStorage`, řazení
dělá prohlížeč nad veřejným `articles.json`, který je pro všechny stejný.
Nic se nikam neposílá a my se to nedozvíme.

Tři pravidla, která se neporušují:

1. Zdravotní zájmy nikdy neopustí zařízení. Žádný server, formulář, účet
   ani analytika, která by je mohla přijmout.
2. Personalizace jen mění pořadí. Nikdy necenzuruje — skryje se jen
   výslovně ztlumené téma a i tehdy se napíše, kolik zpráv je skrytých.
3. Blok „mimo tvůj okruh" je povinný. Noviny, které ti jen přitakávají,
   jsou zrcadlo.

Podrobně: `data/EDITORIAL-CODE.md`, oddíl 5.

## Obrázky — bezpečnostní síto

Nevhodný obrázek u článku je horší než žádný. Síto má čtyři vrstvy
(`engine/imagebank.py`): zakázaná slova včetně názvu souboru, kategorie
na Wikimedia Commons, kontrola smysluplnosti dotazu na Wikipedii
a měření podílu kůže po stažení. **Nikdy žádnou z nich neobcházej
a při pochybnosti obrázek nepoužij.** Podrobně: `data/EDITORIAL-CODE.md`,
oddíl 8.

## Co v tomhle repozitáři nikdy nedělat

- neobcházet detekci automatického publikování na sociálních sítích
- nepoužívat cizí fotky bez volné licence a bez uvedení autora
- negenerovat obrázky umělou inteligencí
- nesahat na `data/state.json` ručně
