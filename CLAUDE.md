# The Deeper Story — trvalá pravidla projektu

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

- GitHub Actions — sběr zpráv, publikace, hlídač (zdarma, veřejný repo)
- ranní směna Claude Code na Jardově počítači — píše původní články
- vše ostatní je statický web na GitHub Pages, žádný server, žádné platby

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

## Co v tomhle repozitáři nikdy nedělat

- neobcházet detekci automatického publikování na sociálních sítích
- nepoužívat cizí fotky bez volné licence a bez uvedení autora
- negenerovat obrázky umělou inteligencí
- nesahat na `data/state.json` ručně
