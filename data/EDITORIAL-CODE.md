# REDAKČNÍ KODEX A PRÁVNÍ POJISTKY

Tenhle soubor je závazný pro celou redakci — pro AI i pro tebe.
Kontrolní agent (`engine/prompts/guardian.md`) i pravidlové síto
(`engine/inbox.py`) z něj vycházejí. Když se rozhoduješ, jestli něco
vydat, rozhoduje tenhle text, ne dojem.

Nejsem právník a tohle není právní stanovisko. Je to soubor pravidel,
který drastricky snižuje riziko — ale než z webu uděláš byznys s příjmy,
nech si ho projít někým, kdo se v mediálním právu vyzná.

---

## 0. K ČEMU JE ČLÁNEK (nadřazené pravidlo)

Tohle stojí před vším ostatním v tomhle souboru, protože právní pojistky
řeší, co **nesmí** vyjít. Tenhle bod řeší, co **má cenu** vydat.

**Každý článek na tomhle webu musí mít přidanou hodnotu.**
Musí být praktický, zábavný, edukativní a napsaný čtivou formou.

- **Přidaná hodnota** — čtenář odchází s něčím, co neměl. Přepsaná
  agenturní zpráva bez vlastního vkladu sem nepatří.
- **Praktický** — aspoň jedna věc, kterou lze použít, ověřit,
  nebo podle ní rozhodnout.
- **Zábavný** — dočte to i ten, kdo nemusí. Obraz, příběh, přirovnání.
- **Edukativní** — vysvětluje, *jak to funguje*, ne jen *co se stalo*.
  Čtenář má potom rozumět i příští podobné zprávě.
- **Čtivý** — krátké věty, odstavce do 120 slov, žádný žargon bez
  vysvětlení, nikdy blahosklonně.

Tenhle test je nadřazený kvótám. Když se rubriku nedaří naplnit článkem,
který testem projde, zůstane ten den prázdná. Prázdná rubrika je menší
škoda než jeden odbytý text — ten totiž bere důvěru všem ostatním.

Kontrolní verze testu je v `engine/prompts/FORMAT.md`, oddíl 0.

---

## 1. CO NEVYJDE NIKDY (absolutní zákazy)

Tyhle věci nesmí projít ani se souhlasem člověka. Systém je zastaví.

**Nenávistné projevy.** Nic, co uráží, dehumanizuje nebo podněcuje
nenávist vůči lidem kvůli rase, etnicitě, národnosti, náboženství,
pohlaví, sexuální orientaci, věku nebo zdravotnímu postižení.
V EU je to trestné a v řadě států i osobní odpovědnost vydavatele.

**Podněcování k násilí.** Ani v nadsázce, ani „jen citujeme".

**Popírání zločinů proti lidskosti.** Popírání či zlehčování holokaustu
a genocid je v Německu, Rakousku, Francii, Česku a dalších zemích
trestný čin. Bez výjimky.

**Teroristická propaganda** a cokoli, co by mohlo sloužit jako návod
k útoku, výrobě zbraní, výbušnin nebo malwaru.

**Cokoli, co ohrožuje děti.** Žádný obsah sexualizující nezletilé,
žádné identifikovatelné děti bez souhlasu.

**Konkrétní obvinění jmenovaných osob bez pravomocného rozhodnutí.**
„X ukradl peníze" je žalovatelné. Píše se: „X čelí obvinění z…, které
odmítá" — a vždy s uvedením zdroje.

**Návody k útokům a podvodům.** V rubrice Bezpečně vysvětlujeme, jak
podvod poznat. Nikdy ne, jak ho spáchat.

---

## 2. KONSPIRAČNÍ TEORIE

Zásada je jednoduchá: **nikdy je nešíříme, ale mlčet o nich je taky
chyba.** Když o nich mlčí seriózní média, zůstane čtenář jen s tím
zdrojem, který mu je podává jako pravdu.

Proto o nich píšeme — ale vždycky metodou, které se říká
**„pravdivý sendvič"**:

```
1. PRAVDA     Začni tím, co je doloženo. Nikdy ne tvrzením.
2. TVRZENÍ    Až teď uveď, co koluje — jednou větou, bez obrazů,
              bez dramatizace, bez odkazu na zdroj, který to šíří.
3. PROČ TO NEPLATÍ   Konkrétní doklady, čísla, jména institucí.
4. PROČ TOMU LIDÉ VĚŘÍ   Tohle je nejdůležitější část. Za každou
              konspirací je skutečná obava — z ovládání, ze lži
              mocných, ze ztráty kontroly. Tu obavu pojmenuj vážně
              a s respektem. Kdo se cítí zesměšněný, změní názor nikdy.
5. PRAVDA ZNOVU   Skonči tím, co platí.
```

**Nikdy nedávej tvrzení do titulku.** Ani s otazníkem. Ani „prý".
Lidé si pamatují titulek, ne vyvrácení. Titulek musí obsahovat
to, co platí.

Nikdy se čtenáři nesměj. Nikdy nepiš „kdo tomu věří, je hlupák".

---

## 3. PODVODY NA LIDECH — pravidelná rubrika

Tohle je jedna z nejužitečnějších věcí, které web může dělat. Cíl:
**ušetřit lidem čas a peníze.** Formát „anatomie podvodu":

- ukaž skutečnou zprávu nebo webovou stránku (jména a čísla začerni)
- označ v ní jednotlivé signály a vysvětli každý
- vysvětli, **proč to psychologicky funguje** — spěch, autorita,
  stud, strach ze ztráty
- napiš, co dělat, když už člověk naletěl: koho volat, co zablokovat,
  kam podat oznámení
- nikdy nenaznačuj, že si za to oběť může sama

Nikdy neuváděj funkční odkazy na podvodné stránky.

---

## 4. PRÁVNÍ POJISTKY

**Autorská práva.** Cizí text jen ze zdrojů v `data/syndication.yml`,
vždy s uvedením autora a licence. Fotky jen public domain, CC0, CC BY
a CC BY-SA — vždy s autorem pod obrázkem. Nikdy fotku ze sociální sítě.

**Osobní údaje (GDPR).** Nezveřejňujeme adresy, rodná čísla, telefony,
zdravotní údaje ani fotografie soukromých osob. U obětí a nezletilých
nepoužíváme jména.

**Průhlednost o AI.** Na webu je uvedeno, že obsah vzniká s pomocí AI
a prochází kontrolou. To není slabina — je to podmínka důvěry a v EU
i směr, kterým jde regulace. Nikdy to netajíme.

**Zdraví.** Popisujeme, co ukazuje výzkum. Nikdy nedáváme diagnózu ani
léčebná doporučení. U citlivých témat uvádíme, kam se obrátit.

**Peníze.** Nikdy investiční doporučení. U finančních textů se připojuje
upozornění, že jde o vzdělávací obsah.

**Politika.** Popisujeme pozice, nefandíme. Před volbami v jakékoli zemi
platí zvlášť přísná zdrženlivost — a takové články nikdy nevycházejí
automaticky.

---

## 5. ČTENÁŘOVA DATA A PERSONALIZACE

Čtenář si tady sám nastavuje dvě věci: **rovnováhu čtení** (kolik toho
na něj web pustí a jak natvrdo) a **zájmy**, podle kterých se mu články
řadí. Obojí žije výhradně v jeho prohlížeči (`localStorage`). Web je
statický — žádný server, žádná databáze, žádné účty. Řazení dělá
prohlížeč sám nad veřejným seznamem článků, který je pro všechny stejný.
K nám se z toho nedostane nic.

**Zdravotní údaje.** To, co si čtenář naklikne ve skupině `health`
v `data/interests.yml`, jsou podle GDPR údaje zvláštní kategorie
(čl. 9). Naše obrana není procedurální, ale architektonická: ty údaje
nikdy neopustí zařízení, takže je nezpracováváme. Z toho plynou pravidla,
která se neporušují nikdy:

- nikdy nepřidat server, formulář, účet ani analytiku, která by tohle
  nastavení mohla přijmout
- nikdy je neposílat v přihlášce k newsletteru, v parametru adresy
  ani v hlášení o chybě
- kdyby někdy server přece jen byl potřeba, tenhle katalog se z něj
  vyřadí jako první
- zaškrtnuté políčko znamená „tohle mě zajímá", nikdy „tohle mám".
  Žádný text na webu neoslovuje čtenáře jako pacienta.

**Co personalizace nesmí dělat.**

- Nikdy neschovat zprávu proto, že si čtenář to téma nevybral.
  Personalizace mění pořadí, nic víc. Odfiltruje se jen téma, které
  čtenář výslovně ztlumil — a i tehdy se mu napíše, kolik zpráv je
  skrytých.
- **Pravidlo proti bublině.** Osobní stránka vždycky nese blok článků
  mimo čtenářův výběr a je označený jako záměr. Noviny, které ti jen
  přitakávají, jsou zrcadlo, ne noviny. Ve vlastní bublině si člověk
  připadá chytřejší a ví míň, a to je poslední věc, kterou mu chceme
  prodat.
- Nikdy neoptimalizovat na čas strávený na webu ani na kliky. Naše míra
  je, jestli čtenář odchází líp informovaný, ne jestli tu vydržel dýl.
- Nikdy nedovozovat citlivé věci z chování — zdraví, víru, politiku,
  sexualitu. Buď nám to čtenář řekne sám, nebo to nevíme.

**Zdravotní obsah v článcích.** Platí, co je v oddílu 4, a tady se to
zpřísňuje:

- popisujeme, co ukazuje výzkum — vždy s institucí, počtem účastníků
  a fází studie
- vždycky napíšeme i to, co se zatím neví
- nikdy diagnóza, nikdy doporučení léčby, nikdy dávkování
- článek, který se čtenáři ukázal kvůli zdravotnímu zájmu, nese stálou
  poznámku, že zdraví je tady téma, ne rada
- vždycky odkážeme na lékaře a na oficiální zdroje

**Rovnováha vydání.** Režim „vyváženě" omezuje, kolik těžkých článků na
čtenáře v jednom vydání spadne, aby se v tom neutopil. Tohle nesmí být
nikdy důvod něco změkčit nebo zahrabat. Strop mění pořadí a podobu,
nikdy ne to, co vyjde. Důležitá zlá zpráva vyjde vždycky — čtenář, který
si to tak nastavil, ji jen nejdřív uvidí jako klidné shrnutí a rozklikne
si ji, kdy bude chtít.

---

## 6. NOVINÁŘSKÁ PRAVIDLA

**Fakta a názor oddělené.** Vrstvy `FACTS` a `CONTEXT` jsou fakta.
Úvaha patří výhradně do `DEEPER` a musí být poznat, že je to úvaha.

**Vždy uveď zdroj.** Nejméně dva nezávislé u zpravodajství.

**Co nevíme, řekni.** „Zatím nepotvrzeno" je věta, která buduje důvěru.

**Právo na odpověď.** Když píšeme kriticky o konkrétním člověku nebo
firmě, uvedeme jejich vyjádření — a když je nemáme, napíšeme, že jsme
o ně požádali a nedostali je.

**Opravy zůstávají viditelné.** Chybu opravíme v textu, s datem
a poznámkou co bylo špatně. Tiché přepsání je lež s lepšími způsoby.

**Nezneužívej utrpení.** Žádné detaily kvůli detailům.

---

## 7. CO VŽDY ČEKÁ NA ČLOVĚKA

Tyhle články systém nikdy nevydá sám, ať si je jistý jakkoli:

- volby a předvolební kampaň v kterékoli zemi
- konkrétní obvinění jmenované osoby nebo firmy
- oběti násilí, sexuálního násilí a týrání
- počty mrtvých a raněných
- proroctví a výklad konce světa
- vše, co se dotýká dětí
- vyvracení konspirací (dokud se formát neusadí)

Nastaveno v `data/site.yml` → `editorial.always_review`.

---

## 8. KDYŽ SE PŘESTO STANE CHYBA

1. Opravit do hodiny, jakmile se o ní ví.
2. Nechat pod článkem poznámku: co bylo špatně, kdy opraveno.
3. Když šlo o konkrétní osobu, dát jí vědět.
4. Zapsat, proč to prošlo, a doplnit pravidlo, aby se to neopakovalo.

Rychlá a viditelná oprava je nejlepší obrana — právní i lidská.
