"""Validate the public UI against Markdown; no database or private sources."""

from collections import Counter
from dataclasses import replace
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from unittest.mock import patch

import build_ui


class InspectHTML(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.questions = []
        self.texts = []
        self.tables = {}
        self.detail = None
        self.in_body = False
        self.row = None
        self.cell = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if "data-question" in attrs:
            self.questions.append(attrs)
        if "data-text-key" in attrs:
            self.texts.append(attrs)
        if tag == "details":
            self.detail = attrs["id"].removeprefix("tabulka-")
            self.tables[self.detail] = []
        if tag == "tbody":
            self.in_body = True
        if tag == "tr" and self.in_body:
            self.row = []
        if tag in {"th", "td"} and self.in_body:
            self.cell = []

    def handle_data(self, text):
        if self.cell is not None:
            self.cell.append(text)

    def handle_endtag(self, tag):
        if tag in {"th", "td"} and self.cell is not None:
            self.row.append("".join(self.cell).strip())
            self.cell = None
        if tag == "tr" and self.row is not None:
            self.tables[self.detail].append(self.row)
            self.row = None
        if tag == "tbody":
            self.in_body = False
        if tag == "details":
            self.detail = None


class PublicUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_source = build_ui.DATA.read_text(encoding="utf-8")
        cls.copy_source = build_ui.COPY.read_text(encoding="utf-8")
        cls.questions = build_ui.parse_data(cls.data_source)
        cls.copy = build_ui.parse_copy(cls.copy_source)
        cls.pages = build_ui.build_pages()
        cls.inspected = InspectHTML(cls.pages["index.html"])

    def test_build_reads_only_three_approved_public_sources(self):
        allowed = {build_ui.DATA, build_ui.COPY, build_ui.SHELL}
        reads = []
        original = Path.read_text

        def restricted_read(path, *args, **kwargs):
            self.assertIn(path, allowed)
            reads.append(path)
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", restricted_read):
            build_ui.build_pages()
        self.assertEqual(Counter(allowed), Counter(reads))

    def test_generated_files_exactly_match_markdown(self):
        for filename, expected in self.pages.items():
            self.assertEqual(expected, (build_ui.ROOT / filename).read_text(encoding="utf-8"), filename)

    def test_generated_pages_have_no_trailing_whitespace(self):
        for filename, html in self.pages.items():
            self.assertTrue(all(line == line.rstrip() for line in html.splitlines()), filename)

    def test_all_31_questions_and_17_text_fields_are_present_once(self):
        self.assertEqual(31, len(self.inspected.questions))
        self.assertEqual(set(self.questions), {item["data-question"] for item in self.inspected.questions})
        self.assertEqual(17, len(self.inspected.texts))
        self.assertEqual(set(self.copy.texts), {item["data-text-key"] for item in self.inspected.texts})
        self.assertEqual(275, sum(int(item["data-text-count"]) for item in self.inspected.texts))
        self.assertEqual(len(self.inspected.ids), len(set(self.inspected.ids)))

    def test_every_public_table_cell_matches_markdown(self):
        self.assertEqual(set(self.questions), set(self.inspected.tables))
        for key, question in self.questions.items():
            expected = [[build_ui.answer_label(option.label), str(option.count), build_ui.decimal_text(option.percentage) + " %", str(option.complete_count), build_ui.decimal_text(option.complete_percentage) + " %"] for option in question.options]
            self.assertEqual(expected, self.inspected.tables[key], key)

    def test_answer_labels_capitalize_only_the_first_letter(self):
        examples = {"živá": "Živá", "lepší MHD": "Lepší MHD", "MHD": "MHD", "UNESCO": "UNESCO", "P+R": "P+R", "„jiné“": "„Jiné“", "18–24": "18–24", "": ""}
        for original, expected in examples.items():
            self.assertEqual(expected, build_ui.answer_label(original))
        chart = build_ui.render_chart(self.questions["a2"])
        self.assertIn('data-value="živá"', chart)
        self.assertIn('class="chart-label">Živá</span>', chart)
        self.assertEqual("živá", self.questions["a2"].options[0].label)

    def test_counts_use_responses_but_questionnaire_still_names_the_form(self):
        page = self.pages["index.html"]
        self.assertIn("odpovědí celkem", page)
        self.assertIn("187 odpovědí na dotazník", page)
        self.assertIn("v dotazníku", page)
        self.assertIn("jedna chválí dotazník", page)
        self.assertIn("187 odpovědí na dotazník", self.pages["metodika.html"])
        for html in self.pages.values():
            self.assertNotRegex(html, r"\bdotazní(?:ků|ky|cích)\b")
        self.assertIn("jeden záznam nemusí znamenat jednu unikátní osobu", self.copy.methodology)

    def test_multiselect_note_is_directly_after_the_question(self):
        for question in self.questions.values():
            rendered = build_ui.render_question(question, self.copy.texts)
            if question.kind == "checkbox":
                self.assertRegex(rendered, rf'<h3 id="title-{question.key}">[^\n]+</h3>\s*<p class="chart-note">')
            else:
                self.assertNotIn('class="chart-note"', rendered)

    def test_tables_are_last_and_other_summaries_have_compact_headings(self):
        for question in self.questions.values():
            rendered = build_ui.render_question(question, self.copy.texts)
            self.assertTrue(rendered.rstrip().endswith("</details>\n</article>"), question.key)
            key = question.key + "-other"
            if key in self.copy.texts:
                self.assertLess(rendered.index(f'id="{key}"'), rendered.index(f'id="tabulka-{question.key}"'))
                summary = build_ui.render_text(self.copy.texts[key], True)
                self.assertIn('class="supplement-heading"', summary)
                self.assertNotIn("Otevřené odpovědi", summary)
                self.assertIn("Jiné odpovědi · shrnutí", summary)
        self.assertIn("Otevřené odpovědi", build_ui.render_text(self.copy.texts["c1b"]))

    def test_question_bases_are_preserved(self):
        for item in self.inspected.questions:
            question = self.questions[item["data-question"]]
            self.assertEqual(question.n, int(item["data-n"]))
            self.assertEqual(question.complete_n, int(item["data-complete-n"]))
        self.assertEqual((187, 144, 43), (self.copy.total, self.copy.complete, self.copy.partial))

    def test_small_and_zero_categories_are_not_suppressed(self):
        self.assertEqual(5, len(self.inspected.tables["n3"]))
        self.assertEqual(7, len(self.inspected.tables["n4"]))
        self.assertEqual(20, len(self.inspected.tables["n5"]))
        self.assertTrue(any(row[1] == "1" for row in self.inspected.tables["n5"]))
        self.assertTrue(any(row[1] == "0" for row in self.inspected.tables["n5"]))

    def test_all_graphs_keep_every_original_option(self):
        for question in self.questions.values():
            chart = build_ui.render_chart(question)
            found = re.findall(r'data-count="(\d+)"', chart)
            self.assertEqual(len(question.options), len(found), question.key)
            self.assertEqual(sorted(o.count for o in question.options), sorted(map(int, found)), question.key)

    def test_age_and_single_choice_order_is_not_ranked(self):
        question = self.questions["n2"]
        chart = build_ui.render_chart(question)
        positions = [chart.index(build_ui.escape(build_ui.answer_label(option.label))) for option in question.options]
        self.assertEqual(sorted(positions), positions)

    def test_multiselect_graph_is_ranked_without_losing_ties(self):
        chart = build_ui.render_chart(self.questions["c1"])
        found = list(map(int, re.findall(r'data-count="(\d+)"', chart)))
        self.assertEqual(sorted(found, reverse=True), found)
        self.assertEqual(len(found), 11)

    def test_bad_source_percentage_is_rejected(self):
        broken = self.data_source.replace("| bezpečná | bezpečná | 113 | 60,4 |", "| bezpečná | bezpečná | 113 | 60,5 |")
        self.assertNotEqual(self.data_source, broken)
        with self.assertRaisesRegex(ValueError, "percentage"):
            build_ui.parse_data(broken)

    def test_missing_question_is_not_silently_skipped(self):
        broken = self.data_source.replace('<a id="a2"></a>', "")
        with self.assertRaises(ValueError):
            build_ui.parse_data(broken)

    def test_changed_filter_cannot_keep_a_stale_public_explanation(self):
        broken = self.data_source.replace("- Filtr: E1 obsahuje auto.", "- Filtr: E1 obsahuje kolo.")
        self.assertNotEqual(self.data_source, broken)
        with self.assertRaisesRegex(ValueError, "filter changed"):
            build_ui.parse_data(broken)
        self.assertEqual(set(build_ui.SOURCE_FILTERS), set(build_ui.FILTER_COPY))

    def test_duplicate_copy_section_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            build_ui.parse_copy(self.copy_source + "\n## uvod\nAnother introduction")

    def test_all_topic_navigation_targets_exist(self):
        for link in self.inspected.links:
            if link.startswith("#"):
                self.assertIn(link[1:], self.inspected.ids)
            else:
                self.assertIn(link, {"index.html", "metodika.html"})

    def test_source_text_cannot_inject_html_or_attributes(self):
        dangerous = '<img src=x onerror="alert(1)">'
        q = replace(self.questions["a2"], title=dangerous, options=(replace(self.questions["a2"].options[0], value='" onclick="bad', label=dangerous),))
        rendered = build_ui.render_question(q, {})
        self.assertNotIn("<img", rendered)
        self.assertIn("&lt;img", rendered)
        self.assertIn('data-value="&quot; onclick=&quot;bad"', rendered)
        self.assertEqual("<strong>Safe</strong> &lt;script&gt;", build_ui.inline("**Safe** <script>"))

    def test_methodology_is_short_and_contains_key_caveats(self):
        self.assertLessEqual(len(self.copy.methodology.split()), 230)
        self.assertEqual(5, len(re.split(r"\n\s*\n", self.copy.methodology)))
        for phrase in ("reprezentativní", "rozpracovaných", "vícevýběru", "identifikujících", "databáze nebyla upravena"):
            self.assertIn(phrase, self.copy.methodology)

    def test_no_editorial_picks_or_individual_working_entries_are_published(self):
        page = self.pages["index.html"]
        for forbidden in ("Hlavní zjištění v kostce", "report/odpovedi", "KONTROLA-DAT", "data-uuid", "data-respondent", "save.php", "stats.php", "admin.php", ".db"):
            self.assertNotIn(forbidden, page)
        self.assertNotRegex(page, r"[\w.+-]+@[\w.-]+\.[\w-]+")
        self.assertNotRegex(page, r"\b[0-9a-f]{64}\b")

    def test_no_browser_data_fetching_or_storage(self):
        script = (build_ui.ROOT / "assets" / "vysledky.js").read_text(encoding="utf-8")
        self.assertNotRegex(script, r"\b(?:fetch|XMLHttpRequest|localStorage|sessionStorage)\b")

    def test_all_runtime_resources_are_local(self):
        for page in self.pages.values():
            self.assertNotIn("fonts.googleapis.com", page)
            self.assertNotIn("fonts.gstatic.com", page)
            self.assertNotRegex(page, r'<script[^>]+src="https?://')
        for name in ("sofia-sans-latin.woff2", "sofia-sans-latin-ext.woff2", "Sofia-Sans-LICENSE.txt"):
            self.assertTrue((build_ui.ROOT / "assets" / "fonts" / name).is_file())

    def test_displayed_l2_uses_existing_l3_source_key(self):
        answer = build_ui.render_text(self.copy.texts["l3"])
        self.assertIn('data-text-key="l3"', answer)
        self.assertIn('class="question-code">L2<', answer)

    def test_results_are_homepage_with_root_canonical_and_no_stale_links(self):
        self.assertEqual({"index.html", "metodika.html"}, set(self.pages))
        homepage = self.pages["index.html"]
        self.assertIn('<link rel="canonical" href="https://www.jakoutrebic.cz/">', homepage)
        self.assertIn('<meta property="og:url" content="https://www.jakoutrebic.cz/">', homepage)
        for page in self.pages.values():
            self.assertNotIn('href="vysledky.html', page)
            self.assertNotIn('https://www.jakoutrebic.cz/vysledky.html', page)
        method = InspectHTML(self.pages["metodika.html"])
        self.assertEqual(4, method.links.count("index.html"))

    def test_user_edited_intro_is_preserved_in_the_source(self):
        expected = "Děkujeme všem, kteří se zapojili. Jak jsme slíbili, zveřejňujeme výsledky všech otázek. Získali jsme celkem **187 odpovědí**. Nejde sice o reprezentativní průzkum, ale odpovědi i tak přinášejí zajímavý vhled do života obyvatel našeho města."
        self.assertEqual(expected, self.copy.intro)
        self.assertIn(build_ui.paragraphs(expected), self.pages["index.html"])


if __name__ == "__main__":
    unittest.main()