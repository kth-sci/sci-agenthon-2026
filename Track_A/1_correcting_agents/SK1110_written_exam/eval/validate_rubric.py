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
        # Sub-points are carve-outs of their parent (spec §4): their total
        # must not exceed the parent's points. Catches transcription errors
        # where a parent-level rubric line was mis-entered as a sub.
        for item in items:
            sub_sum = sum(sub["points"] for sub in item.get("sub", []))
            if sub_sum > item["points"] + POINT_TOLERANCE:
                raise RubricError(
                    f"problem {n}, item {item.get('id')!r}: sub-points sum to "
                    f"{sub_sum:g}, exceeds parent points {item['points']:g}"
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
