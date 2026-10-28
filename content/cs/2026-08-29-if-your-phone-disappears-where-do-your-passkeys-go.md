---
slug: if-your-phone-disappears-where-do-your-passkeys-go
title: "Když vám zmizí telefon, kam se podějí vaše přístupové klíče?"
dek: "Přístupové klíče odstraní z přihlašování heslo, ale neodstraní obnovu přístupu. Důležitá otázka zní, jestli se váš klíč synchronizuje, je vázaný na zařízení, nebo má v záloze jinou cestu."
section: tech
type: daily
depth: flagship
lang: cs
date: '2026-08-29'
status: published
confidence: 95
load: 0
topics: []
automation_generated: true
edition_slot: 1
automation_role: edition
generator: chatgpt-work
format: ''
event_id: passkey-lost-device-recovery-audit
series: ''
image_query: conceptual passkey recovery across a missing phone and trusted devices
  no readable interface no logos
sources:
- name: NIST — Digital Identity Guidelines, Authentication and Authenticator Management
  url: https://csrc.nist.gov/pubs/sp/800/63/b/4/final
  published: '2025-07-31'
- name: FIDO Alliance — Apple, Google and Microsoft Expand Passwordless Sign-In Support
  url: https://fidoalliance.org/apple-google-and-microsoft-commit-to-expanded-support-for-fido-standard-to-accelerate-availability-of-passwordless-sign-ins/
  published: '2022-05-05'
- name: FIDO Alliance — Multi-Device FIDO Credentials
  url: https://fidoalliance.org/white-paper-multi-device-fido-credentials/
  published: '2022-03-17'
- name: Passkey Central — Passkey Management UI Best Practices
  url: https://www.passkeycentral.org/design-guidelines/optional-patterns/passkey-management-ui-best-practices-for-combining-all-passkey-types
  published: '2024-05-24'
- name: Apple Support — Set Up iCloud Keychain
  url: https://support.apple.com/en-us/109016
  published: '2026-05-12'
qma_path: ''
tickers: []
quiz:
  question: "Co nejpříměji rozhoduje o tom, jestli ztráta jednoho telefonu znamená i okamžitou ztrátu přístupu k přístupovému klíči?"
  options:
  - "Jestli mu web říká přístupový klíč, a ne bezpečnostní klíč"
  - "Jestli se přístupový klíč synchronizuje přes správce přihlašovacích údajů, nebo je vázaný na ztracené zařízení"
  - "Jestli telefon používal rozpoznávání obličeje místo PIN"
  answer: 1
  explanation: "Synchronizované přístupové klíče se obvykle dají obnovit, jakmile získáte zpět přístup k účtu správce přihlašovacích údajů. Přístupový klíč vázaný na zařízení zůstává ve svém zařízení nebo hardwarovém klíči, takže je potřeba jiný registrovaný klíč nebo postup obnovy, který nabízí daná služba."
---

## BRIEFLY

**Co se stalo.** Přístupové klíče se šíří, protože odolávají phishingu a nevyžadují psaní opakovaně použitelného tajemství. Bodrý pokyn „uložte si přístupový klíč do tohoto telefonu“ ale zakrývá důležitý rozdíl: mnoho přístupových klíčů se synchronizuje přes správce přihlašovacích údajů, jiné zůstávají vázané na jedno zařízení nebo hardwarový bezpečnostní klíč.

**Co to znamená.** Ztráta telefonu obvykle neznamená, že synchronizovaný přístupový klíč navždy zmizel. Znamená, že přístup teď závisí na obnovení účtu, který ho synchronizuje. U klíče vázaného na zařízení je to jinak: bez dalšího registrovaného klíče rozhoduje postup obnovy účtu na samotném webu.

**Rizika a dopad.** Přístupové klíče útočníkům zavírají jedny známé dveře, ale obnova přístupu se může stát bočním vchodem. Slabý záchranný e-mail, nedostupné telefonní číslo nebo jediný hardwarový klíč mohou z bezpečného přihlášení udělat buď převzetí účtu, nebo zbytečné zablokování.

**Co se dá dělat.** Zjistěte, kde jsou uložené vaše důležité přístupové klíče, zabezpečte účet správce, zaregistrujte druhou cestu a vyzkoušejte obnovu dřív, než o něco přijdete.

**Na co si dát pozor.** Užitečnou obrazovkou není výzva k vytvoření přístupového klíče. Je to stránka zabezpečení účtu, kde vidíte přístupové klíče, způsoby obnovy a nedávno použitá zařízení.

## FACTS

Přístupový klíč není heslo uložené v módnější krabičce. Když se vytváří, autentizátor vygeneruje pro daný účet a danou online službu pár kryptografických klíčů. Služba dostane veřejný klíč. Soukromý klíč zůstane ve správci přihlašovacích údajů nebo na bezpečnostním klíči.

Při přihlášení pošle služba novou výzvu. Vaše zařízení si vyžádá místní schválení, třeba otisk prstu, sken obličeje nebo PIN, a pak soukromým klíčem výzvu podepíše. Služba podpis ověří veřejným klíčem, který už má. Biometrická šablona na web vůbec necestuje.

Na tomhle návrhu záleží, protože přístupový klíč je vázaný na doménu skutečného webu. Neexistuje žádné opakovaně použitelné heslo, které by mohl posbírat přesvědčivě vypadající podvodný web, a únik databáze ze služby odhalí veřejné klíče, ne hashe hesel, které by se útočník mohl pokusit prolomit. Současná doporučení NIST k autentizaci považují správně implementovanou kryptografickou autentizaci za odolnou vůči phishingu, protože odpověď je vázaná na ověřovatele.

Otázka „kde je soukromý klíč?“ má ale dvě odpovědi.

Většina spotřebitelských telefonů a notebooků ukládá přístupové klíče do správce přihlašovacích údajů, který je umí synchronizovat mezi schválenými zařízeními. Apple popisuje Klíčenku na iCloudu jako službu, která udržuje hesla a přístupové klíče aktuální na schválených zařízeních s koncovým šifrováním. Jiní platformní i nezávislí správci nabízejí podobné modely synchronizace.

Přístupový klíč vázaný na zařízení se nesynchronizuje. Může být uložený v hardwarovém bezpečnostním klíči nebo v místním úložišti zařízení. Doporučení FIDO k uživatelskému rozhraní uvádějí, že většina hardwarových bezpečnostních klíčů drží přístupové klíče vázané na zařízení, zatímco většina telefonů a notebooků používá klíče synchronizované přes správce. Přihlašovací obrazovka může obojí označovat prostě jako „přístupové klíče“, což se snadněji používá, ale méně to pomáhá, když plánujete, co dělat při ztrátě.

## EVIDENCE

Zlepšení bezpečnosti je skutečné. Základní standardy vytvořily FIDO a konsorcium World Wide Web Consortium; v květnu 2022 Apple, Google a Microsoft oznámily rozšířenou podporu, která měla zpřístupnit přihlašovací klíče na nových zařízeních a umožnit přihlašování napříč zařízeními. Cílem nebylo jen pohodlí. Šlo o to, aby se silná autentizace odolná vůči phishingu stala natolik praktickou, že může hesla nahradit ve velkém.

Daň v podobě obnovy přístupu byla vidět od začátku. Dokument FIDO o klíčích pro více zařízení z března 2022 tvrdil, že synchronizace může zpřístupnit autentizaci FIDO, i když uživatel vymění zařízení. To řeší starý problém, kdy se každý telefon nebo počítač musel registrovat zvlášť.

Zároveň to mění mapu důvěry. Pokud se přístupový klíč synchronizuje přes váš účet u platformy nebo správce hesel, obnova tohoto účtu může vrátit mnoho přístupových klíčů. Bezpečnost přístupových klíčů proto zčásti závisí na šifrování správce, schvalování zařízení a postupu obnovy. Soukromé klíče se pořád nepředávají jednotlivým webům, ale účet správce se stává neobvykle důležitým.

Doporučení NIST z července 2025 neprohlašují všechny synchronizované autentizátory za stejné. Žádají organizace, aby zvážily, jak jsou klíče chráněné, jak se obnovují účty, jestli je přístup k synchronizační infrastruktuře silně ověřený a jestli úroveň záruky odpovídá riziku. Banka, zaměstnavatel a web s recepty se mohou rozumně rozhodnout různě.

Žádný univerzální obřad obnovy neexistuje. Jedna služba může povolit několik přístupových klíčů, jiná kód pro obnovu, další ověření totožnosti a další záložní heslo. Tahle rozmanitost je pro běžné uživatele největší nejistotou. „Používám přístupové klíče“ popisuje hlavní vchod. Nepopisuje požární východy budovy.

## PERSPECTIVES

Nadšený pohled říká, že přístupové klíče odstraňují nejhorší návyky života s hesly: opakované používání, psaní tajemství do phishingových stránek a obnovování zapomenutých řetězců. To je v zásadě pravda. Přístupový klíč může být jednodušší a zároveň výrazně bezpečnější než heslo s SMS kódem.

Skeptický pohled říká, že synchronizace jen přesouvá jediný bod selhání z hesla k webu na Apple, Google, Microsoft nebo správce hesel. To je příliš zjednodušené, ale upozorňuje to na vážné soustředění důvěry. Dobře chráněný účet správce, šifrovaná synchronizace a schválená zařízení nejsou totéž co jedno opakovaně použité heslo. Ztráta kontroly nad tímto účtem ale může zasáhnout mnoho služeb najednou.

Pohled s důrazem na vysokou úroveň zabezpečení dává přednost hardwarovým klíčům vázaným na zařízení, protože soukromý klíč se z nich nedá zkopírovat do cloudové synchronizace. Pro správce systémů, novináře, vedoucí pracovníky nebo regulovanou práci to může být správná volba. Vytváří to ale i všední fyzické riziko: jediný klíč se může ztratit ve stejném taxíku jako klíče od domu. Vysoká úroveň zabezpečení potřebuje náhradní klíč a řízený plán obnovy, ne posvátnou úctu k jednomu kousku plastu.

Praktický závěr nezní, že si máte pro všechny účty vybrat jednu architekturu. Zní, že máte vědět, kterou architekturu skutečně máte.

## CONTEXT

Hesla naučila lidi chápat ověřování jako vědění: zapamatuj si tajemství a můžeš dovnitř. Přístupové klíče posouvají ověřování blíž k vlastnictví a místnímu schválení. Držíte autentizátor a ten po odemčení prokáže, že má soukromý klíč.

Obnova přístupu je proto rozhodnutím o totožnosti. Když původní autentizátor zmizí, někdo musí rozhodnout, jestli ten, kdo o přístup žádá, je oprávněný držitel účtu. Synchronizovaný správce může použít stávající zařízení, heslo k účtu, kód zařízení, kontakt pro obnovu nebo jiný faktor. Web může sáhnout po e-mailu, kódech, zákaznické podpoře nebo formálním ověření totožnosti.

Útočníci tomuhle posunu rozumějí. Jak phishing na hlavní vchod ztrácí účinnost, tlak se přesouvá k obnově účtů, výměnám SIM karet, kompromitovaným e-mailům a sociálnímu inženýrství vůči zákaznické podpoře. Bezpečný přístupový klíč spojený s nedbalou obnovou připomíná ocelové vchodové dveře vedle otevřeného okna do kuchyně.

To není argument proti přístupovým klíčům. Je to obyčejná historie bezpečnosti: posílení jedné vrstvy změní místo, kam soustředí pozornost obránci i útočníci.

## PEOPLE

Představte si, že ve vlaku zmizí telefon.

Pro jednoho člověka je náhradní telefon jen mírná otrava. Znovu se přihlásí ke správci přihlašovacích údajů, schválí nové zařízení přes notebook, kterému už důvěřuje, a synchronizované přístupové klíče se vrátí. Pak ztracený telefon zablokuje a odebere ho ze seznamu zařízení.

Pro druhého byl ztracený telefon jediným schváleným zařízením, držel jedinou kopii klíče vázaného na zařízení a chodily na něj SMS zprávy pro obnovu. Na tom telefonu závisel i jeho e-mailový účet. Nic kryptografického nezklamalo. Zklamal plán obnovy.

Oba mohli po pravdě říct: „Moje účty používají přístupové klíče.“ Rozdíl se ukáže až ve zlý den.

## DEEPER

Užitečná kontrola přístupových klíčů zabere asi patnáct minut a nevyžaduje nic mazat ani resetovat.

**1. Najděte vrstvu, kde jsou klíče uložené.** Otevřete správce hesel nebo přihlašovacích údajů, kterého skutečně používáte. Zkontrolujte, jestli se důležité přístupové klíče zobrazují na víc než jednom schváleném zařízení. Nepředpokládejte, že se přístupový klíč vytvořený na pracovním počítači synchronizuje do osobního telefonu, ani že je hardwarový bezpečnostní klíč zálohovaný.

**2. Zabezpečte účet, který synchronizaci obstarává.** Projděte si jeho záchranný e-mail, záchranný telefon, důvěryhodná zařízení a druhé faktory. Odeberte zařízení, která už nevlastníte. Pokud má účet správce ještě heslo, použijte jedinečné. Záchranná adresa, do které se nedostanete, je jen ozdoba.

**3. Přidejte další cestu dřív, než odeberete první.** U zásadního účtu zaregistrujte druhý přístupový klíč na jiném důvěryhodném zařízení nebo náhradní bezpečnostní klíč, pokud to služba dovolí. Náhradní hardwarový klíč mějte jinde než ten každodenní. Nikdy nezkoušejte odolnost tím, že smažete jediný fungující klíč.

**4. Uložte si kódy pro obnovu offline.** Pokud služba nabízí jednorázové kódy, uložte je tam, kam se dostanete bez ztraceného telefonu a bez účtu, který chrání. Vytištěné a bezpečně uschované mohou být odolnější než snímek obrazovky uložený jen ve stejném cloudovém účtu.

**5. Nacvičte si bezpečné přihlášení.** Použijte druhé zařízení nebo anonymní okno prohlížeče a ověřte si, že můžete zvolit náhradní způsob. Zastavte se, pokud by postup vyžadoval odebrat klíč nebo změnit nastavení zabezpečení. Smyslem je najít cestu, ne inscenovat nouzovou situaci.

**6. Sepište si postup pro ztracené zařízení.** Zamkněte nebo vymažte zařízení přes službu platformy pro ztracená zařízení; při podezření na krádež zabezpečte své telefonní číslo; přihlaste se z důvěryhodného zařízení; prohlédněte si nedávnou aktivitu; pak u každé služby odeberte zastaralé přístupové klíče, jakmile začne fungovat náhradní klíč. Přesné pořadí závisí na platformě a službě, takže při skutečné ztrátě se řiďte jejich aktuálními oficiálními pokyny.

Organizace by měly jít dál. Potřebují soupis povolených typů autentizátorů, postup technické podpory odolný vůči sociálnímu inženýrství a oddělenou obnovu pro privilegované účty. Zavedení přístupových klíčů bez promyšlené obnovy je nedokončený projekt ověřování.

## REFLECT

Přístupové klíče odstraňují břemeno, se kterým si lidé poradí špatně: vymýšlení a ochranu opakovaně používaných řetězců. Neodstraňují ztrátu, výměnu, dědění, cestování, rozbité displeje ani potřebu prokázat, kdo jsme, když obvyklé zařízení není po ruce.

Nejlepší plán obnovy je skoro nudný. Dvě cesty, uložené odděleně, vyzkoušené ve chvíli, kdy se nic neděje.

Kdyby vám dnes odpoledne zmizel telefon, který účet byste potřebovali, abyste obnovili všechny ostatní, a jak byste se do něj dostali?
