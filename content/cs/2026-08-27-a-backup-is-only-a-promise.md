---
slug: a-backup-is-only-a-promise
title: "Záloha je jen slib, dokud z ní nic neobnovíte"
dek: "Zelená fajfka dokazuje, že se něco zkopírovalo. Malá zkouška obnovy dokazuje, že vám ta kopie ještě dokáže pomoct."
section: tech
type: analysis
depth: open
lang: cs
date: '2026-08-27'
status: published
confidence: 95
load: 0
topics: []
automation_generated: true
edition_slot: 3
automation_role: edition
generator: chatgpt-work
format: ''
event_id: ''
series: ''
image_query: conceptual archive box with one recovered family photo and document no
  logos
sources:
- name: NIST SP 800-184 — Guide for Cybersecurity Event Recovery
  url: https://csrc.nist.gov/pubs/sp/800/184/final
  published: 2016-12
- name: UK National Cyber Security Centre — Mitigating malware and ransomware attacks
  url: https://www.ncsc.gov.uk/guidance/mitigating-malware-and-ransomware-attacks
  published: '2020-02-13'
- name: UK National Cyber Security Centre — Ransomware-resistant cloud backups
  url: https://www.ncsc.gov.uk/collection/ransomware-resistant-backups/principles-for-ransomware-resistant-cloud-backups
  published: '2024-11-22'
- name: Apple Support — Back up your Mac with Time Machine
  url: https://support.apple.com/en-us/104984
  published: '2026-07-06'
- name: Apple Support — Restore your Mac from a backup
  url: https://support.apple.com/en-asia/102551
  published: '2025-11-10'
qma_path: ''
tickers: []
quiz:
  question: "Co dokáže úspěšná malá zkouška obnovy, co hlášení „záloha dokončena“ nedokáže?"
  options:
  - "Že zkopírovaná data jde najít, otevřít a použít"
  - "Že každá budoucí záloha proběhne bezchybně"
  - "Že se ransomware nedostane k žádnému zařízení"
  answer: 0
  explanation: "Zkouška obnovy ověřuje, jestli jde vybraná data skutečně obnovit. Nezaručí budoucí zálohy ani neodstraní jiná bezpečnostní rizika."
---

## BRIEFLY

**Co se stalo.** Telefony, notebooky a cloudové služby dělají z kopírování dat něco, co působí samozřejmě. Dokončená záloha ale ještě není soubor, který jde obnovit.

**Co to znamená.** Zelená fajfka potvrzuje, že nějaký proces ohlásil úspěch. Nedokazuje, že se zálohovaly správné složky, že ještě existuje starší verze, že je po ruce šifrovací heslo ani že obnovený soubor půjde otevřít.

**Rizika a dopad.** Chybějící složky, prošlou dobu uchovávání, poškozená média nebo ztracené přihlašovací údaje lidé často objeví až po krádeži, poruše hardwaru, nechtěném smazání nebo útoku ransomwaru.

**Co se dá dělat.** Udělejte si malé a neškodné cvičení obnovy: vyberte typické soubory, obnovte je do samostatné složky, otevřete je, zapište si, jak dlouho to trvalo, a opravte první věc, která selhala.

**Na co si dát pozor.** Kontrolujte rozsah, stáří, historii verzí, oddělení od původního zařízení, přístupové údaje a datum poslední úspěšné obnovy, ne jen poslední zálohy.

## FACTS

Přímá odpověď je jednoduchá: že záloha funguje, nevíte, dokud z ní něco nevytáhnete a nepoužijete.

Zálohovací software obvykle podle rozvrhu kopíruje data. Může ohlásit, že úloha doběhla, kolik souborů zpracoval a kdy se naposledy připojil. To jsou užitečné signály. O tom, jestli kopie obsahuje soubor, na kterém vám záleží, a jestli ho dokážete obnovit v reálných podmínkách, ale říkají málo.

Tři nástroje se běžně pletou. Synchronizace drží pracovní složky stejné na všech zařízeních. To je pohodlné, jenže se může zesynchronizovat i smazání nebo poškozený soubor. Historie verzí uchovává po určitou dobu dřívější stavy. Záloha drží samostatnou kopii pro obnovu podle vlastního rozvrhu a pravidel. Některé služby spojují všechny tři. Z názvu samotného ale nepoznáte, jakou poruchu přežijí.

Dokumentace k Time Machine od Applu ukazuje pohodlí i hranici. Time Machine dělá hodinové, denní a týdenní kopie a nejstarší maže, když se disk zaplní. Umí obnovit jednotlivé soubory nebo přenést celý účet. Užitečný je právě proto, že má cestu zpátky. Jeho rozvrh ale neslibuje, že se zálohoval každý externí disk, každá cloudová složka a každé vyloučené místo.

## EVIDENCE

Příručka NIST pro obnovu po kybernetických incidentech bere obnovu jako schopnost, kterou je potřeba naplánovat, ne jako poslední tlačítko, které se zmáčkne po škodě. Netýká se to jen ransomwaru. Organizace potřebuje vědět, co se musí obnovit, v jakém pořadí a kteří lidé, systémy a návaznosti musí být k dispozici.

Britské Národní centrum kybernetické bezpečnosti NCSC praktické poučení říká naplno. Jeho doporučení k malwaru radí pravidelně zálohovat, mít víc kopií na různých místech a pravidelně zkoušet, že soubory jdou obnovit. Varuje také před tím, nechávat výměnná zálohovací zařízení trvale připojená, protože útočníci se mohou zaměřit na dostupné kopie.

Novější zásady NCSC vysvětlují, proč může záloha existovat, a přesto selhat. Útočník ji může smazat, změnit pravidla uchovávání, poškodit postupně jednu verzi po druhé nebo odstranit účty, přes které se k ní dá dostat. Doporučení proto žádají chráněnou historii verzí, dohled, nezávislé přístupové cesty a zkoušky obnovy na požádání.

Ty dokumenty jsou psané hlavně pro organizace, domácí verzi v nich ale snadno poznáte. Když jediná kopie leží na disku, který je pořád připojený k napadenému notebooku, není dobře oddělená. Když je jediné heslo k obnově uložené ve ztraceném telefonu, točíte se v kruhu. A když se fotoknihovna ze zálohy vyřadila a nikdo si toho nevšiml, úspěšná záloha chránila něco jiného, než měla.

## PERSPECTIVES

Jedna odpověď zní: všechno zautomatizovat a systému věřit. Automatizace má cenu, protože paměť je nespolehlivá. Brání tomu, aby z plánu „o víkendu si udělám zálohu“ časem zbyla jen rodinná legenda. Jenže automatizace umí chybu opakovat dokonale: špatná složka, plný disk, odpojený účet nebo doba uchovávání kratší, než jste čekali.

Opačná odpověď je dělat několik ručních kopií. To může přinést oddělení, ale ruční kopie se snadno odkládají a těžko se v nich udržuje přehled. Několik složek s názvem „finální“ na jednom disku nejsou několik nezávislých záloh.

Třetí pohled tvrdí, že cloudové úložiště udělalo z domácího zkoušení přežitek. Cloudové služby mohou chránit před rozbitým notebookem a mohou uchovávat staré verze. Závisejí ale na přístupu k účtu, na pravidlech poskytovatele a na rozdílu mezi synchronizací a zálohou. Rozumný závěr nezní „cloud je špatný a disk dobrý“. Zní tak, že obnova nesmí záviset na téže jediné události, která zničí originál.

Žádné domácí cvičení nedokáže, že jsou pokryté všechny soubory a všechny katastrofy. Dokument obnovený dnes nezaručí, že příští měsíc záloha proběhne. Zkoušení nejistotu zmenšuje, ale neodstraní.

## CONTEXT

Obnova má dvoje hodiny. První ukazují stáří nejnovější použitelné kopie: kolik nedávné práce můžete přijít? Druhé měří, jak dlouho trvá, než zase můžete pracovat: u jednoho dokumentu minuty, u fotoknihovny hodiny, u celého počítače třeba dny.

Tyhle dvoje hodiny vysvětlují, proč je věta „mám zálohu“ neúplná. Měsíční kopie může stačit pro archiv, který se skoro nemění, a být nedostatečná pro projekt, na kterém pracujete denně. I dokonalá kopie může být k ničemu, když vyžaduje heslo, které nikdo nenajde, nebo připojení, které při výpadku nefunguje.

Záleží i na době uchovávání. Rozvrh Time Machine, jak ho Apple zveřejňuje, drží postupně stále méně historických bodů a nejstarší kopie maže, jak dochází místo. Pravidla uchovávání mají i cloudové služby. Když si poškození dost dlouho nikdo nevšimne, čisté verze mohou vypršet, zatímco poškozené nebo zašifrované soubory dál přibývají.

Zkouška obnovy by proto měla napodobit malý kousek poruchy, aniž by nějakou způsobila. Nemažte původní zařízení, jen abyste dokázali odvahu. Obnovte vybrané soubory do samostatného umístění a výsledek porovnejte.

## DEEPER

Zkuste tenhle dvacetiminutový audit obnovy.

Nejdřív vyberte čtyři typické položky: nedávný dokument, starší fotku, složku s několika soubory a jeden soubor z místa, o kterém si nejste jistí, jestli je chráněné. Jako pokus nepoužívejte nic, čeho máte jedinou kopii.

Zadruhé si zapište, co čekáte. Která služba nebo který disk drží jednotlivé položky? Jak staré by měly být dostupné verze? Jaké přihlašovací údaje nebo šifrovací heslo budete potřebovat? Na tomhle odhadu záleží, protože zkouška, která najde jen to, o čem už víte, že je snadné, může dát falešný pocit bezpečí.

Zatřetí obnovujte do nové složky, ne přes živý soubor. Otevřete dokument, prohlédněte si fotku a zkontrolujte strukturu složky. Název souboru v katalogu nestačí. Pokud to jde, porovnejte velikosti souborů nebo kontrolní součty. Pro většinu domácností je ale už samotné otevření typických souborů mnohem lepší než důvěra v ikonku stavu.

Začtvrté si zapište čtyři údaje: datum zkoušky, nejnovější použitelnou zálohu, nejstarší užitečnou verzi a potřebný čas. Poznamenejte si vyloučené složky, chybějící hesla nebo matoucí návody.

Nakonec opravte jednu slabinu. Připojte disk, na který se má podle rozvrhu zálohovat. Přidejte chybějící složku. Uložte klíč pro obnovu někam, kde je fyzicky chráněný a nezávislý na zařízení, které denně používáte. Pro nenahraditelné věci přidejte druhé místo. Pak si stanovte rozumný termín opakování: po každé větší změně zařízení a potom pravidelně.

Pokud data patří zaměstnavateli, škole nebo regulované službě, řiďte se jejich postupem obnovy a nepřesouvejte kopie do osobního účtu. Domácí audit má zlepšit možnost obnovy, ne vytvořit nový problém s ochranou soukromí.

## REFLECT

Záloha je slib, který včerejšek dává budoucímu vám na hodně špatné ráno. Nejlaskavější způsob, jak ten slib ověřit, je nečekat na to ráno.

Které čtyři soubory by vám rychle a poctivě řekly, jestli je váš plán obnovy skutečný?
