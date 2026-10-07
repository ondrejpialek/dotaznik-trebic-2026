# Metodika a ochrana soukromí

## Účel a hranice výsledků

Výstup popisuje odpovědi v dobrovolné internetové anketě k životu v Třebíči, nikoli reprezentativní průzkum obyvatel. Dotazník vznikl pro přípravu komunálního programu; samovýběr a způsob šíření mohou složení odpovědí ovlivnit. Nevážíme data na populaci, neuvádíme výběrovou chybu ani intervaly spolehlivosti a nepíšeme „Třebíčané si myslí“, pokud tím míníme pouze účastníky ankety.

Jednotkou je **uložený dotazník**, ne ověřená unikátní osoba. Identifikátor prohlížeče omezuje opakované uložení, ale nezaručuje jednoho člověka na jeden záznam. Shodné jednotlivé odpovědi nejsou důvodem k mazání. Databáze se otevírá výhradně pro čtení; žádné záznamy se neupravují ani nemažou.

## Co zahrnujeme

- Hlavní výsledek každé otázky zahrnuje platné odpovědi z dokončených i rozpracovaných dotazníků. Nevyřazujeme užitečný podnět jen proto, že člověk nedošel na konec.
- Vedlejší sloupce ukazují stejné výpočty pouze z dokončených dotazníků. Jde o kontrolu citlivosti, ne druhý nezávislý vzorek.
- Jmenovatelem procent je počet dotazníků s platnou odpovědí **na danou otázku a v její příslušné větvi**. U každé otázky je uveden zvlášť.
- U vícevýběru počítáme dotazníky, které označily možnost, ne podíl ze všech zaškrtnutí. Součet procent může překročit 100 %. Počet označení nepředstavuje pořadí uvnitř jednoho dotazníku.
- „Nevím“, „nemám přehled“, neutrální odpověď a „nechci odpovědět“ zůstávají platnými kategoriemi. Chybějící odpověď není nesouhlas ani nula.
- Výběr „jiné“ zůstává samostatnou kvantitativní kategorií. Volný text nepřepočítáváme zpětně do nabízených voleb.
- Procenta zaokrouhlujeme na jedno desetinné místo až při zobrazení, při přesné polovině směrem nahoru. Součet se může kvůli zaokrouhlení mírně lišit od 100 %. Pro další výpočty slouží celočíselné počty a jmenovatele.

## Větvení a validace

Zdroj znění, pořadí a nabízených možností je skutečný HTML formulář, nikoli starší slovník administrace. Druhá osobní otevřená otázka je ve formuláři označena L2, ale její uložený klíč je `l3`; výstupy zachovávají oba údaje.

Podmínky: E2 pouze pro řidiče; E4a a E4b pouze pro uživatele kola/koloběžky; E3b a E4b pouze při pravidelných či občasných problémech; F3 při závažném hodnocení bydlení nebo osobní/zprostředkované zkušenosti s problémem; G2 pro domácnosti s dětmi; G1a pro předškolní děti, G1b pro děti na ZŠ, G1c pro děti na ZŠ/SŠ, G3 pro předškolní děti nebo ZŠ; H1b při nespokojenosti se sportovními podmínkami; I2 při pocitu nebezpečí. Text „jiné“ se zahrne pouze při aktivní odpovídající volbě a splněném filtru rodičovské otázky.

Formulář některé již zadané hodnoty při skrytí větve nemaže. Proto nestačí přítomnost položky v databázi: odpovědi mimo aktuálně platnou větev se vykazují odděleně a nezařazují do výsledku. Kontroluje se typ hodnoty, známé možnosti, opakované volby a maximum výběru. Logicky napjaté kombinace typu „nemám problém“ spolu s konkrétním problémem se označí v kontrole dat, ale bez důkazu chyby se svévolně neopravují.

## Otevřené odpovědi: pracovní podklad versus veřejný text

Pro každé ze 17 textových polí vzniká samostatný redakční podklad. Každá zařazená odpověď má vlastní **parafrázi**, případně poznámku, že neobsahuje věcný podnět. Číslování je místní pro danou otázku, nikoli identifikátor člověka; pořadí neodpovídá času odeslání. Mezi otázkami není zveřejněn žádný spojovací klíč. Stejné podněty se zachovají odděleně, pokud pocházejí z různých uložených odpovědí.

Odstraňují se kontakty, jména osob, podpisy, odkazy na osobní profily, čísla domů, zaměstnavatelé či konkrétní osobní vazby a kombinace rodinných, zdravotních, pracovních či časových okolností, podle kterých by šlo člověka poznat. Popis osobního příběhu se mění na obecný problém nebo návrh. Názvy ulic, čtvrtí, veřejných prostranství a projektů lze ponechat jako **místo podnětu**, nikoli jako bydliště autora. Identifikující souvislosti se nesmějí vrátit ani při pozdější stylistické úpravě.

Nepřebírají se doslovné citace ani individuální demografické profily. U osobních obvinění se zachovává obecný požadavek na správu města nebo kvalitu služby, ne jméno ani neověřené obvinění. Znevažující zobecnění o skupinách se nereprodukují; lze věcně popsat obavu o soužití, pořádek či kapacity služeb, aniž se z domněnky stane fakt. Místa zmíněná u bezpečnosti jsou **subjektivní zkušeností**, nikoli statistikou kriminality.

Veřejné shrnutí má u bohatších otázek jeden až dva odstavce. Zachycuje opakující se motivy, konkrétní užitečné nápady i protichůdné postoje. Ojedinělý podnět nesmí být vydáván za většinový. Neuvádíme procenta výskytu témat bez úplného, doložitelného kódování všech odpovědí. Počty textů nejsou počtem všech podporovatelů tématu; mlčení není nesouhlas.

Pracovní parafráze slouží pro další redakci, **nejsou určeny k automatickému zveřejnění jako seznam individuálních odpovědí**. Ani odstranění jmen samo o sobě nezaručuje nulové riziko rozpoznání místním čtenářem. Veřejný web má převzít souhrny a agregované tabulky, nikoli propojit pracovní podklady do profilů nebo mapovat jednotlivé osobní příběhy.

## Demografie a další ochrana

Demografii uvádíme pouze jako samostatné rozdělení odpovědí na jednotlivé otázky pro popis zapojeného vzorku. **Všechny původní možnosti zůstávají samostatné**, včetně nulových a málo četných kategorií v N3, N4 a N5. Samotný nízký počet bez vazby na konkrétního člověka nebo jeho jiné odpovědi není automatickým důvodem pro slučování. Původně použitá plošná pravidla slučování byla při redakční revizi odstraněna, protože u těchto samostatných tabulek zbytečně ztrácela věcně důležité rozdíly.

Nevytváříme kombinace ulice/čtvrť × věk × rodina × názor ani spojení s jednotlivými texty. Rozložení bydliště není mapa problémů ani míra podpory tématu v dané části města. Pokud by později vznikly podrobné průniky, veřejné seznamy účastníků nebo možnost spojovat jednotlivé odpovědi, je nutné riziko identifikace znovu posoudit. Ochrana otevřených osobních příběhů zůstává beze změny.

Souhrnné ukazatele, například „velmi + spíše spokojení“ nebo „alespoň jedna věková kategorie dětí“, jsou **dodatečná shrnutí s uvedenou definicí**, nikoli náhrada původních možností. Všech 15 ukazatelů je vypsáno na konci kvantitativních tabulek; úplné rozdělení každé otázky zůstává dostupné nad nimi.

E-maily, souhlasy se zasláním výsledků, UUID, databázová ID a individuální časové údaje se neexportují. UTM značky nejsou otázkami ankety a do komunitního reportu nevstupují. V souborech pro výsledkový web se neukládá řádkový datový soubor respondentů. Technická kontrola obsahuje pouze souhrnné počty a kontrolní součty zdrojových souborů.

## Doporučená veřejná prezentace

1. Krátké poděkování, počet zapojených dotazníků a viditelné upozornění na nereprezentativnost.
2. Několik nejvýraznějších zjištění s odkazem na konkrétní otázku a jejím jmenovatelem.
3. Tematické oddíly: kvantitativní rozdělení, stručná interpretace, souhrn otevřených podnětů.
4. Přístupná tabulka pod každým grafem; nespoléhat jen na barvu a nevytvářet koláčové grafy z vícevýběru.
5. Oddělit „co lidé napsali“ od pozdější redakční odpovědi „co s tím lze dělat“. Doporučení nebo závazek není výsledek měření.

Výchozím zdrojem budoucího UI budou Markdownové výsledky a tabulky. Databáze je potřeba pouze pro novou kontrolu nebo změnu výběru; stylistickou úpravu shrnutí lze provést z anonymizovaných podkladů.