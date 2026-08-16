---
slug: why-ai-still-makes-things-up
title: "Proč si AI pořád něco vymýšlí — a jediný návyk, který to odhalí"
dek: 'Chatboti nelžou tak, jak lžou lidé. Předvídají pravděpodobný text, a sebejistě
  vymyšlená citace soudního rozhodnutí je pro model stejně „pravděpodobná" jako
  skutečná.'
section: ai
type: analysis
depth: open
lang: cs
date: '2026-08-16'
status: draft
automation_generated: true
edition_slot: 4
automation_role: edition
generator: claude-code
format: ''
event_id: ''
series: ''
image_query: computer screen glitching text
sources:
- name: Wikipedia — Mata v. Avianca, Inc.
  url: https://en.wikipedia.org/wiki/Mata_v._Avianca,_Inc.
  published: ''
- name: Wikipedia — Hallucination (artificial intelligence)
  url: https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)
  published: ''
- name: Wikipedia — Large language model
  url: https://en.wikipedia.org/wiki/Large_language_model
  published: ''
- name: 'Lin, Hilton, Evans — TruthfulQA: Measuring How Models Mimic Human Falsehoods'
  url: https://arxiv.org/abs/2109.07958
  published: '2021-09-08'
impact:
  areas:
  - life
  - money
  line: 'Anyone who uses a chatbot for research, writing or legal or medical questions
    is exposed to this: fabricated citations, dates, and quotes that read as confidently
    as true ones.'
  todo: Before you rely on any specific name, number, date or quote an AI gives you,
    search for it independently — the model itself cannot reliably tell you which
    of its own claims are real.
quiz:
  question: According to this article, why do language models produce confident false
    statements instead of saying 'I don't know'?
  options:
  - They are deliberately programmed to deceive users
  - They predict plausible-sounding text and rarely saw honest uncertainty rewarded
    in training
  - They run out of processing power partway through an answer
  answer: 1
  explanation: The mechanism is statistical prediction of likely text, shaped by training
    and feedback that tends to favor fluent, confident answers over hedged or uncertain
    ones.
---

## BRIEFLY

**Co se stalo.** AI chatboti dál generují vymyšlená fakta, citace a citáty se stejnou plynulou sebejistotou jako ty přesné — dobře zdokumentovaná chyba, které výzkumníci říkají „halucinace".

**Co to znamená.** Nejde o chybu, kterou spraví aktualizace softwaru. Vyplývá to z toho, jak tyhle systémy vůbec fungují: předpovídají pravděpodobná další slova, ne že by ověřovaly tvrzení proti realitě.

**Rizika a dopady.** Kdokoli, kdo používá AI pro rešerši, psaní, právní podání nebo zdravotní otázky, může dostat špatný fakt oblečený přesně jako ten správný — bez jakéhokoli vestavěného varování.

**Co se s tím dá dělat.** Ke každému konkrétnímu jménu, číslu, datu, citátu nebo citaci od AI asistenta přistupuj jako ke stopě k ověření, ne jako k hotovému faktu. Požádej model, ať ukáže zdroje, a pak ověř, že ty zdroje skutečně existují.

**Na co se dívat dál.** Jestli techniky „zakotvení" — kdy je model nucený citovat z reálných, dohledatelných dokumentů místo ze své paměti — dál zmenšují tenhle rozdíl, nebo se ukáže, že problém je těžší úplně technicky odstranit.

## FACTS

V případu Mata v. Avianca předložil newyorský advokát Steven Schwartz soudní podání, které citovalo dřívější rozhodnutí na podporu svého argumentu. Několik z těch rozhodnutí neexistovalo. Požádal ChatGPT o podpůrné případy, nástroj vygeneroval citace, které vypadaly přesně jako skutečná judikatura, se jmény i čísly jednacími, a on je podal bez kontroly. Federální soudce ho v roce 2023 potrestal sankcí. Stal se z toho jeden z prvních široce medializovaných, zdokumentovaných případů toho, čemu výzkumníci říkají AI „halucinace" se skutečnými důsledky.

Halucinace v tomhle technickém smyslu znamená, že AI systém generuje obsah, který je plynulý, sebejistý a nepravdivý. Není to systém, který by „lhal" — lhaní vyžaduje znát pravdu a vědomě ji skrývat. Jazykový model nemá žádný vnitřní fact-checker běžící pod svými odpověďmi. Je to statistický systém natrénovaný předvídat, jaké slovo pravděpodobně přijde další, na základě všeho, co už viděl, včetně vlastních trénovacích dat.

Tenhle mechanismus vysvětluje, proč halucinace tak často vypadají jako skutečná fakta, ne jako nesmysly: model nehádá náhodně, produkuje statisticky nejpravděpodobněji znějící pokračování, a vymyšlená, ale dobře zformulovaná citace je pro tenhle proces stejně „pravděpodobná" jako skutečná. Nic v základní architektuře nerozlišuje „tohle je pravda" od „tohle je typ věty, která se objevuje po tomhle typu otázky".

## EVIDENCE

Výzkumníci se napříč velkým množstvím publikovaných prací shodují, že halucinace je strukturální vlastnost toho, jak velké jazykové modely generují text, ne příležitostná chyba specifická pro produkt jedné firmy. To je dobře podložené a v oboru se to vážně nezpochybňuje.

Méně jasné je, o kolik danou halucinaci sníží konkrétní technika. Metody založené na vyhledávání — kdy je model nucený citovat z dokumentů dohledaných v okamžiku dotazu, místo aby se spoléhal čistě na to, co vstřebal během trénování — měřitelně snižují míru vymýšlení v benchmarkových testech. Problém neodstraní úplně, protože model si i tak může reálný dokument, který dostal, špatně přečíst nebo špatně citovat.

Benchmark TruthfulQA z roku 2021, postavený přesně na testování tohohle jevu, zjistil, že modely dokážou produkovat sebejistě špatné odpovědi u otázek, kde se v textu, na kterém se model pravděpodobně trénoval, běžně vyskytovala věrohodně znějící, ale nepravdivá odpověď — napodobují rozšířené lidské mylné představy místo toho, aby je opravovaly. To je užší a konkrétnější zjištění než „AI je nespolehlivá" — ukazuje, že chyba sleduje to, co je běžné v trénovacím textu, ne náhodnou chybu.

Co nemáme, je spolehlivý způsob, jak by model zevnitř poznal, které z jeho vlastních výstupů jsou halucinace. Sebejistota vyjádřená tónem odpovědi spolehlivě nekopíruje přesnost — model může znít úplně stejně jistě, když se mýlí, jako když má pravdu.

## PERSPECTIVES

**Pohled technologického pokroku**: míra halucinací měřitelně klesla s tím, jak přibylo zakotvení ve vyhledávání, lepší kurátorství trénovacích dat a vrstvy pro kontrolu faktů, a trend ukazuje na další zlepšování. Tenhle pohled dobře podpírají srovnání benchmarků v čase, ale má sklon podceňovat, že „nižší míra" pořád znamená, že se chyby dějí — a uživatel nemá v tu chvíli spolehlivý způsob, jak poznat, která odpověď je ta špatná.

**Pohled strukturálního limitu**: protože podkladový mechanismus je předpovídání dalšího slova, ne ověřené vyhledávání faktů, může být určitá základní míra vymýšlení bez zásadně jiné architektury téměř nevyhnutelná. Je to opatrnější, na výzkumu založená pozice, ale může podceňovat, jak užitečné se silně zakotvené systémy citující zdroje už staly pro užší úkoly.

**Pohled odpovědnosti uživatele**, běžný v tom, jak firmy problém veřejně rámují: nástroj je generátor konceptů a ověření je práce uživatele. To je pravda, pokud jde jen o tohle, ale přenáší celou cenu za tuhle chybu na člověka, který je na její odhalení nejméně vybavený — na někoho, kdo se ptá právě proto, že odpověď ještě nezná.

## CONTEXT

Slovo „halucinace" je samo o sobě metafora vypůjčená z lidské psychologie a je to metafora nedokonalá. Člověk, který halucinuje, má poruchu vnímání něčeho, co existuje, nebo neexistuje. Jazykový model nemá žádné vnímání, které by mohlo selhat — má proces předpovídání textu fungující přesně podle návrhu, jen aplikovaný na případ, kdy statisticky nejpravděpodobnější pokračování náhodou není pravdivé.

Na tom záleží, protože to mění, jak vůbec může vypadat „oprava". Poctivost jazykového modelu nejde záplatovat stejně jako bezpečnostní chybu, protože model nikdy poctivost neověřoval. Co skutečně dosavadní výsledky zlepšilo, jsou obchvaty: požadavek na citace ze skutečných, dohledatelných dokumentů; trénování modelů, aby v případech skutečné nejistoty častěji říkaly „nevím"; a budování samostatných ověřovacích kroků mimo samotný model.

Případ advokáta Stevena Schwartze, zdokumentovaný v soudním sankčním usnesení, je spíš orientační bod než výjimka: byl v době, kdy se stal, široce medializovaný přesně proto, že šlo o raný, neobvykle čistý příklad stejné chyby, kterou výzkumníci už předtím popisovali v benchmarcích jako TruthfulQA — plynulá, konkrétní, nepravdivá a neoznačená nástrojem, který ji vyprodukoval. Zatím není jasné, jak rychle techniky zakotvení zmenší tenhle rozdíl u otevřených, obecných otázek, na rozdíl od úzkých otázek vázaných na konkrétní dokument.

## DEEPER

Existuje specifický druh důvěry, kterou si plynulý jazyk vysloužil takřka automaticky, bez ohledu na to, kdo nebo co ho vyprodukovalo. Lidé jsou nastavení číst sebejisté, dobře strukturované věty jako signál spolehlivého vědění — je to zkratka, která u ostatních lidí docela dobře funguje, protože plynule blafovat o konkrétním faktu je pro nás těžší, než to vypadá, a časem se to sociálně odhalí.

Jazykový model tuhle zkratku rozbíjí, aniž by věděl, že to dělá. Dokáže vyprodukovat špatnou citaci případu se stejnou plynulostí, strukturou a sebejistým tónem jako správnou, protože plynulost je přesně to, na co byl natrénovaný. Přesnost, když se objeví, je vedlejší produkt dobrých trénovacích dat a zakotvení — ne samostatná, kontrolovaná vlastnost té věty.

Tahle propast mezi „zní to správně" a „je to správně" není u AI nová. Je to stejná propast, díky které sebejistý amatér přehluší v diskusi váhajícího experta, nebo díky které je dobře napsaný podvodný dopis přesvědčivější než neobratný pravdivý. Nové je měřítko a rychlost: nástroj, který dokáže tenhle plynulý, sebejistý povrch vyprodukovat na požádání, o téměř jakémkoli tématu, během vteřin, zadarmo.

Návyk, který to skutečně odhalí, není chytřejší AI model. Je to ten starý, nevzrušující: brát plynulost a přesnost jako dvě různé věci, které se většinou náhodou pohybují spolu — a tu druhou přesto kontrolovat.

## REFLECT

Když něco zní sebejistě a dobře uspořádaně, kolik z tvé důvěry v to pochází z obsahu a kolik z podání?

Kdyby ti nějaký nástroj dokázal přesně říct, jak moc si je jistý u každého konkrétního tvrzení, opravdu by ses zastavil a ověřil ta málo jistá — nebo by plynulá formulace stejně vyhrála?
