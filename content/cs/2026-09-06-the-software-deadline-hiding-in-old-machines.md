---
slug: the-software-deadline-hiding-in-old-machines
title: "03:14:08 — softwarová lhůta, která se skrývá ve starých strojích"
dek: "Problém roku 2038 je skutečný, ale rozumnou odpovědí na něj je soupis systémů a kontrola rozhraní, ne panika s odpočítáváním."
section: tech
type: feature
depth: open
lang: cs
date: '2026-09-06'
status: published
confidence: 95
load: 0
topics: []
automation_generated: true
edition_slot: 7
automation_role: edition
generator: chatgpt-work
format: ''
event_id: ''
series: ''
image_query: embedded industrial computer clock timestamp maintenance audit
sources:
- name: Linux man-pages project
  url: https://man7.org/linux/man-pages/man2/time.2.html
  published: '2026-02-08'
- name: GNU C Library Manual
  url: https://sourceware.org/glibc/manual/latest/html_node/Feature-Test-Macros.html
  published: ''
- name: GNU Gnulib Manual
  url: https://www.gnu.org/software/gnulib/manual/html_node/Avoiding-the-year-2038-problem.html
  published: ''
- name: RFC Editor — RFC 9636
  url: https://www.rfc-editor.org/info/rfc9636/
  published: 2024-11
- name: Oracle MySQL 8.0.28 Release Notes
  url: https://dev.mysql.com/doc/relnotes/mysql/8.0/en/news-8-0-28.html
  published: '2022-01-18'
qma_path: ''
tickers: []
quiz:
  question: "Jaký je nejbezpečnější první krok při prověrce problému roku 2038?"
  options:
  - "Přenastavit všechny hodiny v ostrém provozu na rok 2038"
  - "Vyměnit každý 32bitový procesor"
  - "Sepsat dlouho sloužící systémy, uložená časová razítka a rozhraní"
  answer: 2
  explanation: "Ohrožení závisí na datových typech, softwarových rozhraních a závislostech, takže soupis musí přijít před řízeným testováním nebo výměnou."
---

## BRIEFLY

**Co se stalo.** Některé systémy, které používají unixový čas jako 32bitové číslo se znaménkem, neumějí zapsat 19. leden 2038 ve 3:14:08 UTC ani žádný pozdější okamžik.

**Co to znamená.** Mnoho moderních platforem používá širší hodnoty, ale starý software, firmware, databáze a rozhraní mohou tenhle limit dál nést.

**Rizika a dopad.** Selhání se mohou projevit odmítnutými daty, chybným řazením, propadlými přihlašovacími údaji nebo chybami služeb. Všeobecný kolaps ale není věrohodná předpověď.

**Co se dá dělat.** Sepsat dlouho sloužící systémy, chtít po dodavatelích doloženou podporu a budoucí data testovat jen na bezpečných kopiích.

**Na co si dát pozor.** Rozhraní mezi modernizovanými a staršími součástmi toho často prozradí víc než označení procesoru na krabici.

## FACTS

Technik otevře konfigurační obrazovku stroje, který má běžet až do čtyřicátých let. Procesor může být moderní, skříň čerstvě natřená a síťové připojení aktuální. Hluboko uvnitř ale může pole s časovým razítkem pořád počítat sekundy do 32bitové škatulky se znaménkem.

Unixový čas počítá sekundy od 1. ledna 1970, 00:00:00 UTC. Největší kladné 32bitové celé číslo se znaménkem je 2 147 483 647. Tolik sekund odpovídá 19. lednu 2038, 3:14:07 UTC. O sekundu později už stejný typ novou hodnotu správně zapsat nedokáže.

Manuál k času v Linuxu ten důsledek pojmenovává bez obalu: program s 32bitovým time_t může v 3:14:08 UTC narazit na přetečení, a to i na 64bitovém jádře. Aplikace, které mají běžet i po tomto okamžiku, by měly používat rozhraní s time_t širším než 32 bitů.

To je problém roku 2038. Není to proroctví, že selže každý počítač. Je to hranice, na které záleží všude, kde přežívá příliš úzké časové razítko.

## EVIDENCE

Aritmetika je snadná. Rozšíření hodnoty se znaménkem z 32 na 64 bitů posune praktický limit nepředstavitelně daleko. Mnoho běžných 64bitových platforem to už dělá.

Těžší je kompatibilita. Program neuchovává čas na jednom místě. Časová razítka se objevují v uspořádání paměti, v databázových sloupcích, binárních souborech, zprávách mezi zařízeními, autentizačních tokenech i ve voláních knihoven. Když jedna součást čeká čtyři bajty a druhá posílá osm, z matematicky správné opravy se může stát selhání rozhraní.

GNU C Library popisuje nastavení TIME_BITS, které na podporovaných 32bitových linuxových platformách umí zajistit 64bitové time_t. Vyžaduje ale také kompatibilní nastavení posunů v souborech. GNU Gnulib varuje, že přechodu může bránit propojení s knihovnami, jejichž veřejná binární rozhraní stále očekávají 32bitové time_t. Aplikace je ekosystém.

Vyvíjejí se i standardy. RFC 9636 popisuje formát informací o časových pásmech, který unixové systémy hojně používají, a podporuje verzované struktury, do nichž se vejdou i širší časy přechodů. Změny v produktech jsou nerovnoměrné: poznámky k vydání MySQL 8.0.28 popisují rozšíření podporovaných hodnot TIMESTAMP na 64bitových platformách. Aktualizace databáze může zlepšit jednu vrstvu, zatímco starý klient, exportní formát nebo vestavěný odběratel si ponechá jiný limit.

## PERSPECTIVES

Jeden tábor bere rok 2038 jako další Y2K a sahá po dramatickém odpočítávání. To přitahuje pozornost, ale zakrývá práci. Nemocniční přístroj, router, řídicí jednotka v továrně a aplikace na stolním počítači mohou selhat úplně odlišně – anebo vůbec nemusí být ohrožené.

Druhý tábor tvrdí, že moderní stroje jsou 64bitové, a problém je tedy vyřešený. To zaměňuje schopnosti hardwaru za kompatibilitu od začátku do konce. Staré binární soubory mohou běžet na nových jádrech. Aplikace mohou úzká pole ukládat záměrně. Zařízení instalovaná dnes mohou zůstat v provozu patnáct let.

Střízlivý pohled začíná u důkazů. Ptejte se, jaká reprezentace časového razítka se používá na každém rozhraní, jak daleko do budoucna se data zpracovávají a zda dodavatel otestoval celou podporovanou konfiguraci.

Y2K nabízí užitečné kulturní poučení. To, že katastrofa nepřišla, nedokazovalo, že obavy byly smyšlené; pomohla rozsáhlá náprava. Kopírování rétoriky Y2K ale může vést k mlhavým soupisům a drahé plošné výměně. Cílem není vyhrát spor o paniku. Cílem je najít konkrétní závislosti.

## CONTEXT

Některá selhání mohou přijít ještě před rokem 2038. Systém, který počítá patnáctiletou smlouvu, certifikát, splátkový kalendář hypotéky nebo životnost zařízení, už možná potřebuje zapsat data za touto hranicí. Spouštěčem není jen to, že nástěnné hodiny dojdou k onomu dni.

Způsoby selhání se liší. Datum může být odmítnuto jako neplatné. Řazení může budoucí událost zařadit do minulosti. Doba trvání může vyjít záporná. Logika ověřování nebo uchovávání dat se může chovat chybně. Jindy software vrátí čistou chybovou hlášku a nic nepoškodí.

Časová pásma a unixový čas spolu souvisejí, ale nejsou totéž. Unixové časové razítko označuje okamžik; pravidla místního času určují, jak se zobrazí. Aktualizace databáze časových pásem nerozšíří každé uložené časové razítko. A široké časové razítko nezaručí správná místní pravidla.

Šířka procesoru je také slabá zkratka. Některá 32bitová prostředí podporují 64bitová časová rozhraní. Některé 64bitové aplikace stále používají v souborech nebo protokolech úzká celá čísla. Na otázku po rozhraní reklamní leták neodpoví.

## PEOPLE

Lidé, kteří vědí, kde riziko sídlí, se málokdy sejdou v jedné místnosti. Provozní personál ví, které stroje nejde zastavit. Vývojáři znají současný kód. Nákupní oddělení drží smlouvy s dodavateli. Bezpečnostní týmy znají platnost certifikátů. Archiváři vědí, jak dlouho musí záznamy zůstat čitelné.

Dobrá prověrka jim dá společnou mapu. Nezačíná otázkou, kdo zanedbal modernizaci. Dlouho sloužící zařízení často zůstává proto, že spolehlivě dělá užitečnou fyzickou práci. Jde o to, jak tu spolehlivost udržet přes hranici, se kterou první konstruktéři u svého výrobku možná vůbec nepočítali.

Dodavatelům patří přesné otázky. Která podporovaná vydání používají široké hodnoty času? Které uložené formáty a protokoly zůstávají úzké? Jaké testy pokrývají data po lednu 2038? Jaká existuje cesta k migraci a jak dlouho bude podporovaná?

## DEEPER

Začněte prověrkou, která do provozu nezasahuje.

Sepište systémy, které mají zůstat v provozu i v roce 2038, včetně vestavěných řídicích jednotek, přístrojů, databází, zálohovacích nástrojů a autentizačních služeb. Doplňte jejich operační systémy, verze aplikací, dodavatele a odpovědné osoby.

Označte každou funkci, která pracuje s daty ve vzdálené budoucnosti: záruky, nájmy, certifikáty, harmonogramy, pravidla uchovávání a opakované události. Sledujte časová razítka napříč rozhraními, exporty a obnovenými zálohami. Systém může být uvnitř v pořádku, a přesto dostat nebezpečnou hodnotu od souseda.

Chtějte dokumentaci, ne ústní ujištění. Zaznamenejte, zda se podpora vztahuje přesně na hardware, operační systém, knihovny, databázi a připojené klienty, které používáte.

Testujte jen na bezpečné kopii nebo v prostředí schváleném dodavatelem. Hodiny v ostrém provozu na rok 2038 nepřenastavujte; může to zneplatnit certifikáty, spustit naplánované úlohy, poškodit logy nebo narušit licence. Před testem si stanovte očekávané výsledky, zálohy a postup návratu.

Nakonec berte nápravu jako správu konfigurace. Aktualizace jedné knihovny bez nového sestavení softwaru, který na ní závisí, může nechat stará rozhraní na místě. Výměna databázového sloupce bez kontroly exportů může chybu jen posunout dál po proudu.

Ve 3:14:08 nebude hlavní zprávou přetočení čísla. Bude jí to, zda organizace začaly dost brzy, aby našly tiché smlouvy mezi stroji. Lhůta je vidět. Na světlo je potřeba vynést závislosti.
