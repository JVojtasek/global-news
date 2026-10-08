---
slug: an-e-ink-screen-spends-power-to-change-not-to-remember
title: Displej z elektronického papíru platí energií za změnu, ne za paměť
dek: Nabité částice pigmentu zůstanou po překreslení na svém místě. Proto vydrží elektronický
  papír dlouho ukazovat stejný obraz a proto se také nápadně pomaleji obnovuje.
section: tech
type: feature
depth: open
lang: cs
date: '2026-10-04'
status: reserve
confidence: 94
load: 0
topics: []
automation_generated: true
edition_slot: 7
automation_role: edition
generator: chatgpt-work
format: wider-lens
event_id: evergreen-electrophoretic-display-bistability
series: ''
image_query: macro close-up electronic paper e-reader black white pixels
sources:
- name: E Ink — How electronic ink works
  url: https://www.eink.com/tech/detail/How_it_works
  published: ''
- name: Microchip Developer Help — ePaper Display Fundamentals
  url: https://developerhelp.microchip.com/xwiki/bin/view/software-tools/mgs/dev-kits/epd-ug/fundamentals/
  published: ''
- name: Journal of Printing Science and Technology — Electrophoretic Electronic Paper
    Displays
  url: https://www.jstage.jst.go.jp/article/nig/44/5/44_5_257/_article/-char/en
  published: '2007-01-01'
- name: IEEE Spectrum — How E Ink Developed Full-Color e-Paper
  url: https://spectrum.ieee.org/how-e-ink-developed-full-color-epaper
  published: '2022-01-25'
qma_path: ''
tickers: []
quiz:
  question: Proč může na běžném elektroforetickém displeji z elektronického papíru
    zůstat text vidět i po odpojení napájení?
  options:
  - Displej ze zbylého náboje napájí skryté podsvícení.
  - Displej pro každou stránku vytiskne jednorázovou fólii.
  - Částice pigmentu zůstávají ve svých posledních stabilních polohách, dokud je
    nepřesune další elektrické pole.
  answer: 2
  explanation: 'Elektroforetický papír je bistabilní: při překreslení elektrické
    pole přeskupí nabité částice pigmentu a výsledný obraz pak může vydržet i bez
    trvalého napájení displeje.'
---

## BRIEFLY

**Co se stalo.** Elektroforetický elektronický papír skládá obraz tak, že posouvá nabité částice pigmentu kapalinou uvnitř drobných buněk nebo kapslí.

**Co to znamená.** Jakmile částice dorazí do stabilní polohy, displej může stránku dál ukazovat, aniž by musel každý pixel trvale napájet. Energie se spotřebuje hlavně při překreslení, ne na udržení statického obrazu.

**Rizika a dopady.** Stejný mechanismus přináší kompromisy. Obnovování je pomalejší než u displejů LCD nebo OLED, předchozí obrazy mohou zanechat slabé stopy a barvy, animace i provoz v zimě vyžadují složitější řízení.

**Co se s tím dá dělat.** Elektronický papír volte pro informace, které se mění jen občas a mají zůstat dlouho čitelné. Běžný displej volte tam, kde víc záleží na plynulém pohybu a častých změnách.

**Na co se dívat dál.** Údaje výrobců by měly oddělovat spotřebu displeje od zbytku zařízení. Bezdrátové moduly, procesory, přední osvětlení i dotyková vrstva berou energii, i když elektronický papír zrovna jen drží stránku.

## FACTS

Většina známých čteček s elektronickým papírem používá elektroforetický displej. V běžném černobílém provedení obsahují mikroskopické buňky tmavé a světlé částice pigmentu s opačným elektrickým nábojem, rozptýlené v kapalině. Elektrody vytvářejí elektrické pole, které jednu skupinu částic přitáhne k povrchu, na který se díváme, a druhou odtlačí.

Když nahoru vystoupají světlé částice, místo vypadá světle. Když tmavé, vypadá tmavě. Řadič z těchto míst skládá písmena a obrázky. Firma E Ink popisuje displej jako reflexní, protože využívá okolní světlo, místo aby každý pixel světlo vyzařoval. Zařízení může mít přední osvětlení, to je ale od základního mechanismu tvorby obrazu oddělené.

Displej je také bistabilní. Částice mohou zůstat tam, kam je překreslení posunulo, i když elektrické pole zmizí, takže statický obraz nepotřebuje trvalé napájení displeje. Samotné překreslení energii potřebuje. Časový a napěťový průběh, často nazývaný průběh buzení (waveform), závisí na druhu přechodu a typu displeje.

## EVIDENCE

Technické materiály firmy E Ink uvádějí, že oblasti, které se nemění, není třeba překreslovat, a popisují režimy obnovování pro různé nároky na rychlost a kvalitu obrazu. Firma také tvrdí, že k udržení obrazu není potřeba žádná energie. Jako výrobce je autoritativním zdrojem ke své vlastní technologii, ale má zjevný zájem zdůrazňovat její přednosti.

Nezávislá vývojářská dokumentace firmy Microchip vysvětluje stejný mechanismus: opačně nabité částice se pohybují v elektrickém poli, po překreslení zůstanou na místě a hodí se pro rozhraní, která se mění jen zřídka. Uvádí také omezení, se kterými musí inženýři počítat: pomalé obnovování, omezené barvy nebo odstíny šedi a rozhraní, která by neměla stát na plynulé animaci.

Technický přehled z roku 2007 v časopise Journal of Printing Science and Technology dokumentuje první komerční rozšíření elektroforetického papíru a jako hlavní vývojové výzvy označuje dobu odezvy a barvy. Technická historie v IEEE Spectrum, kterou napsali technologičtí ředitelé firmy E Ink a která je tak také označená, podrobněji popisuje napěťové průběhy, reflexní barevné filtry a buňky s více pigmenty.

Důkazy podporují přesné tvrzení: vrstva displeje dokáže udržet statický obraz s malou nebo žádnou energií na jeho držení. Nepodporují ale širší slogan, že celá čtečka nespotřebuje nic, dokud je stránka vidět.

## PERSPECTIVES

### Pohled čtenáře

Stránka působí klidně, protože ji nepřetržitě nepřekresluje vyzařované světlo. V jasném prostředí může víc okolního světla čtení dokonce zlepšit. Ve tmě pomůže přední osvětlení, jenže pak část proslulé úspornosti padne na svícení.

### Pohled vývojáře vestavěných systémů

Elektronický papír je lákavý tam, kde čidlo, štítek nebo cedule mezi změnami minuty či dny spí. Displej udrží poslední stav, zatímco procesor odpočívá. Pro pohybující se kurzor, video nebo rychlou nabídku se ale tentýž displej hodí špatně.

### Pohled marketéra

„Týdny na jedno nabití“ se dobře pamatují. Zároveň ale mohou rozmazat hranici mezi panelem a celým výrobkem. Bezdrátové moduly stahující knihy, procesory indexující stránky, dotykové řadiče i osvětlení mají vlastní spotřebu.

### Pohled vědce zabývajícího se displeji

Černobílá buňka je jen začátek. Barva vyžaduje filtry nebo víc druhů pigmentu a každá volba vyměňuje jas, rozlišení, sytost a rychlost překreslení. Úkolem není jen přidat barvu. Úkolem je řídit několik druhů nabitých částic a neztratit přitom přednosti reflexního papíru.

## CONTEXT

Běžné displeje a elektronický papír řeší jiné úlohy. LCD reguluje procházející světlo pomocí podsvícení a vrstvy tekutých krystalů. Pixel OLED světlo sám vyzařuje. Tyto konstrukce se mohou měnit rychle, protože jejich obraz je aktivně buzen. Elektroforetický papír fyzicky přeskupuje pigment, což trvá déle, ale výsledek vydrží.

Překreslení připomíná spíš stěhování nábytku než rozsvícení lampy. Elektrické pole tlačí a táhne částice do nového uspořádání. Řadič může displej nechat probliknout mezistavy, aby smazal zbytkový náboj a omezil takzvané duchy, tedy stopy předchozího obrazu. Částečné překreslení bývá rychlejší, ale opakované zkratky mohou nechat zbytky, které nakonec vyžadují úplnější obnovení.

Na teplotě záleží, protože se částice pohybují kapalinou. Řadiče a průběhy buzení to vyrovnávají, přesto může chlad odezvu zpomalit. Barva přidává další vrstvu obtíží. Systémy s filtry dělí odražené světlo mezi barevné subpixely, což snižuje jas nebo skutečné rozlišení. Systémy s více pigmenty musí částice třídit podle různých nábojů, velikostí a pohybu.

Tato omezení vysvětlují, kde se elektronickému papíru daří nejlépe: v knihách, cenovkách v regálech, jmenovkách, jízdních řádech a stavových panelech. Jejich obsah se mění, ale ne šedesátkrát za sekundu. Stránka může zůstat deset minut, cenovka několik dní. Trpělivost displeje se stává výhodou.

Soulad média a sdělení je důležitější než novota. Správná otázka nezní, jestli elektronický papír dokáže napodobit každou úlohu displeje telefonu. Zní, jestli informaci prospívá stálost, čitelnost na denním světle a řídké změny.

## DEEPER

O digitální technice se často mluví jako o neklidné: všechno se obnovuje, dotazuje a žádá si pozornost. Elektronický papír nabízí jinou představu. Informace může být elektronická, aniž by byla v pohybu. Displej odvede energickou práci ve chvíli změny a pak výsledek nechá být.

Na tomhle časovém vzorci záleží. Technologii nelze posuzovat jen podle špičkové rychlosti, ale také podle rytmu práce, kterou má dělat. Displej, který je na video k ničemu, může být skvělý pro ceduli na baterie. Označit jeden displej za „lepší“, aniž bychom řekli, jak často se má měnit, je jako srovnávat nástěnku s kinoplátnem podle počtu snímků za sekundu.

Bistabilita také zviditelňuje stálost. Běžný displej zhasne, když zmizí napájení, které ho drží. Elektroforetická stránka může zůstat a ukazovat poslední zprávu, i když se procesor zastavil. To může být užitečné, ale vzniká tím drobné úskalí výkladu: vidět neznamená aktuální. Zastaralý čas odjezdu vlaku nebo údaj z čidla může vypadat úplně živě.

Praktická otázka je proto dvojí. Kolik energie stojí informaci ukázat a jak systém dá najevo, že je informace čerstvá? První problém řeší elektronický papír elegantně. Druhý musí konstruktéři teprve vyřešit, zvlášť když zamrzlý obraz může působit stejně důvěryhodně jako právě obnovený.

## PRACTICAL IMPACT

Když srovnáváte zařízení, zjistěte, jak často se displej mění, jestli má přední osvětlení a kolik spotřebuje procesor a bezdrátové připojení. U stavového displeje hledejte viditelný časový údaj nebo ukazatel čerstvosti. Obraz může výpadek napájení přežít. Informace pod ním nemusí.

## READER OUTCOME

Měli byste umět vysvětlit, jak nabité částice vytvářejí a udržují obraz na elektronickém papíru, proč to u statického obsahu šetří energii a proč rychlost obnovování a čerstvost informace zůstávají dvěma samostatnými omezeními.

## REFLECT

Které informace ve vašem dni se opravdu potřebují hýbat a které by byly užitečnější, kdyby prostě zůstaly čitelné a nežádaly si pozornost?

Když displej dokáže přežít systém, který za ním stojí, co by mělo starý obraz prozradit, že je starý?

Změnil by pomalejší displej jen výdrž baterie zařízení, nebo možná i tempo, v jakém čekáte, že informace přicházejí a mizí?
