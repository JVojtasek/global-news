# Naplánovaná Claude úloha — text k vložení

Tohle je ta část, která píše články z tvého předplatného, ne z API.
Běží v cloudu, takže nepotřebuješ mít zapnutý počítač.

---

## Krok 1: vyrob si přístupový token pro GitHub

Aby mohla úloha ukládat články do tvého repozitáře, potřebuje klíč.

1. Otevři <https://github.com/settings/personal-access-tokens/new>
2. **Token name:** `newsroom`
3. **Expiration:** `No expiration` (jinak ti to za rok tiše umře)
4. **Repository access:** `Only select repositories` → vyber svůj repozitář
5. **Permissions → Repository permissions → Contents:** nastav na `Read and write`
6. Klikni **Generate token** a zkopíruj si ho. Ukáže se jen jednou.

Ten token má přístup **jen k tomuhle jednomu repozitáři** a neumí nic
jiného než číst a zapisovat soubory. To je nejmenší možné oprávnění.

---

## Krok 2: vytvoř naplánovanou úlohu

V aplikaci Claude na počítači: **nová úloha → v pravém horním rohu vyber
„In the cloud" → napiš zprávu níž → pak v úloze zadej opakování každý den ráno.**

Do textu úlohy vlož tohle a nahraď dvě věci:
`UZIVATEL/REPOZITAR` a `TVUJ_TOKEN`.

---

```
Jsi šéfredaktor média My Paper. Tvoje dnešní směna:

1) Stáhni si redakci a přečti dnešní zadání:

   bash -c 'git clone --depth 20 https://x-access-token:TVUJ_TOKEN@github.com/UZIVATEL/REPOZITAR.git /tmp/newsroom 2>/dev/null || (cd /tmp/newsroom && git fetch -q origin && git reset --hard -q origin/main)'

   Pak si přečti tyhle soubory (jsou to tvoje pravidla, drž se jich doslova):
   - /tmp/newsroom/data/brief.md            ← co se má dnes napsat
   - /tmp/newsroom/data/memory/analyst-brief.md  ← co se v běžících tématech změnilo
   - /tmp/newsroom/engine/prompts/FORMAT.md ← v jakém formátu
   - /tmp/newsroom/engine/prompts/news_article.md
   - /tmp/newsroom/engine/prompts/feature_article.md
   - /tmp/newsroom/engine/prompts/analysis_article.md
   - /tmp/newsroom/engine/prompts/deep_article.md
   - /tmp/newsroom/engine/prompts/demand_article.md
   - /tmp/newsroom/engine/prompts/factcheck.md
   - /tmp/newsroom/engine/prompts/guardian.md
   - /tmp/newsroom/engine/prompts/sceptic.md

2) Napiš všechny články ze zadání. U každého článku postupuj takto:

   a) Napiš první verzi podle příslušného promptu (news_article.md
      nebo bible_article.md) a přesně podle FORMAT.md.
   b) U ČLÁNKU DNE navíc: projdi ji v roli KONTROLORA FAKTŮ podle
      factcheck.md a porovnej každé číslo, jméno a rok s podklady
      z `data/brief.json` → `daily_assignment.sources`. Cokoli, co
      v podkladech není, buď oprav podle nich, nebo z textu vyhoď.
      Nic si nedomýšlej.
   c) Projdi ji sám sebou v roli GUARDIAN podle guardian.md.
   d) Projdi ji sám sebou v roli SCEPTIC podle sceptic.md.
   e) Přepiš článek tak, aby zmizely všechny blokující připomínky.
   e) Do hlavičky nastav pole `confidence` na číslo 0-100 podle toho,
      jak si věříš. Buď přísný. Když je pod 82, nastav `status: review`
      místo `published` — člověk to pak zkontroluje.
   f) U zpravodajských článků MUSÍ být v hlavičce nejméně dva zdroje
      s funkčním odkazem, převzaté ze zadání.
   g) DODRŽ REŽIM `depth`, který je u každého zadání uvedený:
      `open` = závěrečná vrstva je obecně myšlenková a Bibli NESMÍŠ zmínit
               ani slovem (systém to kontroluje a takový článek zahodí)
      `scripture` = k té otázce přineseš i biblický text, ale jako jeden
               ze zdrojů moudrosti, nikdy jako autoritu ukončující debatu
   h) Vždy vyplň `image_query` — dvě až pět anglických slov, podle kterých
      se dá najít ilustrační fotka. Bez jmen žijících osob.

3) Ulož každý článek jako samostatný soubor do
   /tmp/newsroom/content/inbox/ pod názvem
   RRRR-MM-DD-kratky-nazev.md

4) Odešli hotovou práci:

   bash /tmp/newsroom/scripts/odesli.sh /tmp/newsroom

5) Napiš mi krátké shrnutí: kolik článků jsi napsal, u kterých sis
   nebyl jistý a proč, a jestli něco v zadání nedávalo smysl.

DŮLEŽITÉ:
- Nikdy nevydávej článek, který tvrdí, že konkrétní událost naplňuje
  proroctví. To je v tomhle projektu absolutní zákaz.
- Nikdy nekaž a nikdy nepiš, co si má čtenář myslet. Poslední vrstva
  se ptá, neodpovídá.
- Nikdy si nevymýšlej čísla, jména ani citace. Když něco nevíš, napiš
  do textu, že to není potvrzené.
- Nepřepisuj věty ze zdrojových článků. Fakta ano, formulace vlastní.
- Radši napiš méně článků a lépe.
```

---

## Jak se to spáruje s GitHubem

```
GitHub Actions (zdarma, každé 3 hodiny)
        │
        ├── posbírá zprávy z 50 zdrojů
        ├── sloučí duplicity do událostí
        ├── seřadí podle důležitosti
        └── zapíše data/brief.md      ← objednávka práce
                     │
                     ▼
Naplánovaná Claude úloha (z tvého předplatného, každé ráno)
        │
        ├── přečte objednávku
        ├── napíše články + zkontroluje je
        └── uloží do content/inbox/   ← odevzdaná práce
                     │
                     ▼
GitHub Actions (zdarma, každé ráno)
        │
        ├── prověří články podle pevných pravidel
        ├── vydá jeden delší článek ze zásoby
        ├── dohledá obrázky ve volných zdrojích
        ├── rozešle příspěvky na sociální sítě
        ├── postaví web
        └── vystaví ho na internet
```

Repozitář je ta společná zásuvka. Jedna strana do ní odkládá zadání,
druhá hotovou práci. Ani jedna nemusí být zrovna zapnutá.

---

## Když předplatné vypadne

Systém to pozná sám: v inboxu nic nepřibude, zásoba článků začne klesat.
Nastane jedno ze dvou:

- **Máš uložený API klíč** → GitHub si články dopíše sám a jede se dál.
- **Nemáš klíč** → web dál vydává ze zásoby, dokud nedojde
  (při 30 článcích v zásobě to je zhruba deset týdnů), a hlídač ti
  jednou týdně založí úkol na GitHubu, že něco není v pořádku.

Ani v jednom případě web nespadne a nikdy nevydá nezkontrolovaný nesmysl.
