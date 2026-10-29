---
slug: a-password-manager-is-not-the-whole-risk
title: "Správce hesel je jediný bod selhání. To ale není celé riziko"
dek: "Trezor soustřeďuje tajemství na jedno místo. Poctivé srovnání ale nevede s dokonalou bezpečností, nýbrž s opakovaně používanými hesly, ztracenými obnovovacími kódy a obyčejnou lidskou pamětí."
section: tech
type: analysis
depth: open
lang: cs
date: '2026-08-25'
status: published
confidence: 89
load: 0
topics: []
automation_generated: true
edition_slot: 5
automation_role: edition
generator: chatgpt-work
format: ''
event_id: nist-800-63b-password-manager-household-risk
series: ''
image_query: conceptual encrypted vault with separate recovery key and household devices
  no logos
sources:
- name: NIST Special Publication 800-63B
  url: https://pages.nist.gov/800-63-4/sp800-63b.html
  published: '2025-07-31'
- name: USENIX Security 2018 — Better Managed than Memorized?
  url: https://www.usenix.org/conference/usenixsecurity18/presentation/lyastani
  published: '2018-08-15'
- name: 'USENIX Security 2022 — Password Managers: Attacks and Defenses'
  url: https://www.usenix.org/system/files/sec22-mayer.pdf
  published: 2022-08
- name: ETH Zurich — Password managers less secure than promised
  url: https://ethz.ch/en/news-and-events/eth-news/news/2026/02/password-managers-less-secure-than-promised.html
  published: '2026-02-16'
qma_path: ''
tickers: []
quiz:
  question: "Který problém hlavně řeší uložení obnovovacích kódů mimo trezor s hesly?"
  options:
  - "Opakované používání stejného hesla"
  - "Zablokování přístupu do trezoru"
  - "Malware na odemčeném zařízení"
  answer: 1
  explanation: "Obnovovací cesta mimo trezor zlepšuje dostupnost, když se k trezoru nebo k druhému faktoru nejde dostat. Kompromitované zařízení tím ale bezpečné nebude."
---

## BRIEFLY

**Co se stalo.** Správci hesel se doporučují čím dál častěji, protože pro každý účet umějí vytvořit a uložit jiné přihlašovací údaje. Novější výzkum přitom dál odhaluje slabiny v tom, jak se napojují na prohlížeče a aplikace.

**Co to znamená.** Trezor soustřeďuje riziko na jedno místo. Jenže totéž dělá i jedno heslo použité pro e-mail, nákupy i finanční účty. Užitečná otázka zní, které způsoby selhání můžete omezit a na které se musíte připravit, abyste je přežili.

**Rizika a dopad.** Ukradené hlavní heslo, kompromitované zařízení nebo neodhlášená relace mohou odhalit mnoho účtů. Ztracené zařízení nebo zapomenutá cesta k obnově mohou majitele zase zamknout venku.

**Co se dá dělat.** Chraňte trezor jedinečnou heslovou frází a silným druhým faktorem, údaje k obnově uložte zabezpečené zvlášť a jako první převeďte účty, na kterých nejvíc záleží.

**Na co si dát pozor.** Ověřte si, jestli váš správce hesel srozumitelně popisuje svou bezpečnostní architekturu, nezávislé audity, postup obnovy, formát exportu a to, jak reaguje na zveřejněné chyby.

## FACTS

Správce hesel dělá něco, v čem lidská paměť při opakování selhává: pro každou službu vytvoří a vybaví si samostatné, nepředvídatelné přihlašovací údaje. Na tom záleží, protože opakované používání hesla promění jeden únik v několik. Když diskusní fórum přijde o heslo, které používáte i jinde, útočník může stejnou dvojici e-mailu a hesla vyzkoušet na webmailu, v e-shopech a dalších službách. Únik se týkal prvního účtu, ostatní může otevřít automat.

Výzkum představený na konferenci USENIX v roce 2018 zjistil, že používání správce hesel souvisí se silnějšími hesly a s menším opakováním, i když chování záviselo na tom, jak lidé nástroj používali. To nedokazuje, že je bezpečný každý správce nebo každý uživatel. Dokazuje to, že záleží na realistické alternativě. „Zapamatuju si čtyřicet silných, navzájem nesouvisejících hesel“ je obvykle přání, ne bezpečnostní architektura.

Aktuální doporučení NIST k digitální identitě berou hesla jen jako jeden z druhů autentizátorů a výslovně uvádějí, že hesla nejsou odolná proti phishingu. Na vyšších úrovních zabezpečení vyžadují nebo doporučují silnější kombinace, včetně vícefaktorového ověření a ověření odolného proti phishingu. Správce hesel může vrstvu hesel vylepšit. Sám od sebe z hesla nic odolného proti phishingu neudělá.

## EVIDENCE

Nejsilnější argument pro správce hesel je proto srovnávací. Jedinečné uložené přihlašovací údaje omezují dosah úniku z jedné služby. Dlouhá, jedinečná hlavní heslová fráze snižuje riziko uhodnutí. Druhý faktor znamená, že ani znalost této fráze nemusí stačit k otevření trezoru z nového zařízení. Přístupové klíče mohou při dobrém provedení snížit riziko podvodných přihlašovacích stránek, protože jsou kryptograficky svázané s legitimní službou.

Zátěžový test je nepříjemný, ale nutný. Bezpečnostní výzkumníci ukázali, že rozšíření prohlížečů a systémy automatického vyplňování žijí v nepřátelském prostředí: stránky, rámce, skripty, schránky i výzvy v uživatelském rozhraní tu soupeří o pozornost a o přístup. Analýza z konference USENIX v roce 2022 zdokumentovala celé třídy útoků a nejednotnou ochranu u různých správců. Zpráva ETH Zurich o novějším výzkumu z roku 2026 rovněž zdůraznila, že slibovaná ochrana ne vždy přežije skutečné chování integrací.

To neznamená, že šifrované trezory nemají smysl. Znamená to, že šifrování uložených dat odpovídá jen na jednu otázku: co se stane, když někdo získá zamčenou databázi? Neodpovídá na to, co se stane, když malware sleduje odemčený počítač, když škodlivá stránka obelstí automatické vyplňování nebo když uživatel schválí špatnou žádost. Ocelový sejf působí impozantně. Méně platný je, když už v místnosti sedí zloděj.

## PERSPECTIVES

Skeptická fráze „jediný bod selhání“ obsahuje skutečný postřeh. Jedno hlavní heslo a jeden trezor mohou přístup soustředit na jedno místo. Únik u poskytovatele, chyba v implementaci nebo převzetí účtu mohou mít neobvykle velké následky. Nikomu by se nemělo tvrdit, že nějaký produkt ruší potřebu úsudku.

Ta fráze ale také umí zakrýt výchozí stav. Jedno zapamatovatelné heslo používané všude je samo o sobě jediný bod selhání, jen bez přehledu, generátoru, upozornění na úniky a promyšleného plánu obnovy. Desítky hesel v nahodilých poznámkách vytvářejí jiný druh soustředění rizika. Rozhodnutí je málokdy mezi trezorem a dokonalostí. Je mezi trezorem a systémem, který unavená domácnost opravdu udrží.

Záleží i na volbě produktu. Správci synchronizovaní přes cloud nabízejí pohodlí a obnovu, zatímco čistě lokální trezory mohou omezit část vzdáleného ohrožení, ale přenášejí víc odpovědnosti na zálohy. Obnova účtu, která je snadná pro majitele, může lákat i útočníka. Řešení, u kterého poskytovatel trezor obnovit nedokáže, chrání důvěrnost, ale zapomenutá hlavní heslová fráze pak znamená definitivní konec. Pohodlí, utajení a možnost obnovy táhnou každé jiným směrem.

## CONTEXT

Ověřování totožnosti má dva samostatné cíle, které se často pletou dohromady. Důvěrnost se ptá, jestli si tajemství může přečíst někdo nepovolaný. Dostupnost se ptá, jestli se oprávněný majitel dostane dovnitř i poté, co ztratí telefon, selže profil prohlížeče nebo vypoví paměť. Zlepšení jednoho může oslabit druhé.

Proto obnovovací kódy nepatří jen do trezoru, který mají obnovovat. Papírová kopie na fyzicky chráněném místě nebo jiná pečlivě zabezpečená offline metoda může poskytnout nezávislou cestu. Šifrovaný export může pomoct s přechodem, když poskytovatel skončí nebo databáze přestane být dostupná, ale sám se tím stává citlivým aktivem. Záloha, ze které nikdo nikdy nic neobnovil, je jen optimistický soubor.

Domácnosti přidávají ještě jeden problém: nezpůsobilost. Když jeden člověk spravuje všechny platby, daňový portál i smlouvy na energie, dokonalé utajení se může během nemoci změnit v praktickou krizi. To neospravedlňuje ledabylé sdílení všech hesel. Volá to po promyšleném plánu nouzového přístupu, který určí, kdo smí přístup získat, za jakých podmínek a kde jsou uložené pokyny.

## DEEPER

Rozumný přechod se vejde do čtyř kroků.

Zaprvé zabezpečte e-mailový účet, přes který se obnovují ostatní účty. Dejte mu jedinečné přihlašovací údaje a nejsilnější vhodný druhý faktor, který je k dispozici. Obnovovací kódy uložte mimo zařízení, které používáte každý den.

Zadruhé vytvořte pro trezor jedinečnou heslovou frázi, kterou nepoužíváte nikde jinde. Délka a zapamatovatelnost znamenají víc než ozdobné záměny znaků. Jedinou kopii hlavního hesla neukládejte do nezamčené poznámky vedle zařízení.

Zatřetí převeďte účty s největšími následky: správu financí, státní služby, cloudová úložiště, pracovní systémy a nákupní účty s uloženými platebními údaji. Opakovaně používaná hesla měňte, jak na ně narazíte. Za přesun všeho během jednoho vyčerpávajícího večera žádná cena není.

Začtvrté vyzkoušejte selhání. Přihlásíte se na náhradním nebo novém zařízení? Dostanete se k materiálům pro obnovu, aniž byste otevřeli trezor? Dokážete data exportovat ve zdokumentovaném formátu a ten export ochránit? Ví jeden důvěryhodný člověk, jak najít nouzové pokyny, aniž by měl běžný přístup?

Starejte se také o samotné zařízení: aktualizujte operační systém a prohlížeč, odstraňte rozšíření, která nepotřebujete, zamykejte obrazovku a nečekané výzvy k přihlášení berte jako podezřelé. Žádný trezor neochrání tajemství, která se kopírují ze zařízení, jež už ovládá někdo jiný.

## REFLECT

Dobré zabezpečení není talisman. Je to soubor selhání, která se podařilo zmenšit a zviditelnit a z nichž se dá snáz zotavit. Správce hesel může jeden nebezpečný lidský zvyk – opakování hesel – nahradit systémem, který má vlastní ostré hrany. Dospělá otázka nezní, jestli je trezor dokonale bezpečný. Nic připojeného není. Zní, jestli vaše uspořádání dokáže průnik ohraničit, přežije zablokování a funguje i v obyčejné úterý, kdy dochází trpělivost i paměť.
