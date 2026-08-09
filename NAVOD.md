# The Deeper Story — návod krok za krokem

Psáno pro člověka, který neprogramuje. Nemusíš rozumět ani řádku kódu.
Celé zprovoznění zabere zhruba 40 minut a nic z toho není nevratné.

---

## Co to vlastně je

Redakce, která běží sama. Skládá se ze čtyř věcí:

| Co | Kde to běží | Co to stojí |
|---|---|---|
| Sběr zpráv z 50 zdrojů a plánovač | GitHub Actions | 0 Kč |
| Psaní článků | naplánovaná Claude úloha (tvoje předplatné) | 0 Kč navíc |
| Obrázky | Openverse + Wikimedia Commons | 0 Kč |
| Web | GitHub Pages | 0 Kč |
| Bluesky a Telegram | oficiální rozhraní platforem | 0 Kč |
| Doména | u registrátora | ~300 Kč/rok |
| Záložní API klíč | Anthropic nebo OpenAI | volitelné, pár $ měsíčně |

---

## KROK 1 · Nahrát projekt na GitHub  (10 minut)

1. Rozbal ZIP, který jsi dostal.
2. Jdi na <https://github.com/new>.
   - **Repository name:** `newsroom` (nebo jak chceš)
   - **Public** — musí být veřejný, jinak jsou GitHub Actions omezené
   - **NEZAŠKRTÁVEJ** „Add a README file"
   - **Create repository**
3. Na další stránce klikni na odkaz **„uploading an existing file"**.
4. Přetáhni do okna **všechen obsah** rozbalené složky.
   ⚠️ Pozor na skrytou složku `.github` — bez ní nebude nic fungovat.
   Na Macu ji zobrazíš klávesami `Cmd + Shift + .`, ve Windows
   ve Zobrazení → Skryté položky.
5. Dole klikni **Commit changes**.

---

## KROK 2 · Zapnout web  (3 minuty)

1. V repozitáři nahoře **Settings** → vlevo **Pages**.
2. **Source:** přepni na `GitHub Actions`.
3. Hotovo. Adresa webu bude
   `https://TVUJ-UCET.github.io/newsroom/`

---

## KROK 3 · První spuštění naprázdno  (5 minut)

1. Nahoře **Actions**. Když se zeptá, potvrď zelené tlačítko
   „I understand my workflows, go ahead and enable them".
2. Vlevo klikni **„1 · Sběr zpráv"** → vpravo **Run workflow** → **Run workflow**.
3. Počkej dvě minuty a obnov stránku. Když je u běhu zelená fajfka, funguje to.
4. V repozitáři se objevil soubor `data/brief.md`. Otevři si ho —
   to je objednávka práce pro redakci. Uvidíš v ní dnešní nejdůležitější
   události i s odkazy na zdroje.

**Když je červený křížek:** klikni na běh, rozklikni krok, který spadl,
a přečti si poslední řádky. Nejčastější příčina je chybějící složka
`.github` (viz krok 1).

---

## KROK 4 · Napojit psaní článků  (15 minut)

Otevři soubor `NAPLANOVANA-ULOHA.md` a udělej, co je v něm.
Ve zkratce: vyrobíš si na GitHubu přístupový token a založíš v aplikaci
Claude naplánovanou úlohu, která každé ráno napíše články a uloží je
zpátky do repozitáře.

Až úloha jednou proběhne, podívej se do složky `content/inbox/`.
Když tam něco je, spusť ručně **Actions → „2 · Redakce" → Run workflow**
a sleduj, jak se články zkontrolují a vydají.

---

## KROK 5b · Vlastní doména  (volitelné, 10 minut)

1. Kup si doménu (Forpsi, Wedos, Cloudflare, Namecheap — je to jedno).
2. U registrátora nastav DNS záznamy:
   - `A` záznam pro `@` → `185.199.108.153`
   - `A` záznam pro `@` → `185.199.109.153`
   - `A` záznam pro `@` → `185.199.110.153`
   - `A` záznam pro `@` → `185.199.111.153`
   - `CNAME` pro `www` → `TVUJ-UCET.github.io`
3. V repozitáři **Settings → Pages → Custom domain** vlož svoji doménu
   a zaškrtni **Enforce HTTPS**.
4. V souboru `data/site.yml` uprav řádek `url:` na svoji adresu.

---

## KROK 5 · Admin sekce  (10 minut)

Tohle je tvoje ovládací místnost. Najdeš ji na adrese
`https://TVUJ-UCET.github.io/newsroom/admin/` a otevřeš ji i z mobilu.

**Jak se do ní dostaneš:**

1. Jdi na <https://github.com/settings/personal-access-tokens/new>
2. **Token name:** `admin`, **Expiration:** `No expiration`
3. **Repository access:** `Only select repositories` → vyber svůj repozitář
4. V **Permissions → Repository permissions** nastav:
   - **Contents:** `Read and write`
   - **Actions:** `Read and write`
5. **Generate token**, zkopíruj ho.
6. Otevři admin, vlož jméno repozitáře (`tvujucet/newsroom`) a token, přihlas se.

**Co v adminu máš:**

| Záložka | K čemu je |
|---|---|
| **Přehled** | kolik je vydáno, co čeká, jak jsi na tom s předpověďmi, dnešní objednávka práce |
| **Ke schválení** | články, u kterých si systém nebyl jistý — přečteš, upravíš, vydáš nebo zahodíš |
| **Sociální sítě** | připravené příspěvky pro každou síť zvlášť — upravíš text, odkliknéš, systém odešle |
| **Články** | všechno vydané, s možností kdykoli přepsat |
| **Předpovědi** | otevřené předpovědi, které můžeš rozhodnout ručně |
| **Nastavení** | kolik článků denně, jak často biblická vrstva, poloautomat vs. automat |
| **Spustit** | tlačítka „nečekej na plán, udělej to teď" |

**Dvě věci k bezpečnosti, ať se nelekneš.** Ta stránka je veřejně dostupná, ale
**bez tokenu na ní nic není** — je to prázdný formulář. Token se ukládá jen
do tvého prohlížeče, nikam se neodesílá a v repozitáři není. Kdybys přišel
o notebook, jdi na stejnou stránku, kde jsi token vyrobil, a zruš ho — tím
okamžitě přestane platit a nikdo se nikam nedostane.

---

## KROK 8 · Trychtýř na čtenáře  (30 minut, dělej až po spuštění)

Web je hotový a technicky připravený, ale dokud tě vyhledávače neznají,
nikdo nepřijde. Tohle je pořadí, ve kterém to udělat.

**1. Google Search Console** — <https://search.google.com/search-console>
Přidej svoji doménu, Google ti dá ověřovací kód. Vlož ho v adminu
do `seo.google_verification`. Pak tam vlož adresu `tvujweb.cz/sitemap.xml`.
Bez tohohle kroku tě Google najde možná za měsíc, s ním za dva dny.

**2. Bing Webmaster Tools** — <https://www.bing.com/webmasters>
To samé. Bing napájí i vyhledávání v ChatGPT, takže to není zbytečné.

**3. Newsletter.** Založ si účet u kterékoli e-mailové služby (MailerLite
a Buttondown mají použitelný tarif zdarma). Vytvoř přihlašovací formulář,
zkopíruj z něj adresu, kam odesílá, a vlož ji do `newsletter.form_action`.
Formulář na webu se tím rozsvítí sám.

**4. Google News** — <https://publishercenter.google.com>
Přihlas web až ve chvíli, kdy tam bude aspoň třicet vlastních článků
a stránka „About". Dřív tě odmítnou a přihlásit se dá znovu až za čas.

**Co už je hotové a nemusíš řešit:** hreflang pro obě jazykové verze,
strukturovaný popis článků, drobečková navigace, otázky a odpovědi pro
bohatý výsledek ve vyhledávači, kanonické odkazy, sitemapy včetně
zpravodajské, náhledy pro sdílení, doba čtení a související články.

---

## Jak ten trychtýř funguje

```
1. PŘIJDE     z vyhledávače na konkrétní otázku
                 („why does burnout happen at work")
                 ↓
2. ZŮSTANE    na konci článku najde tři související
                 ↓
3. VRÁTÍ SE   přihlásí se k odběru
                 ↓
4. POSUNE SE  otevře „What we are doing here"
```

Každé patro má na webu své místo a všechna už fungují. Jediné, co jim
chybí, jsou lidé — a ty přivede až ten první krok, tedy vyhledávač.

---

## Co se stane, až systém poběží pár týdnů

První dva týdny to bude vypadat jako obyčejný zpravodajský web. Pak se
začnou dít dvě věci, které jinde nenajdeš.

**Analýzy z paměti.** Systém si u každého tématu vede časovou osu. Jakmile
má nějaké téma tři a víc záznamů, začne z něj vznikat analýza typu
„co se za tři týdny opravdu změnilo" — a najde v ní věci, které z jednoho
dne vidět nejsou: že něco bylo v červenci popřeno a v srpnu potvrzeno,
nebo že se o něčem přestalo mluvit, aniž by se to vyřešilo.

**Předpovědi.** Systém začne vydávat konkrétní tvrzení s pravděpodobností
a termínem a po termínu si sám spočítá, jak dopadl. Najdeš to na adrese
`/en/forecasts/`. Bude tam i to, co nevyšlo — a právě proto to má cenu.

Nemusíš pro to nic udělat, jen to nechat běžet.

---

## KROK 6 · Sociální sítě  (volitelné, 15 minut)

Systém umí sám publikovat na Bluesky a Telegram. Obojí je zdarma a schválení
netrvá ani minutu. Facebook a Instagram vyžadují firemní účet a schvalovací
proces, takže pro ně systém jen připraví hotové texty do souboru
`data/social/k-vlozeni.md` a ty je jednou denně zkopíruješ.

**Bluesky:**

1. Založ si účet na <https://bsky.app>.
2. V aplikaci: Settings → Privacy and Security → App Passwords → Add App Password.
3. V repozitáři **Settings → Secrets and variables → Actions** přidej dva klíče:
   `BLUESKY_HANDLE` (např. `thedeeperstory.bsky.social`)
   a `BLUESKY_APP_PASSWORD` (to heslo, co ti Bluesky ukázalo).

**Telegram:**

1. V Telegramu napiš uživateli **@BotFather**, pošli `/newbot` a projdi otázky.
   Na konci ti pošle token.
2. Založ si kanál, přidej do něj svého bota jako administrátora.
3. ID kanálu zjistíš tak, že do kanálu něco napíšeš a otevřeš v prohlížeči
   `https://api.telegram.org/bot<TVUJ_TOKEN>/getUpdates` — hledáš číslo
   u `"chat":{"id":`. Bývá záporné, to je v pořádku.
4. Přidej klíče `TELEGRAM_BOT_TOKEN` a `TELEGRAM_CHAT_ID`.

Když klíče nepřidáš, nic se nerozbije — systém jen připraví texty k vložení.

---

## KROK 7 · Záložní API klíč  (volitelné, doporučeno)

Tohle je pojistka pro případ, že by naplánovaná úloha přestala fungovat.

1. Klíč získáš na <https://console.anthropic.com> nebo
   <https://platform.openai.com/api-keys>.
2. V repozitáři **Settings → Secrets and variables → Actions →
   New repository secret**.
3. **Name:** `ANTHROPIC_API_KEY` (nebo `OPENAI_API_KEY`),
   **Secret:** vlož klíč.

Denní strop útraty je nastavený v `data/site.yml` na 2 USD. Systém přes něj
nepřejde ani kdyby se něco zbláznilo.

---

## Co budeš dělat ty

Prakticky nic. Ale jednou týdně se vyplatí:

**Otevřít admin.** Uvidíš na jednom místě, co čeká na schválení a co je potřeba
odklepnout do sociálních sítí. To je celá týdenní údržba.

**Mrknout na `content/inbox/_rejected/`.** Sem padá to, co neprošlo kontrolou.
U každého odmítnutého článku je vedle textový soubor s vysvětlením proč.
Když se tam něco hromadí pořád dokola, je potřeba upravit pravidla.

**Doplnit stálá témata v `data/site.yml → topics.evergreen_seeds`.**
To jsou základy, ze kterých systém dolová otázky, které lidé píší do
vyhledávače. Čím líp je trefíš, tím líp bude web růst.

**Přidat témata do `data/series.yml`.** To je plán delších článků pro rubriky
Historie, Velké otázky a Mysl a smysl. Když dojde, systém začne opakovat —
radši ho průběžně doplňuj.

**Zkontrolovat obrázky.** Systém je hledá ve volných zdrojích a občas najde
něco, co k článku nesedí. Vlastní obrázek vložíš tak, že ho uložíš jako
`static/covers/<slug>.jpg` — slug je ta část adresy článku za poslední lomítkem.

**Přenastavit `depth_ratio`.** V `data/site.yml` určuje, v kolika procentech
článků je závěrečná vrstva výslovně biblická. Začni na 0.3 a podle toho,
jak lidé reagují, ho posuň nahoru nebo dolů.

---

## Jak to zastavit

**Actions → vyber workflow → tři tečky vpravo → Disable workflow.**
Nic se nesmaže, jen to přestane běžet. Zapnout jde stejně.

---

## Když si nebudeš vědět rady

V repozitáři je nástroj, který ti řekne česky, co je špatně.
**Actions → „4 · Hlídač" → Run workflow.** Za minutu ti vypíše zprávu
o stavu celé redakce. Ten samý hlídač běží automaticky každé pondělí
a když najde problém, založí ti na GitHubu úkol.

---

## Důležité upozornění o autorských právech

Systém nikdy nepřebírá cizí texty — bere z RSS jen titulek a krátký popis,
fakta si přepisuje vlastními slovy a ke každému článku vždy uvádí odkazy
na původní zdroje. To je běžná a přijatelná praxe.

U obrázků přijímá jen licence public domain, CC0, CC BY a CC BY-SA, autora
a licenci vždy uvádí pod obrázkem, a ostatní licence rovnou zahazuje.

Co bys dělat **neměl**: kopírovat celé odstavce z cizích webů, používat
cizí fotografie bez licence, nebo systém přenastavit tak, aby stahoval
plné texty článků. Tam už začínají problémy.

Než z toho uděláš něco komerčního (reklama, předplatné), nech si podmínky
projít někým, kdo se v tom vyzná. Do té doby to je nekomerční projekt
a riziko je malé.
