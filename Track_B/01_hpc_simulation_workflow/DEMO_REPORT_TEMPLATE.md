# Demo report — Sub-team 01 (HPC workflow preparation)

This report is **not only for the end**. Use it during the exercise: update the relevant
section after each task, before moving on. It can later become your 5-minute presentation
outline. Fill in each section yourself, from what your team actually did and observed —
do not copy text out of the README.

## Team members

-

## Task 1 — Agent setup

- Which agent tool did you use?
- Which role file did you copy, and what did you rename it to
  (`CLAUDE.md` / `AGENT_ROLE.md` / pasted as a system prompt)?
- Which folder did you scope the agent to?

## Task 2 — Workflow inspection

- What parameters are swept, and how many runs are there?
- What command runs a single simulation? What command runs the local sweep?
- What is the job script trying to do?
- What do the sample logs suggest?
- Which issues look like local workflow issues, and which would only be verifiable on a
  real cluster?

## Task 3 — Local reproducibility

- What did the validation report and dry-run show?
- What happened when you ran the full local sweep?
- What fixes did the agent propose, and which did you approve and why?
- Which commands did you run after the fixes, and what outputs were produced?

## Task 4 — Pre-submission guardrails

- Before editing, which checks did you decide the package should pass, and what does each
  catch or rule out?
- Which checks did you add to `validate_package.py` (or a helper script)?
- What does the validation report now show (PASS / WARN / FAIL)?
- Which problems are now caught before submission?

## Task 5 — Submission-ready package or diagnosis tool

- What did you build, and what is it meant to communicate?
- What command regenerates it, and what file(s) does it produce?
- What check or command verifies it was produced correctly?

## Final demo outline

- What will you show in 5 minutes? (commands, the validation report, the one improvement
  worth presenting)

## What not to overclaim

- What is verified only locally, and what remains an unverified cluster assumption?
- What would still need a real cluster (or more information) to confirm?

## Links

Paths to the key files, reports, or figures inside this sub-team folder.

-
