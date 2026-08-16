---
slug: why-ai-still-makes-things-up
title: "Proč si AI pořád vymýšlí — a jediný návyk, který to odhalí"
dek: "Chatboti nelžou tak, jak lžou lidé. Predikují pravděpodobný text, a vymyšlená citace soudního rozhodnutí je pro model stejně 'pravděpodobná' jako skutečná."
section: ai
type: analysis
depth: open
lang: cs
date: '2026-08-16'
status: draft
confidence: 82
load: 0
topics: []
automation_generated: true
edition_slot: 4
automation_role: edition
generator: claude-code
format: ""
event_id: ""
series: ""
image_query: computer screen glitching text
sources:
  - name: "Wikipedia — Mata v. Avianca, Inc."
    url: "https://en.wikipedia.org/wiki/Mata_v._Avianca,_Inc."
    published: ""
  - name: "Wikipedia — Hallucination (artificial intelligence)"
    url: "https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)"
    published: ""
  - name: "Wikipedia — Large language model"
    url: "https://en.wikipedia.org/wiki/Large_language_model"
    published: ""
  - name: "Lin, Hilton, Evans — TruthfulQA: Measuring How Models Mimic Human Falsehoods"
    url: "https://arxiv.org/abs/2109.07958"
    published: "2021-09-08"
impact:
  areas: [life, money]
  line: "Kdokoli používá chatbota k rešerši, psaní nebo právním či zdravotním dotazům, je vystaven tomuhle riziku: vymyšlené citace, data a výroky, které znějí stejně sebejistě jako ty pravdivé."
  todo: "Než se spolehnete na konkrétní jméno, číslo, datum nebo citaci od AI, ověřte si to nezávisle — model sám vám spolehlivě neřekne, které z jeho vlastních tvrzení jsou vymyšlená."
quiz:
  question: "Proč podle článku jazykové modely produkují sebejistá nepravdivá tvrzení místo toho, aby řekly 'nevím'?"
  options:
    - "Jsou záměrně naprogramované, aby klamaly uživatele"
    - "Predikují pravděpodobně znějící text a při trénování jen zřídka viděly odměněnou upřímnou nejistotu"
    - "Uprostřed odpovědi jim dojde výpočetní kapacita"
  answer: 1
  explanation: "Mechanismus je statistická predikce pravděpodobného textu, formovaná trénováním a zpětnou vazbou, která má tendenci upřednostňovat plynulé, sebejisté odpovědi před opatrnými nebo nejistými."
---

## BRIEFLY

**Co se stalo.** AI chatboti dál generují vymyšlená fakta, citace a výroky se stejnou plynulou sebejistotou jako ty správné — dobře zdokumentovaný jev, kterému výzkumníci říkají „halucinace".

**Co to znamená.** Nejde o chybu, kterou spraví aktualizace softwaru. Vyplývá to z toho, jak tyhle systémy fungují: predikují pravděpodobná další slova, ne že by ověřovaly tvrzení proti realitě.

**Rizika a dopady.** Kdokoli používá AI k rešerši, psaní, právním podáním nebo zdravotním dotazům, může dostat špatný fakt oblečený přesně jako ten správný — bez jakéhokoli vestavěného varování.

**Co se s tím dá dělat.** Ke každému konkrétnímu jménu, číslu, datu, citaci nebo odkazu od AI asistenta přistupujte jako ke stopě k ověření, ne jako k faktu k použití. Požádejte model, ať ukáže zdroje, a pak si ověřte, že ty zdroje existují.

**Na co se dívat dál.** Jestli techniky „ukotvení" — nucení modelu citovat ze skutečných dohledaných dokumentů místo z vlastní paměti — dál zmenšují mezeru, nebo jestli se problém ukáže jako těžší úplně zkonstruovat pryč.

## FACTS

V případu Mata v. Avianca podal newyorský právník Steven Schwartz podání, které jako oporu argumentace citovalo předchozí soudní rozhodnutí. Několik z nich neexistovalo. Požádal ChatGPT o podpůrné případy, nástroj vygeneroval citace, které vypadaly přesně jako skutečná judikatura, s celými jmény a čísly jednání, a on je podal bez kontroly. Federální soudce ho v roce 2023 potrestal sankcí. Stal se z toho jeden z prvních široce publikovaných, doložených případů toho, čemu výzkumníci říkají AI „halucinace" se skutečnými důsledky v reálném světě.

Halucinace v tomhle technickém smyslu znamená, že AI systém generuje obsah, který je plynulý, sebejistý a nepravdivý. Není to „lež" systému, protože lhaní vyžaduje znát pravdu a záměrně ji tajit. Jazykový model nemá žádný vnitřní kontrolor faktů běžící pod svými odpověďmi. Je to statistický systém trénovaný k predikci, jaké slovo pravděpodobně následuje, na základě všeho, co viděl předtím, včetně vlastních trénovacích dat.

Tenhle mechanismus vysvětluje, proč halucinace tak často vypadají jako skutečná fakta, ne jako nesmysly: model nehádá náhodně, produkuje statisticky nejpravděpodobněji znějící pokračování, a vymyšlená, ale dobře formulovaná citace je pro tenhle proces stejně „pravděpodobná" jako skutečná. Nic v základní architektuře nerozlišuje „tohle je pravda" od „tohle je typ věty, která se objevuje po tomhle typu otázky".

## EVIDENCE

Výzkumníci se napříč rozsáhlým souborem publikovaných prací shodují, že halucinace je strukturální vlastnost toho, jak velké jazykové modely generují text, ne příležitostná chyba specifická pro produkt jedné firmy. To je dobře doložené a v oboru se o tom vážně nepolemizuje.

Méně jasné je, o kolik danou míru snižuje konkrétní technika. Metody založené na vyhledávání — kdy je model nucen citovat z dokumentů dohledaných v okamžiku dotazu, místo aby se spoléhal čistě na to, co vstřebal při trénování — měřitelně snižují míru vymýšlení v benchmarkových testech. Problém neodstraňují úplně, protože model může skutečný dodaný dokument i tak nesprávně přečíst nebo nesprávně citovat.

Benchmark TruthfulQA z roku 2021, postavený přímo k prozkoumání tohoto jevu, zjistil, že modely dokážou produkovat sebejistě nesprávné odpovědi na otázky, kde se pravděpodobně znějící, ale nepravdivá odpověď běžně vyskytovala v textu, na kterém model pravděpodobně trénoval — napodobují rozšířené lidské mylné představy, místo aby je opravovaly. To je užší a konkrétnější zjištění než „AI je nespolehlivá" — ukazuje, že chyba kopíruje to, co je běžné v trénovacím textu, ne náhodnou chybu.

Co nemáme, je spolehlivý způsob, jak by model zevnitř poznal, které z jeho vlastních výstupů jsou halucinace. Sebejistota vyjádřená tónem odpovědi spolehlivě nekopíruje přesnost — model může znít stejně jistě, když se mýlí, jako když má pravdu.

## PERSPECTIVES

**Pohled technologického pokroku**: míra halucinací měřitelně klesla s přidáváním ukotvení ve vyhledávání, lepší kurací trénovacích dat a vrstvami kontroly faktů, a trendová čára ukazuje na další zlepšování. Tenhle pohled je dobře podložený srovnáním benchmarků v čase, ale má tendenci podceňovat, že „nižší míra" pořád znamená, že se chyby dějí, a uživatel nemá spolehlivý způsob, jak v danou chvíli poznat, která odpověď je ta špatná.

**Pohled strukturálního limitu**: protože je základní mechanismus predikcí dalšího slova, ne ověřeným vyhledáním faktů, může být určitá základní míra vymýšlení blízko nevyhnutelné bez zásadně odlišné architektury. Je to opatrnější, na výzkumu založená pozice, ale může podceňovat, jak užitečné se už silně ukotvené systémy citující zdroje staly pro užší úlohy.

**Pohled odpovědnosti uživatele**, běžný v tom, jak firmy problém veřejně rámují: nástroj je generátor návrhů a ověřování je práce uživatele. To platí, pokud jde jen o tohle, ale přesouvá to celou cenu za tenhle typ chyby na člověka, který je nejméně vybavený ji odhalit — na někoho, kdo se ptá právě proto, že odpověď ještě nezná.

## CONTEXT

Slovo „halucinace" je samo o sobě metafora vypůjčená z lidské psychologie, a je to nedokonalá metafora. Člověk, který halucinuje, má poruchu vnímání něčeho, co existuje, nebo neexistuje. Jazykový model žádné vnímání, které by mohlo selhat, nemá — má proces predikce textu fungující přesně tak, jak byl navržen, jen aplikovaný na případ, kdy je statisticky nejpravděpodobnější pokračování náhodou nepravdivé.

Na tom záleží, protože to mění, jak vůbec může „oprava" vypadat. Nejde poctivost jazykového modelu opravit záplatou tak, jako se opravuje bezpečnostní chyba, protože model poctivost nikdy nekontroloval. Co zatím výsledky skutečně zlepšilo, jsou obchvaty: vyžadovat citace ze skutečných, dohledatelných dokumentů; trénovat modely, aby v případech skutečné nejistoty častěji řekly „nevím"; a stavět samostatné ověřovací kroky mimo samotný model.

Případ právníka Stevena Schwartze, zdokumentovaný v samotném sankčním rozhodnutí soudu, je spíš užitečným mezníkem než výjimkou: byl široce publikovaný právě proto, že šel o raný, neobvykle čistý příklad stejného typu selhání, který výzkumníci už popisovali v benchmarcích jako TruthfulQA — plynulý, konkrétní, nepravdivý a neoznačený nástrojem, který ho vyprodukoval. Co ještě není jasné, je, jak rychle techniky ukotvení zmenší mezeru u otevřených, obecných otázek oproti úzkým, na dokument navázaným.

## DEEPER

Existuje specifický druh důvěry, který si plynulý jazyk vysluhuje téměř automaticky, bez ohledu na to, kdo nebo co ho vyprodukovalo. Lidé jsou stavění tak, že čtou sebejisté, dobře strukturované věty jako signál spolehlivého vědění — je to zkratka, která u ostatních lidí funguje docela dobře, protože plynule blafovat konkrétní fakt je pro nás těžší, než to vypadá, a časem se to sociálně odhalí.

Jazykový model tuhle zkratku ruší, aniž by to věděl. Dokáže vyprodukovat špatnou citaci případu se stejnou plynulostí, strukturou a sebejistým tónem jako správnou, protože plynulost je to, co byl skutečně trénovaný produkovat. Přesnost, když k ní dojde, je vedlejší produkt dobrých trénovacích dat a ukotvení — ne samostatná, kontrolovaná vlastnost věty.

Tahle mezera mezi „zní to správně" a „je to správně" není v AI nová. Je to stejná mezera, která dovolí sebejistému amatérovi přehlasovat v diskuzi váhavého experta, nebo která dělá dobře napsaný podvodný dopis přesvědčivější než neohrabaný pravdivý. Co je nové, je rozsah a rychlost: nástroj, který dokáže tenhle plynulý, sebejistý povrch vyprodukovat na požádání, o téměř jakémkoli tématu, během vteřin, zdarma.

Návyk, který to skutečně odhalí, není chytřejší AI model. Je to ten starý, nevzrušující: brát plynulost a přesnost jako dvě různé věci, které se většinu času náhodou pohybují spolu, a tu druhou si stejně ověřit.

## REFLECT

Když něco zní sebejistě a dobře uspořádaně, kolik z vaší důvěry v to pochází z obsahu a kolik z podání?

Kdyby vám nástroj dokázal přesně říct, jak moc si je jistý u každého konkrétního tvrzení, opravdu byste se zastavili u těch s nízkou jistotou — nebo by plynulá formulace stejně zvítězila?
