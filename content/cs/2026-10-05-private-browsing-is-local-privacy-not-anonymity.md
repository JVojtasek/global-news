---
slug: private-browsing-is-local-privacy-not-anonymity
title: "Soukromé prohlížení chrání soukromí v zařízení, ne anonymitu"
dek: "Anonymní a soukromá okna mají hlavně omezit, co po relaci zůstane v prohlížeči. Provoz, účet ani uživatele neviditelnými neudělají."
section: tech
type: analysis
depth: open
lang: cs
date: '2026-10-05'
status: published
confidence: 95
load: 0
topics: []
automation_generated: true
edition_slot: 2
automation_role: edition
generator: chatgpt-work
format: wider-lens
event_id: ''
series: ''
image_query: ''
impact:
  areas: [safety, life]
  line: "Anonymní okno skryje relaci před dalším člověkem u stejného prohlížeče, ne před weby, přihlášenými účty, zaměstnavatelem, školou nebo poskytovatelem internetu. Stažené soubory a záložky zůstávají."
  todo: "Než se na anonymní režim spolehnete, řekněte si, před kým chcete soukromí, a přečtěte si v nápovědě svého prohlížeče, co anonymní okno uchovává."
sources:
- name: Google Chrome Help — Browse in Incognito mode
  url: https://support.google.com/chrome/answer/95464/browse-in-private-computer?hl=en-GB
- name: Mozilla Support — Private Browsing
  url: https://support.mozilla.org/en-US/kb/private-browsing-use-firefox-without-history
- name: Microsoft Support — Browse InPrivate in Microsoft Edge
  url: https://support.microsoft.com/en-us/edge/browse-inprivate-in-microsoft-edge
- name: Apple Support — Browse privately in Safari on Mac
  url: https://support.apple.com/en-ph/guide/safari/ibrw1069/mac
- name: Abu-Salma and Livshits — Evaluating the End-User Experience of Private Browsing
    Mode
  url: https://arxiv.org/html/1811.08460v2
  published: '2019-06-03'
qma_path: ''
tickers: []
quiz:
  question: "Co obvykle zůstane v zařízení i po skončení soukromé relace?"
  options:
  - Soubor stažený během relace
  - Běžný záznam relace v historii prohlížeče
  - Cookies relace, které prohlížeč slibuje zahodit
  answer: 0
  explanation: "Chrome, Firefox, Edge i Safari upozorňují, že stažené soubory zůstávají. Soukromý režim po skončení relace hlavně maže nebo vůbec neukládá data, která spravuje prohlížeč, například historii a dočasné cookies."
review_reason: ''
---

## BRIEFLY

**Co se stalo.** Každý velký prohlížeč nabízí režim, kterému říká anonymní, InPrivate nebo soukromé prohlížení. Ty názvy slibují víc, než kolik ochrany mají tyhle režimy v první řadě poskytovat.

**Co to znamená.** Soukromé prohlížení hlavně omezuje, co si prohlížeč po relaci uloží v zařízení: historii, dočasné cookies, údaje z formulářů a data v mezipaměti. Je to užitečné soukromí před dalším člověkem, který k zařízení usedne.

**Rizika a dopady.** Weby, účty, do kterých jste přihlášení, zaměstnavatelé, školy i poskytovatelé internetu mohou vaši činnost dál vidět. Stažené soubory, záložky a část činnosti rozšíření navíc mohou soukromé okno přežít.

**Co se s tím dá dělat.** Nástroj volte podle toho, koho se obáváte. Soukromý režim slouží k oddělení v rámci zařízení. Na jiná rizika je ochrana účtu, sítě a zařízení.

**Na co se dívat dál.** Funkce prohlížečů se mění. Soukromý režim může doprovázet ochrana proti sledování. Ani ta z něj ale neudělá anonymitu, ochranu před malwarem ani povolení obejít pravidla spravovaného zařízení.

## FACTS

Čtyři výrobci prohlížečů popisují podobné jádro. Chrome spustí samostatnou relaci a po zavření všech anonymních oken smaže její data webů i záznam o navštívených stránkách. Firefox nepřidává navštívené stránky do běžné historie a cookies ze soukromé relace zahodí. Edge po zavření všech oken InPrivate vymaže historii, cookies, soubory v mezipaměti a data formulářů. Safari neukládá navštívené stránky, nedávná hledání ani změny cookies a dat webů.

Zároveň uvádějí důležité výjimky. Chrome si ponechá záložky a stažené soubory. Firefox uloží nové záložky, hesla a stažené soubory. Edge zachová oblíbené položky a stažené soubory. Safari stažené soubory odstraní ze svého seznamu, ale v počítači zůstanou.

Hranice sítě je jiná než hranice zařízení. Chrome uvádí, že činnost mohou vidět navštívené weby i organizace, které spravují síť, třeba škola, zaměstnavatel nebo poskytovatel internetu. Firefox píše, že soukromé prohlížení nikoho anonymním nedělá a nechrání před programy, které zaznamenávají stisky kláves, ani před spywarem. Edge stejně varuje před školami, pracovišti a poskytovateli.

Soukromý režim tedy není podvod. Jen řeší užší problém, než by naznačoval jeho název.

## EVIDENCE

Technický cíl se dá popsat jako model hrozby. Když soukromá relace skončí, člověk, který se později k zařízení dostane, by v prohlížeči měl najít méně stop po webech navštívených během ní. Je to místní ochrana a působí zpětně. Neskryje činnost před tím, kdo přihlíží během relace, před webem, ke kterému se připojujete, ani před službou, do které se přihlásíte.

Vlivná studie z oboru interakce člověka s počítačem z roku 2019 zkoumala, proč lidé tuhle hranici chápou špatně. Výzkumníci spojili posouzení použitelnosti, rozhovory o tom, jak si lidé fungování režimu představují, a cvičení, ve kterém účastníci rozhraní sami navrhovali znovu. Pro rozhovory a návrhovou část získali 25 demograficky různorodých účastníků. Téměř nikdo z nich nechápal hlavní bezpečnostní cíl režimu. Všichni, kdo soukromý režim používali, v něm byli přihlášení k osobnímu účtu a věřili, že se historie prohlížení či hledání po odchodu smaže.

Je to malý kvalitativní vzorek, ne odhad pro celou populaci. Jeho cena je ve vysvětlení. Výzkumníci zjistili, že názvy a upozornění sváděly k širšímu výkladu, než jaký technologie unesla. Starší průzkumy, které studie shrnuje, také zachytily přetrvávající omyly. Samotná studie ale nedokazuje, jak časté jsou jednotlivé představy dnes.

Ochrana v prohlížečích se mezitím vyvíjela. Chrome v anonymním režimu ve výchozím stavu blokuje cookies třetích stran. Firefox k soukromým oknům přidává ochranu proti sledování. Safari zapíná pokročilou ochranu proti sledování a proti otiskům prohlížeče. Tahle vylepšení mají váhu, ale dokumentace samotných výrobců je od anonymity dál odlišuje.

## PERSPECTIVES

Pro člověka, který sdílí rodinný počítač, je soukromý režim praktický. Udrží nákup dárku mimo historii, zabrání tomu, aby se dočasné přihlášení smíchalo s obvyklou relací, a sníží šanci, že automatické vyplňování později prozradí, co jste hledali. Ochrana funguje nejlépe, když zavřete všechna soukromá okna a se staženými soubory naložíte zvlášť.

Zaměstnanci nebo žákovi nemusí zařízení vůbec patřit. Spravovaný prohlížeč může mít pravidla, monitorovací software, povolená rozšíření a záznamy síťového provozu, na které soukromé okno nedosáhne. Tmavé barvy okna nejsou slibem, že vás neuvidí organizace, které patří počítač nebo připojení.

Na web uživatel stejně dorazí. Web vidí připojení a může přijímat informace, které mu prohlížeč posílá. Když se uživatel přihlásí, má služba ten nejsilnější běžný identifikátor: účet. Čistá sada cookies může jednu relaci méně provázat s předchozím stavem prohlížeče. Přihlášení ji ale záměrně propojí znovu.

Pro tvůrce prohlížečů je pojmenování tvrdý oříšek. „Neukládat tuto relaci do běžné místní historie“ je přesné, ale nikoho to neláká. „Soukromé“ si člověk zapamatuje, jenže si k tomu slovu dosadí vlastní význam. Ani nejlepší rozhraní nenahradí model hrozby. Může ale jasně říct, kdo činnost dál uvidí a co v zařízení zůstane.

## CONTEXT

Soukromí není jedna opona. Je to soubor vztahů mezi daty a těmi, kdo je mohou vidět. Člověk, který si půjčí notebook, provozovatel webu, výrobce prohlížeče, správce sítě, poskytovatel internetu i malware v zařízení stojí každý na jiném místě.

Soukromé prohlížení mění hlavně vztah k pozdějším uživatelům stejného profilu prohlížeče. Oddělí dočasné cookies a historii od běžné relace a na konci zahodí vyjmenovaná data, která prohlížeč spravuje. Může také zapnout další ochranu proti sledování. Samo o sobě ale nevede připojení jinudy, neopraví napadené zařízení a nesmaže záznamy uložené u vzdálené služby.

Užitečnější než otázka, jestli je režim „bezpečný“, je minutový test:

1. **Před kým činnost skrýváte?** Pokud před dalším člověkem u tohoto zařízení, soukromý režim se hodit může.
2. **Přihlásíte se?** Pokud ano, počítejte s tím, že služba může činnost spojit s vaším účtem.
3. **Kdo ovládá zařízení a síť?** Ve škole nebo v práci počítejte s tím, že pravidla i záznamy platí dál.
4. **Budete stahovat, přidávat záložky nebo ukládat heslo?** Berte to jako trvalé, dokud to sami výslovně neodstraníte.
5. **Může být zařízení napadené?** Soukromý režim není ochrana proti malwaru.

Test nedoporučuje žádný další produkt. VPN, prohlížeč zaměřený na soukromí i anonymizační síť mají své provozovatele, limity i způsoby, jak selhat. Prvním úkolem je určit, kdo se dívá, ne sbírat nálepky se slovem soukromí.

## PEOPLE

Vezměme cestovatele, který se přihlásí do e-mailu na počítači v hotelovém business centru. Soukromé okno omezí zbylou historii a cookies. Stažená palubní vstupenka ale dál existuje, poskytovatel e-mailu ví, že byl účet použit, a samotnému počítači nemusí jít věřit. Správný postup není jen zavřít kartu. Je třeba zavřít všechna soukromá okna, odhlásit se, kde to jde, smazat soubor a citlivé věci na nedůvěryhodném stroji raději nedělat.

Nebo dospívajícího, který na sdíleném rodinném notebooku hledá odpověď na osobní otázku. Soukromý režim ochrání jeho důstojnost před pozdějšími návrhy z historie prohlížeče. Ten přínos je skutečný, i když poskytovatel internetu nebo vyhledávač mohou mít záznamy dál. Říct, že ochrana je „jen místní“, neznamená říct, že je bezcenná.

Klíčový zvyk je dokončit větu: soukromé před kým, kdy a na čím zařízení?

## DEEPER

Nedorozumění kolem soukromého prohlížení je příkladem širšího problému designu. Lidé jednají podle názvů a ikon, zatímco bezpečnost stojí na neviditelných hranicích. Když produkt použije slovo s běžným společenským významem, jako je *soukromý*, lidé rozumně čekají právě ten. Technický význam je užší a platí jen za určitých podmínek.

Dobrá komunikace o bezpečnosti by proto měla popsat, co přesně je chráněno, místo aby funkci oslavovala. „Po zavření všech soukromých oken si prohlížeč z této relace neponechá běžnou historii“ je méně elegantní než „Přejděte do anonymního režimu“. Dává ale uživateli něco, co si může ověřit. Druhá věta pak může vyjmenovat, kdo činnost uvidí dál.

Platí tu i užitečná nesouměrnost. Soukromý režim ovládá, co ukládá jeho vlastní prohlížeč. Nemůže slíbit, co uloží jiný systém, protože ten mu nepatří. Web má pod kontrolou své záznamy, poskytovatel účtu historii účtu, zaměstnavatel spravovanou síť a útočník možná napadené zařízení.

Proto je třeba nástroje na ochranu soukromí posuzovat podle rozsahu, ne podle atmosféry. Tmavé okno, ikona masky nebo vážné varování mohou vyvolat pocit, že relace stojí mimo běžný provoz počítače. Datové pakety ale na náladu nereagují. Jdou po stejné síťové cestě, dokud ji nezmění jiná technologie.

Soukromé prohlížení zůstává dobrým nástrojem, když je úkol správně pojmenovaný: omezit stopy v zařízení a oddělit dočasnou relaci. Nebezpečné se stává teprve tehdy, když si malý štít spleteme s neviditelností.

## REFLECT

Kdo vás doopravdy znepokojuje: jiný uživatel zařízení, web, poskytovatel účtu, nebo majitel sítě?

Co zůstane, až okno zavřete: stažené soubory, záložky, uložená hesla, nebo činnost na vzdáleném účtu?

Popisuje nálepka „soukromé“ ochranu, kterou si můžete ověřit, nebo pocit, který si do ní vkládáte sami?
