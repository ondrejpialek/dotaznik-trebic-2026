"""Synthetic-data and Markdown checks; the real backup is not needed."""

from collections import Counter
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3
import tempfile
import unittest

import analyza


def row(data, status="complete"):
    return {"status": status, "data": data}


class QuestionnaireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = analyza.questionnaire()
        cls.by_key = {q.key: q for q in cls.questions}

    def test_inventory_is_complete_and_unique(self):
        self.assertEqual(48, len(self.questions))
        self.assertEqual(48, len(self.by_key))
        self.assertEqual(31, sum(q.kind != "text" for q in self.questions))
        self.assertEqual(17, sum(q.kind == "text" for q in self.questions))

    def test_real_form_wording_and_stored_alias(self):
        self.assertTrue(self.by_key["l3"].label.startswith("L2."))
        self.assertNotIn("l2", self.by_key)
        self.assertIn("ze všeho nejvíc chybí", self.by_key["l1"].label)
        self.assertIn("město pečuje", self.by_key["b1"].label)

    def test_followup_heading_is_not_parent_heading(self):
        self.assertTrue(self.by_key["e3b"].label.startswith("E3b."))
        self.assertTrue(self.by_key["i2"].label.startswith("I2."))

    def test_full_labels_not_only_short_storage_values(self):
        options = dict(self.by_key["c1"].options)
        self.assertIn("silnice I/23", options["obchvat"])
        self.assertEqual(11, len(options))
        self.assertEqual(20, len(self.by_key["n5"].options))

    def test_limits_and_nonquestion_fields(self):
        limited = {q.key for q in self.questions if q.maximum == 3}
        self.assertEqual({"a2", "b2", "c1", "d2", "f3", "j2"}, limited)
        self.assertIsNone(self.by_key["e1"].maximum)
        for private in ("email", "consent", "uuid", "utm_source"):
            self.assertNotIn(private, self.by_key)


class BranchingTests(unittest.TestCase):
    def test_driver_branch(self):
        self.assertTrue(analyza.eligible("e2", {"e1": ["auto", "pěšky"]}))
        self.assertFalse(analyza.eligible("e2", {"e1": ["pěšky"]}))
        self.assertFalse(analyza.eligible("e2", {}))

    def test_walking_followup(self):
        for value, expected in [("ano", True), ("občas", True), ("ne", False)]:
            self.assertEqual(expected, analyza.eligible("e3b", {"e3a": value}))

    def test_cycling_followup_checks_both_parents(self):
        self.assertTrue(analyza.eligible("e4b", {"e1": ["kolo"], "e4a": "občas"}))
        self.assertFalse(analyza.eligible("e4b", {"e1": ["auto"], "e4a": "ano"}))
        self.assertFalse(analyza.eligible("e4b", {"e1": ["kolo"], "e4a": "ne"}))
        self.assertTrue(analyza.eligible("e4a", {"e1": ["kolo"]}))

    def test_housing_branch_is_or_not_and(self):
        for data in ({"f1a": "velmi vážný"}, {"f1a": "spíše vážný"}, {"f1b": "přímo já"}, {"f1b": "blízkých"}):
            self.assertTrue(analyza.eligible("f3", data))
        self.assertFalse(analyza.eligible("f3", {"f1a": "spíše ne", "f1b": "ne"}))

    def test_child_branches(self):
        expected = {
            "predskolak": {"g1a", "g2", "g3"},
            "zsak": {"g1b", "g1c", "g2", "g3"},
            "ssak": {"g1c", "g2"},
            "ne": set(), "nechci": set(),
        }
        for answer, active in expected.items():
            for key in {"g1a", "g1b", "g1c", "g2", "g3"}:
                with self.subTest(answer=answer, key=key):
                    self.assertEqual(key in active, analyza.eligible(key, {"g0": [answer]}))

    def test_sport_and_safety_branches(self):
        self.assertTrue(analyza.eligible("h1b", {"h1a": "spíše nespokojen/a"}))
        self.assertFalse(analyza.eligible("h1b", {"h1a": "spokojen/a"}))
        self.assertTrue(analyza.eligible("i2", {"i1": "spíše nebezpečně"}))
        self.assertFalse(analyza.eligible("i2", {"i1": "spíše bezpečně"}))

    def test_other_requires_trigger_and_active_parent(self):
        self.assertTrue(analyza.eligible("a2-other", {"a2": ["jiná"]}))
        self.assertFalse(analyza.eligible("a2-other", {"a2": ["zelená"]}))
        self.assertFalse(analyza.eligible("e2-other", {"e1": ["pěšky"], "e2": ["jiné"]}))
        self.assertTrue(analyza.eligible("e2-other", {"e1": ["auto"], "e2": ["jiné"]}))


class AggregationTests(unittest.TestCase):
    def setUp(self):
        self.single = analyza.Question("x", "Question", "radio", "page-x", [("a", "A"), ("b", "B")])
        self.multi = analyza.Question("x", "Question", "checkbox", "page-x", [("a", "A"), ("b", "B"), ("c", "C")], 2)

    def test_single_denominator_and_complete_subset(self):
        stats, counts, complete = analyza.aggregate(self.single, [row({"x": "a"}), row({"x": "b"}, "partial"), row({})])
        self.assertEqual((2, 1, 1), (stats["n"], stats["complete_n"], stats["missing"]))
        self.assertEqual(Counter(a=1, b=1), counts)
        self.assertEqual(Counter(a=1), complete)

    def test_multi_counts_respondents_not_share_of_selections(self):
        stats, counts, _ = analyza.aggregate(self.multi, [row({"x": ["a", "b"]}), row({"x": ["a"]}, "partial")])
        self.assertEqual(2, stats["n"])
        self.assertEqual(3, sum(counts.values()))
        self.assertEqual("100,0", analyza.percent(counts["a"], stats["n"]))
        self.assertEqual("50,0", analyza.percent(counts["b"], stats["n"]))

    def test_invalid_selection_rejected(self):
        for value in (["a", "a"], ["z"], ["a", "b", "c"], "a", [1]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                analyza.choices(self.multi, value)
        with self.assertRaises(ValueError):
            analyza.choices(self.single, ["a"])

    def test_gateway_exclusivity(self):
        q = next(q for q in analyza.questionnaire() if q.key == "g0")
        with self.assertRaises(ValueError):
            analyza.choices(q, ["predskolak", "ne"])
        self.assertEqual(["predskolak", "zsak"], analyza.choices(q, ["predskolak", "zsak"]))

    def test_stale_branch_answer_excluded_and_counted(self):
        q = next(q for q in analyza.questionnaire() if q.key == "g1c")
        rows = [row({"g0": ["ne"], "g1c": "ne"}), row({"g0": ["zsak"], "g1c": "ne"})]
        stats, counts, _ = analyza.aggregate(q, rows)
        self.assertEqual((1, 1, 1), (stats["n"], stats["eligible"], stats["outside_branch"]))
        self.assertEqual(1, counts["ne"])

    def test_mixed_answer_is_flagged_not_silently_changed(self):
        q = next(q for q in analyza.questionnaire() if q.key == "j1")
        stats, counts, _ = analyza.aggregate(q, [row({"j1": ["zubař", "nemám problém"]})])
        self.assertEqual(1, stats["mixed_exclusive"])
        self.assertEqual(1, stats["n"])
        self.assertEqual(2, sum(counts.values()))

    def test_empty_and_whitespace_are_not_no_answers(self):
        for value in (None, "", "  ", []):
            self.assertIsNone(analyza.choices(self.single, value))

    def test_rounding_uses_decimal_half_up(self):
        self.assertEqual("16,3", analyza.percent(26, 160))
        self.assertEqual("63,8", analyza.percent(102, 160))
        self.assertEqual("0,0", analyza.percent(0, 22))
        self.assertEqual("—", analyza.percent(0, 0))

    def test_grouped_children_indicator_is_a_union(self):
        qs = analyza.questionnaire()
        rows = [row({"g0": ["predskolak", "zsak"]}), row({"g0": ["ssak"]}, "partial"), row({"g0": ["ne"]})]
        line = next(line for line in analyza.render_indicators(qs, rows).splitlines() if line.startswith("| g0-deti |"))
        self.assertIn("| 2 | 3 | 66,7 | 1 | 2 | 50,0 |", line)


class PublishedOptionsTests(unittest.TestCase):
    def test_economic_categories_remain_separate(self):
        q = next(q for q in analyza.questionnaire() if q.key == "n3")
        values = [value for value, _ in q.options]
        counts = Counter(dict(zip(values, [40, 30, 8, 2, 10])))
        complete = Counter(dict(zip(values, [38, 27, 7, 1, 9])))
        published = analyza.published_options(q, counts, complete)
        self.assertEqual([(v, label, counts[v], complete[v]) for v, label in q.options], published)
        self.assertEqual(5, len(published))
        self.assertEqual(90, sum(n for _, _, n, _ in published))
        self.assertEqual(8, next(n for key, _, n, _ in published if key.startswith("napjatá")))
        self.assertEqual((2, 1), next((n, completed) for key, _, n, completed in published if key.startswith("tíživá")))
        self.assertEqual(10, next(n for key, _, n, _ in published if key == "nechci odpovědět"))

    def test_housing_categories_remain_separate(self):
        q = next(q for q in analyza.questionnaire() if q.key == "n4")
        counts = Counter({"vlastním bytě": 20, "nájemním bytě": 15, "družstevním bytě": 3, "vlastním domě": 30, "nájemním domě": 4, "jiné": 10, "nechci odpovědět": 8})
        published = analyza.published_options(q, counts, counts)
        self.assertEqual([(v, label, counts[v], counts[v]) for v, label in q.options], published)
        self.assertEqual(7, len(published))
        self.assertEqual(90, sum(n for _, _, n, _ in published))
        self.assertEqual(3, next(n for key, _, n, _ in published if key == "družstevním bytě"))
        self.assertEqual(4, next(n for key, _, n, _ in published if key == "nájemním domě"))
        self.assertEqual(10, next(n for key, _, n, _ in published if key == "jiné"))

    def test_areas_preserve_zero_singleton_and_small_complete_counts(self):
        q = analyza.Question("n5", "Area", "select", "page-n", [("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("bydlím mimo Třebíč", "Outside")])
        counts, complete = Counter(A=8, B=5, C=1), Counter(A=7, B=4)
        published = analyza.published_options(q, counts, complete)
        self.assertEqual([(v, label, counts[v], complete[v]) for v, label in q.options], published)
        self.assertEqual((1, 0), next(item[2:] for item in published if item[0] == "C"))
        self.assertEqual((0, 0), next(item[2:] for item in published if item[0] == "D"))
        self.assertEqual(sum(counts.values()), sum(n for _, _, n, _ in published))


class PrivacyTests(unittest.TestCase):
    def test_text_order_is_question_local_and_preserves_duplicates(self):
        qs = {q.key: q for q in analyza.questionnaire()}
        rows = [row({"l1": f"Návrh {i}", "l3": f"Návrh {i}"}) for i in range(12)]
        a = analyza.text_entries(qs["l1"], rows)
        b = analyza.text_entries(qs["l3"], rows)
        self.assertNotEqual(a, b)
        self.assertEqual(a, analyza.text_entries(qs["l1"], list(reversed(rows))))
        self.assertEqual(2, len(analyza.text_entries(qs["l1"], [row({"l1": "Stejný podnět"}), row({"l1": "Stejný podnět"})])))

    def test_operator_masking_is_only_a_first_pass(self):
        text = "Kontakt private@example.invalid, https://example.invalid/profile, +420 123 456 789, č. p. 123."
        masked = analyza.preview_redaction(text)
        self.assertNotIn("private@", masked)
        self.assertNotIn("https://", masked)
        self.assertNotIn("123 456 789", masked)
        self.assertNotIn("č. p. 123", masked)

    def test_loader_whitelists_fields_and_does_not_modify_sqlite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.db"
            with closing(sqlite3.connect(path)) as db:
                db.execute("CREATE TABLE responses (status TEXT, data TEXT, created_at TEXT, updated_at TEXT)")
                data = {"a2": ["zelená"], "email": "private@example.invalid", "consent": ["ano"], "utm_source": "test"}
                db.execute("INSERT INTO responses VALUES (?, ?, ?, ?)", ("partial", json.dumps(data), "2026-01-01", "2026-01-01"))
                db.commit()
            before = path.read_bytes()
            rows, dates = analyza.load_rows(path)
            self.assertEqual([row({"a2": ["zelená"]}, "partial")], rows)
            self.assertEqual(("2026-01-01",) * 3, dates)
            self.assertEqual(before, path.read_bytes())


class MarkdownSnapshotTests(unittest.TestCase):
    EXPECTED_TEXT_COUNTS = {
        "a2-other": 1, "b2-other": 15, "c1b": 35, "d2-other": 4,
        "e1-other": 2, "e2-other": 6, "e3b": 50, "e4b": 9,
        "f3-other": 3, "g2-other": 5, "g3-other": 3,
        "j1-other": 7, "j2-other": 4, "h1b": 11, "i2": 5, "l1": 81, "l3": 34,
    }

    def test_each_text_field_has_every_paraphrase_once(self):
        self.assertEqual(275, sum(self.EXPECTED_TEXT_COUNTS.values()))
        files = {p.stem for p in (analyza.REPORT / "odpovedi").glob("*.md")}
        self.assertEqual(set(self.EXPECTED_TEXT_COUNTS), files)
        for key, count in self.EXPECTED_TEXT_COUNTS.items():
            text = (analyza.REPORT / "odpovedi" / (key + ".md")).read_text(encoding="utf-8")
            labels = re.findall(r"^- \*\*(\d{3})\.\*\*", text, flags=re.M)
            self.assertEqual([f"{i:03d}" for i in range(1, count + 1)], labels, key)

    def test_no_direct_identifiers_in_markdown_outputs(self):
        patterns = [
            r"[\w.+-]+@[\w.-]+\.[\w-]+",
            r"\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b",
            r"\+420[\s-]*\d",
            r"\b(?:č\.?\s*p\.?|číslo\s+domu)\s*\d",
        ]
        for path in analyza.REPORT.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for pattern in patterns:
                self.assertIsNone(re.search(pattern, text, flags=re.I), path.name)

    def test_all_local_markdown_links_exist(self):
        for path in analyza.REPORT.rglob("*.md"):
            for destination in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" in destination or destination.startswith("#"):
                    continue
                relative = destination.split("#", 1)[0].replace("%20", " ")
                self.assertTrue((path.parent / relative).resolve().exists(), f"Broken link in {path.name}")

    def test_data_has_one_table_section_per_quantitative_question(self):
        text = (analyza.REPORT / "kvantitativni-data.md").read_text(encoding="utf-8")
        keys = [q.key for q in analyza.questionnaire() if q.kind != "text"]
        for key in keys:
            self.assertEqual(1, text.count(f'<a id="{key}"></a>'), key)
        self.assertEqual(15, len(analyza.INDICATORS))

    def test_every_published_table_percentage_and_total(self):
        text = (analyza.REPORT / "kvantitativni-data.md").read_text(encoding="utf-8")
        for q in analyza.questionnaire():
            if q.kind == "text":
                continue
            block = text.split(f'<a id="{q.key}"></a>', 1)[1].split('<a id="', 1)[0]
            match = re.search(r"Platné odpovědi N: \*\*(\d+)\*\*; z toho dokončené N: \*\*(\d+)\*\*", block)
            self.assertIsNotNone(match, q.key)
            n, completed_n = map(int, match.groups())
            totals = [0, 0]
            published_labels = []
            for line in block.splitlines():
                if not line.startswith("| ") or line.startswith("| Hodnota"):
                    continue
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
                self.assertEqual(6, len(cells), q.key)
                published_labels.append(tuple(cells[:2]))
                count, completed = int(cells[2]), int(cells[4])
                self.assertEqual(analyza.percent(count, n), cells[3], q.key)
                self.assertEqual(analyza.percent(completed, completed_n), cells[5], q.key)
                self.assertLessEqual(completed, count, q.key)
                self.assertLessEqual(count, n, q.key)
                self.assertLessEqual(completed, completed_n, q.key)
                totals[0] += count
                totals[1] += completed
            self.assertEqual([(analyza.md(value), analyza.md(label)) for value, label in q.options], published_labels, q.key)
            if q.kind != "checkbox":
                self.assertEqual([n, completed_n], totals, q.key)
            else:
                self.assertGreaterEqual(totals[0], n, q.key)
                self.assertGreaterEqual(totals[1], completed_n, q.key)
                if q.maximum:
                    self.assertLessEqual(totals[0], n * q.maximum, q.key)
                    self.assertLessEqual(totals[1], completed_n * q.maximum, q.key)

    def test_headline_percentages_match_their_counts(self):
        text = (analyza.REPORT / "VYSLEDKY.md").read_text(encoding="utf-8")
        headlines = re.findall(r"(?m)^\|.*\| (\d+) (?:z|ze) (\d+) \| (\d+,\d+) % \|", text)
        self.assertEqual(7, len(headlines))
        for count, n, displayed in headlines:
            self.assertEqual(analyza.percent(int(count), int(n)), displayed)

    def test_presentation_covers_all_questions(self):
        text = (analyza.REPORT / "PREZENTACE.md").read_text(encoding="utf-8")
        for q in analyza.questionnaire():
            entries = re.findall(rf"(?m)^\| {re.escape(q.key)}(?: \(L2\))? \|", text)
            self.assertEqual(1, len(entries), q.key)

    def test_public_data_excludes_internal_fingerprints(self):
        for filename in ("VYSLEDKY.md", "kvantitativni-data.md", "PREZENTACE.md"):
            text = (analyza.REPORT / filename).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\b[0-9a-f]{64}\b")

    def test_private_directories_excluded_from_deployment(self):
        workflow = (analyza.ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
        self.assertIn("--exclude-glob 'report/'", workflow)
        self.assertIn("--exclude-glob 'backup/'", workflow)


if __name__ == "__main__":
    unittest.main()