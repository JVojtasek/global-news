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

## Krok 1 — tabulky v Neonu (5 minut)

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

## Krok 3 — program na Cloudflare (5 minut)

Otevři si na počítači příkazovou řádku a piš postupně:

```bash
cd D:\projekty\global-news\infra\subscribe
npm install
npx wrangler login
```

(Poslední příkaz otevře prohlížeč a zeptá se, jestli to povoluješ.)

Teď zadáš ty tajné údaje. U každého příkazu se tě řádka zeptá na hodnotu
a ta se **nikde nezobrazí**:

```bash
npx wrangler secret put DATABASE_URL
```
→ vlož připojovací řetězec z Neonu (v konzoli **Connect** → *Connection string*,
zvol variantu **Pooled connection**)

```bash
npx wrangler secret put PROVIDER_KEY
```
→ vlož API key z beehiiv

```bash
npx wrangler secret put BEEHIIV_PUBLICATION_ID
```
→ vlož to `pub_…`

```bash
npx wrangler secret put IP_SALT
```
→ vlož jakoukoli dlouhou náhodnou změť znaků, třeba čtyřicet písmen
a číslic. Slouží k tomu, aby se z uložených otisků IP adres nedala
zpětně poskládat čitelná IP.

A nakonec:

```bash
npx wrangler deploy
```

Vypíše to adresu, něco jako
`https://mypaper-subscribe.tvuj-ucet.workers.dev`. **Tu adresu mi pošli** —
je veřejná, není to žádné tajemství, a já ji zapíšu do webu.

## Krok 4 — já dopíšu zbytek

Zapíšu tu adresu do `data/site.yml` pod `newsletter.form_action`, přidám
děkovnou stránku a odhlašovací odkaz a nasadím to. Od té chvíle okénko
funguje.

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
