## Za pět minut

AI může připravit odpověď na poptávku. Oprávnění odeslat zákazníkovi cenu je jiná věc. Pro první firemní pokus dává smysl oddělit návrh od provedení: stroj připraví podklady, člověk zkontroluje příjemce, částku a přílohy. Náš návrh je začít u jedné činnosti a měřit i čas oprav. Rychle napsaný chybný e-mail je pořád chybný e-mail.

Toto vydání vychází z dokumentace tří dodavatelů. Nástroje jsme pro tuto ukázku neporovnávali v provozu a žádnou úsporu času zatím netvrdíme.

## Schválení patří před akci

**Co je doložené.** Power Automate nabízí akci „Start and wait for an approval“, která čeká na odpověď schvalovatele. n8n popisuje lidskou kontrolu jednotlivých nástrojů AI agenta: při zamítnutí se příslušná akce neprovede. [Microsoft](https://learn.microsoft.com/en-us/power-automate/get-started-approvals), [n8n](https://docs.n8n.io/build/integrate-ai/ai-examples/human-in-the-loop-for-tools.md)

**Co z toho plyne podle redakce.** Zpracování poptávky lze navrhnout ve dvou částech. První vytáhne zadání a připraví návrh odpovědi. Druhá smí odeslat e-mail až po kontrole. Stejnou brzdu lze požadovat před zápisem do CRM, tedy evidence zákazníků. Samotné potvrzovací tlačítko ovšem není důkazem správného zapojení.

**Co si ověřit.** Ukáže schvalovací krok přesného příjemce, celý text, částku a přílohy? Zastaví se odeslání při zamítnutí i tehdy, když nikdo neodpoví? Nemá agent jinou cestu k odeslání bez schválení? Dokumentace produktu sama odpovědi na tyto otázky ve vaší firmě nedává.

## Firemní tarif není univerzální povolenka pro data

**Co je doložené.** OpenAI uvádí, že firemní data standardně nepoužívá k trénování modelů; výslovné zapojení do sdílení dat může být výjimkou. Tento slib není tvrzení, že se data vůbec nezpracovávají nebo neukládají. [OpenAI](https://openai.com/enterprise-privacy/)

**Co z toho plyne podle redakce.** Před vložením skutečné poptávky je dobré pojmenovat, co v ní vlastně je. Veřejný katalog výrobků, neveřejný ceník a osobní údaje zákazníka jsou tři různé věci. Pro ukázku postupu stačí smyšlená firma a fiktivní dokument, který neobsahuje skutečné kontakty ani obchodní tajemství.

**Co si ověřit.** Který účet a tarif zaměstnanec používá? Jaké propojené aplikace dostávají obsah? Kdo má k výsledku přístup a jak dlouho se uchovává? Nejde o závěr o právní přípustnosti vašeho zpracování; ten závisí na konkrétních datech a podmínkách.

## Malý test, který nespolkne celý týden

Následující postup je **návrh redakce**, nikoli popis uskutečněného měření. Vyberte deset fiktivních poptávek. Číslo deset je velikost navrženého pokusu, ne statistický důkaz spolehlivosti. Zahrňte jasné zadání, chybějící termín, neznámou cenu a dokument, ze kterého se něco špatně čte.

U každého případu si zapište:

- čas přípravy běžným postupem;
- čas přípravy s AI včetně kontroly a oprav;
- chyby v příjemci, částce, termínu a přílohách;
- zda systém přiznal chybějící údaj;
- zda zamítnutá nebo nevyřízená žádost opravdu zabránila odeslání.

Úsporu počítejte jako rozdíl obou celkových časů. Pokud stroj připravuje návrh rychle, ale kontrola trvá déle než původní práce, výsledek není úspora. Jestli je výsledek dobrý jen u přehledných dokumentů, vymezte podle toho rozsah použití. Test na deseti případech není důvod pustit systém bez dozoru na všechny zákazníky.

## Co vzít na příští poradu

Jednu stránku se čtyřmi odpověďmi: která činnost se zkouší, kdo odpovídá za kontrolu, kde se postup zastaví a jak poznáme přínos. Nákup další licence může počkat, dokud nevíte, jaký problém má vyřešit.

V dalším vyhodnocení má cenu sledovat naměřený čas oprav, opakující se chyby a výsledek zamítnutých akcí. Ani hezký návrh odpovědi nezachrání automatizaci, která odešle jiný soubor, než člověk právě schválil.
