# Dotazník — editovatelný zdroj obsahu

Tento soubor je **autoritativní zdroj textů** pro dotazník v `index.html`.
Pokud chcete změnit text otázky, možnost, intro, závěr atd., upravte to tady
a HTML se z toho vygeneruje (styly a JavaScript se nemění).

> Verze **v2** — přepracováno z brněnské verze (`dotaznik-trebic-v1.md`) pro
> **Třebíč**. Odstraněny otázky a projekty specifické pro Brno (tramvaje, SJKD,
> lanovka, ulice Veveří, brněnské části) a doplněna témata relevantní pro
> Třebíčsko: dostavba Dukovan, nedostatek lékařů, obchvat a historické centrum
> (UNESCO — bazilika sv. Prokopa a židovská čtvrť, Karlovo náměstí).

---

## Konvence formátu

> **Pravidlo č. 1:** Pokud si nejste jistí, zkopírujte existující otázku stejného
> typu a jen přepište texty. Ničemu jinému se nevyhnete.

### Blok = stránka

```
## BLOK X — NÁZEV BLOKU
```

Každý druhý nadpis úrovně `##` (kromě „ÚVOD", „ZÁVĚR", „PŘEHLED VĚTVENÍ"
a „TECHNICKÉ POZNÁMKY") představuje **jednu stránku** dotazníku.
Pořadí bloků v souboru = pořadí stránek v dotazníku.

Volitelně může blok začínat „vysvětlivkou" v blockquotu:
```
> *Vysvětlivka v dotazníku: ...*
```
— zobrazí se jako `<div class="block-note">` pod nadpisem bloku.

### Otázka

```
**X1. Text otázky.**
*(typ, parametry — volitelná podmínka)*

- možnost A
- možnost B
- jiné (s upřesněním)
```

- **Text otázky:** vždy `**Xn. ...**`. Identifikátor (`X1`, `e3a`, ...) je
  povinný a JS ho používá pro mapování dat. Z uživatelského pohledu je číslo
  na začátku skryto (JS ho strippuje).
- **Typ otázky** v kurzívě v závorce, dovolené hodnoty:
  - `radio` — jediná volba
  - `checkbox` — vícenásobná volba; lze přidat `max N` nebo `min N`
  - `volný text` — `<textarea>`
  - `rozbalovací menu` — `<select>` (jen N5)
  - `gateway` — checkbox/radio, který řídí viditelnost dalších otázek (G0)
- **Atributy** v té samé kurzívě, oddělené čárkou:
  - `volitelné` — otázka může zůstat nevyplněná (default je povinné u radio/select; volný text bývá většinou volitelný)
  - `povinné` — explicitní zvýraznění (zobrazí se hvězdička `*`)
  - `max N` / `min N` — pro checkbox
- **Podmínka zobrazení** — za pomlčkou v kurzívě:
  *„(checkbox, max 3 — zobrazí se, pokud F1a = velmi/spíše vážný)"*
  Popisná, lidsky čitelná. Závazná „strojová" podmínka je v tabulce
  **Přehled větvení** na konci souboru a v JS — pokud chcete větvení změnit,
  ozvěte se, je třeba upravit i JS.

### Možnosti (options)

Dva ekvivalentní zápisy:

1. **Seznam** (preferovaný pro delší texty):
   ```
   - dostupné nájemní bydlení
   - obnova historického centra
   ```
2. **Inline s `|`** (jen pro krátké stejnorodé volby):
   ```
   - živé | mladé | kulturní | jiné
   ```

Speciální položka **„jiné (s upřesněním)"** automaticky přidá textareu pro
volný text. Placeholder lze přepsat v sekci `## OTHER-INPUT PLACEHOLDERS`
na konci souboru.

### Inline follow-up

Některé otázky (E3b, E4b, H1b, I2) jsou „navazující" — zobrazují se uvnitř
karty hlavní otázky. V MD je píšeme jako samostatnou otázku těsně za hlavní,
s podmínkou v kurzívě. Generátor je rozpozná podle ID prefixu
(`e3a`→`e3b`, `e4a`→`e4b`, `h1a`→`h1b`, `i1`→`i2`).

---

## ÚVOD

*Stránka `page-intro`. Default je následující; alternativy podle `utm_source`
jsou definovány v JS v `INTRO_VARIANTS`.*

**Nadpis:** Jakou Třebíč chcete?
**Lead:** Co vás v Třebíči štve a co tu máte rádi?

Píšeme volební program Zelených pro komunální volby. Vaše odpovědi nám pomůžou program dolaďovat a budou se hodit i pro další práci v Třebíči. Když nám necháte e-mail, pošleme vám zajímavá zjištění z dotazníku i hotový program.

Vyplnění zabere asi 6 minut a je anonymní.

**Tlačítko start:** Vyplnit dotazník →
**Poznámka pod tlačítkem:** Pošlete prosím dotazník dál — čím víc odpovědí, tím přesnější program.

---

## BLOK A — TŘEBÍČ ZA 10 LET

**A2. Vyberte až 3 pojmy, které by měly vystihovat Třebíč ZA 10 LET.**
*(checkbox, max 3)*

- živé | mladé | kulturní | bohaté | klidné | bezpečné | zelené | čisté | cenově dostupné | inovativní | solidární | jiné (s upřesněním)

**A3. Co jsou silné stránky Třebíče — věci, které tu fungují dobře?**
*(volný text, volitelné)*

**A4. Co považujete za největší problémy Třebíče a co byste současnému vedení nejvíce vytknul/a?**
*(volný text, povinné)*

---

## BLOK B — HISTORICKÉ CENTRUM A PAMÁTKY

> *Vysvětlivka v dotazníku: Třebíč má dvě památky UNESCO — baziliku sv. Prokopa a židovskou čtvrť — a jedno z největších náměstí v Česku, Karlovo náměstí.*

**B1. Jak jste spokojen/a s tím, jak město pečuje o historické centrum a památky?**
*(radio)*

- velmi spokojen/a | spíše spokojen/a | spíše nespokojen/a | nespokojen/a | nedokážu posoudit

**B2. Co by historickému centru Třebíče nejvíc pomohlo?**
*(checkbox, max 3)*

- více obchodů, kaváren a služeb (oživení parteru)
- méně aut a parkování na náměstí, více prostoru pro lidi
- opravy fasád, ulic a veřejných prostranství
- kulturní akce a lepší využití památek
- lepší propojení centra, židovské čtvrti a baziliky
- podpora bydlení přímo v centru
- nevím
- jiné (s upřesněním)

**B3. Karlovo náměstí dnes z velké části slouží jako parkoviště. Uvítal/a byste, aby se větší část náměstí proměnila na prostor pro lidi (zeleň, posezení, akce)?**
*(radio)*

- rozhodně ano | spíše ano | spíše ne | rozhodně ne | nemám vyhraněný názor

---

## BLOK C — PRIORITY A VELKÉ PROJEKTY

**C1. Které tři záměry jsou pro vás jako obyvatele Třebíče nejdůležitější?**
*(checkbox, max 3, volitelné)*

- dokončení obchvatu města (silnice I/23) a odvedení tranzitní dopravy
- dostatek lékařů a zdravotní péče (praktici, zubaři, specialisté)
- dostupné nájemní bydlení
- obnova historického centra a památek UNESCO
- oživení Karlova náměstí a veřejných prostranství
- revitalizace nábřeží řeky Jihlavy a parků
- využití brownfieldů (např. areál Borovina) pro bydlení a služby
- rozvoj cykloinfrastruktury a bezpečných cest
- zkvalitnění a kapacita základních a středních škol
- kroužky, příměstské tábory a volnočasové aktivity pro děti
- rozvoj služeb pro seniory
- zvládnutí dopadů dostavby Dukovan na město

**C1b. Chybí v seznamu něco, co považujete za opravdu důležité?**
*(volný text, volitelné)*

**C2. Kde má Třebíč největší nevyužitý potenciál?**
*(volný text, volitelné — hint: „Co by mohlo fungovat lépe, ale zatím se to nedaří?")*

---

## BLOK D — DUKOVANY A ROZVOJ REGIONU

> *Vysvětlivka v dotazníku: V Dukovanech se připravuje stavba nových jaderných bloků. Je to jedna z největších staveb v ČR a výrazně ovlivní celé Třebíčsko — pracovní místa, bydlení, dopravu i veřejné služby.*

**D1. Jak vnímáte plánovanou dostavbu jaderné elektrárny Dukovany?**
*(radio)*

- jednoznačně pozitivně — je to příležitost pro region
- spíše pozitivně, ale záleží na zvládnutí dopadů
- mám smíšené pocity
- spíše negativně
- jednoznačně negativně
- nemám vyhraněný názor

**D2. Čeho se v souvislosti s dostavbou Dukovan nejvíce obáváte nebo co by mělo město ohlídat?**
*(checkbox, max 3)*

- tlak na ceny a dostupnost bydlení (příliv pracovníků)
- přetížení dopravy a stav silnic
- kapacita škol, školek a zdravotní péče
- dopady na životní prostředí a krajinu
- aby z toho region a město reálně profitovaly (peníze a práce pro místní)
- bezpečnost
- nic zásadního mě netrápí
- jiné (s upřesněním)

**D3. Jak by podle vás mělo město využít příležitost spojenou s rozvojem Dukovan?**
*(volný text, volitelné)*

---

## BLOK E — DOPRAVA A VEŘEJNÝ PROSTOR

**E1. Jakými způsoby se pravidelně pohybujete po Třebíči?**
*(checkbox, vícenásobný výběr)*

- autem (jako řidič/ka)
- MHD (městské autobusy)
- na kole nebo koloběžce
- pěšky (jako hlavní způsob pohybu, nejen přesun na zastávku)
- jinak (s upřesněním)

**E2. Co by vás motivovalo jezdit autem méně nebo ho omezit?**
*(checkbox, vícenásobný výběr — zobrazí se, pokud E1 obsahuje „autem")*

- lepší a častější spoje MHD (frekvence, přímé linky)
- bezpečnější a lépe propojená cykloinfrastruktura
- více záchytných parkovišť na okraji města (P+R)
- lepší sdílená mobilita (sdílená kola, koloběžky, auta)
- nic — auto je pro mě nenahraditelné
- jiné (s upřesněním)

**E3a. Setkáváte se při pohybu pěšky v Třebíči s problémy?**
*(radio)*

- ano, pravidelně | občas | ne

**E3b. S jakými problémy se nejčastěji setkáváte, případně kde?**
*(volný text, volitelné — zobrazí se, pokud E3a = „ano" nebo „občas"; inline follow-up u E3a)*

**E4a. Setkáváte se při jízdě na kole nebo koloběžce s problémy?**
*(radio — zobrazí se, pokud E1 obsahuje „kolo nebo koloběžku")*

- ano, pravidelně (chybějící pruhy, nebezpečná místa, chybějící stojany…)
- občas
- ne

**E4b. S jakými problémy se nejčastěji setkáváte, případně kde?**
*(volný text, volitelné — zobrazí se, pokud E4a = „ano" nebo „občas"; inline follow-up u E4a)*

**E8a. Některá města rozšiřují chodníky, přidávají zeleň, lavičky a místa k posezení namísto části parkovacích míst. Jak byste přijal/a takovou přeměnu a rozšíření pěších zón v centru Třebíče?**
*(radio)*

- rozhodně pro — ulice by měly sloužit lidem, ne parkujícím autům
- spíše pro, záleží ale na konkrétní části města a dostupnosti alternativ
- spíše proti — obávám se dopadů na dostupnost centra
- rozhodně proti — parkovací místa v centru je nutné zachovat
- nemám vyhraněný názor

**E10. Mělo by město aktivně regulovat vizuální smog v Třebíči — billboardy, neuspořádané reklamy, plachty a výlohy, které narušují vzhled ulic?**
*(radio)*

- rozhodně ano | spíše ano | spíše ne | rozhodně ne | nepřemýšlel/a jsem o tom

**E11. Třebíčí denně projíždí tranzitní doprava. Jak důležité je pro vás dokončení obchvatu města?**
*(radio)*

- velmi důležité | spíše důležité | spíše nedůležité | vůbec ne | nemám vyhraněný názor

---

## BLOK F — BYDLENÍ

> *Vysvětlivka v dotazníku: Dostupností bydlení máme na mysli dvě věci — jestli v Třebíči jde sehnat byt, který vám vyhovuje, a jestli se dá z běžného příjmu zaplatit.*

**F1a. Jak vážný problém je podle vás dostupnost bydlení v Třebíči?**
*(radio)*

- velmi vážný | spíše vážný | spíše ne | vůbec ne | nemám přehled

**F1b. Řešíte vy nebo někdo z vašich blízkých problém s bydlením v Třebíči — ať už to je shánění bytu, nebo problém ho zaplatit?**
*(radio)*

- přímo já
- ano, někdo z mých blízkých
- ne, osobně se mě netýká

**F3. Co by město mělo dělat pro zvýšení dostupnosti bydlení?**
*(checkbox, max 3 — zobrazí se, pokud F1a = velmi/spíše vážný NEBO F1b = přímo já / blízkých)*

- stavět vlastní nájemní byty
- více využít prázdné byty ve vlastnictví města
- podporovat družstevní výstavbu
- podmínit větší developerské projekty podílem dostupných bytů
- využít brownfieldy a opuštěné areály pro bydlení
- regulovat výši nájmů v obecních bytech
- nevím
- jiné (s upřesněním)

---

## BLOK G — RODINY A DĚTI

**G0. Máte doma dítě či děti do 18 let?**
*(gateway, checkbox, povinné — vícenásobný výběr; větví celý blok G)*

- ano, předškolního věku
- ano, na základní škole
- ano, na střední škole
- ne
- nechci odpovědět

> *Pokud G0 obsahuje aspoň jedno z „ano…", zobrazí se relevantní podotázky.
> Volby „ne" a „nechci odpovědět" jsou mutual-exclusive s ostatními.*

**G1a. Zaznamenali jste problémy s dostupností míst ve školce v Třebíči?**
*(radio — zobrazí se, pokud G0 obsahuje „předškolního věku")*

- ano, přímo u nás | ano, v okolí nebo u známých | ne

**G1b. Jak hodnotíte dostupnost a kvalitu základních škol ve vaší části Třebíče?**
*(radio — zobrazí se, pokud G0 obsahuje „na základní škole")*

- jsem spokojený/á s dostupností i kvalitou
- kapacita je dobrá, ale kvalita škol se liší
- mám problém najít vhodnou školu v dosahu
- jsem nespokojen/á — kapacita i kvalita jsou problém
- nedokážu posoudit

**G1c. Narazili jste vy nebo vaši blízcí na problém s nabídkou nebo kapacitou středních škol v Třebíči (ať už při hledání pro vlastní dítě, nebo v okolí)?**
*(radio — zobrazí se, pokud G0 obsahuje „na základní škole" nebo „na střední škole")*

- ano, přímo u nás | ano, v okolí nebo u známých | ne | téma teprve řešit budeme

**G2. Co pro rodiny s dětmi v Třebíči nejvíce chybí nebo potřebuje zlepšit?**
*(checkbox, vícenásobný výběr)*

- dostatečná kapacita cenově dostupných jeslí, školek a dětských skupin
- kapacita a kvalita základních škol
- nabídka a kapacita středních škol
- dětská hřiště a bezpečné veřejné prostory
- bezpečné cesty do školy (chodníky, přechody, cyklostezky)
- kroužky, zájmové a volnočasové aktivity pro děti
- dostupnost lékařské a psychologické péče pro děti
- podpora rodin v bytové nouzi nebo s vysokým nájmem
- jiné (s upřesněním)

**G3. Jak město může nejlépe pomoci rodinám s péčí o děti během školních prázdnin?**
*(checkbox — zobrazí se, pokud G0 obsahuje „předškolního věku" nebo „na základní škole")*

- finanční příspěvek na tábory v přírodě a příměstské tábory
- příměstské tábory pořádané přímo městem nebo jeho organizacemi
- rozšíření školních družin a klubů v době prázdnin
- přehledná databáze dostupných táborů a aktivit v Třebíči
- nepotřebuji v tomto ohledu pomoc — péči mám zajištěnou
- město by se tím zabývat nemělo
- jiné (s upřesněním)

---

## BLOK J — ZDRAVOTNÍ PÉČE

> *Vysvětlivka v dotazníku: Na Třebíčsku dlouhodobě chybí lékaři — praktici, zubaři, dětští i odborní lékaři.*

**J1. Máte vy nebo vaši blízcí problém sehnat v Třebíči lékaře?**
*(checkbox, vícenásobný výběr)*

- praktický lékař pro dospělé
- zubař
- dětský lékař
- odborný lékař / specialista
- nemám problém — péči mám zajištěnou
- jiné (s upřesněním)

**J2. Co by podle vás mělo město dělat pro zlepšení dostupnosti lékařské péče?**
*(checkbox, max 3)*

- nabízet lékařům dostupné bydlení nebo ordinace (např. obecní prostory)
- finanční pobídky a stipendia pro nové lékaře
- podpora a rozvoj nemocnice
- zajištění lékařské i zubní pohotovosti
- lepší koordinace s krajem a zdravotními pojišťovnami
- nevím
- jiné (s upřesněním)

---

## BLOK H — SPORT A VOLNÝ ČAS

**H1a. Jak hodnotíte v Třebíči podmínky pro amatérský sport a běžný pohyb (běh, kolo, plavání, hřiště, sportovní areály pro veřejnost, tělocvičny)?**
*(radio)*

- spokojen/a | spíše spokojen/a | spíše nespokojen/a | nespokojen/a | toto téma mě nezajímá

**H1b. Jaká sportoviště nebo místa pro volný čas a v jaké části Třebíče byste uvítali?**
*(volný text, volitelné — zobrazí se, pokud H1a = spíše nespokojen/a nebo nespokojen/a; inline follow-up u H1a)*

**H3. Peníze, které dává město na sport, by měly přednostně směřovat na:**
*(radio)*

- běžná sportoviště pro veřejnost
- podporu mládežnického a amatérského sportu (kluby, oddíly, kroužky)
- podporu profesionálních sportovních klubů
- velké projekty (sportovní haly a stadiony)
- reprezentativní vrcholné akce
- nemám vyhraněný názor

---

## BLOK I — BEZPEČNOST

**I1. Cítíte se v Třebíči bezpečně?**
*(radio)*

- naprosto bezpečně | spíše bezpečně | spíše nebezpečně | velmi nebezpečně

**I2. Co je hlavním zdrojem pocitu nebezpečí nebo nepohody? Máte na mysli konkrétní místo?**
*(volný text — zobrazí se, pokud I1 = spíše nebezpečně nebo velmi nebezpečně; inline follow-up u I1)*

---

## BLOK K — CELOSPOLEČENSKÝ POHLED

**K2. Jak velký vliv má celostátní politická situace na to, koho zvolíte do třebíčského zastupitelstva?**
*(radio)*

- velký — komunální volby vnímám v kontextu celostátního dění
- částečný — záleží mi na obou rovinách
- žádný — komunální a celostátní politiku striktně odděluji
- nevím

**K1. Které z následujících jevů vás osobně znepokojují?**
*(checkbox, max 3 — zobrazí se, pokud K2 ≠ „žádný")*

- oslabování demokracie a právního státu v ČR
- geopolitická nestabilita a nárůst autoritářství
- korupce a klientelismus ve veřejné správě
- zdražování, inflace a růst nákladů na bydlení
- války a násilí ve světě
- klimatická změna a extrémní výkyvy počasí
- extremismus a polarizace české společnosti
- migrace
- žádné z výše uvedených výrazněji
- jiné (s upřesněním)

---

## BLOK L — TŘEBÍČ OSOBNĚ

**L1. Co si v Třebíči ze všeho nejvíce přejete?**
*(volný text, volitelné)*

**L2. Co se v Třebíči v žádném případě nesmí stát?**
*(volný text, volitelné)*

**L3. Máte nějaký vzkaz nebo téma, které se v dotazníku neobjevilo?**
*(volný text, volitelné)*

---

## BLOK N — O VÁS

> *Tyto otázky jsou statistické. Dotazník je anonymní — nikde nesbíráme jméno ani kontakt (pokud jej sami nezadáte na závěr).*

**N1. Jsem:**
*(radio)*

- muž | žena | jiné | nechci odpovědět

**N2. Věková skupina:**
*(radio)*

- 18–24 | 25–34 | 35–44 | 45–54 | 55–64 | 65+

**N3. Jak byste popsal/a svoji aktuální ekonomickou situaci?**
*(radio)*

- pohodlná — vychází mi peníze, mohu spořit a mám rezervy
- přiměřená — vychází mi, ale na spoření nebo rezervy nezbývá
- napjatá — příjmy pokryjí základní výdaje, ale nic navíc
- tíživá — mám problém pokrýt i základní výdaje
- nechci odpovědět

**N4. Bydlím v:**
*(radio)*

- vlastním bytě | nájemním bytě | družstevním bytě | vlastním domě | nájemním domě | jiné | nechci odpovědět

**N5. Část Třebíče, kde bydlím**
*(rozbalovací menu — placeholder: „— Vyberte část Třebíče —")*

- **Centrální části:** Vnitřní Město | Stařečka | Jejkov | Podklášteří | Zámostí (židovská čtvrť) | Nové Dvory
- **Ostatní části:** Horka-Domky | Borovina | Týn | Nové Město | Kočičina | Hájek | Budíkovice | Pocoucov | Ptáčov | Račerovice | Řípov | Slavice | Sokolí | bydlím mimo Třebíč

**N6. Koho jste volili v posledních sněmovních volbách (2025)?**
*(radio, volitelné)*

- SPOLU (ODS, TOP09, KDU-ČSL)
- ANO
- Piráti + Zelení
- STAN
- SPD
- Motoristé sobě
- STAČILO
- jiná strana
- nevolil/a
- nepamatuji si
- nechci odpovědět

---

## ZÁVĚR

*Stránka `page-end` — co uživatel vidí před odesláním.*

**Nadpis:** Chcete vědět, jak Třebíčané a Třebíčanky odpověděli a jaký program z dotazníku vznikne?

**E-mail input placeholder:** vas@email.cz

**Souhlas (checkbox, volitelný):** Chci zaslat zajímavá zjištění z dotazníku i náš hotový program — bez spamu.

**Tlačítko odeslat:** Odeslat dotazník →

> *Po odeslání se zobrazí poděkování + sdílecí tlačítka (Facebook, Messenger, WhatsApp, Zkopírovat odkaz) + odkazy na sociální sítě Zelených + CTA „Mám zájem pomoct v kampani" — celá tato post-submit obrazovka je generovaná v JS (funkce `doSubmit()`), nikoli z tohoto MD.*

---

## NAVIGACE A SYSTÉMOVÉ TEXTY

| Klíč | Text |
|---|---|
| Zpět | ← Zpět |
| Pokračovat | Pokračovat → |
| Scroll hint | ↓ Posuňte dolů pro další otázky |
| Validační chyba | Prosím vyplňte označená pole. |
| Logo v hlavičce | (prázdné) |

---

## OTHER-INPUT PLACEHOLDERY

*Pro otázky s volbou „jiné (s upřesněním)". Pokud chybí, použije se default „Upřesněte…".*

| Otázka | Placeholder |
|---|---|
| A2 | Upřesněte… |
| B2 | Upřesněte… |
| D2 | Upřesněte… |
| E1 | Jak jinak? |
| E2 | Upřesněte… |
| F3 | Upřesněte… |
| G2 | Upřesněte… |
| G3 | Upřesněte… |
| J1 | Upřesněte… |
| J2 | Upřesněte… |
| K1 | Upřesněte… |

---

## PŘEHLED VĚTVENÍ

*Pokud chcete změnit podmínku zobrazení nebo přidat nové větvení, je potřeba
upravit i JavaScript v `index.html` (sekce „Branching logic"). Texty otázek
lze měnit bez zásahu do JS.*

| Otázka | Podmínka zobrazení |
|---|---|
| E2 | E1 obsahuje „autem" |
| E3b | E3a = „ano" nebo „občas" |
| E4a | E1 obsahuje „kolo nebo koloběžku" |
| E4b | E4a = „ano" nebo „občas" |
| F3 | F1a = velmi/spíše vážný **nebo** F1b = přímo já / blízkých |
| Blok G (G1a–G3) | G0 obsahuje aspoň jedno z „ano…" |
| G1a | G0 obsahuje „předškolního věku" |
| G1b | G0 obsahuje „na základní škole" |
| G1c | G0 obsahuje „na základní škole" nebo „na střední škole" |
| G3 | G0 obsahuje „předškolního věku" nebo „na základní škole" |
| H1b | H1a = spíše nespokojen/a nebo nespokojen/a |
| I2 | I1 = spíše nebezpečně nebo velmi nebezpečně |
| K1 | K2 ≠ „žádný" |

---

## TECHNICKÉ POZNÁMKY

- **Identifikátory otázek** (`a2`, `e3a`, `n5` …) se v HTML používají jako
  `name`/`id` atributy. Při ukládání odpovědí slouží jako klíče v JSONu.
  Změnou textu otázky se identifikátor **nemění** — zůstává v HTML.
- **Hodnoty `value`** u možností (např. `value="dostupné nájemní bydlení"`) se
  ukládají do databáze. Pokud změníte text možnosti, generátor se snaží
  hodnotu zachovat (mapuje podle pořadí v rámci otázky), aby nezlomil
  data již sebraných odpovědí. Pro úplné přejmenování smažte záznamy
  v `value-map.json` (vytvořeno generátorem).
- **Volný text „jiné"** se ukládá pod `*-other` (např. `a2-other`, `k1-other`).
- **Multiselect** odpovědi jsou pole stringů, `radio` jediný string.
- **UTM parametry** (`utm_source`, `utm_medium`, `utm_campaign`,
  `utm_content`, `utm_term`) se sbírají automaticky z URL při prvním
  načtení a posílají s daty.
- **Průběžné ukládání:** po každém přepnutí stránky se POSTuje aktuální
  stav na `/save.php` (status `partial`); po finálním odeslání `complete`.
- **Anonymita:** identifikátor respondenta je UUID v `localStorage`,
  nikoliv osobní údaj. E-mail je dobrovolný a sbírá se jen se souhlasem.
- **Intro varianty** podle `utm_source` jsou v JS v `INTRO_VARIANTS`.
  Default přepisuje až tehdy, když je daná varianta neprázdná.
