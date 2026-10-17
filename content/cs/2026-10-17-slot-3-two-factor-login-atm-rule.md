---
slug: two-factor-login-is-the-atm-rule-for-your-email
title: "Dvoufázové přihlášení je pravidlo bankomatu, jen pro váš e-mail"
dek: "Karta a PIN hlídají hotovost celá desetiletí. Stejný princip dnes hlídá vaše účty a víc než to, jestli druhý krok máte, rozhoduje, jaký to je."
section: culture
type: analysis
depth: open
lang: cs
date: '2026-10-17'
status: draft
confidence: 80
load: 0
topics: []
automation_generated: true
edition_slot: 3
automation_role: edition
generator: claude-code
format: ''
event_id: ''
series: ''
image_query: hardware security key laptop keyboard
impact:
  areas: [safety, money]
  line: "Komu e-mail nebo bankovnictví chrání jen heslo, může o účet přijít, jakmile heslo zjistí někdo cizí. Druhý faktor takového člověka zastaví, i když kódy z textových zpráv mají známá slabá místa."
  todo: "Otevřete bezpečnostní nastavení svého hlavního e-mailu, podívejte se, jaký druhý faktor máte zapnutý, a ověřte si, jak byste se dostali dovnitř, kdybyste ztratili telefon."
sources:
  - name: "Wikipedia — Multi-factor authentication"
    url: "https://en.wikipedia.org/wiki/Multi-factor_authentication"
    published: ""
  - name: "Wikipedia — Authentication"
    url: "https://en.wikipedia.org/wiki/Authentication"
    published: ""
  - name: "Wikipedia — Comparison of OTP applications"
    url: "https://en.wikipedia.org/wiki/Comparison_of_OTP_applications"
    published: ""
qma_path: ''
tickers: []
quiz:
  question: "Proč číslo karty a trojmístný kód na její zadní straně nejsou dvoufázové ověření?"
  options:
    - "Obojí je něco, co víte, takže jde o stejný druh důkazu"
    - "Trojmístný kód je příliš krátký, aby se počítal jako faktor"
    - "Víc než jeden faktor smějí používat jen banky"
  answer: 0
  explanation: "Dvoufázové ověření znamená dva různé druhy důkazu. Číslo karty i kód jsou znalosti a článek o vícefaktorovém ověření to řadí mezi jednoduché ověření."
---

## BRIEFLY

**Co se stalo.** Vícefaktorové ověření, často nazývané dvoufázové, chce před otevřením účtu dva různé druhy důkazu a používá se čím dál víc.

**Co to znamená.** Heslo samo se dá uhodnout, může uniknout nebo ho z vás někdo vyláká. Když k němu přibude něco, co máte, nebo něco, čím jste, ukradené heslo už nestačí.

**Rizika a dopady.** Týká se to každého, kdo má e-mail, bankovní účet nebo sociální síť. Účty se zapnutým druhým faktorem někdo cizí převezme mnohem méně často. Obejít se to přesto dá opakovanými výzvami k přihlášení, falešnými přihlašovacími stránkami a převzetím telefonního čísla. Kódy z textových zpráv mají známé slabiny.

**Co se s tím dá dělat.** Zjistěte, jaký druhý faktor používá váš hlavní e-mail a jak se do něj dostanete, když telefon zmizí. Nikdy neschvalujte přihlášení, které jste sami nezačali.

**Na co se dívat dál.** Jestli služby, na kterých závisíte, nabízejí ověřovací aplikaci nebo hardwarový klíč, a ne jen kódy v textových zprávách.

## FACTS

Představte si bankomat. Zasunete kartu a naťukáte krátký PIN. Ani jedno samo bankovku nevydá. Zloděj s vaší kartou pořád potřebuje PIN. Kdo vás při psaní PINu sledoval, pořád potřebuje kartu.

Tahle dvojice je dvoufázové ověření v nejstarší každodenní podobě. Encyklopedické heslo o vícefaktorovém ověření (MFA) používá právě tenhle příklad. Pravidlo je jednoduché: web nebo aplikace vás pustí dovnitř, až když předložíte dva nebo více *různých druhů* důkazu. Když jeden chybí nebo nesedí, dveře zůstanou zavřené.

Hlavní druhy jsou tři. Něco, co víte: heslo nebo PIN. Něco, co máte: platební kartu, klíč, bezpečnostní token nebo telefon, který je dosažitelný na určitém čísle. Něco, čím jste: otisk prstu, obličej, hlas, dokonce rytmus psaní na klávesnici. Některé systémy přidávají čtvrtý signál, a to kde jste. Přihlášení zevnitř firemní sítě může mít jiná pravidla než přihlášení na dálku.

Důležité slovo je *různých*. Číslo karty a trojmístný kód na zadní straně jsou dva kusy důkazu. Obojí je ale něco, co víte, nebo co ví kdokoli, kdo má fotku karty. Článek o MFA to řadí mezi jednoduché ověření, ne mezi dva faktory.

## EVIDENCE

V čem se zdroje shodují: MFA se používá víc a účty, které ho mají zapnuté, jsou výrazně méně často napadeny. Pasáž, ze které jsme vycházeli, neuvádí žádné konkrétní procento, a my si ho proto nevymýšlíme.

Co stejný zdroj jmenuje jako slabá místa: tři cesty, jak ho obejít, totiž útoky únavou, phishing a výměnu SIM karty. Vypočítává i problémy, které mají právě kódy posílané textovou zprávou. Telefony se dají naklonovat. Aplikace mohou běžet na několika telefonech. Technici mobilních operátorů mohou SMS číst. A napadený telefon už není něco, co máte jen vy.

Kódy v textových zprávách jsou na poměry internetu stará technika. Článek dohledává tu myšlenku do roku 1996, kdy AT&T popsala systém, který schvaloval transakce výměnou kódů přes obousměrné pagery.

Co nám tyhle zdroje říct neumějí: jak často se který způsob obejití děje, ani o kolik je aplikace nebo hardwarový klíč bezpečnější než textový kód, v číslech. Všechny tři zdroje jsou články z Wikipedie, které shrnují cizí práci a mohou se měnit. Berte je jako dobře nakreslenou mapu, ne jako krajinu samotnou.

## PERSPECTIVES

**„Jakýkoli druhý faktor je lepší než žádný."** To je praktický pohled a zdroj podporuje jeho jádro: útočník, který má jen vaše heslo, se zastaví. Jeho slepé místo je pohodlí. Lidé si zapnou kódy v SMS, mají pocit, že je hotovo, a nikdy se nedozvědí, že nejslabší varianta má známé díry.

**„Textové kódy jsou k ničemu, berte hardwarový klíč."** Tenhle pohled bere vyjmenované slabiny SMS vážně. Článek o MFA uvádí, že klíče FIDO2, které podporují FIDO Alliance a W3C, mají běžnou podporu v prohlížečích od roku 2015. Vynechává ale náklady, které stejný článek vypisuje. Fyzické tokeny se musejí nosit u sebe, dají se ztratit nebo ukrást, většinou se nedají snadno použít pro mnoho účtů a jejich nákup i výměna stojí peníze.

**„Bezpečnost vždycky něco stojí na pohodlí."** Článek o MFA to říká skoro doslova: mezi použitelností a bezpečností jsou nevyhnutelné kompromisy. Oba předchozí tábory na to rády zapomínají. Rozumný střed je docela prostý. Nejlepší druhý faktor je ten nejsilnější, který člověk opravdu bude dál používat.

## CONTEXT

Začněme tím, jak funguje ověřovací aplikace, protože vypadá jako kouzlo a není. Aplikace ukazuje krátký kód, který se pořád mění. Říká se mu časové jednorázové heslo, anglicky TOTP. Váš telefon i služba mají stejné tajemství, které článek nazývá klíčovým materiálem. Každá strana ho spojí s aktuálním časem a obě dojdou ke stejnému číslu. Tajemství samo nikam necestuje a kód, který unikne, brzy zestárne.

Srovnávací stránka uvádí dvě příbuzné metody. HOTP místo času počítá použití. Mobile-OTP je starší systém s otevřeným kódem, který míchá PIN, čas a tajemství uložené v zařízení. Stránka také dělí aplikace na dvě rodiny: samostatné ověřovače a správce hesel s vestavěným ověřovačem. Druhá varianta je pohodlná. Zároveň ale věší oba klíče na jeden kroužek, a to stojí za chvilku přemýšlení.

Hardwarové klíče stojí na nejstarším principu ze všech. Článek o MFA připomíná, že faktory vlastnictví se po staletí používají v podobě klíče k zámku. Klíč nese tajemství, které sdílí se zámkem. Softwarový token v telefonu se dá zkopírovat. Vyhrazený hardwarový token ne, pokud se do něj někdo fyzicky nevloupá.

A teď tři způsoby obejití, srozumitelně. Při útoku únavou někdo, kdo už má vaše heslo, spouští výzvy k přihlášení znovu a znovu a doufá, že ťuknete na „schválit", jen aby to přestalo. Při phishingu chce falešná přihlašovací stránka vaše heslo i kód a obojí hned předá dál. Při výměně SIM někdo přemluví mobilního operátora, aby vaše číslo převedl na jeho kartu, a vaše textové kódy jdou za ním.

Jedna rozšířená představa si zaslouží opravit. Bezpečnostní otázka, třeba jméno vašeho prvního mazlíčka, není druhý faktor. Je to jen další věc, kterou víte, stejného druhu jako heslo.

## DEEPER

Slovo *autentizace* pochází z řeckého *authentikos*, „skutečný, pravý", a z *authentés*, „původce". Pod každou výzvou k přihlášení tedy leží velmi stará otázka: kdo je původcem téhle žádosti?

Dávno před počítači na ni lidé odpovídali třemi způsoby, jak vysvětluje článek o autentizaci. Za předmět se mohl zaručit důvěryhodný svědek. Znalec mohl porovnat jeho rysy se známými originály. Nebo ho mohl potvrdit dokument, třeba certifikát. Každou z těch cest šlo zfalšovat. Syn Hana van Meegerena, známého padělatele obrazů, padělal díla svého otce a přidal k nim i certifikát o původu.

Obrana proto nikdy nestála na dokonalosti. Stála na počtech. Padělání se vyplácí jen tak dlouho, dokud falešná věc stojí míň, než vynese, a dobré ověření tu cenu zvedá. Dvoufázové přihlášení nedělá nic velkolepějšího. Nedělá účet nedobytným. Jen zařídí, že vloupání dá víc práce, než je ochotna vynaložit většina útočníků.

Děje se tu i něco tiššího. Lidé, kteří nás znají, nás poznají podle tváře a hlasu, tedy podle faktoru, kterému inženýři říkají „něco, čím jste". Na internetu se prokazujeme věcmi, které nosíme, a věcmi, které si pamatujeme, protože server nás nikdy neviděl. Většina z nás každý den kus času přesvědčuje stroje, že jsme opravdu ti, za koho se vydáváme.

## REFLECT

Ztráta kterého účtu by vás bolela nejvíc a víte, jak ten účet ověřuje, že jste to vy?

Kdy jste naposledy schválili výzvu k přihlášení, aniž byste přemýšleli, odkud přišla?

Zkuste dnes: otevřete bezpečnostní nastavení svého hlavního e-mailu a poznamenejte si, jaký druhý faktor používá.
