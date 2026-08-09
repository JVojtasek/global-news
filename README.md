# The Deeper Story — autonomní zpravodajský portál

Plnohodnotný zpravodajský web (svět, byznys, technologie, věda, zdraví,
kultura, cestování, sport a další), který ke každé zprávě přidává vrstvu,
kterou jinde nenajdeš: otázku, co za tou zprávou vlastně leží.

Běží sám. Denní obsluhu nepotřebuje.

**Začni tady: [NAVOD.md](NAVOD.md)**

## Co kde je

```
data/site.yml               ← jediné nastavení, které budeš měnit
data/sources.yml            ← 50 zpravodajských zdrojů, rozdělených po rubrikách
data/series.yml             ← plán delších článků (historie, otázky, mysl)
data/brief.md               ← dnešní objednávka práce (generuje se sama)
data/pages/                 ← stránky "About" a "What we are doing here"
data/covers/                ← stažené ilustrační obrázky + jejich licence
data/social/k-vlozeni.md    ← hotové příspěvky na Facebook, Instagram, X, LinkedIn

content/en/                 ← hotové články
content/inbox/              ← sem odkládá články naplánovaná Claude úloha
content/inbox/_rejected/    ← co neprošlo kontrolou + proč

engine/prompts/             ← redakční pravidla pro AI (tady se ladí kvalita)
static/covers/              ← sem si můžeš položit vlastní obrázek: <slug>.jpg
.github/workflows/          ← plánovač (běží zdarma na GitHubu)
```

## Stavba článku

Každý článek má stejné vrstvy ve stejném pořadí:

| Vrstva | Co v ní je |
|---|---|
| **What happened** | holá fakta, jak by je napsala agentura |
| **The background** | souvislosti, čísla, co je sporné, co nevíme |
| **Who it touches** | konkrétní lidé místo statistiky |
| **The deeper story** | otázka, která pod zprávou leží ← **tohle je celý smysl webu** |
| **Something to sit with** | dvě tři otázky, nic víc |

Poslední vrstva má dva režimy, řízené polem `depth` v hlavičce článku:

- `open` — historie, filosofie, psychologie, literatura. Bible se nezmiňuje.
- `scripture` — k té otázce se přinese i biblický text, jako jeden ze zdrojů
  moudrosti vedle ostatních. Nikdy jako autorita, která debatu ukončuje.

Poměr mezi nimi nastavuješ v `data/site.yml` položkou `depth_ratio`
(výchozí 0.3 = zhruba třetina článků). V rubrikách sport, jídlo, cestování
a auto-moto je biblická vrstva vypnutá vždy.

## Článek dne

Jeden pořádně propracovaný původní text denně. Rubriky se střídají podle
pořadí v `data/site.yml → editorial.daily_feature.rotation`, takže žádná
nezůstane hluchá:

```
technologie → vztahy → věda → rodina a výchova → mysl a smysl →
historie → zdraví → velké otázky → byznys → kultura → (znovu)
```

Téma se bere z doložené poptávky (co lidé opravdu hledají) a **k němu se
stáhnou podklady z Wikipedie**, takže AI nepíše z hlavy. Pak jde text
delší cestou než běžné zpravodajství:

```
podklady → draft → KONTROLA FAKTŮ → teologie → skeptik → přepis
```

Kontrola faktů projde text větu po větě, vypíše každé číslo, jméno, rok
a citaci a porovná je s podklady. Cokoli, co v nich není, se buď opraví,
nebo z textu vyhodí. Jediné vymyšlené číslo shodí článek k ruční kontrole.

Nad tím ještě běží kontrola čitelnosti: odstavec delší než 190 slov nebo
průměrná věta přes 32 slov článek zastaví. Zeď textu nikdo nečte.

## Témata, po kterých je poptávka

`engine/trends.py` hledá, o čem lidé skutečně chtějí číst — ale ne tak,
jak to dělá většina webů.

**Denní žebříčky vyhledávání jsou past.** Když se na ně dnes podíváš,
uvidíš „Benfica", „Kylie Jenner", „Djoković". Sport a celebrity tvoří
zhruba devadesát procent trendů a nikdy je nevyhrajeme — píše o nich
tisíc redakcí, které tam byly dřív a mají větší váhu.

Co má cenu, jsou **otázky, které lidé píší do vyhledávače pořád dokola**.
Modul proto z trendů, Wikipedie a Hacker News vytáhne jen to, co vůbec
patří do našich rubrik, a každé téma rozvine na skutečné dotazy:

```
burnout
  „why does burnout happen“
  „why does burnout happen at work“
  „why is burnout so common“
  „why is burnout so high in emergency medicine“
```

Tyhle otázky mají stálou poptávku, slabou konkurenci a nezastarají za týden.
Redakce na ně pak píše původní články s jediným tvrdým pravidlem:
**odpověď musí být v prvním odstavci.** Ne po třech odstavcích úvodu.

Zdroje signálu jsou zdarma a bez klíčů: Google Trends, Wikipedia pageviews,
Hacker News a našeptávač vyhledávače. Seznam stálých témat, ze kterých
se doluje i ve dnech, kdy jsou trendy k ničemu, je v `data/site.yml → topics`.

## Analytik s pamětí

Zpravodajství má krátkou paměť — každý den začíná od nuly. Tenhle systém ne.

`engine/memory.py` spojuje související události do **vláken** a u každého drží
celou časovou osu. Po pár týdnech běhu systém ví věci, které z jednoho dne
poznat nejde: že se tohle letos stalo počtvrté, že to bylo v květnu popřeno
a v srpnu potvrzeno, nebo že se o něčem tři týdny nemluvilo a najednou zase ano.

Z toho vznikají **původní analýzy**, které nikdo jiný napsat nemůže, protože
nemá záznam. Zadání pro ně najdeš v `data/memory/analyst-brief.md`.

## Veřejný záznam předpovědí

Místo mlhavého „experti očekávají" vydáváme konkrétní tvrzení s pravděpodobností
a termínem — a po termínu si sami veřejně spočítáme, jak jsme dopadli.
Včetně případů, kdy jsme se spletli. Nic se z té stránky nikdy nemaže.

Měří se Brierovým skóre: 0,00 je dokonalé, 0,25 dostane ten, kdo na všechno
řekne 50 %, nad 0,30 už jde o hádání. Stránka je na `/en/forecasts/`.

Tohle nedělá skoro žádné médium na světě a je to nejsilnější možný doklad,
že to s poctivostí myslíš vážně.

## Přebírání celých článků

V `data/syndication.yml` jsou zdroje, které přebírání výslovně dovolují —
Global Voices (CC BY) a NASA (veřejné vlastnictví). U každého je zapsáno,
co přesně smíme, a systém to dodržuje doslova: kde licence zakazuje překlad,
článek se nepřeloží; kde nejsou fotky pod licencí, fotky se zahodí.

⚠️ **Nepřidávej do toho souboru nic, u čeho sis licenci neověřil.**
Špatný řádek tam znamená porušení autorských práv na tvém webu.

## SEO a trychtýř na čtenáře

```
1. PŘIJDE     vyhledávač → článek odpovídající na konkrétní otázku
2. ZŮSTANE    tři související články na konci textu
3. VRÁTÍ SE   přihlášení k odběru
4. POSUNE SE  stránka „What we are doing here"
```

Co je v každém článku hotové:

- `hreflang` pro obě jazykové verze (bez toho si je Google plete)
- `NewsArticle`, `BreadcrumbList` a u otázkových článků `FAQPage`
  (bohatý výsledek ve vyhledávači)
- kanonický odkaz — u převzatých a importovaných míří na originál
- náhled pro sdílení včetně `twitter:card`
- doba čtení a tři související články
- `sitemap.xml` jako rejstřík + samostatná zpravodajská sitemapa

Ověřovací kódy pro Google a Bing a adresu přihlašovacího formuláře
vyplníš v `data/site.yml → seo` a `newsletter`. Postup je v NAVOD.md, krok 8.

## Admin sekce

`/admin/` — ovládací místnost dostupná i z mobilu. Schvalování článků,
příspěvky na sítě, předpovědi, nastavení a ruční spouštění úloh.

Nepotřebuje žádný server. Je to jedna statická stránka, která přes GitHub API
mluví přímo s repozitářem. Bez přístupového tokenu je to prázdný formulář,
takže může být klidně veřejně dostupná. Token se ukládá jen v prohlížeči.

Sociální sítě mají dva režimy (`social.mode` v `data/site.yml`):

- `review` — **poloautomat.** Systém texty připraví, odešle je až po odklepnutí.
- `auto` — odesílá rovnou.

## Vlastní články z QMA

`data/site.yml → import.qma` — systém si každý den vezme nové analýzy z QMA,
uloží je jako české články a přeloží je do angličtiny. U finančních textů
sám připojí upozornění, že jde o vzdělávací obsah, ne investiční doporučení.

Jsou to tvoje články, takže nejdou pod licenční poznámku jako cizí obsah,
ale pod tvoje jméno s odkazem na původní vydání na QMA.

Převzaté i importované články mají `rel="canonical"` na originál — tím říkáš
vyhledávačům, že prvenství patří QMA. Bez toho by si oba tvoje weby navzájem
kanibalizovaly pozice.

## Nabídka k převzetí

Aby tvoje články přebírala velká média, musíš jim to co nejvíc usnadnit —
tohle je přesně model, kterým se ProPublica dostala do velkých novin.

- pod každým vlastním článkem je blok **♻︎ Free to republish** s hotovým HTML
  včetně řádku o původu, odkazu zpět a licence
- stránka `/en/republish/` vysvětluje podmínky
- v článcích je strukturovaný popis `NewsArticle` a existuje `sitemap-news.xml`
  — bez toho tě Google News ani Apple News nezaindexují

Licenci a podmínky nastavíš v `data/site.yml → republish`.
Výchozí je CC BY-ND: smí se přebírat, ale ne přepisovat.

⚠️ Počítadlo v tom bloku (`px.gif`) na GitHub Pages neměří — statický hosting
nedá přístup k logům. Až budeš chtít vědět, kolik lidí článek přes cizí web
přečetlo, bude na to potřeba malá služba navíc.

## Ruční ovládání

```bash
pip install -r requirements.txt

python -m engine.collect      # posbírej zprávy z 50 zdrojů
python -m engine.memory       # zanes události do dlouhodobé paměti
python -m engine.analyst brief   # co se v běžících tématech změnilo
python -m engine.analyst resolve # vyhodnoť splatné předpovědi
python -m engine.analyst propose # navrhni nové předpovědi
python -m engine.syndicate    # převezmi celé články z povolených zdrojů
python -m engine.qma          # převezmi vlastní analýzy z QMA
python -m engine.trends       # najdi témata, po kterých je poptávka
python -m engine.daily        # co je téma článku dne a jaké má podklady
python -m engine.brief        # připrav zadání pro redakci
python -m engine.write        # napiš články (potřebuje API klíč)
python -m engine.inbox        # zpracuj, co dodala Claude úloha
python -m engine.release      # vydej delší článek ze zásoby
python -m engine.translate    # přelož do češtiny
python -m engine.build        # postav web + dohledej obrázky
python -m engine.social prepare  # připrav příspěvky do fronty
python -m engine.social send     # odešli, co je schválené
python -m engine.doctor       # zkontroluj, jestli je všechno v pořádku
```

Zkouška naprázdno bez API klíče a bez placení:

```bash
AI_MOCK=1 python -m engine.write
```

## Obrázky

Hledají se v tomhle pořadí a generativní AI mezi nimi schválně není:

1. `static/covers/<slug>.jpg` — obrázek, který jsi tam položil ty
2. vlastní knihovna už jednou stažených obrázků
3. **Openverse** — asi 800 milionů volně licencovaných fotografií
4. **Wikimedia Commons** — mimo jiné celé klasické malířství
5. typografická obálka — vždycky funguje

Přijímají se jen licence public domain, CC0, CC BY a CC BY-SA a autor
se vždy uvádí pod obrázkem.

## Sociální sítě

Publikuje se přes oficiální rozhraní platforem, nic se nemaskuje.

- **Bluesky a Telegram** systém zvládne sám (stačí přístupové údaje)
- **Facebook, Instagram, X, LinkedIn** dostaneš připravené v
  `data/social/k-vlozeni.md` a vložíš je ručně

Každá síť dostane vlastní podobu textu — stejný text všude je to,
co dosah opravdu sráží.

## Redakční pravidla

Celá redakční ústava je v [engine/prompts/FORMAT.md](engine/prompts/FORMAT.md).
Šest pravidel bez výjimky:

1. Nikdy nevysvětluj pointu.
2. Nikdy neoznač současnou událost za naplnění proroctví.
3. Nikdy nekaž.
4. Nikdy nepřepisuj cizí článek.
5. Nikdy nezamlčuj špatnou zprávu kvůli pozitivnímu ladění.
6. Web se nepředstavuje. Ukazuje.
