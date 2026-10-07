"""Read-only survey audit and aggregate Markdown export (Python 3.10+, stdlib).

No respondent-level dataset is written. `review` is an operator-only preview,
NOT an anonymization/export command: every paraphrase still needs manual review.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sqlite3


ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report"
DATABASE = ROOT / "backup" / "dotaznik.db"
HTML = ROOT / "index.html"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    parent: Node | None = None
    children: list = field(default_factory=list)

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def closest(self, predicate):
        node = self
        while node is not None:
            if predicate(node):
                return node
            node = node.parent
        return None

    def text(self):
        return re.sub(r"\s+", " ", "".join(child.text() if isinstance(child, Node) else child for child in self.children)).strip()


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.current = self.root
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        node = self.current.closest(lambda candidate: candidate.tag == tag)
        if node is not None and node.parent is not None:
            self.current = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


@dataclass
class Question:
    key: str
    label: str
    kind: str
    page: str
    options: list[tuple[str, str]] = field(default_factory=list)
    maximum: int | None = None


def questionnaire(path=HTML):
    document = Document(path.read_text(encoding="utf-8"))
    result = []
    seen = set()
    for node in document.root.walk():
        if node.tag not in {"input", "select", "textarea"}:
            continue
        page = node.closest(lambda n: n.has_class("page"))
        if page is None or page.attrs.get("id") in {"page-intro", "page-end"}:
            continue
        key = node.attrs.get("name") or node.attrs.get("id")
        if not key or key in seen:
            continue
        card = node.closest(lambda n: n.has_class("question") or n.has_class("gateway-card"))
        if card is None:
            raise ValueError("Form field outside a question card")
        followup = node.closest(lambda n: n.has_class("inline-followup"))
        heading_class = "followup-label" if followup else "question-text"
        heading = next(n for n in (followup or card).walk() if n.has_class(heading_class))
        label = heading.text()
        if key.endswith("-other"):
            label += " — upřesnění možnosti jiné"
        kind = "text" if node.tag == "textarea" else node.attrs.get("type", "select")
        options = []
        maximum = None
        if kind in {"radio", "checkbox"}:
            for inp in card.walk():
                if inp.tag == "input" and inp.attrs.get("name") == key:
                    option_label = inp.closest(lambda n: n.tag == "label")
                    options.append((inp.attrs["value"], option_label.text()))
            container = node.closest(lambda n: n.has_class("options"))
            if container and container.attrs.get("data-max"):
                maximum = int(container.attrs["data-max"])
        elif kind == "select":
            options = [(n.attrs["value"], n.text()) for n in node.walk() if n.tag == "option" and n.attrs.get("value")]
        seen.add(key)
        result.append(Question(key, label, kind, page.attrs["id"], options, maximum))
    return result


CONDITIONS = {
    "e2": "E1 obsahuje auto",
    "e3b": "E3a = ano nebo občas",
    "e4a": "E1 obsahuje kolo",
    "e4b": "E1 obsahuje kolo a E4a = ano nebo občas",
    "f3": "F1a = velmi/spíše vážný nebo F1b = přímo já/blízkých",
    "g1a": "G0 obsahuje předškolní dítě",
    "g1b": "G0 obsahuje dítě na ZŠ",
    "g1c": "G0 obsahuje dítě na ZŠ nebo SŠ",
    "g2": "G0 obsahuje alespoň jednu věkovou kategorii dětí",
    "g3": "G0 obsahuje předškolní dítě nebo dítě na ZŠ",
    "h1b": "H1a = spíše nespokojen/a nebo nespokojen/a",
    "i2": "I1 = spíše nebezpečně nebo velmi nebezpečně",
}


def eligible(key, data):
    if key.endswith("-other"):
        parent = key.removesuffix("-other")
        trigger = "jiná" if parent == "a2" else "jiné"
        return eligible(parent, data) and trigger in data.get(parent, [])
    if key == "e2":
        return "auto" in data.get("e1", [])
    if key == "e3b":
        return data.get("e3a") in {"ano", "občas"}
    if key in {"e4a", "e4b"}:
        return "kolo" in data.get("e1", []) and (key == "e4a" or data.get("e4a") in {"ano", "občas"})
    if key == "f3":
        return data.get("f1a") in {"velmi vážný", "spíše vážný"} or data.get("f1b") in {"přímo já", "blízkých"}
    if key in {"g1a", "g1b", "g1c", "g2", "g3"}:
        wanted = {
            "g1a": {"predskolak"}, "g1b": {"zsak"}, "g1c": {"zsak", "ssak"},
            "g2": {"predskolak", "zsak", "ssak"}, "g3": {"predskolak", "zsak"},
        }
        return bool(wanted[key].intersection(data.get("g0", [])))
    if key == "h1b":
        return data.get("h1a") in {"spíše nespokojen/a", "nespokojen/a"}
    if key == "i2":
        return data.get("i1") in {"spíše nebezpečně", "velmi nebezpečně"}
    return True


def condition(key):
    if key.endswith("-other"):
        parent = key.removesuffix("-other")
        return condition(parent) + "; označena možnost jiné/jiná"
    return CONDITIONS.get(key, "Bez podmíněného filtru")


def load_rows(path=DATABASE):
    """Whitelist only question fields; no IDs, emails, timestamps or UTM retained."""
    allowed = {q.key for q in questionnaire()}
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only = ON")
        check = [row[0] for row in db.execute("PRAGMA quick_check")]
        if check != ["ok"]:
            raise ValueError("SQLite quick_check failed")
        source = db.execute("SELECT status, data FROM responses").fetchall()
        dates = db.execute("SELECT MIN(date(created_at)), MAX(date(created_at)), MAX(date(updated_at)) FROM responses").fetchone()
    result = []
    for status, text in source:
        data = json.loads(text)
        if status not in {"complete", "partial"} or not isinstance(data, dict):
            raise ValueError("Unexpected status or JSON shape")
        unexpected = set(data) - allowed - {"email", "consent"} - {k for k in data if k.startswith("utm_")}
        if unexpected:
            raise ValueError("Unmapped data fields; revise the questionnaire mapping before export")
        result.append({"status": status, "data": {key: value for key, value in data.items() if key in allowed}})
    return result, dates


def nonempty(value):
    return value not in (None, "", [], {}) and (not isinstance(value, str) or bool(value.strip()))


def choices(question, value):
    if not nonempty(value):
        return None
    if question.kind == "checkbox":
        if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
            raise ValueError("Wrong multi-select type")
        values = [v.strip() for v in value]
    else:
        if not isinstance(value, str):
            raise ValueError("Wrong single-choice type")
        values = [value.strip()]
    allowed = {v for v, _ in question.options}
    if len(values) != len(set(values)) or not set(values).issubset(allowed):
        raise ValueError("Unknown or repeated option")
    if question.maximum and len(values) > question.maximum:
        raise ValueError("Too many options")
    if question.key == "g0" and len(values) > 1 and {"ne", "nechci"}.intersection(values):
        raise ValueError("Inconsistent child gateway")
    return values


def aggregate(question, rows):
    stats = Counter()
    counts = Counter()
    complete = Counter()
    for row in rows:
        data = row["data"]
        value = data.get(question.key)
        if not eligible(question.key, data):
            stats["outside_branch"] += int(nonempty(value))
            continue
        stats["eligible"] += 1
        try:
            selected = choices(question, value)
        except ValueError:
            stats["invalid"] += 1
            continue
        if selected is None:
            stats["missing"] += 1
            continue
        stats["n"] += 1
        counts.update(selected)
        if row["status"] == "complete":
            stats["complete_n"] += 1
            complete.update(selected)
        exclusive = {
            "b2": {"nevím"}, "d2": {"nic"}, "e2": {"auto nenahraditelné"},
            "f3": {"nevím"}, "g3": {"nepotřebuji", "město by se tím nezabývalo"},
            "j1": {"nemám problém"}, "j2": {"nevím"},
        }.get(question.key, set())
        if len(selected) > 1 and exclusive.intersection(selected):
            stats["mixed_exclusive"] += 1
    return stats, counts, complete


def text_entries(question, rows):
    values = [row["data"][question.key].strip() for row in rows if eligible(question.key, row["data"]) and isinstance(row["data"].get(question.key), str) and row["data"][question.key].strip()]
    # Different order per question, derived from text, never from respondent ID/time.
    return sorted(values, key=lambda value: hashlib.sha256((question.key + "\0" + value).encode("utf-8")).digest())


def text_stats(question, rows):
    return {
        "stored": sum(nonempty(row["data"].get(question.key)) for row in rows),
        "eligible": sum(eligible(question.key, row["data"]) for row in rows),
        "included": len(text_entries(question, rows)),
        "outside_branch": sum(nonempty(row["data"].get(question.key)) and not eligible(question.key, row["data"]) for row in rows),
    }


def published_options(question, counts, complete):
    """Preserve every original option in these unlinked marginal tables."""
    return [(value, label, counts[value], complete[value]) for value, label in question.options]


def md(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def percent(count, base):
    if not base:
        return "—"
    value = (Decimal(count) * 100 / Decimal(base)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return str(value).replace(".", ",")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


INDICATORS = [
    ("b1-spokojeni", "b1", "Spokojení s péčí o centrum", {"velmi spokojen/a", "spíše spokojen/a"}),
    ("d1-pozitivni", "d1", "Pozitivní postoj k dostavbě Dukovan", {"jednoznačně pozitivně", "spíše pozitivně"}),
    ("e3a-problemy", "e3a", "Pěší problémy alespoň občas", {"ano", "občas"}),
    ("e4a-problemy", "e4a", "Cyklistické problémy alespoň občas", {"ano", "občas"}),
    ("e8a-pro", "e8a", "Pro přeměnu části parkování na pěší prostor a zeleň", {"rozhodně pro", "spíše pro"}),
    ("e8a-proti", "e8a", "Proti přeměně části parkování", {"rozhodně proti", "spíše proti"}),
    ("e10-dulezity", "e10", "Obchvat je důležitý", {"velmi důležité", "spíše důležité"}),
    ("f1a-vazny", "f1a", "Bydlení jako vážný problém", {"velmi vážný", "spíše vážný"}),
    ("f1b-zkusenost", "f1b", "Problém s bydlením osobně nebo u blízkých", {"přímo já", "blízkých"}),
    ("g0-deti", "g0", "Domácnosti alespoň s jednou kategorií dětí", {"predskolak", "zsak", "ssak"}),
    ("g1a-problemy", "g1a", "Problém s místem ve školce osobně nebo v okolí", {"ano, přímo u nás", "ano, v okolí nebo u známých"}),
    ("g1c-problemy", "g1c", "Problém se SŠ osobně nebo v okolí", {"ano, přímo u nás", "ano, v okolí nebo u známých"}),
    ("h1a-spokojeni", "h1a", "Spokojení se sportovními podmínkami", {"spokojen/a", "spíše spokojen/a"}),
    ("h3-verejny-amatersky", "h3", "Peníze přednostně na veřejný nebo mládežnický/amatérský sport", {"běžná sportoviště", "mládež a amatéři"}),
    ("i1-bezpecne", "i1", "Pocit bezpečí", {"naprosto bezpečně", "spíše bezpečně"}),
]


def render_indicators(questions, rows):
    by_key = {q.key: q for q in questions}
    lines = [
        '<a id="souhrnne-ukazatele"></a>', "", "## Souhrnné ukazatele pro přehled", "",
        "Každý ukazatel je sjednocením uvedených možností uvnitř jedné otázky. Dotazník se počítá nejvýše jednou, i když u vícevýběru splňuje více možností. Základ N je shodný s příslušnou otázkou výše; jde o doplněk, nikoli náhradu úplného rozdělení.", "",
        "| Klíč | Ukazatel | Otázka | Zahrnuté hodnoty | Počet | N | Podíl (%) | Počet – dokončené | N – dokončené | Podíl – dokončené (%) |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key, parent, label, wanted in INDICATORS:
        q = by_key[parent]
        stats, _, _ = aggregate(q, rows)
        all_count = complete_count = 0
        for row in rows:
            if not eligible(parent, row["data"]):
                continue
            selected = choices(q, row["data"].get(parent))
            if selected and wanted.intersection(selected):
                all_count += 1
                complete_count += int(row["status"] == "complete")
        values = "; ".join(value for value, _ in q.options if value in wanted)
        lines.append(f"| {key} | {md(label)} | {parent} | {md(values)} | {all_count} | {stats['n']} | {percent(all_count, stats['n'])} | {complete_count} | {stats['complete_n']} | {percent(complete_count, stats['complete_n'])} |")
    return "\n".join(lines) + "\n"


def render_tables(questions, rows):
    lines = [
        "# Úplné kvantitativní tabulky", "",
        "Agregovaný podklad pro výsledkový web; neobsahuje individuální odpovědi. Všechna procenta jsou podíly z platných odpovědí na konkrétní otázku, u vícevýběru nikoli podíly ze všech zaškrtnutí. Dokončené dotazníky tvoří podmnožinu hlavního souboru. Údaje bez odpovědi nejsou započteny do jmenovatele.", "",
        "Názvy možností a jejich pořadí odpovídají HTML. Všechny původní kategorie včetně nulových a málo četných zůstávají samostatné. Klíč označuje otázku nebo možnost, nikoli respondenta. Tabulky nepropojují jednotlivé odpovědi mezi otázkami; souhrnné ukazatele na konci jsou pouze doplněk úplných rozdělení.", "",
    ]
    for q in questions:
        if q.kind == "text":
            continue
        stats, counts, complete = aggregate(q, rows)
        if stats["invalid"]:
            raise ValueError(f"Invalid values in {q.key}; no aggregate files should be published")
        lines += [
            f'<a id="{q.key}"></a>', "", f"## {q.label}", "",
            f"- Klíč: `{q.key}`; typ: `{q.kind}`; maximum voleb: {q.maximum or ('bez stanoveného maxima' if q.kind == 'checkbox' else '1')}.",
            f"- Filtr: {condition(q.key)}.",
            f"- Platné odpovědi N: **{stats['n']}**; z toho dokončené N: **{stats['complete_n']}**; rozpracované: **{stats['n'] - stats['complete_n']}**.",
            f"- Záznamy splňující filtr: {stats['eligible']}; bez odpovědi v této skupině: {stats['missing']}; uložené odpovědi mimo větev: {stats['outside_branch']}.",
            "", "| Hodnota | Možnost | Počet | Podíl (%) | Počet – dokončené | Podíl – dokončené (%) |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for value, label, count, completed in published_options(q, counts, complete):
            lines.append(f"| {md(value)} | {md(label)} | {count} | {percent(count, stats['n'])} | {completed} | {percent(completed, stats['complete_n'])} |")
        if q.kind == "checkbox":
            lines += ["", f"Celkem označení: **{sum(counts.values())}** (dokončené: **{sum(complete.values())}**). Součet procent může přesahovat 100 %."]
        if stats["mixed_exclusive"]:
            lines += ["", f"Poznámka ke kvalitě: počet odpovědí kombinujících variantu typu „nevím / nic / nepotřebuji“ s další volbou je **{stats['mixed_exclusive']}**; původní volby jsou zachovány."]
        lines.append("")
    return "\n".join(lines) + render_indicators(questions, rows)


def render_audit(questions, rows, dates):
    statuses = Counter(row["status"] for row in rows)
    lines = [
        "# Kontrola dat a pokrytí otázek", "",
        f"- Uložené dotazníky: **{len(rows)}**; dokončené: **{statuses['complete']}**; rozpracované: **{statuses['partial']}**.",
        f"- Rozsah data založení záznamů v záloze: **{dates[0]} až {dates[1]}**; nejnovější den aktualizace: **{dates[2]}** (data SQLite v UTC). Nejde o nezávisle ověřené datum zahájení/ukončení sběru.",
        f"- Kvantitativní otázky: **{sum(q.kind != 'text' for q in questions)}**; textová pole: **{sum(q.kind == 'text' for q in questions)}**.",
        "- SQLite quick_check: **ok**; JSON má očekávaný objektový tvar; neočekávané datové klíče nejsou povoleny.",
        f"- SHA-256 zálohy: `{digest(DATABASE)}`.",
        f"- SHA-256 zdrojového HTML: `{digest(HTML)}`.", "",
        "Interní kontrolní soubor: hashe a technická metadata nejsou určeny do veřejného UI. Publikační zdroj obsahuje pouze agregované výsledky.", "",
        "## Kvantitativní kontrola", "",
        "Bez odpovědi znamená prázdnou otázku v záznamu splňujícím filtr; u nepodmíněných otázek sem patří i lidé, kteří na stránku vůbec nedošli.", "",
        "| Klíč | Platné N | Dokončené N | Bez odpovědi | Mimo větev | Neplatné | Napjatá kombinace |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for q in questions:
        if q.kind != "text":
            stats, _, _ = aggregate(q, rows)
            lines.append(f"| {q.key} | {stats['n']} | {stats['complete_n']} | {stats['missing']} | {stats['outside_branch']} | {stats['invalid']} | {stats['mixed_exclusive']} |")
    lines += ["", "## Textová pole", "", "Počet zařazených textů zahrnuje i odpovědi typu „nic“ nebo „nevím“; jejich věcná hodnota je popsána v jednotlivých redakčních podkladech. Nejde o počet unikátních lidí napříč otázkami.", "", "| Klíč | Uložené neprázdné | Příslušná skupina | Zařazené texty | Mimo větev |", "|---|---:|---:|---:|---:|"]
    for q in questions:
        if q.kind == "text":
            stats = text_stats(q, rows)
            lines.append(f"| {q.key} | {stats['stored']} | {stats['eligible']} | {stats['included']} | {stats['outside_branch']} |")
    payloads = Counter(json.dumps(row["data"], ensure_ascii=True, sort_keys=True) for row in rows)
    duplicate_sizes = sorted(count for count in payloads.values() if count > 1)
    lines += ["", "## Shodné sady odpovědí", "", f"Po odložení kontaktů a technických údajů byly nalezeny shodné sady odpovědí o velikostech: **{duplicate_sizes or 'žádné'}**. Samotná shoda (zejména u krátkého rozpracovaného formuláře) nedokazuje opakované vyplnění stejným člověkem. Automatické slučování se neprovádí.", "", "## Omezení kontroly", "", "Stav complete znamená dokončení podle aplikace, nikoli ověření identity nebo pravdivosti. Čistá technická kontrola nevylučuje testovací či nepravdivé odpovědi. Znění je převzato ze současného HTML; záloha neobsahuje číslo verze formuláře pro každého respondenta. Odlišné historické varianty formuláře proto nelze zpětně beze zbytku ověřit.", ""]
    return "\n".join(lines)


def preview_redaction(text):
    """First-pass masking only. Never treat this as publication-ready output."""
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[\w-]+", "[kontakt odstraněn]", text)
    text = re.sub(r"(?:https?://|www\.)\S+", "[odkaz odstraněn]", text, flags=re.I)
    text = re.sub(r"(?<!\w)(?:\+420[\s-]*)?(?:\d[\s-]*){9}(?!\d)", "[telefon odstraněn]", text)
    text = re.sub(r"\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b", "[identifikátor odstraněn]", text, flags=re.I)
    text = re.sub(r"\b(?:č\.?\s*p\.?|číslo\s+domu)\s*\d+(?:/\d+)?", "[číslo domu odstraněno]", text, flags=re.I)
    text = re.sub(r"\b(?:paní|pana|pan|MUDr\.|Mgr\.|Ing\.|Bc\.|Dr\.)\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\w-]+(?:\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\w-]+)?", "[osoba odstraněna]", text)
    return re.sub(r"\s+", " ", text).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["audit", "tables", "review", "check"])
    parser.add_argument("keys", nargs="*", help="Question-local text fields for operator review")
    parser.add_argument("--replace", action="store_true", help="Explicitly replace generated aggregate Markdown only")
    args = parser.parse_args()
    questions = questionnaire()
    rows, dates = load_rows()
    tables = render_tables(questions, rows)
    audit = render_audit(questions, rows, dates)
    if args.action == "audit":
        print(audit)
    elif args.action == "tables":
        targets = {REPORT / "kvantitativni-data.md": tables, REPORT / "KONTROLA-DAT.md": audit}
        if not args.replace and any(path.exists() for path in targets):
            parser.error("Generated files exist; use --replace only after reviewing source changes")
        for path, content in targets.items():
            path.write_text(content, encoding="utf-8", newline="\n")
        print("Wrote aggregate Markdown only; database unchanged.")
    elif args.action == "check":
        for path, expected in [(REPORT / "kvantitativni-data.md", tables), (REPORT / "KONTROLA-DAT.md", audit)]:
            if path.read_text(encoding="utf-8") != expected:
                raise SystemExit("Aggregate/source mismatch: " + path.name)
        print("Aggregate Markdown exactly matches the read-only database and HTML.")
    elif args.action == "review":
        if not args.keys:
            parser.error("Explicit text field names required; no bulk respondent export")
        by_key = {q.key: q for q in questions if q.kind == "text"}
        if set(args.keys) - by_key.keys():
            parser.error("Unknown text field")
        print("OPERATOR PREVIEW ONLY: initial masking is not full anonymization. Do not publish or redirect to a file.")
        for key in args.keys:
            print("\n###", key, "|", by_key[key].label)
            for i, value in enumerate(text_entries(by_key[key], rows), 1):
                print(f"{i:03d}: {preview_redaction(value)}")


if __name__ == "__main__":
    main()