# Sub-team 03 — Agentic scientific post-processing

## Story

You have received simulation data from another researcher. The data come from multiple
harmonic-oscillator runs performed with different solver choices and time steps. The
handoff is intentionally realistic: there is a summary table, selected time-series
traces, metadata, and a generator script, but the structure is not immediately obvious.
Your goal is to use an analysis agent to understand the data, build a reproducible
analysis, and make claims that are supported by checks, figures, and computed values.

First, you will work on a **reference** dataset. Then you will receive a **challenge**
dataset with the same structure. Your previous analysis should run on the new data, but
it may reveal behaviour that deserves further investigation.

The data layout is deliberately a bit cumbersome, to mimic a real research-data handoff.
You do **not** need to document every column in exhaustive detail — just understand the
structure well enough to make a defensible analysis.

This is not a debugging exercise. The lesson is the workflow: understand the data, build
a reproducible pipeline, ground every claim in evidence, and **verify** what the agent
tells you with your own checks instead of taking it on trust.

The deliverable is a filled `DEMO_REPORT_TEMPLATE.md` saved inside this folder. It is
also the basis for your final 5-minute presentation.

## Scientific background (short)

The data come from the undamped 1D harmonic oscillator `m x'' = -k x`, with angular
frequency `omega = sqrt(k / m)` and period `T = 2 pi / omega`. Each run integrates this
system with one of several time integrators across a range of time steps (and possibly
other settings), so the data supports comparing how accuracy behaves with method and
step size.

- `raw_runs.csv` — one row per simulation run (parameters plus output diagnostics).
- `trajectories_sample.csv` — selected time-series traces for a subset of runs.
- `metadata.json` — describes the files and every column.

That is enough context; you do not need a deeper physics derivation to do the analysis.

## Repo layout

This folder is self-contained after Task 1.

- `README.md` — this file
- `VERIFY.md` — exact setup and verification commands for Windows PowerShell and Linux/macOS
- `DEMO_REPORT_TEMPLATE.md` — fill this in for your readout
- `data/reference/` and `data/challenge/` — the two pre-generated datasets
- `scripts/` — `generate_dataset.py` (for transparency/reproducibility) and `quicklook.py`
- `tests/` — pytest dataset-integrity suite
- `outputs/` — created by your scripts at runtime; gitignored, do not commit

The agent role document lives outside this folder, in
`../00_start_here/agent_role_templates/`, and is copied in during Task 1.

## Task 1 — Set up the analysis agent

**Goal:** Establish the agent's role, scope, and guardrails before any data analysis
begins. This prevents the agent from acting outside the intended project folder or
making unsupported claims.

1. From this folder, copy
   `../00_start_here/agent_role_templates/03_scientific_postprocessing_AGENT_ROLE_TEMPLATE.md`
   into this folder and **rename** the copy:
   - to `CLAUDE.md` if you are using Claude Code, OR
   - to `AGENT_ROLE.md` for any other agent tool, OR
   - paste the file contents directly into your tool if it expects rules or role
     instructions in the interface.
2. Configure your tool so the agent has access **only to
   `Track_B/03_scientific_postprocessing/`**.
3. Ask the agent to read the role file first and summarise back, in its own words, its
   **role, scope, restrictions, and workflow**. Check that the summary is faithful.
4. Do **not** generate any analysis yet.

Before moving on, update the **Task 1** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 2 — Inspect the reference dataset structure yourself

**Goal:** Build a human understanding of the data structure before asking the agent to
analyse it. The team should know what files exist, what one row represents, and how the
files connect.

Understand the **reference** data with your own eyes before asking the agent to analyse it. Inspect
`data/reference/metadata.json` and the CSV files, and get an idea of:

- which files exist
- which file is summary-level and which is time-series-level;
- what one row represents in each file;
- how `run_id` connects the two files;
- which columns are input parameters and which are outputs or diagnostics;
- what `quicklook.py` plots;
- whether the reference quicklook figure shows clear trends;

Run:

```bash
python -m pytest -v tests
python scripts/quicklook.py --dataset reference
```

Open the figures under `outputs/reference/` and `outputs/challenge/`. 

You may ask the agent to explain what `quicklook.py` plots, but start with your own inspection and write
down what you notice. Use the agent to explore and understand after your first attempt on your own.

The goal is to understand the data structure.

Before moving on, update the **Task 2** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 3 — Build a first reproducible analysis on the reference dataset

**Goal:** Create a reproducible analysis pipeline for the reference dataset. The analysis
should produce figures, tables, and claims that can be regenerated from commands.

Now bring the agent in to build your first analysis pipeline on `data/reference`.

Work **test-first**. Before any implementation, ask the agent to propose:

- what outputs the analysis should produce;
- what minimal checks would show that the analysis actually worked;
- which values, tables, or figures should exist after the script runs.

> **Before implementation, define the expected outputs and at least one check that would
> tell you whether the analysis ran correctly.**

Examples of checks (decide which apply to your design):

- the expected output folder exists;
- the expected figures are generated;
- a Markdown summary is generated;
- the grouped table contains all solver labels;
- no claim is written without a computed value, table, or figure behind it.

Remember to work only on `data/reference`.

Then ask the agent to:

1. create a **reproducible** analysis script (for example `scripts/analyze_data.py`)
   rather than a series of one-off manual steps;
2. generate, under `outputs/reference/`, at least two figures, at least one Markdown
   table, and a short interpretation (for example `outputs/reference/SUMMARY.md`)
   grounded in computed values, not impressions.

Run your checks and confirm the expected outputs exist. Then ask the agent explicitly:

> **Does anything look off in the data or plots? Which run, group, or trend should we
> investigate further?**

For the reference dataset it is fine if nothing dramatic appears — the point is to build
a pipeline you can reuse.

Before moving on, update the **Task 3** section of `DEMO_REPORT_TEMPLATE.md`.


## Task 4 — Apply the analysis to the challenge dataset and harden the pipeline

**Goal:** Apply the same analysis to a new dataset and improve the pipeline so suspicious
data are not silently turned into conclusions. Agent observations should be converted
into reproducible checks and visible guardrails.

You now receive a second dataset, `data/challenge/`, with the same structure as the reference dataset. The goal of this task is **not only to find suspicious runs**, but to improve the analysis pipeline from Task 3 so that it does not silently turn questionable data into scientific claims.

In Task 3, you built a first analysis on `data/reference/`. Now you should apply the same analysis to `data/challenge/` and ask:

> Does the same analysis still support the same conclusions, or does something in the new dataset require extra checks?

### Step 1 — Re-run the Task 3 analysis on the challenge dataset

Ask the agent to help you adapt your Task 3 analysis script so it can analyse either dataset, for example with a command such as:

```bash
python scripts/analyze_data.py --dataset reference
python scripts/analyze_data.py --dataset challenge
```

or an equivalent interface.

The script should write separate outputs, for example:

```text
outputs/reference/
outputs/challenge/
```

Run the analysis on both datasets and compare:

- the generated figures;
- the grouped summary table;
- the written summary;
- any trends or conclusions.

Ask yourself and the agent:

> Which run, solver group, parameter value, or trend looks suspicious enough that we should not simply average it into a conclusion?

### Step 2 — Turn observations into explicit checks

The agent may immediately point out suspicious behaviour. That is useful, but it is not enough.

A suspicious observation becomes a result only when it is verified by a reproducible check.

Before writing code, ask the agent to propose a short check plan:

```text
What checks should we add before trusting the challenge-dataset analysis?
For each check, explain:
1. what it tests;
2. what output it should produce;
3. what kind of problem it would catch or rule out;
4. how we will use the result in the final interpretation.
Do not edit files yet.
```

Then implement the checks in a script such as:

```text
scripts/check_data_quality.py
```

The script should produce outputs such as:

```text
outputs/challenge/flagged_runs.csv
outputs/challenge/data_quality_report.md
```

Useful checks may include:

- missing or null values;
- duplicate `run_id` values;
- non-finite metrics;
- unexpected status values;
- inconsistent timing or run-duration information;
- whether each sampled trajectory covers the expected time interval;
- values that sit far from comparable runs;
- values that dominate a group summary;
- whether there are enough points before fitting or trusting a trend.

You do not need to implement every possible check. Choose checks that are motivated by what you saw in the plots and tables.

### Step 3 — Use the checks to improve the analysis

After identifying flagged runs or suspicious groups, update the Task 3 analysis so that it handles them explicitly.

For example, the improved analysis could:

- add a `flagged` column to the summary table;
- mark flagged runs in the plots;
- produce grouped statistics with and without flagged runs;
- avoid using flagged runs in fitted trends unless explicitly justified;
- add a note in `outputs/challenge/SUMMARY.md` explaining how the interpretation changes.

The important point is that the analysis should not silently hide or silently include suspicious data. It should make the decision visible.

### Step 4 — Compare before and after guardrails

Your Task 4 output should make the improvement clear.

At minimum, produce:

```text
outputs/challenge/flagged_runs.csv
outputs/challenge/data_quality_report.md
outputs/challenge/SUMMARY.md
```

and at least one updated figure or table showing how the guardrails affected the interpretation.

In your report, answer:

- What looked suspicious in the challenge dataset?
- Did the agent identify the same issue you noticed, or something different?
- Which checks did you implement?
- Which run(s), group(s), or trends were flagged?
- What evidence supports each flag?
- How did the guardrails change the analysis compared with the first Task 3 version?
- Which conclusions remain valid, and which should be treated more carefully?

Before moving on, update the Task 4 section of `DEMO_REPORT_TEMPLATE.md`.

## Task 5 — Make the result visually compelling

**Goal:** Turn the analysis into a clear visual product for the final presentation. The
result should make the scientific story easier to understand while remaining
reproducible and verified.

This is the creative final task: build a visual product that would make a strong
5-minute presentation. Keep it **check-first**.

Before implementing, define:

- what the visual product is supposed to communicate;
- what command regenerates it;
- what file(s) it should produce;
- what minimal check proves it was generated correctly.

If you build a command-line interface, first write down one or two expected commands and
the output files they should produce, then implement to match.

Some directions you could take (examples only):

- animate selected trajectories with matplotlib;
- a side-by-side reference-vs-challenge dashboard;
- a convergence figure that highlights only the runs flagged by your own guardrail
  script;
- a Markdown or HTML report that embeds your figures and tables;
- a CLI where the user selects dataset, solver, metric, and output folder;
- a trajectory comparison figure or animation across solvers and time steps;
- a compact "analysis summary card" figure for the talk.

Define the message, ask the agent for a small implementation plan, add checks or tests
where appropriate, implement, regenerate the outputs, and run your check.

Before moving on, update the **Task 5** section of `DEMO_REPORT_TEMPLATE.md`.

## Deliverable

A filled `DEMO_REPORT_TEMPLATE.md` saved inside this folder. Use it to build your final
5-minute presentation: what the data were, what you built, what you found in the
challenge dataset, how you verified it, and what you would not overclaim.
