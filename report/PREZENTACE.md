# Plán výsledkové stránky po jednotlivých otázkách

Tento dokument je návrh prezentace, ne implementace UI. Přesné popisky, pořadí odpovědí, počty, filtry a oba jmenovatele jsou v [kvantitativních datech](kvantitativni-data.md). Texty k publikaci jsou ve [výsledkovém reportu](VYSLEDKY.md). Nová stránka je může použít **bez přístupu k databázi**.

## Společná pravidla

- Pro rychlé čtení několik výrazných čísel, ale vždy s `počet / N`, otázkou a odkazem na celé rozdělení. **Žádnou otázku neredukovat natrvalo na osamocené procento.**
- Vodorovné sloupce od nuly jsou základ pro více kategorií a dlouhé české popisky. U vícevýběru třídění sestupně, při shodě stabilně podle formuláře. Poznámku „lze označit více možností“ neukrývat do nápovědy.
- U hodnoticích škál zachovat logické pořadí od kladných k záporným, ne třídění podle četnosti. Vhodný je jeden 100% skládaný pruh; nerozhodné odpovědi mají vlastní neutrální segment. U dlouhých popisků lze dát přednost samostatným sloupcům.
- Výchozí soubor jsou všechny platné odpovědi; dokončené lze zobrazit jako nenápadné kontrolní přepnutí. Vždy současně změnit N. Nevykreslovat je jako další nezávislou skupinu.
- U malých základen zvýraznit počty před procenty. Jeden respondent z 22 změní podíl přibližně o 4,5 bodu; graf nemá navozovat přesnost, kterou soubor nemá.
- „Nevím“, „nechci odpovědět“ a „téma teprve řešit budeme“ nezaměňovat. Nedopočítávat chybějící jako nesouhlas.
- Žádné koláče pro vícevýběr, slovní mraky pro volný text, demografické mikrofiltry ani bodová mapa jednotlivých příběhů. Počet slov není síla podpory tématu.
- Barva není jediný nositel informace; pod každým grafem zůstane přístupná tabulka a popisek se základem N. Počty se berou z Markdownu, procenta lze pro UI přepočítat ze stejných celočíselných základů, nikoli sčítat již zaokrouhlená procenta.

## Kvantitativní otázky – všech 31

`N` je počet platných odpovědí po filtru, `Nd` počet z dokončených dotazníků. Základ je platný pro tuto uloženou zálohu, ne univerzální konstanta komponenty.

| Klíč | Téma | N / Nd | Doporučené zobrazení | Hlavní interpretační pojistka |
|---|---|---:|---|---|
| a2 | Třebíč za deset let | 187 / 144 | Seřazené vodorovné sloupce všech pojmů; zvýraznit první skupinu | Nejvýše 3 volby, přání do budoucna není hodnocení současnosti. |
| b1 | Péče o centrum a památky | 175 / 144 | 100% škála spokojenosti + doplňkové číslo 117/175 spokojených | Ponechat 16 nerozhodných, neskrýt rozdíl velmi/spíše. |
| b2 | Co pomůže centru | 175 / 144 | Seřazené vodorovné sloupce + krátké textové doplnění | Nejvýše 3 volby; nevyřazovat „nevím“ ani „jiné“. |
| c1 | Prioritní záměry | 171 / 144 | Seřazený žebříček všech 11 možností; první tři zvýraznit | Nevybrání při limitu 3 není nesouhlas s opatřením. |
| d1 | Postoj k Dukovanům | 167 / 144 | 100% názorová škála, smíšené a nevyhraněné oddělit; 127/167 jako doplňkové číslo | Podmíněná pozitivní odpověď není bezvýhradný souhlas. |
| d2 | Dopady Dukovan | 167 / 144 | Seřazené vodorovné sloupce | Nejvýše 3 volby; obavy neinterpretovat jako předpovědi. |
| e1 | Způsoby pohybu | 161 / 144 | Vodorovné sloupce | Překrývající se uživatelé, ne podíl dopravy na všech cestách. |
| e2 | Motivace řidičů | 101 / 91 | Vodorovné sloupce; vizuálně přiznat i nenahraditelnost auta | Pouze řidiči; motivace a „nenahraditelné“ nejsou nutně oddělené skupiny. |
| e3a | Pěší problémy | 161 / 144 | Třísegmentový 100% pruh, doplňkově 86/161 alespoň občas | Všichni odpovídající na blok, ne jen lidé s chůzí v E1. |
| e4a | Cyklistické problémy | 22 / 22 | Tři malé sloupce s **počty 7 / 9 / 6**, procenta sekundárně | Pouze současní uživatelé kola/koloběžky; malý základ. |
| e8a | Prostor pro lidi místo části parkování | 161 / 144 | Pětisegmentová názorová škála; číslo 106/161 pro | Podpora „spíše“ je podmíněná lokalitou a alternativami. |
| e10 | Důležitost obchvatu | 161 / 144 | 100% škála důležitosti, doplňkové číslo 135/161 | Není to preference konkrétní trasy obchvatu. |
| f1a | Závažnost bydlení | 160 / 144 | 100% škála + číslo 102/160; neznalost stranou v neutrálním segmentu | Není objektivním indexem cenové dostupnosti. |
| f1b | Osobní/blízká zkušenost s bydlením | 160 / 144 | Tři vodorovné sloupce nebo 100% pruh | Vlastní problém oddělit od problému blízkých. |
| f3 | Bytová opatření | 109 / 97 | Seřazené vodorovné sloupce | Jen aktivní bytová větev; nejvýše 3 volby. |
| g0 | Děti v domácnosti | 157 / 144 | Vodorovné sloupce věkových kategorií a vedle číslo 73/157 s dětmi | 73 je sjednocení skupin, nikoli součet 35 + 34 + 26. |
| g1a | Dostupnost MŠ | 35 / 32 | Tři sloupce s počty, procenta druhotně | Přímá zkušenost 3 versus zprostředkovaná 8; pouze předškolní větev. |
| g1b | Základní školy | 34 / 31 | Vodorovné sloupce všech kombinovaných odpovědí | Není jednoduchá lineární škála ani žebříček škol; filtr vyřadil 2 odpovědi. |
| g1c | Střední školy | 51 / 46 | Vodorovné sloupce, počty vpředu | „Teprve řešit“ není „bez problémů“; filtr vyřadil 2 odpovědi. |
| g2 | Potřeby rodin | 73 / 67 | Seřazené vodorovné sloupce | Pouze rodiny s dětmi; pořadí první trojice je velmi těsné. |
| g3 | Prázdninová péče | 57 / 53 | Seřazené vodorovné sloupce | Zachovat i „nepotřebuji“ a odmítnutí role města; překryvy jsou možné. |
| j1 | Nedostupnost lékařů | 156 / 144 | Vodorovné sloupce, nejvýše jedna souhrnná karta o zubaři | Vlastní i blízká zkušenost; celkový problém nelze odvodit jako 100 % minus „nemám problém“. |
| j2 | Opatření pro lékařskou péči | 156 / 144 | Seřazené vodorovné sloupce | Nejvýše 3 volby; popularita opatření neprokazuje kompetenci města. |
| h1a | Spokojenost se sportem | 155 / 144 | 100% škála + číslo 108/155 spokojených | Nezájem o téma není nespokojenost. |
| h3 | Priority sportovních peněz | 155 / 144 | Seřazené vodorovné sloupce + doplňkové číslo 109/155 | Jedna volba, ne procentní rozdělení rozpočtu. |
| i1 | Pocit bezpečí | 155 / 144 | Čtyřsegmentová škála + doplňkové číslo 143/155 | Pocity nejsou policejní data; „spíše bezpečně“ neznamená bez problémů. |
| n1 | Gender | 149 / 144 | Malý 100% pruh nebo kompaktní tabulka | Pouze popis složení odpovídajících; bez křížení s názory. |
| n2 | Věk | 149 / 144 | Sloupce v přirozeném věkovém pořadí | Neřadit podle velikosti a nevytvářet populační váhy bez dalších dat. |
| n3 | Ekonomická situace | 149 / 144 | Vodorovné sloupce všech pěti původních možností v logickém pořadí | Napjatá a tíživá situace samostatně; malé počty ponechat, nepropojovat s jednotlivými názory. |
| n4 | Forma bydlení | 149 / 144 | Vodorovné sloupce všech sedmi původních možností | Družstevní byt, nájemní dům a jiné zachovat odděleně; jde o samostatné četnosti. |
| n5 | Část města | 149 / 144 | Tabulka všech 20 možností nebo vodorovné sloupce; **bez mapy intenzity** | Zachovat i malé a nulové počty; četnost účasti není četnost problémů v lokalitě. |

## Otevřené otázky a doplňky – všech 17

Pracovní soubory v podadresáři odpovědí obsahují úplné question-local parafráze, ne syrové citace. Jsou určeny k další redakci; veřejný web má použít souhrnný text, nikoli jednotlivé řádky. Nadpis „téma se objevilo“ je bezpečnější než „obyvatelé požadují“. Četnosti témat se bez úplného nového kódování nevyrábějí.

| Klíč | Textů | Forma veřejného zobrazení | Co nesmí při zkrácení zmizet |
|---|---:|---|---|
| a2-other | 1 | Jedna věta pod A2 | Konkrétní návrh na ostrůvky, ne nová procentní kategorie. |
| b2-other | 15 | Dva krátké odstavce pod B2 | Zeleň/stín, dopravní dostupnost i omezení aut, noční klid versus kultura. |
| c1b | 35 | Dva odstavce pod prioritami | Sídliště a hřiště, práce, různé varianty obchvatu a konkrétní menšinové nápady. |
| d2-other | 4 | Jeden krátký odstavec pod D2 | Kapacity služeb a období po skončení stavby. |
| e1-other | 2 | Jedna věta | Spolujízda; nerelevantní text netvoří kategorii. |
| e2-other | 6 | Krátký odstavec pod E2 | Regionální vazby a Brno, návaznost P+R a elektrobusů, komfort. |
| e3b | 50 | Dva odstavce + případně několik oddělených lokalizovaných podnětů | Povrchy, bezbariérovost, semafory, stín, konflikty na lávkách; bezpečnostní dojem není statistika. |
| e4b | 9 | Jeden až dva krátké odstavce | Propojenost a oddělení od provozu, školní stojany, úschova, dětská bezpečnost. |
| f3-other | 3 | Dvě věty pod F3 | Dostupnější stavební pozemky, ne zveřejnění osobního rozpočtu. |
| g2-other | 5 | Krátký odstavec | Duševní zdraví, inkluzivní kroužky, pestrost vzdělávání a hřišť. |
| g3-other | 3 | Krátký odstavec | Reálná dostupnost péče o prázdninách a spolupráce zřizovatelů. |
| j1-other | 7 | Jeden odstavec | Psychologie/psychiatrie, oční péče, kvalita a rozlišení běžné/specializované péče. |
| j2-other | 4 | Krátký odstavec | Kvalita, prostorové zázemí a pravomoci; neověřené návrhy označit. |
| h1b | 11 | Jeden až dva krátké odstavce | Zpřístupnění existujících kapacit, údržba, síť malých sportovišť a půjčování vybavení. |
| i2 | 5 | Velmi opatrné krátké shrnutí + omezení | Pocity/nepohoda versus uskutečněný incident; žádná stigmatizace a mapa kriminality. |
| l1 | 81 | Dva odstavce; maximálně několik tematických podnadpisů v detailu | Pobytové centrum, místní čtvrti, doprava, služby, osobité nápady i dvě pozitivní odpovědi. |
| l3 (L2) | 34 | Dva odstavce | Kvalita správy a služeb, WC/stín, doprava/sport, místní části, ocenění a ověřování tvrzení. |

## Jak z Markdownu postavit UI bez nového parsování databáze

1. V [kvantitativních datech](kvantitativni-data.md) má každá otázka stabilní kotvu odpovídající klíči. Tabulka obsahuje hodnotu, úplný popisek, počet a podíl pro hlavní i dokončený soubor. Metadata těsně nad tabulkou obsahují oba základy N, typ a filtr.
2. Seskupená headline čísla mají samostatnou tabulku `souhrnne-ukazatele`, včetně přesně uvedených vstupních hodnot. U G0 jde o sjednocení respondentů; výsledné 73 nelze získat prostým sečtením věkových kategorií.
3. [Výsledkový report](VYSLEDKY.md) je redakční vrstva: názvy bloků, vysvětlení, souhrny a upozornění. Z něj přebrat text, nikoli dodatečně generovat interpretaci jen z nejvyššího sloupce.
4. U všech otázek zachovat původní kategorie včetně nulových a malých četností. Souhrnné ukazatele mohou být nad tabulkou navíc, nikoli místo ní. Do klienta neposílat respondentové identifikátory ani řádková data „jen pro filtr“; případné nové průniky odpovědí vyžadují samostatné posouzení soukromí.
5. Při čistě stylistické revizi stačí přečíst příslušný soubor odpovědí a upravit souhrn. Nepotřebuje se databáze ani kontakty. Technické skripty a pracovní parafráze se na veřejný hosting nenasazují.

## Doporučené zlepšení pro místní komunitu

Vedle přehledu grafů přidat navazující, zřetelně **redakční** sekci „Podněty a další postup“. Pro vybrané konkrétní návrhy může obsahovat veřejné místo, povahu problému, kdo jej může ověřit a aktuální stav reakce. Například „chybějící osvětlení“, „návaznost autobusu“, „veřejná dostupnost areálu“ je pro komunitu použitelnější než obecné „zlepšit kvalitu života“.

Neuvádět autora, přesný čas podání ani demografii. V první fázi nepředstírat, že podněty byly místně ověřeny nebo že existuje schválené opatření. Rozdílné názory má stránka přiznat, nikoli vybrat jen ty, které se hodí k jedné předem stanovené variantě řešení.