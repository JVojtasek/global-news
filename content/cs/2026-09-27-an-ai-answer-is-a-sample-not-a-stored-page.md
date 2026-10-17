---
title: Odpověď umělé inteligence je vzorek, ne uložená stránka
slug: an-ai-answer-is-a-sample-not-a-stored-page
dek: Stejné zadání může vést po různých cestách tokenů. Pro vymýšlení je to užitečné,
  ověřování důkazů to ale nikdy nenahradí.
date: '2026-09-27'
section: ai
type: analysis
depth: open
lang: cs
status: published
confidence: 88
load: 0
topics: []
edition_slot: 5
automation_generated: true
automation_role: edition
generator: chatgpt-work
event_id: evergreen-ai-answer-sampling-repeatability
image_query: abstract probability distribution tokens generative AI
image_alt: A field of possible word tokens branching into several paths
qma_path: ''
tickers: []
sources:
- name: Hugging Face Transformers — Generation strategies
  url: https://huggingface.co/docs/transformers/generation_strategies
  published: ''
- name: Google Research — Attention Is All You Need
  url: https://research.google/pubs/attention-is-all-you-need/
  published: '2017-06-12'
- name: 'NIST — Artificial Intelligence Risk Management Framework: Generative Artificial
    Intelligence Profile'
  url: https://doi.org/10.6028/NIST.AI.600-1
  published: '2024-07-26'
quiz:
  question: Co samo o sobě dokazuje jiná odpověď na stejné zadání?
  options:
  - Že druhá odpověď je přesnější
  - Že generování může jít po více než jedné věrohodné cestě
  - Že se model mezi oběma dotazy naučil nová fakta
  answer: 1
  explanation: Vzorkování a další změny v procesu generování mohou vést k jinému znění
    i k jiným závěrům. Přesnost ale pořád vyžaduje důkazy. Samotná odlišnost odpovědi
    neseřadí podle kvality.
---

## BRIEFLY

**Co se stalo.** Když se systému generativní umělé inteligence zeptáte dvakrát na totéž, můžete dostat dvě odpovědi, které se liší zněním, důrazem, nebo dokonce závěrem.

**Co to znamená.** Odpověď se obvykle skládá token po tokenu z rozdělení možností. Nevytahuje se jako uložená stránka. Uhlazená stálost proto není důkazem pravdy a odlišnost není důkazem selhání.

**Rizika a dopady.** Lidé mohou jeden plynulý výstup považovat za hotový fakt. Nebo mohou několik podobných výstupů brát jako nezávislé potvrzení, ačkoli všechny pocházejí ze stejného modelu a se stejnou mezerou v důkazech.

**Co se s tím dá dělat.** Uložit si zadání, důležitý kontext, verzi modelu nebo produktu a datum. Vyžadovat zdroje, které se dají zkontrolovat. A důležité úlohy testovat na příkladech se známou odpovědí.

**Na co se dívat dál.** Změny nástrojů, dohledaných dokumentů, systémových pokynů a verzí modelu mohou znamenat stejně mnoho jako viditelné znění. U rozhodnutí s vážnými důsledky ověřte tvrzení mimo model.

## FACTS

Moderní jazykové modely generují text postupně. Architektura Transformer, kterou v roce 2017 popsali výzkumníci z Googlu, umožnila v praxi vztahovat každou pozici v posloupnosti k okolnímu kontextu pomocí takzvané pozornosti. Při generování model přiřadí pravděpodobnosti možným dalším tokenům, jeden podle dekódovacího pravidla vybere, přidá ho do kontextu a celé to opakuje.

Dokumentace Hugging Face rozlišuje několik dekódovacích strategií. Hladové dekódování bere vždy nejpravděpodobnější další token. Vzorkování losuje z rozdělení pravděpodobností a může dávat pestřejší text. Paprskové hledání drží několik kandidátních posloupností a teprve pak mezi nimi vybírá. Produkty k tomu mohou přidávat skryté pokyny, výsledky vyhledávání, nástroje, bezpečnostní pravidla nebo paměť konverzace. Ne každé rozhraní tyto volby ukazuje.

„Stejné zadání“ proto vždy neznamená „stejné podmínky generování“. I při pevných podmínkách může nastavení založené na vzorkování jít jinou cestou. Při změněných podmínkách může jiný výsledek dát i deterministický dekodér. Žádný z těchto mechanismů nekontroluje, zda je výsledná věta pravdivá.

## EVIDENCE

Nejužitečnější je rozlišit **opakovatelnost** a **platnost**. Hladový dekodér v pevně daném softwarovém řetězci může svůj výstup věrně opakovat, protože pořád volí lokálně nejpravděpodobnější token. Běh se pak snáz reprodukuje, ale výstup se tím nestává důkazem. Vzorkující dekodér může ze stejné krajiny pravděpodobností vytvořit několik rozumných formulací. To pomáhá při brainstormingu, ale nesoulad mezi vzorky neřekne, které tvrzení je správné.

Profil rizik generativní umělé inteligence od amerického institutu NIST vysvětluje, proč kontrola faktů zůstává samostatným krokem. Popisuje „konfabulaci“ jako sebejistě podaný, ale nepravdivý nebo chybný obsah. A připomíná, že velké jazykové modely předpovídají další token ze statistických vzorců. Statisticky věrohodné pokračování tedy může být věcně špatně. NIST také varuje, že i vygenerované citace mohou být vymyšlené nebo zavádějící.

Praktický důsledek je trochu nepříjemný. Zeptat se modelu znovu není totéž jako hledat nezávislý zdroj. Deset běhů může sdílet stejné slepé místo z tréninku, stejné selhání při dohledávání nebo stejný nepodložený předpoklad. A naopak dvě různě formulované odpovědi mohou vyjadřovat tentýž dobře doložený fakt. Rozhodovat musí důkazy za tvrzením, ne počet hlasů mezi výstupy.

## PERSPECTIVES

Odlišnost není automaticky vada. Spisovatel může chtít alternativní začátky. Programátor může chtít několik implementací. Učitel může chtít vysvětlení na různých úrovních. Vzorkování může nabídku možností rozšířit. Uživatel je pak může porovnat s jasným zadáním.

Provozní práce potřebuje něco jiného. Když organizace používá generovaný text k třídění případů, k přípravě regulovaných dokumentů nebo v opakovaném pracovním postupu, nevysvětlitelné rozdíly mohou ztížit kontrolu i audit. Týmy pak mohou dávat přednost pevným formátům, zafixovaným verzím modelu, nastavení s menší proměnlivostí a sadám testů. Dokonale stálá chyba je ale pořád chyba.

Napětí nespočívá v abstraktním sporu „tvořivost proti spolehlivosti“. Jde o to, zda strategie generování odpovídá úkolu a zda samostatné vyhodnocení kontroluje vlastnost, na které záleží: věcnou přesnost, úplnost, tón, bezpečnost nebo reprodukovatelnost.

Poskytovatel může proměnlivost podávat jako tvůrčí rozpětí. Tým pro dodržování předpisů v ní může vidět ztrátu kontroly. Výzkumník v ní může vidět problém měření. Každý pohled zachytí něco skutečného, ale každý může zakrýt jinou slabinu. Rozpětí je užitečné jen tehdy, když někdo dokáže možnosti posoudit. Kontrola může zakonzervovat chybu. Měření se může odtrhnout od toho, co čtenář skutečně potřebuje. Společným požadavkem je vyhodnocení šité na konkrétní použití, ne jediné skóre, které systém prohlásí za obecně „dobrý“.

## CONTEXT

Běžná webová stránka má adresu a uložený obsah, i když ho vydavatel může aktualizovat. Vyhledávač hlavně dohledává a řadí dokumenty. Generativní asistent odpověď skládá. Mnoho současných produktů přitom skládání kombinuje s dohledáváním, kalkulačkami, nástroji na kód nebo osobním kontextem. Viditelný odstavec tak může být posledním krokem delšího, zčásti skrytého řetězce.

Takové hybridní uspořádání je užitečné, ale komplikuje srovnávání. Jeden běh může dohledat čerstvý dokument a jiný ne. Poskytovatel může model nebo jeho pokyny aktualizovat. Konverzace může obsahovat jiné dřívější zprávy. Odpověď na otázky o „současnosti“ může změnit i samotné datum v kalendáři.

Proto jsou snímky obrazovky s vytrženými výstupy slabým záznamem. Často na nich chybí zadání, zdroje, model, datum a předchozí kontext, bez kterých nelze pochopit, jak odpověď vznikla.

Další zmatek působí slovo *teplota*. V mnoha systémech mění, jak ostře nebo jak volně pravděpodobnosti ovlivňují vzorkování. Často se popisuje jako knoflík tvořivosti, ale to je jen zkratka. Nižší nastavení tvrzení neověří a vyšší nezaručí užitečnou původnost. Některé produkty toto nastavení vůbec nezpřístupňují. Jiné mohou požadavek uživatele upravit dřív, než se dostane k modelu.

Navíc jen zřídka známe celé rozdělení pravděpodobností za odpovědí ze vzdálené služby. To omezuje, co může vnější pozorovatel ze dvou výstupů vyvodit. Poctivý závěr bývá skromný: řetězec vytvořil tyto texty za podmínek, které jsme viděli. Proč zvítězila právě jedna cesta tokenů, může zůstat zčásti skryto.

## DEEPER

Lepší otázka nezní „Dokážu model přimět, aby říkal pokaždé totéž?“, ale „Jaké selhání by v tomhle úkolu vadilo a jak ho odhalím?“. Při vymýšlení nápadů může být cílem rozmanitost. U věcného podkladu záleží víc na dohledatelných zdrojích a přesných citacích. U strukturovaného pracovního postupu může být zásadní dodržení formátu a opakovatelnost. U rozhodnutí s vysokými sázkami by model neměl mít poslední slovo.

Tento posun mění i psaní zadání. Místo toho, abyste chtěli jen jistotu, určete laťku důkazů: oddělit známá fakta od úsudků, odkázat na původní záznam, uvést nejistotu a odmítnout odpověď, když zdroj chybí. Dobré zadání pravdu nezaručí, ale nepodloženou jistotu pak snáz poznáte.

Je v tom i širší poučení o nástrojích, které mluví celými větami. Plynulost smaže vzdálenost mezi výpočtem a rozhovorem. Slyšíme hlas tam, kde systém vytváří posloupnost, a instinktivně za ní hledáme ustálený záměr. Přirovnání ke „vzorku“ vrací trochu užitečného tření. Připomíná, že byla možná i jiná cesta, že pravděpodobnost není poznání a že čtenáře pořád čeká práce.

Ta práce není podezíravost pro podezíravost. Jde o volbu přiměřené důkazní laťky. Hravý slogan proměnlivost snese. Historické datum potřebuje zdroj. Lékařské, právní nebo finanční rozhodnutí potřebuje kvalifikovaný lidský úsudek a aktuální směrodatná doporučení. Čím víc může odpověď změnit něčí život, tím méně by o ní měla rozhodovat sebejistota na povrchu.

## REFLECT

Když se odpověď změní, na které části záleží: na znění, na doporučení, nebo na faktu pod ním?

Jaký nezávislý záznam by vám pomohl rozhodnout mezi dvěma věrohodnými výstupy?

Kdyby odpověď zůstala desetkrát stejná, co byste stejně museli ověřit?
