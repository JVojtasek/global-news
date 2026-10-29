# Ranní briefing e-mailem – příprava

Stav: návrh, rozesílání ani přihláška nejsou aktivní. Veřejný web je statický, newsletter.form_action je prázdné a v účtu Resend je založena subdoména updates.mypaper.news a prázdný segment My Paper — ranní briefing. DNS bylo přidáno 29. 10. 2026, Resend nyní uvádí verified; doručování ani odběr nebyly ověřeny.

## Návrh pilotu

Samostatný odběr pro e-mail s výběrem obecných rubrik, jazykem a časem doručení. Výběr musí vzniknout výslovně v přihlášce; existující nastavení čtení nepřenášet. Zdravotní zájmy z nastavení čtení nikdy neopouštějí zařízení a ani e-mailový formulář je nesmí shromažďovat. Nevybrané rubriky se neskrývají na webu.

Odběr vyžaduje ověření adresy potvrzovacím odkazem, změnu nastavení, odhlášení, evidenci stavu souhlasu a zpracování nedoručených adres. Denní vydání vybírá jen skutečně publikované články ve zvoleném jazyce; při nedostatku článků nevytváří smyšlený obsah. Odkaz na širší výběr doplní osobní výběr. Posílání má být odolné proti duplicitám po opakování úlohy.

## Před spuštěním

1. Ověřit vlastní účet poskytovatele, jeho cenu, limity a podmínky pro newslettery; nespoléhat na účet jiného projektu.
2. Ověřit odesílací doménu a doručitelnost včetně DNS, bez narušení existující pošty.
3. Připravit backend pro adresy a stav souhlasu, zabezpečit jeho přístup a zajistit správu, odstranění a obnovu dat.
4. Prověřit soukromí a pravidla přihlášky; oddělit veřejné tematické okruhy od zdravotních zájmů uložených v zařízení.
5. V izolovaném testu ověřit potvrzení, výběr témat, obsah, odhlášení, opakování běhu i doručení, teprve pak přihlášku zapnout.

Účet Resend je přístupný přes prohlížeč, ale nástroje konektoru nejsou dostupné. Doména updates.mypaper.news je podle rozhraní Resend ověřená. Její TXT a dva CNAME jsou v Cloudflare, bez změny existujících MX záznamů. Oddělený segment je prázdný. Nepřipojená přihláška a neexistující bezpečný backend znamenají, že rozesílání zatím nefunguje.

Zdroje k provozním omezením: https://developers.cloudflare.com/d1/reference/faq/ a https://resend.com/pricing.

## Ověření 29. 10. 2026

Místní `engine/email_preview.py` připravuje pouze náhled podle nezdravotních zájmů; nic neodesílá. Ve veřejném českém indexu byly za 28.–29. 10. tři články, dva bez tematických štítků. Výběr jen podle štítků proto nezaručí použitelný denní briefing. Je třeba dokončit odpovídající způsob řazení, odběrový backend, kontrolu souhlasu a odhlášení a otestovat doručení.

Místní náhled nyní podporuje volbu nezdravotních rubrik i zájmů. Při ověření na uloženém veřejném českém indexu za 28.–29. 10. 2026 našel pro rubriku Svět dva články. Nejde o přihlášku ani rozesílání; výběr rubrik nenahrazuje chybějící bezpečný backend.

Dřívější `infra/subscribe/src/index.js` nelze pro tento pilot jen zapnout: využívá jiné poskytovatele, při opětovném zaslání formuláře obnovuje odhlášený odběr a odpovídá úspěchem i bez doručení. Doplnit potvrzení vlastnictví adresy, samostatnou evidenci souhlasu a odhlášení, plánovač, ošetření duplicit i omezení provozu. Stávající služba zůstala beze změny.

## Rozpracovaná implementace

`infra/subscribe/src/newsletter-core.js` obsahuje izolovanou validační a stavovou logiku pro potvrzení a odhlášení, bez produkční databáze a bez skutečného odesílání. Test `infra/subscribe/test/newsletter-core.test.mjs` používá pouze simulované úložiště a e-mail. Ještě chybí atomický databázový adaptér, odesílání přes Resend, skutečné API a formulář, plánovač a test doručení; starý worker se nemá zapínat jako hotový odběr.

## Samostatný Neon 29. 10. 2026

Pro My Paper vznikla vlastní organizace na tarifu Free a samostatný projekt `mypaper-briefing` ve Frankfurtu. Je oddělený od projektu QMA a organizace INOVECTRO. Databáze je zatím prázdná a není připojená k odběru. Dřívější zmínka v `infra/README.md` o použití databáze QMA neplatí pro nové řešení. Přihlašovací údaje se nesmějí ukládat do repozitáře.

## Neon schéma 29. 10. 2026

V samostatném projektu `mypaper-briefing` v databázi `neondb` bylo vytvořeno schéma `briefing` se třemi prázdnými tabulkami subscribers, pending_confirmations a deliveries a příslušnými indexy. V databázi byla ověřena obě omezení seznamu rubrik a testovací pokus o uložení `health` byl odmítnut. Neexistuje produkční připojení, databázový adaptér, formulář ani odesílání.

## Pokračování implementace

Připraveny místní moduly `newsletter-worker.js`, `neon-store.js`, `newsletter-edition.js` a `newsletter-delivery.js`. Jejich testy používají simulované úložiště a odesílatele. Worker ani plánovač nejsou nasazeny, nejsou nastaveny přístupové údaje a neproběhla zkouška skutečného doručení. Před spuštěním zůstává nezbytné: ochrana veřejné přihlášky proti zneužití, ověření skutečného databázového adaptéru na izolovaném testu, propojení s formulářem, sestavení a naplánování odesílání, odhlášení a chybové stavy, testy reálného doručení a prověření soukromí. Implementace nesmí být považována za provozní jen na základě simulací.

## Aktuální stav přípravy

Předchozí odstavce zachycují průběžný stav. Formulář, ochrana Turnstile, adaptér Neon, plánovač a odhlašovací hlavičky jsou nyní připravené místně a ověřené simulovanými testy; bez konfigurace zůstávají vypnuté. V samostatném Neonu prošla zkouška potvrzení a odhlášení v transakci ukončené ROLLBACK a omezení rubrik brání uložení zdraví. Úspěšný test doručení do schránky, nasazení, připojení přístupů, zpracování nedoručených zásilek a bezpečné omezení společné kvóty Resendu zatím ověřené nejsou. Plánované automatické odesílání proto zůstává vypnuté. Testy neprokazují správnost DKIM podpisu výsledných hlaviček u skutečně doručeného e-mailu.

Cloudflare nyní obsahuje oddělený worker `mypaper-briefing-subscribe`, zatím pouze s úvodním příkladem. Resend má omezený odesílací klíč pro `updates.mypaper.news`, jeho uložení do workeru není dokončeno. V Neonu existuje tabulka `briefing.send_budget`; kód před každým pokusem o odeslání rezervuje jeden z maximálně 20 denních pokusů My Paper. Tento strop nesleduje využití jiných projektů a nezaručuje, že společný účet Resend nebude vyčerpán. Nedoručené zprávy, nasazení vlastního kódu a skutečná rozesílka zůstávají otevřené úkoly.

Aktualizace: worker nyní obsahuje sestavený kód briefingu a Resend klíč je v něm uložen jako Secret. Bez ostatních proměnných endpoint vrací HTTP 503 a automatické odesílání není zapnuto. Cloudflare Turnstile widget byl vytvořen pro mypaper.news, ale zatím není propojen s webem ani workerem. Databázové připojení se připravuje; skutečný koncový test a správa nedoručených e-mailů stále chybí.

Aktualizace po propojení: DATABASE_URL, RESEND_API_KEY, TURNSTILE_SECRET a UNSUBSCRIBE_SECRET jsou v Cloudflare uloženy jako šifrovaná tajemství; PUBLIC_WORKER_URL je běžná proměnná. Test neplatného potvrzovacího tokenu proti živému workeru vrátil HTTP 400 po databázovém dotazu, CORS předběžný požadavek HTTP 204 a neplatný Turnstile token HTTP 403. Cron spouštění po pěti minutách je nastaveno, ale vlastní odesílání je nadále vypnuto, protože ENABLE_DELIVERY není true. Přihláška na veřejném webu zatím není aktivní. Úspěšné potvrzení, doručení a odhlášení skutečného odběru nebyly prokázány. Limit 20 pokusů sdílený pro potvrzování a rozesílání nepostačuje pro neomezené denní odběry; je nutné dořešit kapacitu, provozní monitoring a zpracování nedoručených e-mailů.

Oddělení kvót: současný tým Resend používá i QMA a různé domény v týmu sdílejí kvótu. Na stránce vytvoření týmu je další tým označen jako placená funkce, takže nebyl založen. K prověření je samostatný bezplatný účet Brevo (podle poskytovatele 300 e-mailů denně, včetně potvrzení; nevyčerpaná kapacita se nepřenáší). Registrace, aktivace odesílání, ověření domény, podpora odhlášení, napojení, sledování chyb a skutečné doručení zatím nejsou dokončené. Na Brevo se nesmí přepnout jen na základě cenové stránky.

Brevo: založen oddělený účet na tarifu Free, jeho rozhraní ukazuje denní kvótu 300 zpráv. Dokončení vyžaduje telefonní ověření vlastníkem účtu. Lokální experimentální adaptér potvrzovací zprávy používá samostatnou navrženou subdoménu mail.mypaper.news, která zatím není u Breva ověřena; adaptér není připojen k workeru. Brevo podle dokumentace vkládá vlastní odhlašovací hlavičku, takže před spuštěním je nutné ověřit, že její použití skutečně zabrání dalšímu odesílání a že se stav odhlášení sladí s databází. Skutečné doručení ani aktivace rozesílky nejsou ověřené.

Aktualizace: vlastník dokončil telefonní ověření. V DNS byly se souhlasem doplněny ověřovací TXT a dva DKIM záznamy pro mail.mypaper.news, které Brevo potvrdilo; na subdoméně byl doplněn DMARC p=none bez reportovací adresy. Brevo požaduje i rua, proto je autentizace stále neúplná a čeká na souhlas s reporty. Klíč pro transakční e-mail je připraven v rozhraní, není vytvořen. Zpracování odhlášení a blokací na straně Breva se musí propojit s místní evidencí a ověřit v reálném provozu; samotný úspěch API požadavku není dokladem doručení. Automatická rozesílka zůstává vypnutá.

Další aktualizace: po souhlasu vlastníka je v DMARC doplněna reportovací adresa Breva, veřejný DNS resolver záznam vidí. Brevo při poslední kontrole hlásilo neúplnou autentizaci; může jít o propagaci. Generování omezeného klíče se zastavilo na jednorázovém kódu zaslaném vlastníkovi e-mailem. Místně je rozpracované přepnutí potvrzení a plánovače na Brevo pomocí MAIL_PROVIDER=brevo a jeho simulovaný integrační test prošel; do workeru nebylo nasazeno. Před ostrým provozem zůstává reálný test doručení a synchronizace odhlášení a blokací.

Aktuální stav: Brevo již potvrdilo autentizaci mail.mypaper.news a ověřilo odesílatele briefing@mail.mypaper.news. Náhradní omezený klíč je šifrovaně uložen v Cloudflare, původní klíč po nechtěném zobrazení ve výstupu deaktivován. Místní kód explicitně vyžaduje zvoleného poskytovatele, aby bez konfigurace nespadl na Resend; spuštění naplánované rozesílky zůstává vypnuto. Připraven a simulovaně testován samostatný modul zpracování událostí odhlášení a blokace, zatím bez autentizovaného webhooku a bez nasazení. Editor Cloudflare se opakovaně zastavil při načítání, takže poslední úpravy kódu nejsou nasazené. Skutečné doručení, odhlášení u poskytovatele a provozní omezení kapacity zůstávají neověřené.

## Ověření 29. 10. 2026 večer

Oddělený Cloudflare worker je nasazen s poskytovatelem Brevo a se zakázaným automatickým doručováním (`ENABLE_DELIVERY=false`). Ověřen skutečný test na soukromé schránce vlastníka: potvrzovací e-mail dorazil, potvrzení aktivovalo odběr, ručně spuštěná dávka doručila briefing s vybranými rubrikami a širším výběrem a odhlášení v těle zprávy fungovalo. Brevo webhook pro odhlášení, stížnosti a nedoručení je připojen a jeho doručenou událost potvrdila databáze. Dočasné testovací endpointy a přístupová tajemství byly po zkoušce odstraněny.

Databázová pojistka omezí pilot na 100 aktivních odběratelů; transakční test limitu prošel a testovací data byla vrácena. Jsou připraveny oddělené limity potvrzení (40) a briefingů (100) za den UTC. Veškeré uvedené testy automatického plánovače jsou simulované; skutečný ranní běh dosud ověřen nebyl. Soukromí a formulář jsou upraveny místně, ale veřejný formulář dosud nebyl zapnut. Zůstává prověřit opětovné přihlášení po odhlášení přes poskytovatele: Brevo může odesílatele zablokovat a samotný nový souhlas v databázi jeho blokaci nezruší. Do vyřešení tohoto stavu a ověření plného formuláře zůstává automatické zasílání vypnuté.
