# My Paper — veřejné noviny a výchozí SEO stav

Zjištěno 29. 10. 2026 přímo v Google Search Console služby
`https://mypaper.news/`. Report indexování uvádí poslední aktualizaci
23. 10. 2026. Jde o výchozí stav, nikoli o výsledek dnešních změn.

## Zachovaný produkt

My Paper zůstávají obecnými novinami pro širokou veřejnost. Veřejné
články, ranní briefing, sobotní vydání, kvízy a čtenářská personalizace
zůstávají veřejné. Dosavadní členství zůstává vypnuté; žádný obsah se
nepřevádí do placeného přístupu.

Firemní AI radar je samostatná volitelná nabídka pod položkou Pro firmy.
Upozornění na titulní straně je až pod veřejnými zprávami, nikoli místo
jejich úvodu. Ukázka je otevřená a případný placený pilot ještě nezačal.

## Ověřená čísla z reportu Google

| Stav | Stránky |
|---|---:|
| Indexováno | 160 |
| Procházeno, momentálně neindexováno | 426 |
| Alternativní stránka se správnou kanonickou značkou | 31 |
| Vyloučeno značkou noindex | 9 |
| Stránka s přesměrováním | 1 |

Poslední tři řádky nejsou automaticky chyby: u převzatého obsahu,
osobní stránky nebo přesměrování mohou být záměrné. Z hlášení
„procházeno, momentálně neindexováno“ nelze vyvozovat penalizaci ani
konkrétní příčinu. Není to totéž jako zákaz procházení.

Ve zobrazeném vzorku deseti URL z této skupiny byly například:

- `/en/country/bg/`
- `/en/problems/ageing/`
- `/en/questions/why-we-procrastinate-even-when-we-know-better/`
- `/en/relationships/strength-of-weak-ties/`
- `/en/culture/library-ebook-dormant-laws/`
- `/en/travel/airline-fuel-surcharge-yq/`
- `/en/meaning/public-disgrace-jason-arday/`

Vzorek obsahuje více typů stránek. Není podklad pro plošné odstranění
kanonických značek nebo noindex, ani pro tvrzení, že problém způsobují
výhradně převzaté články.

## Co se dnes skutečně udělalo

- Google ověřil vlastnictví přes skutečnou HTML metaznačku.
- Mapa `https://mypaper.news/sitemap.xml` byla odeslána a Google ji
  označil jako úspěšnou. Přijetí mapy negarantuje zařazení jejích URL.
- Čtyři nové stránky radaru a ukázky mají HTTP 200, vlastní popisy,
  kanonické URL, jazykové varianty a jsou v mapě veřejných stránek.
- Cloudflare obsahoval již založený web `mypaper.news` s nulou
  hlášených návštěv za posledních 24 hodin. Nastavení bylo přepnuto na
  ruční vložení skutečného měřicího kódu. Sběr se potvrzuje až na
  nasazeném webu a v samostatném přehledu My Paper.

Číslo 41,08 tisíce požadavků z domovské stránky účtu Cloudflare je za
celý účet a není počtem čtenářů My Paper. Zkušební návštěvy při kontrole
instalace rovněž nejsou důkazem organického růstu.

## Další práce pro veřejné noviny

1. Prověřit reprezentativní původní články v Kontrole URL: vrácený
   stav, obsah, zvolenou kanonickou adresu a interní odkazy. Až podle
   výsledků rozhodovat o opravách.
2. Posílit tematické rozcestníky a odkazy mezi souvisejícími texty tam,
   kde mají čtenářský smysl. Nepřidávat další tenké stránky jen kvůli SEO.
3. Opravit jazykovou konzistenci českého briefingu; převzaté anglické
   úryvky nejsou hotovým českým vysvětlením.
4. Připojit skutečnou e-mailovou službu a otestovat potvrzení adresy,
   doručení, volbu četnosti a odhlášení. Zájem o firemní pilot není
   souhlas s veřejným newsletterem.
5. Porovnávat vývoj v Google a samostatném Cloudflare přehledu po
   týdnech. Nečekat okamžitý růst po technickém zapojení.

Tento seznam je návrh následující práce, nikoli tvrzení, že byly všechny
body provedené. Nezapíná placené API, reklamní síť ani účty čtenářů.
