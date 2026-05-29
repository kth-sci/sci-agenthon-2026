# SK1110 Auto-Grader — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a working Claude Code workflow that grades the 9 SK1110 exam submissions problem-by-problem against the teacher's rubric, plus a comparison report against the human-graded ground truth.

**Architecture:** A single Claude Code skill (`grade-sk1110-exam`) drives grading: load context once, index pages, run a per-problem rubric loop, emit structured JSONL. A small stdlib-only Python module validates the hand-built rubric JSON and compares the agent's output to the teacher's XLSX. Tests cover the deterministic helpers; the skill itself is validated by a smoke test on one student before the full run.

**Tech Stack:** Python 3 (stdlib only — `json`, `csv`, `re`, `zipfile`, `xml.etree.ElementTree`, `unittest`). Claude Code skill (Markdown with YAML frontmatter). JSONL for agent output. CSV + Markdown for eval reports.

**Source of truth:** [docs/superpowers/specs/2026-05-26-sk1110-auto-grader-phase1-design.md](../specs/2026-05-26-sk1110-auto-grader-phase1-design.md) — refer to it for any ambiguity in this plan.

---

## Task 1: Project skeleton

**Files:**
- Create: `rubric/.gitkeep`
- Create: `eval/__init__.py`
- Create: `results/.gitkeep`
- Create: `results/page_index/.gitkeep`
- Create: `.claude/skills/grade-sk1110-exam/.gitkeep`

- [ ] **Step 1: Create directories and placeholders**

```bash
mkdir -p rubric eval results/page_index .claude/skills/grade-sk1110-exam
touch rubric/.gitkeep results/.gitkeep results/page_index/.gitkeep .claude/skills/grade-sk1110-exam/.gitkeep
printf '' > eval/__init__.py
```

- [ ] **Step 2: Verify layout**

Run: `find rubric eval results .claude/skills/grade-sk1110-exam -type f | sort`
Expected output (in this order):
```
.claude/skills/grade-sk1110-exam/.gitkeep
eval/__init__.py
results/.gitkeep
results/page_index/.gitkeep
rubric/.gitkeep
```

- [ ] **Step 3: Update .gitignore so the placeholders survive but results stay private**

The .gitignore already excludes `results/`. Add an override for the `.gitkeep` placeholders so the directory structure is committed:

Edit `.gitignore`, find the line `results/`, and append below it:
```
!results/.gitkeep
!results/page_index/
!results/page_index/.gitkeep
```

- [ ] **Step 4: Commit**

```bash
git add rubric/.gitkeep eval/__init__.py results/.gitkeep results/page_index/.gitkeep .claude/skills/grade-sk1110-exam/.gitkeep .gitignore
git commit -m "chore: scaffold rubric/, eval/, results/, and skill dirs"
```

---

## Task 2: Rubric validator — tests first

**Files:**
- Create: `eval/validate_rubric.py`
- Create: `eval/test_validate_rubric.py`
- Create: `rubric/_fixtures/valid_minimal.json`
- Create: `rubric/_fixtures/bad_item_sum.json`
- Create: `rubric/_fixtures/bad_special_case_effect.json`

The validator must:
1. Assert per-problem `items[].points` (parent values only) sum to `max_points`.
2. Assert every `special_cases[].effect == "set_total"` (Phase 1 only supports that mode).
3. Emit `results/rubric_summary.md` listing per problem: item count, line-item total, special-case count, sub-point count.

- [ ] **Step 1: Write the fixture files**

`rubric/_fixtures/valid_minimal.json`:
```json
{
  "exam_id": "TEST",
  "global_deductions": [
    {"id": "g1", "label": "test deduction", "points": -0.1}
  ],
  "problems": [
    {
      "n": 1,
      "max_points": 1.0,
      "items": [
        {"id": "1.a", "label": "step a", "points": 0.5},
        {"id": "1.b", "label": "step b", "points": 0.5,
         "sub": [{"label": "sub", "points": 0.2}]}
      ],
      "special_cases": [
        {"id": "sc1", "label": "case", "effect": "set_total",
         "total_points": 0.4, "apply_global_deductions": false}
      ]
    }
  ]
}
```

`rubric/_fixtures/bad_item_sum.json` (parents sum to 0.9, not 1.0):
```json
{
  "exam_id": "BAD",
  "global_deductions": [],
  "problems": [
    {
      "n": 1,
      "max_points": 1.0,
      "items": [
        {"id": "1.a", "label": "a", "points": 0.5},
        {"id": "1.b", "label": "b", "points": 0.4}
      ],
      "special_cases": []
    }
  ]
}
```

`rubric/_fixtures/bad_special_case_effect.json` (unsupported `effect`):
```json
{
  "exam_id": "BAD",
  "global_deductions": [],
  "problems": [
    {
      "n": 1,
      "max_points": 1.0,
      "items": [
        {"id": "1.a", "label": "a", "points": 1.0}
      ],
      "special_cases": [
        {"id": "sc1", "label": "case", "effect": "cap_total",
         "total_points": 0.6, "apply_global_deductions": false}
      ]
    }
  ]
}
```

- [ ] **Step 2: Write the failing tests**

`eval/test_validate_rubric.py`:
```python
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
```

- [ ] **Step 3: Run the tests, confirm they fail**

Run: `python3 -m unittest eval.test_validate_rubric -v`
Expected: `ModuleNotFoundError: No module named 'eval.validate_rubric'` (or similar import error).

- [ ] **Step 4: Implement `eval/validate_rubric.py`**

```python
"""Validate the hand-built rubric JSON and emit a human-review summary."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

SUPPORTED_EFFECTS = {"set_total"}
POINT_TOLERANCE = 1e-6


class RubricError(ValueError):
    """Raised when the rubric JSON violates Phase 1 constraints."""


def validate(rubric: dict[str, Any]) -> None:
    """Raise RubricError if the rubric is malformed; return None on success."""
    for problem in rubric.get("problems", []):
        n = problem["n"]
        items = problem.get("items", [])
        item_sum = sum(item["points"] for item in items)
        max_points = problem["max_points"]
        if not math.isclose(item_sum, max_points, abs_tol=POINT_TOLERANCE):
            raise RubricError(
                f"problem {n}: item points sum to {item_sum:g}, "
                f"expected {max_points:g}"
            )
        for sc in problem.get("special_cases", []):
            effect = sc.get("effect")
            if effect not in SUPPORTED_EFFECTS:
                raise RubricError(
                    f"problem {n}, special_case {sc.get('id')!r}: "
                    f"effect {effect!r} unsupported; expected one of "
                    f"{sorted(SUPPORTED_EFFECTS)} (currently only 'set_total')"
                )


def summarise(rubric: dict[str, Any]) -> str:
    """Return a Markdown summary of the rubric for human review."""
    lines: list[str] = []
    lines.append(f"# Rubric summary — {rubric.get('exam_id', '?')}")
    lines.append("")
    gd_count = len(rubric.get("global_deductions", []))
    lines.append(f"{gd_count} global deduction{'s' if gd_count != 1 else ''}.")
    lines.append("")
    for problem in rubric.get("problems", []):
        n = problem["n"]
        items = problem.get("items", [])
        sub_count = sum(len(it.get("sub", [])) for it in items)
        sc_count = len(problem.get("special_cases", []))
        item_sum = sum(it["points"] for it in items)
        lines.append(
            f"## Problem {n} (max {problem['max_points']:g} p)"
        )
        lines.append(
            f"- {len(items)} items, line-item total {item_sum:g} p"
        )
        lines.append(
            f"- {sub_count} sub-point{'s' if sub_count != 1 else ''}"
        )
        lines.append(
            f"- {sc_count} special case{'s' if sc_count != 1 else ''}"
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_rubric.py <rubric.json>", file=sys.stderr)
        return 2
    rubric_path = Path(argv[1])
    rubric = json.loads(rubric_path.read_text())
    try:
        validate(rubric)
    except RubricError as err:
        print(f"INVALID: {err}", file=sys.stderr)
        return 1
    summary = summarise(rubric)
    out = Path("results/rubric_summary.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(summary)
    print(f"OK: {rubric_path} — summary written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 5: Run the tests, confirm they pass**

Run: `python3 -m unittest eval.test_validate_rubric -v`
Expected: `OK` with 5 tests passing.

- [ ] **Step 6: Commit**

```bash
git add eval/validate_rubric.py eval/test_validate_rubric.py rubric/_fixtures/
git commit -m "feat(eval): rubric validator with tests"
```

---

## Task 3: Build rubric JSON — problem 1

**Files:**
- Create: `rubric/sk1110-260309.json`

The full rubric is in `Grading_rules/Rättningsmall 260309.pdf`. Problem 1 is the example in the spec (§4).

- [ ] **Step 1: Write problem 1 plus the global deductions**

Create `rubric/sk1110-260309.json`:
```json
{
  "exam_id": "SK1110-260309",
  "global_deductions": [
    {"id": "missing_unit_answer", "label": "Enhet saknas i svaret", "points": -0.2},
    {"id": "missing_unit_intermediate", "label": "Enhet saknas på många mellanresultat", "points": -0.1},
    {"id": "unreasonable_answer", "label": "Orimligt svar", "points": -0.2},
    {"id": "unreasonable_noted", "label": "Orimligt svar men med kommentar om orimlighet", "points": 0.0},
    {"id": "correct_but_called_unreasonable", "label": "Rätt/rimligt svar men med kommentar om orimlighet", "points": -0.2},
    {"id": "unit_error_wrong_answer", "label": "Enhetsfel som leder till fel svar", "points": -0.2},
    {"id": "dimension_error", "label": "Dimensionsfel", "points": -0.2},
    {"id": "rounding_error", "label": "Avrundningsfel (>1 värdesiffra fel)", "points": -0.1},
    {"id": "arithmetic_slip", "label": "Räknefel/slarvfel utan orimligt svar", "points": -0.1}
  ],
  "problems": [
    {
      "n": 1,
      "max_points": 1.0,
      "items": [
        {"id": "1.a", "label": "Omvandla ljudintensitetsnivå till ljudintensitet", "points": 0.3},
        {"id": "1.b", "label": "Uttryck för hur intensitet beror av effekt och avstånd", "points": 0.2,
         "sub": [{"label": "korrekt utformad absorption", "points": 0.1}]},
        {"id": "1.c", "label": "Lösa ut effekten", "points": 0.2,
         "sub": [{"label": "utan/felaktigt utformad absorbans, sub-point forfeit", "points": 0.1}]},
        {"id": "1.d", "label": "Sätta in och räkna ut effekten", "points": 0.3,
         "sub": [{"label": "sätta in rätt absorbans", "points": 0.2}]}
      ],
      "special_cases": [
        {"id": "no_absorption", "label": "Räknat utan absorption (eller felaktigt utformad)",
         "effect": "set_total", "total_points": 0.6, "apply_global_deductions": false},
        {"id": "positive_iL", "label": "Positivt värde på ljudintensitetsnivån",
         "effect": "set_total", "total_points": 0.8, "apply_global_deductions": false}
      ]
    }
  ]
}
```

- [ ] **Step 2: Validate**

Run: `python3 eval/validate_rubric.py rubric/sk1110-260309.json`
Expected: `OK: rubric/sk1110-260309.json — summary written to results/rubric_summary.md`

- [ ] **Step 3: Eyeball the summary**

Run: `cat results/rubric_summary.md`
Expected: a single problem block listing `4 items`, line-item total `1 p`, `3 sub-points`, `2 special cases`, plus `9 global deductions` in the header.

- [ ] **Step 4: Commit**

```bash
git add rubric/sk1110-260309.json
git commit -m "feat(rubric): add problem 1 + global deductions"
```

---

## Task 4: Build rubric JSON — Del A problems 2–5

**Files:**
- Modify: `rubric/sk1110-260309.json`

Source: `Grading_rules/Rättningsmall 260309.pdf` pages 1–2. Each problem's rubric is in red+black ink — black is line items, red is special cases.

- [ ] **Step 1: Add problems 2 through 5 to the `problems` array**

Append to `problems` (after problem 1), keeping JSON valid:

```json
    {
      "n": 2,
      "max_points": 1.0,
      "items": [
        {"id": "2.a", "label": "Förstå att elektrisk effekt blir till värme i motstånd", "points": 0.1},
        {"id": "2.b", "label": "Rätt uträknad elektrisk effekt P", "points": 0.2,
         "sub": [{"label": "P = U^2/R", "points": 0.1}]},
        {"id": "2.c", "label": "Rätt uträknad resistans R", "points": 0.2,
         "sub": [{"label": "R = rho L / A", "points": 0.1}]},
        {"id": "2.d", "label": "Rätt uträknad tvärsnittsarea", "points": 0.3,
         "sub": [{"label": "A = pi r^2", "points": 0.1}]},
        {"id": "2.e", "label": "Rätt uträknad diameter", "points": 0.2}
      ],
      "special_cases": [
        {"id": "factor_sqrt1000", "label": "Fel faktor sqrt(1000)",
         "effect": "set_total", "total_points": 0.9, "apply_global_deductions": false},
        {"id": "factor_1000_uncommented", "label": "Fel faktor 1000 utan kommentar om orimlighet",
         "effect": "set_total", "total_points": 0.7, "apply_global_deductions": false},
        {"id": "rc_circuit", "label": "Räknat på RC-krets för att hitta R",
         "effect": "set_total", "total_points": 0.6, "apply_global_deductions": false}
      ]
    },
    {
      "n": 3,
      "max_points": 1.0,
      "items": [
        {"id": "3.a", "label": "Förstå att cirkelbanan bestäms av Lorentzkraften", "points": 0.1},
        {"id": "3.b", "label": "F = qvB", "points": 0.2},
        {"id": "3.c", "label": "Rätt uträknad hastighet v", "points": 0.3,
         "sub": [{"label": "E_kin = m v^2 / 2", "points": 0.1}]},
        {"id": "3.d", "label": "Rätt uträknad radie r", "points": 0.3,
         "sub": [{"label": "r = m v / (q B)", "points": 0.1}]},
        {"id": "3.e", "label": "Rätt uträknat avstånd från jordytan", "points": 0.1,
         "sub": [{"label": "Rätt figur på sökt avstånd", "points": 0.1}]}
      ],
      "special_cases": [
        {"id": "circle_around_earth", "label": "Cirkelbana utritad runt jorden men rätt svar",
         "effect": "set_total", "total_points": 0.9, "apply_global_deductions": false},
        {"id": "proton_creates_b", "label": "Protonen skapar magnetfältet",
         "effect": "set_total", "total_points": 0.5, "apply_global_deductions": false},
        {"id": "gravity_with_v", "label": "Gravitationskraften med rätt hastighet",
         "effect": "set_total", "total_points": 0.5, "apply_global_deductions": false}
      ]
    },
    {
      "n": 4,
      "max_points": 1.0,
      "items": [
        {"id": "4.a", "label": "Rayleigh-kriteriet i någon form (i objekt/bild, som höjd/vinkel)", "points": 0.2},
        {"id": "4.b", "label": "Sätta in rätt lambda och D", "points": 0.2},
        {"id": "4.c", "label": "Räkna ut s och/eller s' från förstoring och fokallängd", "points": 0.3},
        {"id": "4.d", "label": "Jämföra resultat med pixelstorlek", "points": 0.1},
        {"id": "4.e", "label": "Svara i objektsrymden (och jämföra pixel i rätt rymd)", "points": 0.2}
      ],
      "special_cases": [
        {"id": "f_instead_of_sprime", "label": "Räkna med f istället för s', rätt i övrigt",
         "effect": "set_total", "total_points": 0.7, "apply_global_deductions": false},
        {"id": "tried_s_sprime_failed", "label": "Försöka ta fram s och s' men misslyckas, rätt i övrigt",
         "effect": "set_total", "total_points": 0.7, "apply_global_deductions": false},
        {"id": "sprime_when_resolution_matches_pixel", "label": "Räknat ut s' när upplösningen matchar pixelstorlek, fel f/m",
         "effect": "set_total", "total_points": 0.7, "apply_global_deductions": false},
        {"id": "resolution_matches_pixel", "label": "Matchar upplösningen med pixelstorlek",
         "effect": "set_total", "total_points": 0.7, "apply_global_deductions": false},
        {"id": "max_resolution_from_pixel", "label": "Räkna ut maximal upplösning från pixelstorlek (1,6 µm)",
         "effect": "set_total", "total_points": 0.3, "apply_global_deductions": false}
      ]
    },
    {
      "n": 5,
      "max_points": 1.0,
      "items": [
        {"id": "5.a.1", "label": "Anta ett rimligt bildavstånd vilket ger värdet på f", "points": 0.1},
        {"id": "5.a.2", "label": "Använda linsmakarformeln", "points": 0.1},
        {"id": "5.a.3", "label": "Sätta oändlig krökningsradie på den plana ytan", "points": 0.1},
        {"id": "5.a.4", "label": "Lösa ut och beräkna andra krökningsradien", "points": 0.1},
        {"id": "5.a.5", "label": "Skissa linsens form", "points": 0.1},
        {"id": "5.b.1", "label": "Tydligt visa att krökningsradien minskar med 5 mm",
         "points": 0.2,
         "sub": [{"label": "endast konstaterande utan motivering", "points": 0.1}]},
        {"id": "5.b.2", "label": "Sätta in och beräkna ny fokallängd (inkl. andra ytan plan)", "points": 0.1},
        {"id": "5.b.3", "label": "Presentera skillnaden tydligt med rätt enhet och tecken", "points": 0.2}
      ],
      "special_cases": [
        {"id": "spherical_interface", "label": "Räkna på en sfärisk gränsyta",
         "effect": "set_total", "total_points": 0.6, "apply_global_deductions": false}
      ]
    }
```

(Insert with a trailing comma after problem 1's closing `}` and before this block.)

- [ ] **Step 2: Validate**

Run: `python3 eval/validate_rubric.py rubric/sk1110-260309.json`
Expected: `OK`. If validator complains about a per-problem sum, recheck the rubric PDF — sub-points are carve-outs of their parent and do NOT add to `max_points`.

- [ ] **Step 3: Commit**

```bash
git add rubric/sk1110-260309.json
git commit -m "feat(rubric): add Del A problems 2-5"
```

---

## Task 5: Build rubric JSON — Del B problems 6–8

**Files:**
- Modify: `rubric/sk1110-260309.json`

Source: `Grading_rules/Rättningsmall 260309.pdf` page 3.

- [ ] **Step 1: Append problems 6, 7, 8**

```json
    {
      "n": 6,
      "max_points": 1.0,
      "items": [
        {"id": "6.a", "label": "B-fält för kort spole", "points": 0.1},
        {"id": "6.b", "label": "Rätt approximation vid Z=10 m", "points": 0.1},
        {"id": "6.c", "label": "Rätt uträknad radie på spole a = 0,04 m", "points": 0.3},
        {"id": "6.d", "label": "Rätt uträknad induktans L = 1,13 mH", "points": 0.4,
         "sub": [
           {"label": "Rätt formel för induktans", "points": 0.1},
           {"label": "Rätt B-fält i spolen", "points": 0.1},
           {"label": "Rätt magnetiskt flöde", "points": 0.1}
         ]},
        {"id": "6.e", "label": "Rätt uträknad kapacitans C = 0,1 nF", "points": 0.1,
         "sub": [{"label": "Rätt formel för resonansfrekvens", "points": 0.1}]}
      ],
      "special_cases": [
        {"id": "forgot_n_factor", "label": "Glömt faktor N i induktans",
         "effect": "set_total", "total_points": 0.8, "apply_global_deductions": false},
        {"id": "right_radius_wrong_l_right_c", "label": "Rätt radie och rätt C givet fel L",
         "effect": "set_total", "total_points": 0.6, "apply_global_deductions": false},
        {"id": "right_method_no_numbers", "label": "Helt rätt lösningsgång men inga uträknade värden",
         "effect": "set_total", "total_points": 0.6, "apply_global_deductions": false}
      ]
    },
    {
      "n": 7,
      "max_points": 1.0,
      "items": [
        {"id": "7.a", "label": "i1' = i2 = 30 deg", "points": 0.2,
         "sub": [{"label": "Rätt figur med strålen parallell med sidan", "points": 0.1}]},
        {"id": "7.b", "label": "i1 = i2' = 41 deg", "points": 0.4,
         "sub": [{"label": "Snells lag", "points": 0.1}]},
        {"id": "7.c", "label": "Rätt uträknad brytningsvinkel", "points": 0.2,
         "sub": [{"label": "Rätt formel brytningsvinkel delta_m = 2i - alpha", "points": 0.1}]},
        {"id": "7.d", "label": "Rätt våglängdsberoende på brytningsindex / dispersion", "points": 0.1},
        {"id": "7.e", "label": "Motivering hur brytningsindex påverkar brytningsvinkeln", "points": 0.1}
      ],
      "special_cases": [
        {"id": "small_angle_approx", "label": "Korrekt lösning för små vinklar (sin(i) = i)",
         "effect": "set_total", "total_points": 0.7, "apply_global_deductions": false}
      ]
    },

NOTE on problem 7: the rubric PDF also lists "Formel minimideviation n = sin((α+δ_m)/2)/sin(α/2) 0,2 p" in red. This is an alternative-path credit that does not fit the `set_total` model (0.2 p is too low to be a final-score override). Phase 1 omits it — the agent's normal line-item grading should award similar credit informally if the student used this formula. Flag for Phase 2 to add an `alternative_path` effect.
    {
      "n": 8,
      "max_points": 1.0,
      "items": [
        {"id": "8.a", "label": "Rätt formel diffraktion cirkulär öppning", "points": 0.2},
        {"id": "8.b", "label": "theta_max = 1,34 theta_min", "points": 0.1},
        {"id": "8.c", "label": "Rätt formel för första ringens maximum", "points": 0.3},
        {"id": "8.d", "label": "Uppmätt avstånd på 3 mm för månens synvinkel", "points": 0.1},
        {"id": "8.e", "label": "Rätt figur över intensiteten eller vinklar", "points": 0.1,
         "sub": [{"label": "Rätt uppmätta vinklar blå=1-1.2 deg, röd=1.5-1.7 deg", "points": 0.4}]},
        {"id": "8.f", "label": "Rätt antagna 2 våglängder (450, 550, 650 nm)", "points": 0.1},
        {"id": "8.g", "label": "Rätt uträknad diameter", "points": 0.1}
      ],
      "special_cases": [
        {"id": "interference_not_diffraction", "label": "Räknat på interferens mellan spalter/gitter",
         "effect": "set_total", "total_points": 0.5, "apply_global_deductions": false},
        {"id": "only_one_wavelength", "label": "Räknat på endast en våglängd",
         "effect": "set_total", "total_points": 0.8, "apply_global_deductions": false}
      ]
    }
```

NOTE: Problem 7's rubric mixes part (a) and part (b) items; the IDs `7.b1` / `7.b2` cover part (b). Problem 8's sub-point of 0.4 p is a true carve-out (the rubric lists "Rätt figur ... 0,1 p" with sub "Rätt uppmätta vinklar ... 0,4 p"); per spec §4, this is a deduct-if-missing carve-out — verify the parent points stay 0.1 p after this structure passes the validator.

If the validator rejects this on item-sum grounds, re-read pp. 3 of the rubric PDF and fix the structure here rather than papering over it.

- [ ] **Step 2: Validate**

Run: `python3 eval/validate_rubric.py rubric/sk1110-260309.json`
Expected: `OK`.

- [ ] **Step 3: Eyeball the full summary**

Run: `cat results/rubric_summary.md`
Expected: 8 problem blocks, each with `max 1 p`, `line-item total 1 p`, plus various sub-point and special-case counts.

- [ ] **Step 4: Commit**

```bash
git add rubric/sk1110-260309.json
git commit -m "feat(rubric): add Del B problems 6-8 (rubric complete)"
```

---

## Task 6: Eval helper — `letter_grade()`

**Files:**
- Create: `eval/compare_to_human.py`
- Create: `eval/test_compare.py`

- [ ] **Step 1: Write the failing test**

`eval/test_compare.py`:
```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run, confirm fail**

Run: `python3 -m unittest eval.test_compare -v`
Expected: `ImportError: cannot import name 'letter_grade' from 'eval.compare_to_human'` (or ModuleNotFoundError).

- [ ] **Step 3: Implement `letter_grade()`**

Create `eval/compare_to_human.py`:
```python
"""Compare agent grades (JSONL) to human ground truth (XLSX) for SK1110."""
from __future__ import annotations


def letter_grade(a_del: float, b_del: float) -> str:
    """Deterministic letter-grade rule per spec §9.

    Matches sheet2 of the SK1110 ground-truth workbook:
        F:  a_del < 2.8
        Fx: 2.8 <= a_del < 2.9
        E:  2.9 <= a_del < 3.0
        D:  a_del >= 3.0 and b_del < 0.6
        C:  a_del >= 3.0 and 0.6 <= b_del < 1.1
        B:  a_del >= 3.0 and 1.1 <= b_del < 2.0
        A:  a_del >= 3.0 and b_del >= 2.0
    """
    if a_del < 2.8:
        return "F"
    if a_del < 2.9:
        return "Fx"
    if a_del < 3.0:
        return "E"
    if b_del < 0.6:
        return "D"
    if b_del < 1.1:
        return "C"
    if b_del < 2.0:
        return "B"
    return "A"
```

- [ ] **Step 4: Run, confirm pass**

Run: `python3 -m unittest eval.test_compare -v`
Expected: `OK` with 1 test (`test_boundaries`) passing all 13 subcases.

- [ ] **Step 5: Commit**

```bash
git add eval/compare_to_human.py eval/test_compare.py
git commit -m "feat(eval): letter_grade() with boundary tests"
```

---

## Task 7: Eval helper — `parse_tolerance_note()`

**Files:**
- Modify: `eval/compare_to_human.py`
- Modify: `eval/test_compare.py`

- [ ] **Step 1: Add the failing test**

Append to `eval/test_compare.py` (above the `if __name__` block):

```python
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
```

- [ ] **Step 2: Run, confirm fail**

Run: `python3 -m unittest eval.test_compare.TestParseToleranceNote -v`
Expected: ImportError on `parse_tolerance_note`.

- [ ] **Step 3: Implement**

Append to `eval/compare_to_human.py`:

```python
import re

# Matches a single "kan höjas/sänkas 0,1 [p] på tal N[+M][ och tal M]..." clause.
# Captures: direction (höjas|sänkas), problem-list string.
_TOL_CLAUSE = re.compile(
    r"kan\s+(höjas|sänkas)\s+0,1\s*(?:p\s+)?på\s+tal\s+([0-9+,\s]+(?:och\s+tal\s+[0-9+\s]+)*)",
    re.IGNORECASE,
)
# Inside the problem-list, problem numbers can be joined by "och tal", "+", or ",".
_PROBLEM_NUM = re.compile(r"(\d+)")


def parse_tolerance_note(note: str | None) -> dict[int, tuple[float, float]]:
    """Parse a teacher tolerance note into a per-problem (lo, hi) band.

    Returns {problem_n: (lo, hi)} where lo, hi in {-0.1, 0.0, +0.1}.
    Returns {} for empty input or any unrecognised note (caller falls back).
    Per spec §9, accepted forms include:
      - "kan höjas 0,1 p på tal 7"
      - "kan sänkas 0,1 p på tal 2"
      - "kan höjas 0,1 p på tal 3 och tal 4"
      - "kan höjas 0,1 p på tal 3+4"
      - missing "p" is tolerated ("kan höjas 0,1 på tal 7")
      - multiple clauses separated by "," or ";"
    """
    if not note or not note.strip():
        return {}
    out: dict[int, tuple[float, float]] = {}
    for match in _TOL_CLAUSE.finditer(note):
        direction, problem_list = match.group(1).lower(), match.group(2)
        delta_lo, delta_hi = (
            (-0.1, 0.0) if direction == "sänkas" else (0.0, 0.1)
        )
        for num_str in _PROBLEM_NUM.findall(problem_list):
            n = int(num_str)
            lo, hi = out.get(n, (0.0, 0.0))
            # Merge: keep the most-permissive band on each side
            out[n] = (min(lo, delta_lo), max(hi, delta_hi))
    return out
```

- [ ] **Step 4: Run, confirm pass**

Run: `python3 -m unittest eval.test_compare.TestParseToleranceNote -v`
Expected: `OK` with 8 tests passing.

- [ ] **Step 5: Commit**

```bash
git add eval/compare_to_human.py eval/test_compare.py
git commit -m "feat(eval): parse_tolerance_note() with real-workbook tests"
```

---

## Task 8: Eval helper — `read_jsonl()`

**Files:**
- Modify: `eval/compare_to_human.py`
- Modify: `eval/test_compare.py`

- [ ] **Step 1: Add the failing test**

Append to `eval/test_compare.py`:

```python
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
```

- [ ] **Step 2: Run, confirm fail**

Run: `python3 -m unittest eval.test_compare.TestReadJsonl -v`

- [ ] **Step 3: Implement**

Append to `eval/compare_to_human.py`:

```python
import json
from pathlib import Path
from typing import Iterator


class JsonlError(ValueError):
    """Raised when a JSONL file has a malformed line."""


def read_jsonl(path: Path) -> Iterator[dict]:
    """Yield one parsed dict per non-blank line. Raise JsonlError on bad lines.

    Per spec §9 test 4: must report the line number on failure.
    """
    with path.open("r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                yield json.loads(stripped)
            except json.JSONDecodeError as err:
                raise JsonlError(
                    f"{path}: line {lineno} is not valid JSON: {err.msg}"
                ) from err
```

- [ ] **Step 4: Run, confirm pass**

Run: `python3 -m unittest eval.test_compare.TestReadJsonl -v`
Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add eval/compare_to_human.py eval/test_compare.py
git commit -m "feat(eval): read_jsonl() with malformed-line reporting"
```

---

## Task 9: Eval helper — XLSX reader

**Files:**
- Modify: `eval/compare_to_human.py`
- Modify: `eval/test_compare.py`

The reader uses stdlib `zipfile` + `xml.etree.ElementTree`. It returns:
- A list of student rows (each row a dict with keys: `canvas_id`, `name`, `tal_1..tal_8`, `a_del`, `b_del`, `betyg`, `poangjustering` raw string, `tal_n_comment` per problem).
- A grade-threshold table parsed from sheet2.

For Phase 1 we'll just hit the columns explicitly: column letters are stable in this workbook (see spec §9). A robust implementation looks up by header row 1 instead of hard-coding letters.

- [ ] **Step 1: Add the failing test (uses the real workbook as fixture)**

Append to `eval/test_compare.py`:

```python
from eval.compare_to_human import read_xlsx_human_grades, XLSX_PATH


class TestReadXlsx(unittest.TestCase):
    def test_returns_nine_students(self):
        students, thresholds = read_xlsx_human_grades(XLSX_PATH)
        self.assertEqual(len(students), 9)

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
```

- [ ] **Step 2: Run, confirm fail**

Run: `python3 -m unittest eval.test_compare.TestReadXlsx -v`

- [ ] **Step 3: Implement the XLSX reader**

Append to `eval/compare_to_human.py`:

```python
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

XLSX_PATH = Path("Human_graded/RES_TENSK1110_SK1112_SK1117_260309_med_kommentarer.xlsx")
_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _col_index(ref: str) -> int:
    """Convert an Excel cell ref like 'B12' to a 0-based column index (B -> 1)."""
    letters = ""
    for ch in ref:
        if ch.isalpha():
            letters += ch
        else:
            break
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch.upper()) - ord("A") + 1)
    return n - 1


def _read_shared_strings(z: zipfile.ZipFile) -> list[str]:
    with z.open("xl/sharedStrings.xml") as f:
        root = ET.fromstring(f.read())
    out = []
    for si in root.findall(f"{_NS}si"):
        # An <si> may contain a single <t> or a sequence of <r><t>...</t></r>
        text = "".join(t.text or "" for t in si.iter(f"{_NS}t"))
        out.append(text)
    return out


def _iter_rows(z: zipfile.ZipFile, sheet: str, shared: list[str]):
    """Yield rows as dicts {col_index: value} with shared strings resolved."""
    with z.open(f"xl/worksheets/{sheet}.xml") as f:
        root = ET.fromstring(f.read())
    for row in root.iter(f"{_NS}row"):
        cells: dict[int, str | float] = {}
        for c in row.findall(f"{_NS}c"):
            ref = c.attrib.get("r", "")
            t = c.attrib.get("t", "")
            v = c.find(f"{_NS}v")
            if v is None or v.text is None:
                continue
            raw = v.text
            if t == "s":
                idx = int(raw)
                value: str | float = shared[idx] if 0 <= idx < len(shared) else raw
            elif t == "str":
                value = raw
            else:
                try:
                    value = float(raw)
                except ValueError:
                    value = raw
            cells[_col_index(ref)] = value
        yield int(row.attrib.get("r", "0")), cells


def _as_float_or_none(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, str):
        if v.strip() in ("", "-"):
            return None
        try:
            return float(v.replace(",", "."))
        except ValueError:
            return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def read_xlsx_human_grades(path: Path) -> tuple[list[dict], dict[str, tuple[float, float]]]:
    """Return (students, thresholds).

    Each student dict has:
        name, canvas_id, tal: {1..8: float | None},
        a_del, b_del, betyg, poangjustering (raw note string or ""),
        tal_comments: {1..8: str or ""}.

    `thresholds` maps letter grade -> (a_del_min, b_del_min) read from sheet2.
    """
    with zipfile.ZipFile(path) as z:
        shared = _read_shared_strings(z)
        # --- sheet1: header row, then student rows
        rows = list(_iter_rows(z, "sheet1", shared))
        # Row 1 = headers. Map header text -> column index.
        _, header_cells = rows[0]
        headers = {str(v).strip(): col for col, v in header_cells.items()}
        col_name = headers["Student"]
        col_id = headers["ID"]
        col_betyg = headers["Betyg"]
        col_adel = headers["A-del"]
        col_bdel = headers["B-del"]
        col_poangjust = headers.get("Poängjustering")
        # Per-problem score columns: header is the digit "1"..."8"
        col_tal = {int(h): c for h, c in headers.items() if h.isdigit() and 1 <= int(h) <= 8}
        # Per-problem teacher comment columns: header is "Tal 1".."Tal 8"
        col_tal_comment = {int(h.split()[1]): c for h, c in headers.items() if h.startswith("Tal ")}

        students = []
        for rnum, cells in rows[1:]:
            name = cells.get(col_name)
            if not isinstance(name, str) or "," not in name:
                # Skip "medel" / footer rows
                continue
            canvas_id = cells.get(col_id)
            if isinstance(canvas_id, float):
                canvas_id = str(int(canvas_id))
            elif canvas_id is None:
                canvas_id = ""
            else:
                canvas_id = str(canvas_id)
            students.append({
                "row": rnum,
                "name": name,
                "canvas_id": canvas_id,
                "tal": {n: _as_float_or_none(cells.get(c)) for n, c in col_tal.items()},
                "a_del": _as_float_or_none(cells.get(col_adel)),
                "b_del": _as_float_or_none(cells.get(col_bdel)),
                "betyg": str(cells.get(col_betyg, "")).strip(),
                "poangjustering": (
                    str(cells.get(col_poangjust, "")).strip() if col_poangjust is not None else ""
                ),
                "tal_comments": {
                    n: str(cells.get(c, "")) for n, c in col_tal_comment.items()
                },
            })

        # --- sheet2: threshold table
        thresholds: dict[str, tuple[float, float]] = {}
        for _, cells in _iter_rows(z, "sheet2", shared):
            # Each threshold row: col A = label like "För betyg Fx krävs",
            # col C = a_del threshold, col D = b_del threshold
            label = cells.get(0)
            a_t = _as_float_or_none(cells.get(2))
            b_t = _as_float_or_none(cells.get(3))
            if not isinstance(label, str) or a_t is None or b_t is None:
                continue
            # Extract the grade letter after "betyg "
            m = re.search(r"betyg\s+(\S+)\s+krävs", label, re.IGNORECASE)
            if m:
                thresholds[m.group(1)] = (a_t, b_t)
    return students, thresholds
```

- [ ] **Step 4: Run, confirm pass**

Run: `python3 -m unittest eval.test_compare.TestReadXlsx -v`
Expected: `OK` with 4 tests passing.

- [ ] **Step 5: Commit**

```bash
git add eval/compare_to_human.py eval/test_compare.py
git commit -m "feat(eval): stdlib XLSX reader with thresholds"
```

---

## Task 10: Eval helper — `join_students()`

**Files:**
- Modify: `eval/compare_to_human.py`
- Modify: `eval/test_compare.py`

- [ ] **Step 1: Add the failing test**

Append to `eval/test_compare.py`:

```python
from eval.compare_to_human import join_students


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
```

- [ ] **Step 2: Run, confirm fail**

Run: `python3 -m unittest eval.test_compare.TestJoinStudents -v`

- [ ] **Step 3: Implement**

Append to `eval/compare_to_human.py`:

```python
def join_students(
    agent_rows: list[dict], human_rows: list[dict]
) -> tuple[list[tuple[dict, dict]], list[dict], list[dict]]:
    """Inner-join on canvas_id. Return (matched, only_agent, only_human).

    Per spec §9: join key is canvas_id (the 6-digit XLSX ID column).
    """
    by_human = {r["canvas_id"]: r for r in human_rows}
    by_agent = {r["canvas_id"]: r for r in agent_rows}
    matched: list[tuple[dict, dict]] = []
    only_agent: list[dict] = []
    only_human: list[dict] = []
    for cid, a in by_agent.items():
        h = by_human.get(cid)
        if h is None:
            only_agent.append(a)
        else:
            matched.append((a, h))
    for cid, h in by_human.items():
        if cid not in by_agent:
            only_human.append(h)
    return matched, only_agent, only_human
```

- [ ] **Step 4: Run, confirm pass**

Run: `python3 -m unittest eval.test_compare.TestJoinStudents -v`
Expected: `OK`.

- [ ] **Step 5: Run the full test module**

Run: `python3 -m unittest eval.test_compare -v`
Expected: `OK`, all tests pass.

- [ ] **Step 6: Commit**

```bash
git add eval/compare_to_human.py eval/test_compare.py
git commit -m "feat(eval): join_students() with unmatched-side handling"
```

---

## Task 11: Eval driver — `compare_to_human.py` CLI

**Files:**
- Modify: `eval/compare_to_human.py`

Wire the helpers into a CLI that emits the report files described in spec §9.

- [ ] **Step 1: Add the driver function and `main`**

Append to `eval/compare_to_human.py`:

```python
import csv
import sys
from dataclasses import dataclass


JSONL_PATH = Path("results/agent_grades.jsonl")
COMPARISON_MD = Path("results/comparison.md")
COMPARISON_CSV = Path("results/comparison_summary.csv")


@dataclass
class Row:
    canvas_id: str
    name: str
    agent_tal: dict[int, float]
    human_tal: dict[int, float | None]
    tolerance: dict[int, tuple[float, float]]
    agent_a_del: float
    human_a_del: float | None
    agent_b_del: float
    human_b_del: float | None
    agent_betyg: str
    human_betyg: str


def _signed_error(agent: float, human: float | None) -> float | None:
    if human is None:
        return None
    return round(agent - human, 3)


def _within_tolerance(agent: float, human: float | None, band: tuple[float, float]) -> bool | None:
    if human is None:
        return None
    lo, hi = band  # additive offsets
    return (human + lo) - 1e-9 <= agent <= (human + hi) + 1e-9


def build_rows(
    agent_rows: list[dict],
    human_rows: list[dict],
) -> tuple[list[Row], list[dict], list[dict]]:
    matched, only_agent, only_human = join_students(agent_rows, human_rows)
    rows: list[Row] = []
    for a, h in matched:
        tolerance = parse_tolerance_note(h.get("poangjustering") or "")
        # Spec §9: band is [grade + lo, grade + hi] with lo,hi default 0.
        full_band = {n: tolerance.get(n, (0.0, 0.0)) for n in range(1, 9)}
        agent_tal = {
            int(n): pr["points"]
            for n, pr in (a.get("problem_results") or {}).items()
        }
        rows.append(Row(
            canvas_id=a["canvas_id"],
            name=a.get("name") or h.get("name", ""),
            agent_tal=agent_tal,
            human_tal=h["tal"],
            tolerance=full_band,
            agent_a_del=float(a.get("a_del") or 0.0),
            human_a_del=h.get("a_del"),
            agent_b_del=float(a.get("b_del") or 0.0),
            human_b_del=h.get("b_del"),
            agent_betyg=letter_grade(
                float(a.get("a_del") or 0.0), float(a.get("b_del") or 0.0)
            ),
            human_betyg=h.get("betyg", ""),
        ))
    return rows, only_agent, only_human


def render_markdown(rows: list[Row], only_agent: list[dict], only_human: list[dict]) -> str:
    out: list[str] = []
    out.append("# SK1110 — Agent vs. teacher comparison")
    out.append("")
    out.append(f"{len(rows)} matched students, {len(only_agent)} only-agent, {len(only_human)} only-human.")
    out.append("")
    # Aggregate
    per_problem_errors: dict[int, list[float]] = {n: [] for n in range(1, 9)}
    within_count = 0
    within_total = 0
    letter_agree = 0
    for r in rows:
        if r.human_betyg == r.agent_betyg:
            letter_agree += 1
        for n in range(1, 9):
            a_score = r.agent_tal.get(n, 0.0)
            h_score = r.human_tal.get(n)
            err = _signed_error(a_score, h_score)
            if err is not None:
                per_problem_errors[n].append(abs(err))
                within_total += 1
                if _within_tolerance(a_score, h_score, r.tolerance[n]):
                    within_count += 1
    out.append("## Aggregate")
    out.append("")
    out.append(f"- Letter-grade agreement: {letter_agree}/{len(rows)}")
    if within_total:
        out.append(
            f"- Within-tolerance per-problem: {within_count}/{within_total} "
            f"({100 * within_count / within_total:.0f}%)"
        )
    for n in range(1, 9):
        errs = per_problem_errors[n]
        if errs:
            mae = sum(errs) / len(errs)
            out.append(f"- MAE problem {n}: {mae:.2f} p (n={len(errs)})")
    all_errs = [e for errs in per_problem_errors.values() for e in errs]
    if all_errs:
        out.append(f"- MAE overall: {sum(all_errs) / len(all_errs):.2f} p")
    out.append("")
    # Per-student table
    out.append("## Per-student")
    out.append("")
    header = "| Student | " + " | ".join(f"T{n}" for n in range(1, 9)) + " | A-del | B-del | Betyg |"
    sep = "|" + "---|" * 12
    out.append(header)
    out.append(sep)
    for r in rows:
        cells: list[str] = [r.name]
        for n in range(1, 9):
            a_score = r.agent_tal.get(n, 0.0)
            h_score = r.human_tal.get(n)
            within = _within_tolerance(a_score, h_score, r.tolerance[n])
            mark = "✓" if within else ("·" if within is None else "✗")
            if h_score is None:
                cells.append(f"{a_score:.1f}/–")
            else:
                cells.append(f"{a_score:.1f}/{h_score:.1f}{mark}")
        cells.append(
            f"{r.agent_a_del:.1f}/" + (f"{r.human_a_del:.1f}" if r.human_a_del is not None else "–")
        )
        cells.append(
            f"{r.agent_b_del:.1f}/" + (f"{r.human_b_del:.1f}" if r.human_b_del is not None else "–")
        )
        cells.append(f"{r.agent_betyg}/{r.human_betyg}")
        out.append("| " + " | ".join(cells) + " |")
    out.append("")
    # Top-3 disagreements
    disagreements: list[tuple[float, str, int, float, float]] = []
    for r in rows:
        for n in range(1, 9):
            a_score = r.agent_tal.get(n, 0.0)
            h_score = r.human_tal.get(n)
            if h_score is None:
                continue
            disagreements.append((abs(a_score - h_score), r.name, n, a_score, h_score))
    disagreements.sort(reverse=True)
    out.append("## Top disagreements")
    out.append("")
    for diff, name, n, a, h in disagreements[:3]:
        out.append(f"- {name}, problem {n}: agent {a:.1f} vs. teacher {h:.1f} (Δ {diff:.1f})")
    if only_agent or only_human:
        out.append("")
        out.append("## Unmatched")
        for s in only_agent:
            out.append(f"- only-agent: {s.get('name', s.get('canvas_id'))}")
        for s in only_human:
            out.append(f"- only-human: {s.get('name', s.get('canvas_id'))}")
    out.append("")
    return "\n".join(out)


def render_csv(rows: list[Row], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        header = (
            ["canvas_id", "name"]
            + [f"agent_tal_{n}" for n in range(1, 9)]
            + [f"human_tal_{n}" for n in range(1, 9)]
            + ["agent_a_del", "human_a_del", "agent_b_del", "human_b_del",
               "agent_betyg", "human_betyg"]
        )
        w.writerow(header)
        for r in rows:
            row = [r.canvas_id, r.name]
            row += [f"{r.agent_tal.get(n, 0.0):.1f}" for n in range(1, 9)]
            row += [
                "" if r.human_tal.get(n) is None else f"{r.human_tal[n]:.1f}"
                for n in range(1, 9)
            ]
            row += [
                f"{r.agent_a_del:.1f}",
                "" if r.human_a_del is None else f"{r.human_a_del:.1f}",
                f"{r.agent_b_del:.1f}",
                "" if r.human_b_del is None else f"{r.human_b_del:.1f}",
                r.agent_betyg,
                r.human_betyg,
            ]
            w.writerow(row)


def main(argv: list[str]) -> int:
    jsonl_path = Path(argv[1]) if len(argv) > 1 else JSONL_PATH
    if not jsonl_path.exists():
        print(f"error: {jsonl_path} not found — run the grading skill first", file=sys.stderr)
        return 1
    agent_rows = list(read_jsonl(jsonl_path))
    human_rows, _thresholds = read_xlsx_human_grades(XLSX_PATH)
    rows, only_agent, only_human = build_rows(agent_rows, human_rows)
    COMPARISON_MD.parent.mkdir(parents=True, exist_ok=True)
    COMPARISON_MD.write_text(render_markdown(rows, only_agent, only_human))
    render_csv(rows, COMPARISON_CSV)
    print(f"wrote {COMPARISON_MD} and {COMPARISON_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 2: Smoke-test the driver with a stub JSONL**

Create a temporary file just to exercise the wiring:

```bash
mkdir -p /tmp/sk1110-smoke
cat > /tmp/sk1110-smoke/agent_grades.jsonl <<'EOF'
{"canvas_id": "185729", "submission_id": "1840662", "name": "Abedian, Tara", "filename": "x.pdf", "a_del": 3.5, "b_del": 0.7, "problem_results": {"1": {"points": 0.9}, "2": {"points": 0.7}, "3": {"points": 1.0}, "4": {"points": 0.6}, "5": {"points": 0.3}, "6": {"points": 0.3}, "7": {"points": 0.2}, "8": {"points": 0.2}}, "flags": []}
EOF
python3 eval/compare_to_human.py /tmp/sk1110-smoke/agent_grades.jsonl
cat results/comparison.md
```

Expected: a Markdown report with 1 matched student (Abedian), letter-grade agreement 1/1, MAE columns populated. No tracebacks.

- [ ] **Step 3: Clean up smoke artifact**

```bash
rm /tmp/sk1110-smoke/agent_grades.jsonl
rm results/comparison.md results/comparison_summary.csv
```

- [ ] **Step 4: Commit**

```bash
git add eval/compare_to_human.py
git commit -m "feat(eval): comparison driver — Markdown + CSV outputs"
```

---

## Task 12: Author the grading skill

**Files:**
- Create: `.claude/skills/grade-sk1110-exam/SKILL.md`

This is a Markdown skill with YAML frontmatter, not Python. It's the entire prompt that Claude Code follows when grading one student. The skill is the "code" — review it against the spec rather than running unit tests.

- [ ] **Step 1: Write the skill**

Create `.claude/skills/grade-sk1110-exam/SKILL.md` with this exact content:

````markdown
---
name: grade-sk1110-exam
description: Grade one SK1110 student exam PDF problem-by-problem against the SK1110-260309 rubric. Trigger when the user says "grade this exam", "grade <student>", "run the SK1110 grader", or invokes the skill explicitly. Produces a per-student page index and appends one JSONL row to results/agent_grades.jsonl. Specific to the 2026-03-09 SK1110 exam — do NOT run on other exams without a matching rubric JSON.
---

# Grade SK1110 exam — 2026-03-09

You are grading ONE student submission for the SK1110 written exam given 2026-03-09. You work as a Swedish physics teacher applying a partial-credit rubric.

The full design spec is at `docs/superpowers/specs/2026-05-26-sk1110-auto-grader-phase1-design.md`. The output schema is non-negotiable — read §5 of the spec carefully before producing JSONL.

## Inputs you have

- The student PDF, passed in by the user (path under `Ungraded/`).
- `rubric/sk1110-260309.json` — the canonical rubric. Read it once at the start.
- `Solution/TEN SK1110 260309 lösningar.pdf` — reference solutions. Read once at start.
- `Exam/TEN SK1110 260309.pdf` — problem statements. Optional reference for figure context.

## What you produce

1. `results/page_index/<submission_id>.json` — written FIRST, before any grading.
2. One appended (or in-place updated) line in `results/agent_grades.jsonl`.

If `results/agent_grades.jsonl` already has a line for this `canvas_id`, OVERWRITE it (idempotent re-runs).

## Procedure

### 1. Identify the student from the filename

Filenames follow the pattern `<surname><firstname>_<canvas_id>_<sis_id>_<submission_id>.pdf`. Example: `abediantara_185729_10215146_1840662.pdf` ⇒ `canvas_id="185729"`, `submission_id="1840662"`, `name="Abedian, Tara"`. Do NOT vision-read the first page to re-extract this — the filename is authoritative.

### 2. Load context

Read these three files into context (in this order):
1. `rubric/sk1110-260309.json`
2. `Solution/TEN SK1110 260309 lösningar.pdf`
3. The student PDF (path given by user)

### 3. Page index — first pass

Make ONE pass over the student PDF. Build the page index as a JSON object:

```json
{
  "canvas_id": "<from filename>",
  "submission_id": "<from filename>",
  "filename": "<basename of student PDF>",
  "n_pages": <int>,
  "problem_pages": {
    "1": [{"page_index": <0-based>, "confidence": "high|med|low", "readability": "ok|partial|poor"}],
    "2": [...],
    ...
    "8": [...]
  },
  "non_problem_pages": [<list of page indices for cover sheets, blanks, etc.>]
}
```

Rules:
- The exam instructions require one problem per sheet, front side only. A student may add extra sheets — multiple pages for one problem is normal.
- For each page, identify the problem number from the student's own "Tal N" / "Uppgift N" / "Problem N" label at the top, or from solution content. If unclear, set `confidence: "low"`.
- An A-del problem (1–5) with NO pages → leave the array empty here; the grading loop will treat it as `unindexed`.
- A B-del problem (6–8) with NO pages → leave the array empty; the grading loop will treat it as `not_attempted` (Del B is optional).

Write the page index to `results/page_index/<submission_id>.json` before continuing. This artifact is human-reviewable and is the source of truth for which pages belong to which problem in step 5.

### 4. Per-problem grading — one problem at a time, n = 1..8

For each problem n, build a `problem_results[n]` object matching spec §5. Procedure:

**4a. Decide `attempt_status`** based on the page index:
- Pages present, readable → `attempted`
- No pages, problem in Del A → `unindexed`
- No pages, problem in Del B → `not_attempted`
- Pages present but illegible → `unreadable`
- Ambiguous problem labels but pages exist → `ambiguous_index` (still grade, pick most likely)

If `attempt_status` is `not_attempted`, `unindexed`, or `unreadable`: produce
```json
{
  "attempt_status": "<status>",
  "page_refs": [],
  "max_points": 1.0,
  "raw_points": 0.0,
  "deduction_points": 0.0,
  "points": 0.0,
  "items": [],
  "deductions": [],
  "special_cases_fired": [],
  "comment_sv": "Ej besvarad."   // or "Ingen lösning hittad." / "Olesbar lösning."
}
```
…and move on. Skip steps 4b–4g.

**4b. Pull the rubric entries for problem n** from the loaded JSON: `items`, `special_cases`, `max_points`.

**4c. Check `special_cases` FIRST.** If the student's solution matches a special case (e.g. "räknat utan absorption" for problem 1), record the case id(s) in `special_cases_fired`, set `raw_points` to the case's `total_points`, and skip line items. For this exam every special case has `effect: "set_total"` and `apply_global_deductions: false` — go straight to step 4f. If multiple cases match, pick the one with the lowest `total_points` and record all matching ids.

**4d. Otherwise, walk each rubric item.** For each `item` in `items`:
- Decide `status`: `full` if the step is correct, `partial` if attempted but incomplete, `none` if missing.
- Decide `award`: the points to grant. `award ≤ max`.
- If the item has `sub`, sub-points are *carve-outs* of the parent (spec §4): the parent is awarded if the work is done, and the sub-point is forfeited if the sub-condition is missing. Example: item 1.b is worth 0.2 p, of which 0.1 p depends on "korrekt utformad absorption" — if the student did 1.b but botched the absorption, award 0.1.
- Write a one-sentence Swedish `evidence_sv` (≤ ~80 chars) pointing to what was/wasn't done. Example: `"avståndsberoende finns men absorption saknas"`.

**4e. Apply global deductions** (only when 4c did not fire). Each global deduction id may fire AT MOST ONCE per problem. Mutually exclusive: pick at most one of {`missing_unit_answer`, `unit_error_wrong_answer`, `dimension_error`} for the same root issue. Consequential errors: if a downstream step uses a wrong upstream value but the method is correct, award method points and apply at most one `arithmetic_slip` or `rounding_error` for the root cause — do not double-deduct propagation.

**4f. Compute points:**
```
raw_points        = special-case total_points  OR  sum(items[].award)
deduction_points  = sum(deductions[].points)   # ≤ 0
points            = round( clamp(raw_points + deduction_points, 0, max_points), 1 )
```
Clamping below 0 → add `deductions_clamped` to the top-level `flags`.

**4g. Build `comment_sv`** (Swedish, ≤ 300 chars). Format: `"<points>/<max>: <one-sentence summary of what was awarded and what was missed>. Avdrag: <list>."` Use Swedish decimal comma (`0,7/1,0`). Example: `"0,7/1,0: rätt metod men absorption saknas delvis. Avdrag: avrundning."`

### 5. Aggregate

```
a_del = sum(problem_results[n].points for n in 1..5)
b_del = sum(problem_results[n].points for n in 6..8)
```

Do NOT compute the letter grade. The eval script does that.

### 6. Write the JSONL row

The full schema is in spec §5. Required fields:
`canvas_id`, `submission_id`, `name`, `filename`, `a_del`, `b_del`, `problem_results` (with all 8 keys "1".."8" present), `flags`.

`flags` is a list of short codes; per spec §7:
- `unreadable_problem_<n>` when an A-del problem's pages are present but illegible
- `problem_<n>_unindexed` when an A-del problem has no pages (do NOT raise for Del B `not_attempted`)
- `problem_<n>_ambiguous_index` when the index pass set `ambiguous_index`
- `multi_solution_sheet` if the student put more than one problem on a single sheet
- `special_case:<id>` for every case that fired
- `deductions_clamped` if any problem's clamping kicked in
- `low_confidence_problem_<n>` if any item for that problem has `readability: "poor"` or every awarded item was `partial`

Append (or overwrite, keyed by `canvas_id`) one line in `results/agent_grades.jsonl`.

### 7. Report to the user

Echo a short summary in chat:
- Student name + canvas_id
- Per-problem points
- a_del / b_del
- Any flags
- Path to the JSONL row and the page-index JSON

Do NOT print the full Swedish comments in chat — they're in the JSONL.

## Things to avoid

- Inventing rubric items not in `rubric/sk1110-260309.json`. The rubric is closed.
- Computing the letter grade. That belongs to the eval.
- Re-extracting name/personnummer from the student PDF. Filename is authoritative.
- Awarding more than `max_points` for any problem. Clamp.
- Inventing Swedish — if you're not confident a phrasing is natural Swedish, keep `evidence_sv` short and factual.
- Skipping the page-index step. The grading loop reads from that file.

## When you're done

A successful run leaves:
- `results/page_index/<submission_id>.json` newly written
- One row in `results/agent_grades.jsonl` with `canvas_id` matching the student
- A short summary printed in chat
````

- [ ] **Step 2: Eyeball the skill file**

Run: `wc -l .claude/skills/grade-sk1110-exam/SKILL.md`
Expected: ~150 lines. Open the file and confirm the frontmatter is valid YAML (no stray colons in the `description` field that could break parsing).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/grade-sk1110-exam/SKILL.md
git commit -m "feat(skill): grade-sk1110-exam — per-problem rubric loop"
```

---

## Task 13: Smoke test the skill on one student

**Files:**
- Produces: `results/page_index/1841066.json`
- Produces: `results/agent_grades.jsonl` (1 row)

Pick the shortest ungraded PDF — `Ungraded/anderssonoliver_159724_10215412_1841066.pdf` is one of the smaller ones at ~8 MB.

- [ ] **Step 1: Restart Claude Code so the new skill loads**

Skills are loaded at session start. If you wrote the skill in the same session, restart Claude Code now.

After restart, the skill `grade-sk1110-exam` should appear in the available-skills list.

- [ ] **Step 2: Invoke the skill on one student**

In Claude Code:
> Grade `Ungraded/anderssonoliver_159724_10215412_1841066.pdf` using the grade-sk1110-exam skill.

Wait for the skill to finish. Expected output: a short chat summary and two files written.

- [ ] **Step 3: Review the page index by eye**

Run: `cat results/page_index/1841066.json | python3 -m json.tool`

Check by eye:
- `n_pages` matches the actual PDF (`pdfinfo Ungraded/anderssonoliver_159724_10215412_1841066.pdf | grep Pages` if available, otherwise just trust the agent).
- `problem_pages` has all keys "1".."8".
- A-del problems (1–5) should each have at least one page (this student got an `A`, so they attempted all of Del A).
- B-del entries can be empty if the student skipped them.
- No problem has a wildly suspicious number of pages (e.g. all 8 problems mapped to page 0).

If the indexing looks wrong, fix the SKILL.md (likely the page-index instructions) and re-run.

- [ ] **Step 4: Review the JSONL row by eye**

Run: `cat results/agent_grades.jsonl | python3 -m json.tool`

Check:
- `canvas_id == "159724"`, `submission_id == "1841066"`.
- `a_del` and `b_del` are floats and add to a plausible total. Andersson Oliver scored `4.7 / 0.8` per the teacher.
- All 8 `problem_results` keys present.
- `comment_sv` strings are Swedish, ≤ 300 chars, and reference what was awarded.
- At least one `items[]` has a non-trivial `evidence_sv`, OR at least one `special_cases_fired` is non-empty, OR at least one `deductions[]` fired. A grading row with everything `full` and no deductions is suspicious — eyeball the PDF.
- `flags` is a list (may be empty).

- [ ] **Step 5: Run the eval comparison on just this student**

Run: `python3 eval/compare_to_human.py`
Expected: a `results/comparison.md` with one matched row for Andersson Oliver. Compare agent's per-problem points to the teacher's (`Tal 1..Tal 8` for Andersson Oliver in the workbook). Differences > 0.3 p on any problem are worth investigating before the full run.

- [ ] **Step 6: Commit the smoke-test results**

```bash
git status   # results/ is gitignored, so this should show only intentional changes
git diff
```

No commit needed for the gitignored results files. If you adjusted the skill in step 3, commit that:

```bash
git add .claude/skills/grade-sk1110-exam/SKILL.md
git commit -m "fix(skill): adjust page-index instructions after smoke test"
```

(Skip this commit if no skill changes were needed.)

---

## Task 14: Full grading run — all 9 students

**Files:**
- Produces: `results/page_index/*.json` × 9
- Produces: `results/agent_grades.jsonl` (9 rows)

- [ ] **Step 1: Clear stale results**

```bash
rm -f results/agent_grades.jsonl
rm -f results/page_index/*.json
```

- [ ] **Step 2: Grade each of the 9 students**

For each file under `Ungraded/`, invoke the skill. You can do this one at a time in a Claude Code session, or use `superpowers:subagent-driven-development` to dispatch one subagent per student (independent work, fan-out is safe — each writes its own page-index file and appends to the JSONL).

The 9 students:
```
Ungraded/abediantara_185729_10215146_1840662.pdf
Ungraded/ahlinderbenjamin_184115_10215168_1840736.pdf
Ungraded/anderssongustav_184010_10215213_1840890.pdf
Ungraded/anderssonoliver_159724_10215412_1841066.pdf
Ungraded/andreasenkerneik_184080_10215147_1840668.pdf
Ungraded/burströmwilliam_185699_10215251_1840996.pdf
Ungraded/grigoryangor_185544_10215174_1840749.pdf
Ungraded/göranssonrobin_185466_10215165_1840728.pdf
Ungraded/hanssonfredrik_185779_10215235_1840946.pdf
```

NOTE on parallelism: appending to a single JSONL file from multiple subagents creates a race. Two safer options:
1. Run sequentially (slower but no race).
2. Have each subagent write its own JSONL fragment to `results/agent_grades.<canvas_id>.jsonl`, then concatenate them at the end:
   ```bash
   cat results/agent_grades.*.jsonl > results/agent_grades.jsonl
   ```
   If you choose option 2, update step 6 of SKILL.md to write per-student fragments, then revert it after.

- [ ] **Step 3: Verify all 9 rows are present**

```bash
wc -l results/agent_grades.jsonl
# Expected: 9
python3 -c "import json; ids = sorted(json.loads(l)['canvas_id'] for l in open('results/agent_grades.jsonl') if l.strip()); print(ids)"
# Expected: ['159724', '184010', '184080', '184115', '185466', '185544', '185699', '185729', '185779']
```

- [ ] **Step 4: Verify schema integrity**

```bash
python3 - <<'PY'
import json
required_top = {"canvas_id", "submission_id", "name", "filename", "a_del", "b_del", "problem_results", "flags"}
with open("results/agent_grades.jsonl") as f:
    for i, line in enumerate(f, 1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = required_top - row.keys()
        assert not missing, f"row {i}: missing fields {missing}"
        assert set(row["problem_results"].keys()) == {"1","2","3","4","5","6","7","8"}, f"row {i}: missing problem keys"
        for n, pr in row["problem_results"].items():
            assert 0.0 <= pr["points"] <= pr["max_points"], f"row {i}: problem {n} points out of range"
print("schema OK")
PY
```

Expected: `schema OK`. If anything fails, re-run the offending student and fix.

---

## Task 15: Run the eval and review

**Files:**
- Produces: `results/comparison.md`
- Produces: `results/comparison_summary.csv`

- [ ] **Step 1: Run the comparison**

```bash
python3 eval/compare_to_human.py
cat results/comparison.md
```

- [ ] **Step 2: Check against the demo targets** (spec §1)

From the comparison report, confirm:
- Letter-grade agreement is ≥ 7/9. If not, note which students disagreed and why (likely E↔D borderline cases — teacher's actual call uses judgment, eval is deterministic).
- MAE per problem ≤ 0.2 p in the aggregate. If a single problem is much worse than the rest, investigate.
- No malformed JSONL rows (already checked in Task 14 step 4).

- [ ] **Step 3: Look at the top-3 disagreements**

From `results/comparison.md`, identify the three largest single-problem deltas. For each, open the student PDF and the rubric to figure out whether:
- The agent misread the handwriting.
- The agent missed a special-case override.
- The teacher applied judgment the deterministic eval can't see.

This is the material for the demo's "biggest disagreement" walk-through (spec §10 step 5).

- [ ] **Step 4: Commit the eval module fixes if any were needed**

If steps 2–3 surfaced any bugs in the eval (e.g. tolerance parsing, threshold edge case), fix the helper, re-run its unit test, and commit. The grading results are gitignored, so a new `results/` does not need committing.

```bash
git status
# if there are eval/ changes:
git add eval/
git commit -m "fix(eval): <what you fixed>"
```

- [ ] **Step 5: Final integration check**

Run all unit tests one last time to confirm nothing regressed:
```bash
python3 -m unittest eval.test_validate_rubric eval.test_compare -v
```
Expected: `OK`, all tests pass.

---

## Done

After Task 15:
- `rubric/sk1110-260309.json` — full validated rubric.
- `.claude/skills/grade-sk1110-exam/SKILL.md` — the grading skill.
- `eval/` — validator, comparison, tests, all stdlib-only.
- `results/comparison.md` + `results/comparison_summary.csv` — the demo's eval artifact.
- 9 graded students in `results/agent_grades.jsonl`.

For the agentathon demo, follow spec §10's 5-step script.

Phases 2 (reusable skill) and 3 (eval writeup) are separate specs.
