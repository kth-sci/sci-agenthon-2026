# Project state — SK1110 auto-grader (KTH agentathon, track A1)

## What this project is

Building an AI auto-grader for the SK1110 physics exam given 2026-03-09. Three-phase plan:

1. **Phase 1 — agentathon demo** ✅ **COMPLETE**. Claude Code skill that grades 9 student PDFs problem-by-problem against the teacher's rubric, plus a Python eval script comparing to human grades.
2. **Phase 2 — scale to full cohort** (in progress, 19/155 graded). Same skill + rubric unchanged; apply to all 155 students; report per-problem MAE vs teacher.
3. **Phase 3** — eval / writeup of how well LLM grading works on handwritten Swedish physics exams. (not started)

## Phase 2 status (partial; paused on rate limit)

The full-cohort Ungraded/ directory now has 155 student PDFs (146 new beyond the original 9). The eval's `XLSX_PATH` now points at `Human_graded/RES_TENSK1110_SK1112_SK1117_260309.xlsx` (155 students, same schema, no `Poängjustering` column — eval handles that gracefully).

- **P2.1** ✅ Eval pointed at full-cohort XLSX (uncommitted change in `eval/compare_to_human.py:line ~XLSX_PATH`).
- **P2.2** ⏳ Graded so far: 19/155 (9 from Phase 1 + 10 dispatched in Phase 2 before session rate limit hit). 136 students remain to grade.
- **P2.3** pending — concatenate fragments + schema check on the full 155.
- **P2.4** pending — run eval over 155, report per-problem MAE.

### How to resume

1. The session rate limit reset at the time noted by the harness; wait until then.
2. Read `/tmp/remaining_students.tsv` (4 cols: canvas_id, submission_id, name, filename) for the 136 still-to-grade list. If the file is gone (tmp wiped), regenerate with this snippet against the consolidated `results/agent_grades.jsonl`:
   ```python
   import os, json
   from pathlib import Path
   from eval.compare_to_human import read_xlsx_human_grades, XLSX_PATH
   graded={json.loads(l)["canvas_id"] for l in open("results/agent_grades.jsonl") if l.strip()}
   by_canvas={s["canvas_id"]:s["name"] for s in read_xlsx_human_grades(XLSX_PATH)[0]}
   for fn in sorted(os.listdir("Ungraded")):
       if not fn.endswith(".pdf"): continue
       p=fn[:-4].split("_")
       c,s=p[1],p[3]
       if c in graded: continue
       print(f"{c}\t{s}\t{by_canvas.get(c,c)}\t{fn}")
   ```
3. Dispatch grading subagents (sonnet, general-purpose) using the same prompt template used so far (see git log near where this CLAUDE.md was committed; the template tells the subagent to write ONLY to `results/agent_grades.<canvas>.jsonl` — NOT to touch the main consolidated file). Pace the dispatches to fit within the harness rate-limit window — batches of ~10 ran cleanly, the 17-call burst hit the limit.
4. After all 136 are done, concatenate per-student fragments into `results/agent_grades.jsonl` (the consolidation script in this same git-log range deduplicates by `canvas_id`).
5. Run `python3 eval/compare_to_human.py` → `results/comparison.md` + `results/comparison_summary.csv`. Report per-problem MAE.

### Phase 2 design note

Phase 2 was originally scoped (in the Phase-1 spec §12) as parameterising the skill/eval over arbitrary rubrics. The user redefined it here as scaling the existing Phase 1 grader to the full cohort. SKILL.md and rubric JSON are intentionally unchanged. The only Phase-2 code change is `XLSX_PATH` pointing at the new file.

Each phase gets its own spec → plan → implementation cycle.

## Current status — Phase 1 complete

Plan executed via `superpowers:subagent-driven-development`, working directly on `master`. All 15 plan tasks done:

| Task | Status | Commit |
|---|---|---|
| T1 Scaffold | ✅ | `9889861` |
| T2 Rubric validator + tests | ✅ | `c73ad56` |
| T3 Rubric JSON: problem 1 + globals | ✅ | `e2972b1` |
| T4 Rubric JSON: Del A 2–5 | ✅ | `9b247bf` |
| T5 Rubric JSON: Del B 6–8 | ✅ | `62a3735` |
| T6 `letter_grade()` | ✅ | `f2af939` |
| T7 `parse_tolerance_note()` | ✅ | `8b6e5b0` |
| T8 `read_jsonl()` | ✅ | `4e53196` |
| T9 `read_xlsx_human_grades()` | ✅ | `dbd942f` |
| T10 `join_students()` | ✅ | `885ee3a` |
| T11 Eval driver CLI | ✅ | `c940c61` |
| T12 `grade-sk1110-exam` skill | ✅ | `c2772ca` |
| T13 Smoke test (Andersson Oliver) | ✅ | (results gitignored) |
| T14 Full run on 9 students | ✅ | (results gitignored) |
| T15 Run eval and review | ✅ | (results gitignored) |
| Post-review hardening | ✅ | `14cd3d2` |

**28/28 unit tests pass.** Rubric validator confirms all 8 problems sum to 1.0 p and no sub-point exceeds its parent.

## Eval results (the demo headline)

Agent vs. teacher over 9 students (`results/comparison.md`):
- **Letter-grade agreement: 6/9** (demo target ≥7/9 — missed by one).
- **Overall MAE: 0.14 p** (demo target ≤0.2 — met). Per-problem MAE 0.03–0.26.
- **Systematic over-scoring**: mean signed error +0.067 p/problem; 26/64 problems scored higher than the teacher, 10 lower, 28 exact. The 3 letter disagreements are all the agent being too generous at a boundary — notably **Andreasen: agent C vs teacher F** (passed a student the teacher failed), Grigoryan C vs E, Göransson B vs C.
- Smoke-test student (Andersson Oliver) was a perfect 8/8 match. Special-case detection (forgot_n_factor, spherical_interface, f_instead_of_sprime, etc.) worked well and often matched the teacher's deductions.

## How to reproduce the run

The skill `grade-sk1110-exam` loads at session start. To grade: invoke it on a PDF under `Ungraded/`. For all 9, fan out one subagent per student writing `results/agent_grades.<canvas_id>.jsonl` fragments, then concatenate to `results/agent_grades.jsonl`. Then `python3 eval/compare_to_human.py`.

## Known follow-ups (for Phase 2)

- The 9-student grades were produced before the problem-8 rubric restructure (`14cd3d2`). Re-running T14 would refresh P8 *line-item* partial credit for the ~1–2 students not graded via a P8 special case; headline numbers unaffected.
- Grading subagents must be given the full per-problem JSON template (now in SKILL.md) — they dropped `max_points`/`page_refs` on the first run; these were backfilled.
- Consider parameterizing the skill + eval over an arbitrary rubric JSON / exam (Phase 2).

## Approved artifacts on disk

- **Spec** — [docs/superpowers/specs/2026-05-26-sk1110-auto-grader-phase1-design.md](docs/superpowers/specs/2026-05-26-sk1110-auto-grader-phase1-design.md) (committed `3e98e33`).
- **Plan** — [docs/superpowers/plans/2026-05-26-sk1110-auto-grader-phase1.md](docs/superpowers/plans/2026-05-26-sk1110-auto-grader-phase1.md) (committed `995ad6a`).
- **Rubric** — [rubric/sk1110-260309.json](rubric/sk1110-260309.json).
- **Eval module** — [eval/compare_to_human.py](eval/compare_to_human.py), [eval/validate_rubric.py](eval/validate_rubric.py), [eval/test_compare.py](eval/test_compare.py), [eval/test_validate_rubric.py](eval/test_validate_rubric.py).
- **Grading skill** — [.claude/skills/grade-sk1110-exam/SKILL.md](.claude/skills/grade-sk1110-exam/SKILL.md).
- **Demo slides** — [demo/index.html](demo/index.html). Self-contained 12-slide HTML deck for colleagues: inputs, markdown artifacts, agentic workflow, headline eval metrics, error/bias charts, boundary failures, and Phase 2 takeaways.

## Decisions locked in (from brainstorming + Codex review)

- **Goal:** auto-grading agent + eval against human ground truth.
- **Eval target:** per-problem points + Swedish comments, structured `problem_results[n]` JSONL.
- **Runtime:** Claude Code itself is the agent. One skill drives grading.
- **Join key:** `canvas_id` (6-digit XLSX `ID` column, parsed from filename's second underscore field), NOT the trailing 7-digit submission ID.
- **Letter grade thresholds** (from XLSX sheet2):
  - F < 2.8 in A-del; Fx 2.8–2.9; E 2.9–3.0
  - D ≥ 3.0 (b_del < 0.6); C ≥ 0.6; B ≥ 1.1; A ≥ 2.0 (b_del; conditional on a_del ≥ 3.0)
- **Letter grade computed by eval script, not the agent.**
- **Page indexing** is a dedicated first pass; the page index is written to disk before grading begins.
- **`apply_global_deductions: false`** for all special cases in this exam — overrides are the final score (before clamping).
- **Demo targets** (not hard gates): ≥7/9 letter agreement, MAE per problem ≤ 0.2 p.

## Repository state

- `git init` done, branch `master`, 18 commits after the demo deck commit (3 spec/plan + 13 implementation + project-state + demo slides). No git remote configured.
- The `.gitignore` excludes: `Ungraded/`, `Human_graded/`, `results/`, `Exam/`, `Grading_rules/`, `Solution/`, `__pycache__/`, `.venv/`, `.DS_Store`. Placeholders under `results/` (incl. `results/page_index/`) are whitelisted via `!results/.gitkeep` etc.
- The `consult-codex` / `consult-antigravity` skills now live only at `~/.claude/skills/` (user-global); their source subdirs have been removed from this project.

## Things NOT to forget

- The exam is **Swedish**. All `evidence_sv` / `comment_sv` strings from the grader must be in Swedish to match the teacher's style.
- Student PDFs contain **names and personnummer** — privacy-sensitive. Excluded from git. Do NOT send them through external/non-Anthropic services (e.g. the global `consult-codex` / `consult-antigravity` skills, which route data to OpenAI / Google).
- This is `claude-opus-4-7[1m]` (1M context). Reading whole student PDFs (10–15 MB) in one pass is fine.
- The `eval/` Python is **stdlib-only** by design. Do not introduce `openpyxl` or other dependencies in Phase 1.
- The rubric is **closed** — don't invent rubric items the agent didn't see in `rubric/sk1110-260309.json`.

## Open tasks in tracker

None — all 15 Phase 1 plan tasks plus post-review hardening are complete. Next work is Phase 2 (its own spec → plan → implementation cycle); see "Known follow-ups" above for candidate scope.
