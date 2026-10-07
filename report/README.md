# Analýza ankety – pracovní prostor

## Kde začít

**[VYSLEDKY.md](VYSLEDKY.md)** je český obsahový report pro účastníky ankety a další třebíčskou veřejnost. Obsahuje interpretaci všech otázek a souhrny otevřených odpovědí. UI zatím není implementováno.

| Soubor | Úloha |
|---|---|
| [VYSLEDKY.md](VYSLEDKY.md) | Čitelný report, klíčová čísla a redakční shrnutí. |
| [kvantitativni-data.md](kvantitativni-data.md) | Úplná agregovaná data všech 31 kvantitativních otázek a 15 souhrnných ukazatelů; hlavní i dokončený soubor. Zdrojem budoucích grafů je tento Markdown, ne nová četba DB. |
| [PREZENTACE.md](PREZENTACE.md) | Doporučení grafu či textového zobrazení pro všech 48 polí, pravidla přístupnosti a datová smlouva pro UI. |
| [METODIKA.md](METODIKA.md) | Výběr odpovědí, jmenovatele, větvení, omezení a ochrana soukromí. |
| [KONTROLA-DAT.md](KONTROLA-DAT.md) | Vygenerované kontrolní součty, pokrytí, větvení a kvalita dat. |
| [analyza.py](analyza.py) | Reprodukovatelná agregace ze SQLite otevřené pouze pro čtení; Python 3.10+, bez externích knihoven. |
| [test_analyza.py](test_analyza.py) | Testy analýzy a konzistence pracovních podkladů. |

Výchozí záloha obsahuje **187 dotazníků: 144 dokončených a 43 rozpracovaných**. Datum založení záznamů v záloze sahá od 16. 6. do 7. 10. 2026; toto není nezávisle ověřené vymezení období veřejného sběru. Kontrolní součet zálohy je uveden v technické kontrole. Databáze nebyla upravena.

## Podklady k otevřeným otázkám

**17 samostatných souborů, celkem 275 zařazených textů**, ručně převedených do anonymizovaných parafrází. Žádné exportované kontakty, databázová ID, UUID, individuální časové údaje ani propojitelné respondentové profily. Číslo položky je lokální pořadí v otázce, nikoli identifikátor osoby. I shodné podněty jsou zachovány odděleně; neinterpretovatelné položky jsou označeny, ne tiše ztraceny.

| Oblast | Podklady |
|---|---|
| Vize a centrum | [A2 – jiné](odpovedi/a2-other.md), [B2 – jiné](odpovedi/b2-other.md) |
| Priority a Dukovany | [C1b](odpovedi/c1b.md), [D2 – jiné](odpovedi/d2-other.md) |
| Doprava | [E1 – jiné](odpovedi/e1-other.md), [E2 – jiné](odpovedi/e2-other.md), [E3b – pěší](odpovedi/e3b.md), [E4b – kolo](odpovedi/e4b.md) |
| Bydlení | [F3 – jiné](odpovedi/f3-other.md) |
| Rodiny | [G2 – jiné](odpovedi/g2-other.md), [G3 – jiné](odpovedi/g3-other.md) |
| Zdravotnictví | [J1 – jiné](odpovedi/j1-other.md), [J2 – jiné](odpovedi/j2-other.md) |
| Sport a bezpečnost | [H1b](odpovedi/h1b.md), [I2](odpovedi/i2.md) |
| Osobní otevřené otázky | [L1](odpovedi/l1.md), [L2 – uložený klíč l3](odpovedi/l3.md) |

Podklady umožňují přepsat shrnutí například stručněji, civilněji nebo s jiným tematickým důrazem **bez nového čtení SQL**. Jde o soubor pro redakci, ne seznam výpovědí k automatickému zveřejnění. Odstranění přímých identifikátorů samo o sobě není absolutní zárukou, že velmi specifický podnět místní čtenář nepozná; veřejně mají být použity souhrny, ne individuální řádky.

## Redakční postup bez databáze

1. Otevřít podklad příslušné otázky; přečíst všechny položky, nejen ty nejdelší.
2. Zachovat opakující se motivy, protichůdné názory a několik konkrétních námětů. Jednotlivost označit jako jednotlivost; nevytvářet odhady procent výskytu témat bez úplného doloženého kódování.
3. Upravit pouze odpovídající pasáž reportu. U delších otázek mířit na jeden až dva odstavce. Nepřenášet zpět osobní příběhy, doslovné citace ani domněnky o identitě autora.
4. Číselné výroky ověřit proti agregovaným tabulkám. Nesčítat zaokrouhlená procenta; u souhrnů použít definované ukazatele a správné N.
5. Odlišit subjektivní hodnocení od ověřené události. Zvlášť provoz nemocnice, stav zařízení a osobní obvinění vyžadují případné samostatné ověření.

## Reprodukce a kontroly

Příkazy jsou spouštěné z kořene repozitáře:

- `python -X utf8 report/analyza.py audit` – read-only audit zdroje, pouze agregovaný výpis.
- `python -X utf8 report/analyza.py check` – ověření, že oba vygenerované Markdownové podklady přesně odpovídají současné záloze a HTML; nic nepřepisuje.
- `python -X utf8 -m unittest discover -s report -p "test_*.py"` – testy bez potřeby skutečné databáze.
- `python -X utf8 report/analyza.py tables --replace` – výslovná regenerace pouze dvou agregovaných souborů, nikoli redakčního reportu nebo otevřených parafrází. Bez `--replace` odmítne přepsat existující soubory.

Při změně databázové zálohy či formuláře je nutné znovu posoudit **celý obsahový soulad**, ne jen přegenerovat tabulky: pořadí a pokrytí ručních parafrází platí pro tuto zálohu. Otevřené parafráze nelze bezpečně automaticky obnovit z raw textů pouhým regulárním výrazem.

Pomocný režim `review` sloužil pro lokální redakční čtení po otázkách. Provádí jen počáteční maskování kontaktů, **není plnohodnotnou anonymizací**. Jeho výstup se nesmí přesměrovat do souboru, přidat do Gitu ani publikovat. Nové čtení originálů není pro běžné stylistické úpravy potřeba.

## Zveřejnění a nasazení

- Budoucí UI má čerpat z reportu, agregovaných tabulek a metodiky; nikoli z per-respondentových dat, která zde nejsou.
- Samostatné kvantitativní tabulky zachovávají všechny původní možnosti, včetně malých a nulových četností v N3/N4/N5. Žádné kategorie se neslučují jen kvůli nízkému počtu. Souhrnné ukazatele jsou doplněk, ne náhrada detailu; individuální odpovědi a jejich propojení se nezveřejňují.
- Analyzační složka i zálohy jsou explicitně vyloučeny z [FTP nasazení](../.github/workflows/deploy.yml); nepublikují se tím automaticky skripty, pracovní podklady ani případné zálohy přítomné v pracovním adresáři nasazení. Zálohy jsou navíc ignorované Gitem. Původní nasazení již vylučovalo Markdown, ale ne ostatní soubory tohoto prostoru.
- Kontrolní součty zdrojů a technická metadata zůstávají pouze v interní kontrole dat; veřejné datové tabulky je neobsahují.
- Veřejné texty mají projít běžnou závěrečnou redakční kontrolou. Nebyla provedena nezávislá věcná kontrola tvrzení respondentů ani právní posouzení jejich návrhů.