"""Compare agent grades (JSONL) to human ground truth (XLSX) for SK1110."""
from __future__ import annotations

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator


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


XLSX_PATH = Path("Human_graded/RES_TENSK1110_SK1112_SK1117_260309.xlsx")
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
    """Yield (row_number, {col_index: value}) with shared strings resolved."""
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
        pr_map = a.get("problem_results") or {}
        # Guard: every problem 1..8 must be present, else the eval would
        # silently treat a dropped problem as a legitimate 0 (review finding).
        missing = [n for n in range(1, 9) if str(n) not in pr_map]
        if missing:
            raise JsonlError(
                f"{a.get('canvas_id')}: problem_results missing keys {missing}"
            )
        agent_tal = {int(n): pr["points"] for n, pr in pr_map.items()}
        # Round before the letter-grade boundary test: a_del/b_del are summed
        # by the agent and can carry float dust (e.g. 2.9000000000000004),
        # which would otherwise flip a borderline grade (review finding).
        a_del = round(float(a.get("a_del") or 0.0), 1)
        b_del = round(float(a.get("b_del") or 0.0), 1)
        rows.append(Row(
            canvas_id=a["canvas_id"],
            name=a.get("name") or h.get("name", ""),
            agent_tal=agent_tal,
            human_tal=h["tal"],
            tolerance=full_band,
            agent_a_del=a_del,
            human_a_del=h.get("a_del"),
            agent_b_del=b_del,
            human_b_del=h.get("b_del"),
            agent_betyg=letter_grade(a_del, b_del),
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
