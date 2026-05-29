import unittest

from eval.compare_to_human import letter_grade


class TestLetterGrade(unittest.TestCase):
    def test_boundaries(self):
        cases = [
            (2.79, 0.0, "F"),
            (2.80, 0.0, "Fx"),
            (2.89, 0.0, "Fx"),
            (2.90, 0.0, "E"),
            (2.99, 0.0, "E"),
            (3.00, 0.0, "D"),
            (3.00, 0.59, "D"),
            (3.00, 0.60, "C"),
            (3.00, 1.09, "C"),
            (3.00, 1.10, "B"),
            (3.00, 1.99, "B"),
            (3.00, 2.00, "A"),
            (5.00, 3.00, "A"),
        ]
        for a, b, expected in cases:
            with self.subTest(a_del=a, b_del=b):
                self.assertEqual(letter_grade(a, b), expected)


from eval.compare_to_human import parse_tolerance_note


class TestParseToleranceNote(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(parse_tolerance_note(None), {})
        self.assertEqual(parse_tolerance_note(""), {})
        self.assertEqual(parse_tolerance_note("   "), {})

    def test_single_raise(self):
        self.assertEqual(
            parse_tolerance_note("kan höjas 0,1 p på tal 7"),
            {7: (0.0, 0.1)},
        )

    def test_single_lower(self):
        self.assertEqual(
            parse_tolerance_note("kan sänkas 0,1 p på tal 2"),
            {2: (-0.1, 0.0)},
        )

    def test_two_problems_och(self):
        self.assertEqual(
            parse_tolerance_note("kan höjas 0,1 p på tal 3 och tal 4"),
            {3: (0.0, 0.1), 4: (0.0, 0.1)},
        )

    def test_two_problems_plus(self):
        self.assertEqual(
            parse_tolerance_note("kan höjas 0,1 p på tal 3+4"),
            {3: (0.0, 0.1), 4: (0.0, 0.1)},
        )

    def test_comma_combined(self):
        self.assertEqual(
            parse_tolerance_note(
                "kan sänkas 0,1 p på tal 2, kan höjas 0,1 p på tal 3+4"
            ),
            {2: (-0.1, 0.0), 3: (0.0, 0.1), 4: (0.0, 0.1)},
        )

    def test_semicolon_combined_with_typo(self):
        # Missing "p" after "0,1" — tolerated typo seen in the workbook
        self.assertEqual(
            parse_tolerance_note(
                "kan sänkas 0,1 p på tal 2; kan höjas 0,1 på tal 7"
            ),
            {2: (-0.1, 0.0), 7: (0.0, 0.1)},
        )

    def test_unparseable_logs_and_returns_empty(self):
        # An unrecognised note returns {} (caller falls back to [grade, grade])
        self.assertEqual(parse_tolerance_note("kommentar om bedömning"), {})


import tempfile
from pathlib import Path

from eval.compare_to_human import read_jsonl, JsonlError


class TestReadJsonl(unittest.TestCase):
    def test_reads_well_formed(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write('{"canvas_id": "185729", "a_del": 2.5}\n')
            f.write('{"canvas_id": "184115", "a_del": 3.4}\n')
            path = Path(f.name)
        rows = list(read_jsonl(path))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["canvas_id"], "185729")

    def test_blank_lines_skipped(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write('{"a": 1}\n')
            f.write('\n')
            f.write('   \n')
            f.write('{"a": 2}\n')
            path = Path(f.name)
        rows = list(read_jsonl(path))
        self.assertEqual([r["a"] for r in rows], [1, 2])

    def test_malformed_line_reports_line_number(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write('{"a": 1}\n')
            f.write('not json at all\n')
            f.write('{"a": 3}\n')
            path = Path(f.name)
        with self.assertRaises(JsonlError) as cx:
            list(read_jsonl(path))
        self.assertIn("line 2", str(cx.exception))


from eval.compare_to_human import read_xlsx_human_grades, XLSX_PATH


class TestReadXlsx(unittest.TestCase):
    def test_returns_all_students(self):
        students, thresholds = read_xlsx_human_grades(XLSX_PATH)
        self.assertEqual(len(students), 155)

    def test_canvas_ids_are_strings_no_loss(self):
        students, _ = read_xlsx_human_grades(XLSX_PATH)
        # Abedian is the first row
        abedian = next(s for s in students if s["name"].startswith("Abedian"))
        self.assertEqual(abedian["canvas_id"], "185729")
        # Per-problem scores
        self.assertAlmostEqual(abedian["tal"][1], 0.9, places=2)
        self.assertEqual(abedian["betyg"], "C")

    def test_dash_means_not_attempted(self):
        students, _ = read_xlsx_human_grades(XLSX_PATH)
        # Ahlinder did only Del A
        ahlinder = next(s for s in students if s["name"].startswith("Ahlinder"))
        self.assertIsNone(ahlinder["tal"].get(6))
        self.assertIsNone(ahlinder["tal"].get(7))

    def test_thresholds_match_spec(self):
        _, thresholds = read_xlsx_human_grades(XLSX_PATH)
        # (a_del_min, b_del_min) per spec §9
        self.assertEqual(thresholds["Fx"], (2.8, 0.0))
        self.assertEqual(thresholds["E"], (2.9, 0.0))
        self.assertEqual(thresholds["D"], (3.0, 0.0))
        self.assertEqual(thresholds["C"], (3.0, 0.6))
        self.assertEqual(thresholds["B"], (3.0, 1.1))
        self.assertEqual(thresholds["A"], (3.0, 2.0))


from eval.compare_to_human import join_students, build_rows, JsonlError


class TestBuildRows(unittest.TestCase):
    def _human(self):
        return [{"canvas_id": "1", "name": "T", "tal": {n: 0.0 for n in range(1, 9)},
                 "a_del": 2.9, "b_del": 0.0, "betyg": "E", "poangjustering": ""}]

    def _agent(self, a_del, b_del):
        pr = {str(n): {"points": 0.0, "max_points": 1.0} for n in range(1, 9)}
        return [{"canvas_id": "1", "name": "T", "a_del": a_del, "b_del": b_del,
                 "problem_results": pr, "flags": []}]

    def test_float_dust_does_not_flip_grade(self):
        # 2.9000000000000004 must round to 2.9 -> E, not be mislabelled.
        rows, _, _ = build_rows(self._agent(2.9000000000000004, 0.0), self._human())
        self.assertEqual(rows[0].agent_betyg, "E")

    def test_missing_problem_key_raises(self):
        bad = self._agent(3.0, 0.0)
        del bad[0]["problem_results"]["8"]
        with self.assertRaises(JsonlError):
            build_rows(bad, self._human())


class TestJoinStudents(unittest.TestCase):
    def test_matched_pairs(self):
        agent = [{"canvas_id": "1", "name": "A"}, {"canvas_id": "2", "name": "B"}]
        human = [{"canvas_id": "1", "name": "A"}, {"canvas_id": "2", "name": "B"}]
        matched, only_agent, only_human = join_students(agent, human)
        self.assertEqual(len(matched), 2)
        self.assertEqual(matched[0][0]["canvas_id"], "1")
        self.assertEqual(matched[0][1]["canvas_id"], "1")
        self.assertEqual(only_agent, [])
        self.assertEqual(only_human, [])

    def test_missing_on_agent_side(self):
        agent = [{"canvas_id": "1"}]
        human = [{"canvas_id": "1"}, {"canvas_id": "2"}]
        matched, only_agent, only_human = join_students(agent, human)
        self.assertEqual(len(matched), 1)
        self.assertEqual(only_agent, [])
        self.assertEqual([s["canvas_id"] for s in only_human], ["2"])

    def test_missing_on_human_side(self):
        agent = [{"canvas_id": "1"}, {"canvas_id": "2"}]
        human = [{"canvas_id": "1"}]
        matched, only_agent, only_human = join_students(agent, human)
        self.assertEqual([s["canvas_id"] for s in only_agent], ["2"])
        self.assertEqual(only_human, [])


if __name__ == "__main__":
    unittest.main()
