# Kontrola dat a pokrytí otázek

- Uložené dotazníky: **187**; dokončené: **144**; rozpracované: **43**.
- Rozsah data založení záznamů v záloze: **2026-06-16 až 2026-10-07**; nejnovější den aktualizace: **2026-10-07** (data SQLite v UTC). Nejde o nezávisle ověřené datum zahájení/ukončení sběru.
- Kvantitativní otázky: **31**; textová pole: **17**.
- SQLite quick_check: **ok**; JSON má očekávaný objektový tvar; neočekávané datové klíče nejsou povoleny.
- SHA-256 zálohy: `fde7caf4e6837b65ed3a834d091d290c131a8a75df9a1ae1700b4e5c8b2fbf09`.
- SHA-256 zdrojového HTML: `0126814f52e6553c4506783ed057b5165ed7da9a56037f8fac928346d58e09ea`.

Interní kontrolní soubor: hashe a technická metadata nejsou určeny do veřejného UI. Publikační zdroj obsahuje pouze agregované výsledky.

## Kvantitativní kontrola

Bez odpovědi znamená prázdnou otázku v záznamu splňujícím filtr; u nepodmíněných otázek sem patří i lidé, kteří na stránku vůbec nedošli.

| Klíč | Platné N | Dokončené N | Bez odpovědi | Mimo větev | Neplatné | Napjatá kombinace |
|---|---:|---:|---:|---:|---:|---:|
| a2 | 187 | 144 | 0 | 0 | 0 | 0 |
| b1 | 175 | 144 | 12 | 0 | 0 | 0 |
| b2 | 175 | 144 | 12 | 0 | 0 | 2 |
| c1 | 171 | 144 | 16 | 0 | 0 | 0 |
| d1 | 167 | 144 | 20 | 0 | 0 | 0 |
| d2 | 167 | 144 | 20 | 0 | 0 | 1 |
| e1 | 161 | 144 | 26 | 0 | 0 | 0 |
| e2 | 101 | 91 | 0 | 0 | 0 | 3 |
| e3a | 161 | 144 | 26 | 0 | 0 | 0 |
| e4a | 22 | 22 | 0 | 0 | 0 | 0 |
| e8a | 161 | 144 | 26 | 0 | 0 | 0 |
| e10 | 161 | 144 | 26 | 0 | 0 | 0 |
| f1a | 160 | 144 | 27 | 0 | 0 | 0 |
| f1b | 160 | 144 | 27 | 0 | 0 | 0 |
| f3 | 109 | 97 | 0 | 0 | 0 | 0 |
| g0 | 157 | 144 | 30 | 0 | 0 | 0 |
| g1a | 35 | 32 | 0 | 0 | 0 | 0 |
| g1b | 34 | 31 | 0 | 2 | 0 | 0 |
| g1c | 51 | 46 | 0 | 2 | 0 | 0 |
| g2 | 73 | 67 | 0 | 0 | 0 | 0 |
| g3 | 57 | 53 | 0 | 0 | 0 | 3 |
| j1 | 156 | 144 | 31 | 0 | 0 | 4 |
| j2 | 156 | 144 | 31 | 0 | 0 | 4 |
| h1a | 155 | 144 | 32 | 0 | 0 | 0 |
| h3 | 155 | 144 | 32 | 0 | 0 | 0 |
| i1 | 155 | 144 | 32 | 0 | 0 | 0 |
| n1 | 149 | 144 | 38 | 0 | 0 | 0 |
| n2 | 149 | 144 | 38 | 0 | 0 | 0 |
| n3 | 149 | 144 | 38 | 0 | 0 | 0 |
| n4 | 149 | 144 | 38 | 0 | 0 | 0 |
| n5 | 149 | 144 | 38 | 0 | 0 | 0 |

## Textová pole

Počet zařazených textů zahrnuje i odpovědi typu „nic“ nebo „nevím“; jejich věcná hodnota je popsána v jednotlivých redakčních podkladech. Nejde o počet unikátních lidí napříč otázkami.

| Klíč | Uložené neprázdné | Příslušná skupina | Zařazené texty | Mimo větev |
|---|---:|---:|---:|---:|
| a2-other | 1 | 2 | 1 | 0 |
| b2-other | 15 | 15 | 15 | 0 |
| c1b | 35 | 187 | 35 | 0 |
| d2-other | 4 | 4 | 4 | 0 |
| e1-other | 2 | 3 | 2 | 0 |
| e2-other | 6 | 6 | 6 | 0 |
| e3b | 50 | 86 | 50 | 0 |
| e4b | 9 | 16 | 9 | 0 |
| f3-other | 3 | 4 | 3 | 0 |
| g2-other | 5 | 6 | 5 | 0 |
| g3-other | 3 | 4 | 3 | 0 |
| j1-other | 7 | 8 | 7 | 0 |
| j2-other | 4 | 7 | 4 | 0 |
| h1b | 11 | 30 | 11 | 0 |
| i2 | 5 | 12 | 5 | 0 |
| l1 | 81 | 187 | 81 | 0 |
| l3 | 34 | 187 | 34 | 0 |

## Shodné sady odpovědí

Po odložení kontaktů a technických údajů byly nalezeny shodné sady odpovědí o velikostech: **[2]**. Samotná shoda (zejména u krátkého rozpracovaného formuláře) nedokazuje opakované vyplnění stejným člověkem. Automatické slučování se neprovádí.

## Omezení kontroly

Stav complete znamená dokončení podle aplikace, nikoli ověření identity nebo pravdivosti. Čistá technická kontrola nevylučuje testovací či nepravdivé odpovědi. Znění je převzato ze současného HTML; záloha neobsahuje číslo verze formuláře pro každého respondenta. Odlišné historické varianty formuláře proto nelze zpětně beze zbytku ověřit.
