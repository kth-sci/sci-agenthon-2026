import json
import unittest
from pathlib import Path

from eval.validate_rubric import RubricError, validate, summarise

FIXTURES = Path(__file__).parent.parent / "rubric" / "_fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestValidate(unittest.TestCase):
    def test_valid_minimal_passes(self):
        # Should not raise
        validate(load("valid_minimal.json"))

    def test_bad_item_sum_raises(self):
        with self.assertRaises(RubricError) as cx:
            validate(load("bad_item_sum.json"))
        self.assertIn("problem 1", str(cx.exception))
        self.assertIn("0.9", str(cx.exception))

    def test_unsupported_special_case_effect_raises(self):
        with self.assertRaises(RubricError) as cx:
            validate(load("bad_special_case_effect.json"))
        self.assertIn("effect", str(cx.exception))
        self.assertIn("set_total", str(cx.exception))

    def test_floating_point_tolerance(self):
        # 0.1 + 0.2 == 0.30000000000000004 — validator must tolerate this
        rubric = {
            "exam_id": "T",
            "global_deductions": [],
            "problems": [{
                "n": 1, "max_points": 0.3,
                "items": [
                    {"id": "a", "label": "a", "points": 0.1},
                    {"id": "b", "label": "b", "points": 0.2},
                ],
                "special_cases": []
            }]
        }
        validate(rubric)  # must not raise

    def test_sub_points_exceeding_parent_raises(self):
        # A sub-point total larger than its parent is a carve-out violation.
        # Parents still sum to max_points (1.0) so the sub-check is what fires.
        rubric = {
            "exam_id": "T",
            "global_deductions": [],
            "problems": [{
                "n": 1, "max_points": 1.0,
                "items": [
                    {"id": "a", "label": "a", "points": 0.1,
                     "sub": [{"label": "oops", "points": 0.4}]},
                    {"id": "b", "label": "b", "points": 0.9},
                ],
                "special_cases": []
            }]
        }
        with self.assertRaises(RubricError) as cx:
            validate(rubric)
        self.assertIn("sub-points", str(cx.exception))

    def test_sub_points_within_parent_ok(self):
        rubric = {
            "exam_id": "T",
            "global_deductions": [],
            "problems": [{
                "n": 1, "max_points": 1.0,
                "items": [
                    {"id": "a", "label": "a", "points": 0.4,
                     "sub": [{"label": "ok", "points": 0.2}]},
                    {"id": "b", "label": "b", "points": 0.6},
                ],
                "special_cases": []
            }]
        }
        validate(rubric)  # sub 0.2 <= parent 0.4: must not raise


class TestSummarise(unittest.TestCase):
    def test_summary_lists_each_problem(self):
        md = summarise(load("valid_minimal.json"))
        self.assertIn("Problem 1", md)
        self.assertIn("2 items", md)
        self.assertIn("1 special case", md)
        self.assertIn("1 sub-point", md)
        self.assertIn("1 global deduction", md)


if __name__ == "__main__":
    unittest.main()
