# Track B — Research coding and HPC workflow agents

Track B of the SCI Agentathon 2026 is a one-day, three-sub-team exercise built around
a shared scenario: a small harmonic-oscillator research workflow, end to end. Each
sub-team owns one stage of that workflow and uses an AI coding assistant (e.g. Claude
Code) to make real, demonstrable progress on it in a single day.

The skill Track B teaches is **how to set up, constrain, and drive a coding agent** on
a research-code task — scoping it to a folder, giving it a role document, working in a
propose → approve → verify loop, and reporting only what you can actually verify.

## Where to begin

Open [`00_start_here/README.md`](00_start_here/README.md) first. It explains how to
pick your sub-team, copy the right role template into your sub-team folder, and scope
your agent. From there you follow your sub-team's own README.

The files in `00_start_here/prompts/` are **optional example phrasings and
checkpoints**, not mandatory scripts — use them only if you want a model phrasing.

## Repo layout

```
Track_B/
  README.md                              this file
  00_start_here/                         front door — open this first
  01_hpc_simulation_workflow/            sub-team 1: HPC simulation workflow assistant
  02_research_code_debugging/            sub-team 2: research-code debugging + features
  03_scientific_postprocessing/          sub-team 3: post-processing + interpretation
```

## Deliverable — a working notebook

Each sub-team has (or will have) a local `DEMO_REPORT_TEMPLATE.md`. Treat it as a
**working notebook**, not an end-of-day form: at the end of each task, update the
matching section of the report before moving on. Record what you observed, what the agent
suggested, what you changed, what you verified, and what you should not overclaim. The
finished report can be used directly to prepare your 5-minute presentation.

All three sub-teams have their local templates now.

## Ground rules

- Work only inside your assigned sub-team folder unless the track lead says otherwise.
- Do not assume access to Dardel, external APIs, credentials, or private data.
- Ask the track lead before installing anything outside `requirements.txt`.
- Do not commit generated files (figures, outputs, run artefacts).
