# Odběr e-mailem — jak to zapnout

Tenhle návod je psaný pro člověka, který není programátor. Je to zhruba
dvacet minut a nic z toho nestojí peníze.

Až tohle doděláš, přestane být okénko „odebírat" na webu jen ozdoba.

## Proč to má dvě části

Přihlášení k odběru jsou ve skutečnosti tři různé práce a každou dělá
někdo jiný:

| Práce | Kdo ji dělá | Proč zrovna on |
|---|---|---|
| Přijmout adresu z webu | malý program na Cloudflare | Statický web nemá kam formulář poslat. |
| Uložit ji | Neon (tvoje databáze) | Seznam patří tobě. Poskytovatele vyměníš, lidi ti zůstanou. |
| Doručit e-mail do schránky | rozesílací služba | Za doručením je SPF, DKIM, DMARC, odhlašovací odkaz a reputace domény. Když bys posílal sám z čerstvé domény, spadneš do spamu a **pověst mypaper.news si poškodíš natrvalo.** |

Ten třetí řádek je důvod, proč to nedělám celé v Neonu, i když jsi to
navrhoval. Uložit adresu je snadné. Doručit e-mail není.

---

## Krok 1 — tabulky v Neonu — HOTOVO

Tabulky už v projektu **QMA** stojí, ve vlastním schématu `mypaper`
vedle tabulek QMA. Založil je Claude 18. 8. 2026 přes konektor Neon.
Znovu to dělat nemusíš.

Zkontrolovat si to můžeš takhle — má vrátit prázdný seznam, ne chybu:

```sql
select * from mypaper.subscribers limit 5;
```

Kdyby bylo někdy potřeba je založit znovu (jiný projekt, čistý začátek),
skript `infra/neon-schema.sql` se smí pustit vícekrát a nic nerozbije:

1. Otevři [console.neon.tech](https://console.neon.tech) a vyber projekt,
   který už máš od QMA. Nový zakládat nemusíš — My Paper si sedne vedle
   do vlastního schématu `mypaper`, takže se s QMA nepotkají.
2. Vlevo klikni na **SQL Editor**.
3. Otevři soubor `infra/neon-schema.sql`, celý ho zkopíruj, vlož do
   editoru a dej **Run**.
4. Hotovo. Vzniknou dvě tabulky a dva přehledy.

Zkontrolovat si to můžeš takhle — mělo by to vrátit prázdný seznam,
ne chybu:

```sql
select * from mypaper.subscribers limit 5;
```

## Krok 2 — rozesílací služba (10 minut)

Založ si účet u **beehiiv** ([beehiiv.com](https://www.beehiiv.com)).
Zdarma zvládne 2 500 odběratelů, což ti vydrží hodně dlouho, a řeší
za tebe potvrzování adres, odhlašování i to, aby e-maily nekončily
ve spamu.

Potřebuješ z něj dvě věci:

- **API key** — v nastavení, oddíl *Integrations* nebo *API*
- **Publication ID** — v adrese, když jsi ve svých novinách; začíná `pub_`

Obojí si někam odlož, hned je použiješ. **Neposílej mi je do chatu** —
zadáš je sám v dalším kroku, uloží se zašifrovaně na Cloudflare a už
je nikdo neuvidí.

## Krok 3 — program na Cloudflare (10 minut, jen klikání)

Program schválně nepoužívá žádnou knihovnu, takže se **nic neinstaluje
a nepotřebuješ příkazovou řádku**. Celý se vloží do editoru na webu.

1. Otevři [dash.cloudflare.com](https://dash.cloudflare.com) →
   **Compute** → **Workers & Pages** → **Create** → **Start with Hello World**
   → **Deploy**. Pojmenuj ho `mypaper-subscribe`.
2. Klikni na **Edit code**. Smaž, co tam je, a vlož celý obsah souboru
   `infra/subscribe/src/index.js`. Dej **Deploy**.
3. Zpátky v přehledu Workeru: **Settings** → **Variables and Secrets**.

   Nejdřív tři obyčejné proměnné (typ *Text*):

   | Jméno | Hodnota |
   |---|---|
   | `ALLOWED_ORIGINS` | `https://mypaper.news` |
   | `SITE_URL` | `https://mypaper.news` |
   | `PROVIDER` | `beehiiv` |

   Pak čtyři tajné (typ **Secret** — po uložení je neuvidí ani Cloudflare):

   | Jméno | Co tam patří |
   |---|---|
   | `DATABASE_URL` | připojovací řetězec z Neonu, **Pooled connection** |
   | `PROVIDER_KEY` | API key z beehiiv |
   | `BEEHIIV_PUBLICATION_ID` | to `pub_…` z beehiiv |
   | `IP_SALT` | dlouhá náhodná změť znaků |

   Sůl si vyrobíš třeba tímhle v konzoli prohlížeče (F12):

   ```js
   crypto.randomUUID() + crypto.randomUUID()
   ```

4. Nahoře je adresa Workeru, něco jako
   `https://mypaper-subscribe.tvuj-ucet.workers.dev`. **Tu mi pošli** —
   je veřejná, není to žádné tajemství.

Jestli máš radši příkazovou řádku, jde to pořád i postaru:
`npm install && npx wrangler login && npx wrangler deploy`, pak
`npx wrangler secret put DATABASE_URL` a tak dál. Výsledek je stejný.

### Zkouška, jestli program dělá, co má

Nic se neinstaluje a databáze se nevolá:

```bash
node infra/subscribe/test/subscribe.test.mjs
```

Deset zkoušek — mimo jiné že se parametry nelepí do textu dotazu, že
se ukládá jen otisk IP adresy a že past na roboty tiše zabere.

## Krok 4 — já dopíšu zbytek

Zapíšu tu adresu do `data/site.yml` pod `newsletter.form_action`, přidám
děkovnou stránku a odhlašovací odkaz a nasadím to. Od té chvíle okénko
funguje.

## Dva seznamy, ne jeden

Čtenář si při přihlášení vybere, jak často chce psát:

| Volba | Sloupec `cadence` | Pohled v Neonu |
|---|---|---|
| Každé ráno — briefing na pět minut | `daily` | `mypaper.list_daily` |
| V sobotu — jedno vydání týdně | `weekly` | `mypaper.list_weekly` |

Předvybraná je sobota. Denní a týdenní rytmus jsou dva různé sliby
a jeden se nedá vnutit druhému: kdo chce ranní briefing, chce ho ráno;
komu stačí jedna zpráva týdně, toho denní e-mail odhlásí. Proto si
vybírá čtenář, ne my — a proto je předvybraný ten menší slib, který
se dá dodržet i ve špatném týdnu.

Rozesílat se tedy budou dva seznamy, ne jeden. V beehiiv jim odpovídají
dvě různé kampaně; rozliší se podle pole `cadence`, které tam program
posílá spolu s adresou.

---

## Co se ukládá a co se neukládá

Ukládá se: e-mail, jazyk, odkud člověk přišel, čas souhlasu, znění
souhlasu a **otisk** IP adresy (ne IP samotná).

Neukládá se a nikdy ukládat nebude: zdravotní zájmy, vybraná země,
nastavená míra informační zátěže ani ztlumená témata. Tyhle věci žijí
jen v prohlížeči čtenáře a žádný server je nesmí přijmout — je to
pravidlo z `data/EDITORIAL-CODE.md`, oddíl 5, a platí bez výjimky.

## Když se něco pokazí

- **`npm install` hlásí, že nezná `npm`** — nemáš nainstalovaný Node.js,
  stáhni ho z [nodejs.org](https://nodejs.org) a zkus to znovu.
- **`wrangler deploy` hlásí chybu s účtem** — pusť znovu `npx wrangler login`.
- **Adresa se uloží, ale e-mail nepřijde** — chybí nebo je špatně
  `PROVIDER_KEY` či `BEEHIIV_PUBLICATION_ID`. Adresa se ale **neztratila**,
  je v Neonu; po opravě ji doplníš do beehiiv jedním nahráním souboru.
- **Nic z toho nefunguje** — napiš mi a projdeme to spolu krok za krokem.

## Až budeš mít odběratele

V Neonu si je vypíšeš takhle:

```sql
-- kolik lidí, odkud a v jakém jazyce
select * from mypaper.subscribers_overview;

-- seznam k rozeslání
select email, lang from mypaper.active_subscribers;
```
