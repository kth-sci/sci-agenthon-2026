# SK1110 Auto-Grader — Phase 1 Design

**Date:** 2026-05-26
**Author:** Jonas Sellberg (with Claude Code)
**Status:** Approved for implementation planning
**Scope:** Phase 1 only — agentathon demo. Phases 2 (reusable skill) and 3 (eval/writeup) get their own specs.

## 1. Goal

Build a Claude Code workflow that grades the 9 student submissions from the SK1110 exam given on 2026-03-09, problem-by-problem against the teacher's rubric, and produce a comparison report against the human-graded ground truth.

Success for Phase 1 is a working demo, not production quality. Demo targets:

- ≥ 7 / 9 letter-grade agreements with the teacher.
- Mean per-problem absolute error ≤ 0.2 p.
- No malformed rows in the agent's output.

Missing the targets is acceptable for the demo — the eval report should make failure modes legible either way.

## 2. Inputs (already on disk)

- `Exam/TEN SK1110 260309.pdf` — 8 problems (Del A: 1–5 mandatory, Del B: 6–8 optional). Swedish, physics, includes figures.
- `Solution/TEN SK1110 260309 lösningar.pdf` — reference solutions.
- `Grading_rules/Rättningsmall 260309.pdf` — partial-credit rubric, 0.1–0.4 p per step, plus global deductions and per-problem special-case overrides.
- `Ungraded/<student>.pdf` × 9 — scanned handwritten student submissions (8–15 MB each).
- `Human_graded/annotated-*.pdf` × 9 — teacher-annotated copies (used by eye only, not parsed).
- `Human_graded/RES_TENSK1110_..._med_kommentarer.xlsx` — ground truth: per-student `Tal 1..Tal 8`, `A-del`, `B-del`, `Betyg`, plus tolerance notes like *"kan sänkas 0,1 p på tal 2"*.

## 3. Architecture

Single Claude Code skill drives grading. Static reference assets on disk. One structured rubric JSON built once by hand. One output artifact (JSONL). One small Python eval script.

Components:

1. **Skill `grade-sk1110-exam`** at `.claude/skills/grade-sk1110-exam/SKILL.md`. Encodes the per-problem loop, output schema, and edge-case rules. Swedish-language output comments.
2. **Structured rubric** at `rubric/sk1110-260309.json`. Hand-extracted from the rubric PDF, validated by a sanity script.
3. **Agent output** at `results/agent_grades.jsonl`. One line per student.
4. **Eval script** at `eval/compare_to_human.py`. Stdlib only (`zipfile` + `xml.etree.ElementTree` for the XLSX — no `openpyxl` dependency). Reads JSONL + XLSX, emits a Markdown report and CSV summary. Has unit tests (see §9).
5. **Rubric validator** at `eval/validate_rubric.py`. Asserts per-problem item points sum to `max_points` and emits a human-review summary (`results/rubric_summary.md`) listing per-problem item count, line-item total, special-case count, and global-deduction count — used to sanity-check the hand-built rubric JSON before any grading run.

Boundaries: the skill knows nothing about the eval; the eval reads only the skill's JSONL. The rubric JSON is the contract between the rubric PDF (human-authored) and the skill (machine-consumed).

## 4. Rubric JSON shape

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
         "sub": [{"label": "utan/felaktigt utformad absorbans", "points": 0.1}]},
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
    // problems 2–8 follow the same shape
  ]
}
```

Notes:

- Per-problem `items.points` (parent values only) MUST sum to `max_points`. Sub-points (`sub`) are *carve-outs* of the parent — they identify portions of the parent's points that depend on a specific additional condition. The sub-point is awarded only if (a) the parent is awarded and (b) the sub-condition is met. The parent's full points can still be earned without the sub-condition firing if the rubric treats the sub as a "deduct if missing" carve-out (e.g. item `1.c` is worth 0.2 p, of which 0.1 p is forfeit if absorbance is not correctly handled). Total points awarded for an item never exceed the parent's `points`.
- `special_cases` are total-score overrides triggered by specific misinterpretations. Schema:
  - `effect: "set_total"` — the only mode used in this exam's rubric. When triggered, the problem's score becomes `total_points`; the line-item summation is skipped entirely.
  - `apply_global_deductions: false` — global deductions are not stacked on top of a special-case override. The override is the final score (before clamping).
  - If multiple special cases match for one problem, take the one with the lowest `total_points` (most conservative) and flag both ids.
  - Other `effect` values (`cap_total`, `alternative_path`) are reserved for future rubrics; Phase 1 implementations may assert `effect == "set_total"` and fail loudly otherwise.

## 5. Output JSONL schema

One line per student in `results/agent_grades.jsonl`. Structured grading data is the source of truth; the Swedish comment is a derived display string.

```json
{
  "canvas_id": "185729",
  "submission_id": "1840662",
  "name": "Abedian, Tara",
  "filename": "abediantara_185729_10215146_1840662.pdf",
  "a_del": 2.5,
  "b_del": 0.0,
  "problem_results": {
    "1": {
      "attempt_status": "attempted",
      "page_refs": [{"page_index": 2, "readability": "ok"}],
      "max_points": 1.0,
      "raw_points": 0.8,
      "deduction_points": -0.1,
      "points": 0.7,
      "items": [
        {"id": "1.a", "award": 0.3, "max": 0.3, "status": "full", "evidence_sv": "omvandlar dB till intensitet"},
        {"id": "1.b", "award": 0.1, "max": 0.2, "status": "partial", "evidence_sv": "avståndsberoende finns men absorption saknas"}
      ],
      "deductions": [
        {"id": "rounding_error", "points": -0.1, "evidence_sv": "för många värdesiffror"}
      ],
      "special_cases_fired": [],
      "comment_sv": "0,7/1,0: rätt metod men absorption saknas delvis. Avdrag: avrundning."
    },
    "6": {
      "attempt_status": "not_attempted",
      "page_refs": [],
      "max_points": 1.0,
      "raw_points": 0.0,
      "deduction_points": 0.0,
      "points": 0.0,
      "items": [],
      "deductions": [],
      "special_cases_fired": [],
      "comment_sv": "Ej besvarad."
    }
  },
  "flags": ["special_case:no_absorption"]
}
```

Field semantics:

- `canvas_id`: 6-digit Canvas student ID, used as the eval join key against the XLSX `ID` column. Parsed from the second underscore-separated field of the filename (e.g. `185729` in `abediantara_185729_10215146_1840662.pdf`).
- `submission_id`: 7-digit submission ID from the trailing filename field (e.g. `1840662`). Carried through for traceability but NOT the join key.
- `name`: parsed from filename. The first page of the student PDF is NOT vision-read to extract name/personnummer — that step was cut to reduce privacy surface and is not needed for grading or eval.
- `problem_results[n].attempt_status`: one of `attempted`, `not_attempted` (no pages indexed and problem is in Del B, or pages clearly blank), `unindexed` (indexing failed but the problem may have been attempted), `unreadable` (pages found but illegible), `ambiguous_index` (multiple problems plausible).
- `problem_results[n].page_refs[].readability`: one of `ok`, `partial`, `poor`.
- `problem_results[n].items[].status`: `full` | `partial` | `none`. `award` ≤ `max`; if the item has sub-points, `award` reflects parent-plus-applicable-sub awards (see §4).
- `problem_results[n].raw_points`: sum of `items[].award` (or `total_points` from a fired special case).
- `problem_results[n].deduction_points`: signed sum of `deductions[].points` (≤ 0).
- `problem_results[n].points`: `clamp(raw_points + deduction_points, 0, max_points)`, rounded to nearest 0.1. This is the per-problem score.
- `problem_results[n].special_cases_fired`: list of special-case ids that triggered. Non-empty implies `items` is empty (the override replaces line-item summation per §4).
- `a_del = sum(points for n in 1..5)`, `b_del = sum(points for n in 6..8)`. Letter grade NOT computed by the agent.
- `problem_results[n].comment_sv`: Swedish, ≤ 300 chars, derived from `items` + `deductions` + `special_cases_fired` for display. Eval and Phase 3 analysis MUST read structured fields, not parse this string.
- `flags`: short codes for human review across the whole submission (see §7).

## 6. Per-student data flow

1. **Load context once.** Read `rubric/sk1110-260309.json` and the solution PDF (all pages).
2. **Identify student from filename only.** Parse `canvas_id`, `submission_id`, and `name` from the filename. Do NOT vision-read the first page to re-extract name/personnummer — that step is cut from Phase 1 (it adds privacy surface without improving grading or eval; the filename is authoritative).
3. **Index pages by problem.** Single pass over the student PDF. Produce `results/page_index/<submission_id>.json` with `{problem_n: [{page_index, confidence, readability}]}` AND a `non_problem_pages` list (cover sheet, blanks, continuations, etc.). One student PDF has 17 pages for an 8-problem exam — students adding extra sheets is normal. Cases:
   - Multiple pages for one problem → all listed in order.
   - No pages for an A-del problem (1–5) → `unindexed` (likely skipped or indexing failed).
   - No pages for a B-del problem (6–8) → `not_attempted` (optional; treat as 0 points without flagging as a failure).
   - Pages with ambiguous problem labelling → `ambiguous_index`, agent picks the most likely match.
   The page index is written first; the grading loop reads from it. This artifact is also human-reviewable before kicking off the grading loop.
4. **Per-problem grading loop** (n = 1..8), sequentially in one Claude Code session:
   a. If `attempt_status` ∈ {`not_attempted`, `unindexed`, `unreadable`} → record `points: 0` with appropriate `comment_sv`, skip steps b–g.
   b. Pull rubric entries for problem n from JSON.
   c. Pull solution pages for problem n.
   d. Pull student pages for problem n.
   e. Check `special_cases` FIRST. If one triggers → set `raw_points` to the override, record the special-case id(s) in `special_cases_fired`, skip line-item awards. Per §4: `apply_global_deductions: false` for the special cases in this exam, so go straight to step h.
   f. Otherwise: walk each rubric item, award `full` / `partial` / `none` with a one-sentence Swedish `evidence_sv`. Sub-items awarded only if their parent is awarded.
   g. Apply applicable global deductions. Rules:
      - **Each deduction `id` may fire at most once per problem.** Don't both apply `missing_unit_answer` (-0.2) twice for the same omission.
      - **Mutually exclusive groups:** `missing_unit_answer` and `unit_error_wrong_answer` and `dimension_error` are alternatives for the same underlying issue — pick the single most-applicable one.
      - **Consequential errors:** if a downstream step uses a wrong upstream value but the method is correct, award method points and do not double-deduct for the propagated error. Apply at most one `arithmetic_slip` / `rounding_error` per root cause.
   h. `raw_points = sum(items.award)` (or special-case `total_points`). `deduction_points = sum(deductions.points)` (≤ 0). `points = round(clamp(raw_points + deduction_points, 0, max_points), 1)`. Clamping below 0 sets `flags += deductions_clamped`.
   i. Build `comment_sv` (≤ 300 chars, Swedish) from the structured awards and deductions, for display only.
5. **Aggregate.** `a_del = sum(points for n in 1..5)`, `b_del = sum(points for n in 6..8)`. No letter grade.
6. **Append/overwrite row** in `results/agent_grades.jsonl`. Idempotent on `canvas_id`.

## 7. Flag codes (for `flags` array)

Flags surface conditions that warrant human review. Routine non-attempts on Del B do NOT generate a flag (those are normal and tracked via `attempt_status: "not_attempted"` in `problem_results`).

| Code | Meaning |
|---|---|
| `unreadable_problem_<n>` | Page(s) for problem n were found but illegible |
| `problem_<n>_unindexed` | Problem n in Del A (1–5) has no pages identified — likely a skip or indexing failure, needs review |
| `problem_<n>_ambiguous_index` | Pages exist but problem number unclear; agent picked the most likely match |
| `multi_solution_sheet` | Multiple problems on one sheet (rules violation) |
| `special_case:<id>` | A `special_cases` override fired (see §4); multiple may appear if several matched |
| `deductions_clamped` | Per-problem total would have gone below 0; clamped to 0 |
| `low_confidence_problem_<n>` | The agent's awarded score for problem n is flagged as low-confidence (any item with `readability: "poor"` or all-`partial` awards across the problem) |

## 8. Edge cases & rules

- **Crossed-out work** → ignored; if everything is crossed out, treat as `unreadable` if pages exist, else `unindexed`.
- **Sub-items** in the rubric (`(varav 0,1 p för …)`) → see §4 — sub-points are carve-outs of the parent, conditional on parent being awarded and the sub-condition being met.
- **Special cases** override line-item summation entirely; per §4, `apply_global_deductions: false` for the cases in this exam (the override is the final score before clamping).
- **Multiple special cases match** → take the lowest `total_points` (most conservative), record all matching ids in `special_cases_fired`.
- **Per-problem total < 0** after deductions → clamped to 0, `deductions_clamped` flag.
- **Deduction stacking** → each deduction `id` fires at most once per problem; mutually-exclusive unit/dimension deductions resolved to one (see §6 step 4g).
- **Consequential errors** → don't double-penalize a single root mistake; award method credit downstream when physics is consistent (see §6 step 4g).
- **Missing problem** → 0 points. Del A: `attempt_status: "unindexed"`, raise `problem_<n>_unindexed` flag, `comment_sv: "Ingen lösning hittad."`. Del B: `attempt_status: "not_attempted"`, NO flag, `comment_sv: "Ej besvarad."`.
- **Comments in Swedish** to match the teacher's style.
- **Rounding** to nearest 0.1 happens after deductions, per problem, matching teacher convention.

Out of scope for Phase 1: re-grading from comments, parameterization over different exams, parsing the annotated PDFs.

## 9. Eval script

`eval/compare_to_human.py` — stdlib only (`json`, `csv`, `re`, `zipfile`, `xml.etree.ElementTree`). No `openpyxl` dependency. The XLSX is unzipped and parsed directly from `xl/sharedStrings.xml`, `xl/worksheets/sheet1.xml` (data), and `xl/worksheets/sheet2.xml` (grade thresholds).

**Join key:** `canvas_id` (6-digit) ↔ XLSX column `B` (`ID`). The JSONL field `submission_id` (7-digit, trailing in the filename) is NOT used for the join — it doesn't appear in the XLSX. Students missing from one side or the other are reported as `unmatched`.

**XLSX columns of interest** (sheet1):
- `A` Student name, `B` Canvas ID (join key), `O` `Betyg` (letter grade), `M` `A-del`, `N` `B-del`, `E..L` per-problem scores (`Tal 1`..`Tal 8`; values are floats or `"-"` for not-attempted), `R..` per-problem Swedish comments (`Tal n: ...`).
- Sheet2 holds the threshold table (`Fx` 2.8/0, `E` 2.9/0, `D` 3.0/0, `C` 3.0/0.6, `B` 3.0/1.1, `A` 3.0/2.0) — read it rather than hard-coding, so future exams with different cut-offs still work via this script.

**Letter-grade rule** (matches teacher's threshold table in sheet2):

- `F` if `a_del < 2.8`
- `Fx` if `2.8 ≤ a_del < 2.9`
- `E` if `2.9 ≤ a_del < 3.0`
- `D` if `a_del ≥ 3.0` and `b_del < 0.6`
- `C` if `a_del ≥ 3.0` and `0.6 ≤ b_del < 1.1`
- `B` if `a_del ≥ 3.0` and `1.1 ≤ b_del < 2.0`
- `A` if `a_del ≥ 3.0` and `b_del ≥ 2.0`

The teacher's actual letter-grade call uses judgment (especially around the `E`/`Fx` borderline). The eval's deterministic rule may disagree with the recorded `Betyg`; the report calls out such cases.

**Tolerance-note grammar.** The XLSX `Poängjustering` column (col Q or similar — locate by header) and trailing `Tal N` comment columns carry teacher notes about acceptance bands. Accepted forms (combined with `;` or `,` separators in the same cell):

- `kan höjas 0,1 p på tal N` → upper band of `+0.1` on problem N
- `kan sänkas 0,1 p på tal N` → lower band of `-0.1` on problem N
- `kan höjas 0,1 p på tal N och tal M` → `+0.1` on N and M
- `kan höjas 0,1 p på tal N+M` → `+0.1` on N and M
- `kan höjas 0,1 på tal N` (missing `p`) — accept; tolerated typo seen in the data
- Any unparsed note → log a warning, fall back to `[grade, grade]` for that student
- Implementations MUST be tested against the exact strings in the workbook (see tests below)

For each `(student, problem)` the tolerance band is `[grade + lo, grade + hi]` where `lo, hi ∈ {-0.1, 0, +0.1}` per the parsed notes.

**Outputs:**

- `results/comparison.md` — per-student table (agent / human / signed error / within-tolerance), aggregate stats (MAE per problem, MAE total, letter-grade agreement, % within tolerance), top-3 disagreements with links.
- `results/comparison_summary.csv` — flat numeric summary for spreadsheets.

**Tests** (`eval/test_compare.py`, stdlib `unittest`):

1. `letter_grade()` for the boundary cases: `(2.79, 0) → F`, `(2.8, 0) → Fx`, `(2.9, 0) → E`, `(3.0, 0) → D`, `(3.0, 0.59) → D`, `(3.0, 0.6) → C`, `(3.0, 1.1) → B`, `(3.0, 2.0) → A`.
2. `parse_tolerance_note()` against the exact strings observed in the workbook:
   - `"kan höjas 0,1 p på tal 3 och tal 4"` → `{3: (0, +0.1), 4: (0, +0.1)}`
   - `"kan sänkas 0,1 p på tal 2, kan höjas 0,1 p på tal 3+4"` → `{2: (-0.1, 0), 3: (0, +0.1), 4: (0, +0.1)}`
   - `"kan sänkas 0,1 p på tal 2; kan höjas 0,1 på tal 7"` → `{2: (-0.1, 0), 7: (0, +0.1)}`
   - Empty / `None` → `{}`
3. `join_students()`: missing on agent side → `unmatched_human`; missing on human side → `unmatched_agent`; both present → matched row.
4. `read_jsonl()` raises a clear error on a malformed line and reports the line number.

`eval/validate_rubric.py` — stdlib only. Asserts per-problem item points (parent values only) sum to `max_points`, that every `special_case` has `effect: "set_total"` (the only mode Phase 1 supports), and emits a human-review summary to `results/rubric_summary.md` listing per problem: item count, line-item total, special-case count, global-deduction count, sub-point count. Run once before any grading.

## 10. Testing & demo

**Pre-run checks**
1. `eval/validate_rubric.py` passes; review `results/rubric_summary.md`.
2. `python3 -m unittest eval.test_compare` passes.
3. Smoke-test the skill on the shortest student PDF; eyeball the JSONL output for coherent Swedish, plausible scores, structured per-item awards, and at least one flag/deduction firing.
4. Review `results/page_index/<submission_id>.json` for that student — confirm the 8-problem mapping looks right before trusting full-run scores.

**Full run**
5. Skill invoked on all 9 students → page-index files + `agent_grades.jsonl`.
6. `compare_to_human.py` → `comparison.md` + `comparison_summary.csv`.

**Demo (≤5 min).** A full live grading of a student (8 sequential problems × multiple vision passes against 10–15 MB scans) realistically takes minutes, not seconds. The demo therefore replays a pre-recorded run for most of it and shows live grading for just one problem to keep narrative momentum:

1. Show exam + rubric PDFs (10 s).
2. Show the pre-run page-index file and grading JSONL for one student — narrate the structured per-item awards and deductions (60 s).
3. **Live**: invoke the skill to grade ONE problem (one student, one problem) — narrate the rubric-driven loop (~60 s).
4. Show the pre-run eval report (`comparison.md`) for all 9 students (60 s).
5. Walk through one biggest-disagreement case with the agent's `comment_sv` + structured awards next to the teacher's `Tal N: ...` comment (60 s).

## 11. File layout

```
.
├── .claude/skills/grade-sk1110-exam/SKILL.md
├── rubric/sk1110-260309.json
├── eval/
│   ├── validate_rubric.py
│   ├── compare_to_human.py
│   └── test_compare.py          # stdlib unittest
├── results/
│   ├── page_index/
│   │   └── <submission_id>.json # one per student, produced by skill (step 3)
│   ├── rubric_summary.md        # produced by validate_rubric.py
│   ├── agent_grades.jsonl       # produced by skill
│   ├── comparison.md            # produced by eval
│   └── comparison_summary.csv   # produced by eval
├── Exam/ Solution/ Grading_rules/ Ungraded/ Human_graded/   # existing
└── docs/superpowers/specs/2026-05-26-sk1110-auto-grader-phase1-design.md
```

## 12. Open questions for Phase 2/3 (not blocking)

- Phase 2 will need to parameterize the skill over an arbitrary rubric JSON + exam/solution PDF pair. Phase 1's skill should keep paths in one clearly-marked section to make that refactor easy.
- Phase 3 ablations to consider: with/without solution PDF, with/without rubric JSON, Sonnet 4.6 vs. Opus 4.7, per-problem-subagent vs. sequential.
