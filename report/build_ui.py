"""Build the public static pages from aggregate/editorial Markdown only.

No import of the database analysis module, SQLite, original questionnaire,
internal audit, or individual qualitative working files is needed.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from html import escape
from pathlib import Path
import re
from string import Template


ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report"
DATA = REPORT / "kvantitativni-data.md"
COPY = REPORT / "web-texty.md"
SHELL = REPORT / "templates" / "public.html"

TOPICS = [
    ("vize", "Třebíč za 10 let", ["a2"]),
    ("centrum", "Centrum a památky", ["b1", "b2"]),
    ("priority", "Priority města", ["c1", "c1b"]),
    ("dukovany", "Dukovany a region", ["d1", "d2"]),
    ("doprava", "Doprava a veřejný prostor", ["e1", "e2", "e3a", "e3b", "e4a", "e4b", "e8a", "e10"]),
    ("bydleni", "Bydlení", ["f1a", "f1b", "f3"]),
    ("rodiny", "Rodiny a děti", ["g0", "g1a", "g1b", "g1c", "g2", "g3"]),
    ("zdravi", "Zdravotní péče", ["j1", "j2"]),
    ("sport", "Sport a volný čas", ["h1a", "h1b", "h3"]),
    ("bezpecnost", "Bezpečnost", ["i1", "i2"]),
    ("podnety", "Třebíč osobně", ["l1", "l3"]),
    ("o-odpovidajicich", "O odpovídajících", ["n1", "n2", "n3", "n4", "n5"]),
]

FILTER_COPY = {
    "e2": "Lidem, kteří uvedli, že pravidelně řídí auto.",
    "e4a": "Lidem, kteří uvedli pravidelnou jízdu na kole nebo koloběžce.",
    "f3": "Těm, kdo považují bydlení za vážný problém nebo jej řeší osobně či u blízkých.",
    "g1a": "Domácnostem s předškolními dětmi.",
    "g1b": "Domácnostem s dětmi na základní škole.",
    "g1c": "Domácnostem s dětmi na základní nebo střední škole.",
    "g2": "Domácnostem s dětmi do 18 let.",
    "g3": "Domácnostem s předškolními dětmi nebo dětmi na základní škole.",
}

SOURCE_FILTERS = {
    "e2": "E1 obsahuje auto",
    "e4a": "E1 obsahuje kolo",
    "f3": "F1a = velmi/spíše vážný nebo F1b = přímo já/blízkých",
    "g1a": "G0 obsahuje předškolní dítě",
    "g1b": "G0 obsahuje dítě na ZŠ",
    "g1c": "G0 obsahuje dítě na ZŠ nebo SŠ",
    "g2": "G0 obsahuje alespoň jednu věkovou kategorii dětí",
    "g3": "G0 obsahuje předškolní dítě nebo dítě na ZŠ",
}

NEUTRAL_VALUES = {"nevím", "nevyhraněný", "nedokážu posoudit", "nemám přehled", "nechci odpovědět", "nechci", "nezajímá", "teprve"}


@dataclass(frozen=True)
class Option:
    value: str
    label: str
    count: int
    percentage: Decimal
    complete_count: int
    complete_percentage: Decimal


@dataclass(frozen=True)
class Question:
    key: str
    title: str
    kind: str
    maximum: int | None
    n: int
    complete_n: int
    missing: int
    outside_branch: int
    filter: str
    note: str
    options: tuple[Option, ...]


@dataclass(frozen=True)
class TextAnswer:
    key: str
    title: str
    count: int
    paragraphs: tuple[str, ...]


@dataclass(frozen=True)
class PublicCopy:
    total: int
    complete: int
    partial: int
    snapshot: date
    intro: str
    methodology: str
    texts: dict[str, TextAnswer]


def pct(count, base):
    if base <= 0:
        raise ValueError("A public question must have a positive denominator")
    return (Decimal(count) * 100 / Decimal(base)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def decimal_text(value):
    return str(value).replace(".", ",")


def match(pattern, text, label):
    found = re.search(pattern, text, flags=re.M)
    if found is None:
        raise ValueError("Missing or unsupported Markdown metadata: " + label)
    return found


def cells(line):
    return [value.strip().replace(r"\|", "|") for value in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def parse_data(source):
    blocks = re.split(r'<a id="([a-z0-9-]+)"></a>', source)
    questions = {}
    for i in range(1, len(blocks), 2):
        key, body = blocks[i:i + 2]
        if key == "souhrnne-ukazatele":
            continue  # Editorial headline selections are intentionally not on this page.
        if key in questions or not re.fullmatch(r"[a-z]\d+[a-z]?", key):
            raise ValueError("Duplicate or unsupported question key")
        raw_title = match(r"^## (.+)$", body, key).group(1)
        title = re.sub(r"^[A-Z]\d+[a-z]?\.\s+", "", raw_title)
        metadata = match(r"^- Klíč: `([^`]+)`; typ: `(radio|checkbox|select)`; maximum voleb: (.+)\.$", body, key)
        if metadata.group(1) != key:
            raise ValueError("Question key disagrees with its anchor")
        kind = metadata.group(2)
        maximum = None if metadata.group(3) == "bez stanoveného maxima" else int(metadata.group(3))
        bases = match(r"Platné odpovědi N: \*\*(\d+)\*\*; z toho dokončené N: \*\*(\d+)\*\*; rozpracované: \*\*(\d+)\*\*", body, key)
        n, completed_n, partial_n = map(int, bases.groups())
        if n <= 0 or completed_n <= 0 or completed_n + partial_n != n:
            raise ValueError("Invalid question denominators")
        coverage = match(r"Záznamy splňující filtr: (\d+); bez odpovědi v této skupině: (\d+); uložené odpovědi mimo větev: (\d+)\.", body, key)
        eligible, missing, outside = map(int, coverage.groups())
        if eligible != n + missing:
            raise ValueError("Question coverage does not reconcile")
        condition = match(r"^- Filtr: (.+)\.$", body, key).group(1)
        if condition != SOURCE_FILTERS.get(key, "Bez podmíněného filtru"):
            raise ValueError("Source filter changed; review its reader-facing explanation")
        if key in SOURCE_FILTERS and key not in FILTER_COPY:
            raise ValueError("Add a reader-facing explanation for the branch")
        table = [line for line in body.splitlines() if line.startswith("|")]
        expected_header = ["Hodnota", "Možnost", "Počet", "Podíl (%)", "Počet – dokončené", "Podíl – dokončené (%)"]
        if len(table) < 3 or cells(table[0]) != expected_header:
            raise ValueError("Unexpected source table columns")
        options = []
        for line in table[2:]:
            values = cells(line)
            if len(values) != 6:
                raise ValueError("Unexpected option column count")
            value, label, count, percentage, completed, completed_pct = values
            item = Option(value, label, int(count), Decimal(percentage.replace(",", ".")), int(completed), Decimal(completed_pct.replace(",", ".")))
            if not (0 <= item.complete_count <= item.count <= n and item.complete_count <= completed_n):
                raise ValueError("Option counts exceed their denominator")
            if pct(item.count, n) != item.percentage or pct(item.complete_count, completed_n) != item.complete_percentage:
                raise ValueError("Source percentage does not match counts")
            options.append(item)
        if len({option.value for option in options}) != len(options):
            raise ValueError("Duplicate source option")
        total = sum(option.count for option in options)
        complete_total = sum(option.complete_count for option in options)
        if kind != "checkbox" and (total != n or complete_total != completed_n):
            raise ValueError("Single-choice table must add up to N")
        if kind == "checkbox" and (total < n or complete_total < completed_n or (maximum and (total > n * maximum or complete_total > completed_n * maximum))):
            raise ValueError("Multi-select totals exceed their limits")
        note = next((line for line in body.splitlines() if line.startswith("Poznámka ke kvalitě:")), "")
        questions[key] = Question(key, title, kind, maximum, n, completed_n, missing, outside, condition, note, tuple(options))
    if len(questions) != 31:
        raise ValueError("Expected exactly 31 quantitative questions; review the public inventory")
    return questions


def parse_copy(source):
    parts = re.split(r"^## ([a-z0-9-]+)\s*$", source, flags=re.M)
    sections = {}
    for i in range(1, len(parts), 2):
        key, value = parts[i:i + 2]
        if key in sections:
            raise ValueError("Duplicate public-copy section")
        sections[key] = value.strip()
    metadata = sections.pop("udaje")
    total = int(match(r"^Odpovědí: (\d+)$", metadata, "total").group(1))
    complete = int(match(r"^Dokončených: (\d+)$", metadata, "complete").group(1))
    partial = int(match(r"^Rozpracovaných: (\d+)$", metadata, "partial").group(1))
    snapshot = date.fromisoformat(match(r"^Datum podkladu: ([\d-]+)$", metadata, "date").group(1))
    if total != complete + partial:
        raise ValueError("Overall cohort counts do not add up")
    intro, methodology = sections.pop("uvod"), sections.pop("metodika")
    texts = {}
    for key, body in sections.items():
        if not re.fullmatch(r"[a-z]\d+[a-z]?(?:-other)?", key):
            raise ValueError("Unexpected public text key")
        title = match(r"^Otázka: (.+)$", body, key).group(1)
        count_match = match(r"^Textů: (\d+)$", body, key)
        count = int(count_match.group(1))
        prose = body[count_match.end():].strip()
        paragraphs = tuple(p.strip() for p in re.split(r"\n\s*\n", prose) if p.strip())
        if count < 1 or not 1 <= len(paragraphs) <= 2:
            raise ValueError("Each text field needs one or two summary paragraphs")
        texts[key] = TextAnswer(key, title, count, paragraphs)
    if len(texts) != 17 or sum(text.count for text in texts.values()) != 275:
        raise ValueError("Review text coverage: expected 17 fields and 275 texts")
    return PublicCopy(total, complete, partial, snapshot, intro, methodology, texts)


def inline(text):
    # Only **emphasis** is accepted. Everything else, including HTML, is escaped.
    result = []
    for part in re.split(r"(\*\*[^*]+\*\*)", text):
        result.append("<strong>" + escape(part[2:-2]) + "</strong>" if part.startswith("**") and part.endswith("**") else escape(part))
    return "".join(result)


def paragraphs(source):
    return "\n".join("<p>" + inline(block.strip()) + "</p>" for block in re.split(r"\n\s*\n", source.strip()) if block.strip())


def code(key):
    return "L2" if key == "l3" else key[0].upper() + key[1:]


def count_label(count, noun="odpověď"):
    forms = ("text", "texty", "textů") if noun == "text" else ("odpověď", "odpovědi", "odpovědí")
    return f"{count} {forms[0] if count == 1 else forms[1] if 2 <= count <= 4 else forms[2]}"


def date_text(value):
    months = ["ledna", "února", "března", "dubna", "května", "června", "července", "srpna", "září", "října", "listopadu", "prosince"]
    return f"{value.day}. {months[value.month - 1]} {value.year}"


def answer_label(label):
    """Uppercase the first letter without changing acronyms or stored values."""
    for index, letter in enumerate(label):
        if letter.isalpha():
            return label[:index] + letter.upper() + label[index + 1:]
    return label


def render_text(answer, supplemental=False):
    tag = "section" if supplemental else "article"
    classname = "text-supplement" if supplemental else "question-card qualitative-card"
    if supplemental:
        header = f'''<div class="supplement-heading"><h4 id="title-{answer.key}">Jiné odpovědi · shrnutí</h4><span class="answer-count">{count_label(answer.count, 'text')}</span></div>'''
    else:
        header = f'''<div class="question-meta"><span class="question-code">{code(answer.key)}</span><span>Otevřené odpovědi</span><span class="answer-count">{count_label(answer.count, 'text')}</span></div>
  <h3 id="title-{answer.key}">{escape(answer.title)}</h3>'''
    prose = "\n".join("<p>" + inline(p) + "</p>" for p in answer.paragraphs)
    return f'''<{tag} class="{classname}" id="{answer.key}" data-text-key="{answer.key}" data-text-count="{answer.count}" aria-labelledby="title-{answer.key}">
  {header}
  <div class="prose summary-prose">{prose}</div>
  <p class="summary-label">Anonymizovaný tematický souhrn, nikoli doslovné citace.</p>
</{tag}>'''


def render_chart(question):
    options = list(question.options)
    if question.kind == "checkbox" and question.key != "g0":
        options.sort(key=lambda option: -option.count)  # Stable ties; all options remain visible.
    rows = []
    for option in options:
        width = format(Decimal(option.count) * 100 / question.n, ".5f")
        percent = decimal_text(option.percentage) + " %"
        primary, secondary = (str(option.count), percent) if question.n < 30 else (percent, f"{option.count} odp.")
        if question.n < 30:
            primary = count_label(option.count)
        neutral = " neutral" if option.value in NEUTRAL_VALUES else ""
        rows.append(f'''<li class="chart-row{neutral}" data-value="{escape(option.value, quote=True)}" data-count="{option.count}">
      <span class="chart-label">{escape(answer_label(option.label))}</span>
  <span class="chart-value"><strong>{primary}</strong><span>{secondary}</span></span>
  <span class="bar-track" aria-hidden="true"><span class="bar-fill" style="width:{width}%"></span></span>
</li>''')
    return '<ol class="bar-chart" aria-label="Rozdělení odpovědí">\n' + "\n".join(rows) + "\n</ol>"


def render_table(question):
    rows = []
    for option in question.options:
                rows.append(f'<tr><th scope="row">{escape(answer_label(option.label))}</th><td>{option.count}</td><td>{decimal_text(option.percentage)} %</td><td>{option.complete_count}</td><td>{decimal_text(option.complete_percentage)} %</td></tr>')
    return f'''<details class="data-table" id="tabulka-{question.key}">
    <summary><span>Úplná tabulka</span><span class="table-summary-note">včetně dokončených odpovědí</span><span class="table-toggle-icon" aria-hidden="true"><svg class="table-chevron" viewBox="0 0 24 24" focusable="false"><path d="m6 9 6 6 6-6"/></svg><svg class="table-close" viewBox="0 0 24 24" focusable="false"><path d="m6 6 12 12M6 18 18 6"/></svg></span></summary>
  <div class="table-scroll" role="region" aria-labelledby="caption-{question.key}" tabindex="0">
    <table>
      <caption id="caption-{question.key}">{code(question.key)} · všechny platné odpovědi: {question.n}, z toho dokončené: {question.complete_n}</caption>
      <thead><tr><th scope="col">Možnost</th><th scope="col">Počet</th><th scope="col">Podíl</th><th scope="col">Dokončené:<br>počet</th><th scope="col">Dokončené:<br>podíl</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
    <p class="table-explainer">Dokončené odpovědi jsou podmnožinou všech odpovědí; oba sloupce se nesčítají. Podíl dokončených se počítá z {question.complete_n} odpovědí.</p>
  <p class="table-explainer">Bez uložené odpovědi v příslušné skupině: {question.missing}. Odpovědi mimo větev, které nejsou započteny: {question.outside_branch}.</p>
</details>'''


def render_question(question, texts):
    choice = (f"Nejvýše {question.maximum} možnosti" if question.maximum else "Více možností") if question.kind == "checkbox" else "Jedna možnost"
    filter_note = f'<p class="filter-note"><strong>Komu se otázka zobrazila:</strong> {FILTER_COPY[question.key]}</p>' if question.key in FILTER_COPY else ""
    multi_note = '<p class="chart-note">Lze vybrat více možností. Součet podílů proto může přesáhnout 100 %.</p>' if question.kind == "checkbox" else ""
    small_note = '<p class="small-sample">Malý počet odpovědí — počty jsou zde důležitější než samotná procenta.</p>' if question.n < 30 else ""
    quality = '<p class="quality-note">' + inline(question.note) + '</p>' if question.note else ""
    outside = f'<p class="quality-note">Nezapočtené odpovědi mimo aktuální větev: {question.outside_branch}.</p>' if question.outside_branch else ""
    other_key = question.key + "-other"
    supplemental = render_text(texts[other_key], True) if other_key in texts else ""
    return f'''<article class="question-card" id="{question.key}" data-question="{question.key}" data-n="{question.n}" data-complete-n="{question.complete_n}" aria-labelledby="title-{question.key}">
  <div class="question-meta"><span class="question-code">{code(question.key)}</span><span>{choice}</span><span class="answer-count">{count_label(question.n)}</span></div>
  <h3 id="title-{question.key}">{escape(question.title)}</h3>
    {multi_note}
  {filter_note}
  {small_note}
  {render_chart(question)}
  {quality}{outside}
  {supplemental}
    {render_table(question)}
</article>'''


def render_results(questions, copy):
    expected_cards = {key for _, _, keys in TOPICS for key in keys}
    actual_cards = set(questions) | {key for key in copy.texts if not key.endswith("-other")}
    if expected_cards != actual_cards:
        raise ValueError("Topic navigation does not cover exactly all question cards")
    if any(key.removesuffix("-other") not in questions for key in copy.texts if key.endswith("-other")):
        raise ValueError("Supplemental text has no quantitative parent")
    if questions["a2"].n != copy.total or questions["a2"].complete_n != copy.complete:
        raise ValueError("Public overview and aggregate cohort counts disagree")
    nav, sections = [], []
    for index, (slug, title, keys) in enumerate(TOPICS, 1):
        nav.append(f'<li><a href="#{slug}"><span class="nav-index" aria-hidden="true">{index:02d}</span>{escape(title)}</a></li>')
        cards = [render_question(questions[key], copy.texts) if key in questions else render_text(copy.texts[key]) for key in keys]
        sections.append(f'''<section class="topic-section" id="{slug}" data-topic aria-labelledby="heading-{slug}">
  <div class="topic-heading"><span class="topic-number" aria-hidden="true">{index:02d}</span><h2 id="heading-{slug}">{escape(title)}</h2></div>
  {''.join(cards)}
</section>''')
    return f'''<main id="obsah" tabindex="-1">
  <section class="report-intro" aria-labelledby="page-title">
    <p class="eyebrow">Třebíč · Anketa 2026</p>
    <h1 id="page-title">Všechny výsledky.<br><span>Otázku po otázce.</span></h1>
    <div class="intro-copy">{paragraphs(copy.intro)}</div>
    <a class="method-link" href="metodika.html">Jak výsledky číst a jak chráníme soukromí <span aria-hidden="true">↗</span></a>
    <dl class="survey-counts">
            <div><dt>odpovědí celkem</dt><dd>{copy.total}</dd></div>
      <div><dt>dokončených</dt><dd>{copy.complete}</dd></div>
      <div><dt>rozpracovaných</dt><dd>{copy.partial}</dd></div>
    </dl>
    <p class="snapshot">Stav podkladu k <time datetime="{copy.snapshot.isoformat()}">{date_text(copy.snapshot)}</time></p>
  </section>
  <div class="report-layout">
    <aside class="topics">
      <nav class="topic-navigation" aria-label="Témata výsledků">
        <p class="nav-title">Přejít na téma</p>
        <ol>{''.join(nav)}</ol>
      </nav>
    </aside>
    <div class="results-content">
      <div class="report-toolbar">
        <p>31 otázek s volbami · 17 textových polí</p>
        <div class="toolbar-actions enhanced-only">
          <button type="button" id="toggle-tables" aria-pressed="false">Rozbalit tabulky</button>
          <button type="button" id="print-report">Tisk / PDF</button>
        </div>
      </div>
    <p class="reading-note">U každé otázky uvádíme počet platných odpovědí. Podíly se počítají z tohoto počtu, ne automaticky z celkových {copy.total} odpovědí na dotazník.</p>
      <p class="visually-hidden" id="report-status" role="status" aria-live="polite"></p>
      {''.join(sections)}
      <div class="end-note"><p>To jsou všechny otázky. Děkujeme za váš čas i podněty.</p><a href="metodika.html">Stručná metodika zpracování →</a></div>
    </div>
  </div>
</main>'''


def render_methodology(copy):
    return f'''<main id="obsah" class="methodology-main" tabindex="-1">
    <a class="back-link" href="index.html">← Zpět na všechny výsledky</a>
  <p class="eyebrow">Stručně a transparentně</p>
  <h1>Jak výsledky číst</h1>
  <article class="methodology-card prose" aria-label="Metodika a ochrana soukromí">
    {paragraphs(copy.methodology)}
  </article>
    <a class="primary-link" href="index.html">Prohlédnout výsledky <span aria-hidden="true">→</span></a>
</main>'''


def build_pages(data_path=DATA, copy_path=COPY, shell_path=SHELL):
    questions = parse_data(data_path.read_text(encoding="utf-8"))
    copy = parse_copy(copy_path.read_text(encoding="utf-8"))
    shell = Template(shell_path.read_text(encoding="utf-8"))
    pages = {}
    for filename, title, description, body, is_results in [
        ("index.html", "Výsledky ankety 2026", "Všechny odpovědi v třebíčské anketě: přehledné grafy, úplné tabulky a anonymizované souhrny podnětů.", render_results(questions, copy), True),
        ("metodika.html", "Jak výsledky číst", "Stručná metodika třebíčské ankety: kdo odpovídal, jak počítáme podíly a jak chráníme soukromí.", render_methodology(copy), False),
    ]:
        html = shell.substitute(
            title=escape(title), description=escape(description, quote=True), page="" if is_results else filename,
            content=body, body_class="results-page" if is_results else "methodology-page",
            script='<script src="assets/vysledky.js" defer></script>' if is_results else "",
            results_current=' aria-current="page"' if is_results else "",
            method_current='' if is_results else ' aria-current="page"',
        )
        pages[filename] = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated public pages without writing")
    args = parser.parse_args()
    pages = build_pages()
    for filename, content in pages.items():
        path = ROOT / filename
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise SystemExit("Public page needs rebuilding: " + filename)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
    print("Public pages match Markdown." if args.check else "Built two public static pages from Markdown (no database access).")


if __name__ == "__main__":
    main()