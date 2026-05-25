# Sub-team 03: Agentic Scientific Post-processing

## Story

You have received simulation data from another researcher. The data come from multiple harmonic-oscillator runs performed with different solver choices and time steps. The handoff is intentionally realistic: there is a summary table, selected time-series traces, metadata, and a generator script, but the structure is not immediately obvious.

The exercise happens in two moments, like a real analysis handoff. First, you receive a reference dataset and build a reproducible analysis workflow. Later, you receive a second dataset with the same structure. Your task is to apply the same workflow to the new data and check whether the same interpretation is still defensible.

This is not a debugging exercise. The lesson is the workflow: understand the data, build a reproducible pipeline, ground every claim in evidence, and verify what the agent tells you with your own checks instead of taking it on trust.

The goal is data analysis and defensible data interpretation.

## Scientific Background

The data come from the undamped 1D harmonic oscillator `m x'' = -k x`, with angular frequency `omega = sqrt(k / m)` and period `T = 2 pi / omega`.

Each run integrates this system with one of several time integrators across a range of time steps. The data support comparing how accuracy behaves with method and step size.

- `raw_runs.csv` - one row per simulation run, including parameters and output diagnostics.
- `trajectories_sample.csv` - selected time-series traces for a subset of runs.
- `metadata.json` - describes the files and columns.

That is enough context; you do not need a deeper physics derivation to do the analysis.

## What You Are Building

A good target is a reproducible analysis workflow that:

- runs from clear commands;
- produces figures, tables, or reports under `outputs/`;
- makes data-quality decisions visible;
- connects every claim to a computed value, table, figure, or check.

Use <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a> as a working notebook. It is not only for the end of the day.

## Files to Know

- `00_SUBTEAM_GUIDE.md` - this guide.
- `01_VERIFY.md` - local verification commands for this sub-team.
- `DEMO_REPORT_TEMPLATE.md` - fill this in for your readout.
- `data/reference/` and `data/challenge/` - the two pre-generated datasets.
- `scripts/generate_dataset.py` - deterministic dataset generator.
- `scripts/quicklook.py` - starter inspection script.
- `tests/` - dataset-integrity tests.
- `outputs/` - created by scripts at runtime; do not commit generated files.

Shared commands: <a href="../02_COMMANDS_AND_VERIFY.md" target="_blank" rel="noopener noreferrer">../02_COMMANDS_AND_VERIFY.md</a>  
Local verification notes: <a href="01_VERIFY.md" target="_blank" rel="noopener noreferrer">01_VERIFY.md</a>

## Task 1: Set Up the Analysis Agent

**Goal:** Establish the agent's role, scope, and guardrails before any data analysis begins.

Do both parts of this setup before asking the agent to inspect files.

### Step 1: Copy the role file into the sub-team folder

Run from the repository root, `Track_B/`, or copy the file manually in your file browser:

```bash
cp agent_role_templates/03_scientific_postprocessing_AGENT_ROLE_TEMPLATE.md 03_scientific_postprocessing/CLAUDE.md
```

On Windows PowerShell, run from the repository root, `Track_B/`:

```powershell
Copy-Item agent_role_templates\03_scientific_postprocessing_AGENT_ROLE_TEMPLATE.md 03_scientific_postprocessing\CLAUDE.md
```

If you are not using Claude Code, rename the copy to `AGENT_ROLE.md` instead, or paste the template contents into your tool's rules/system-prompt field.

### Step 2: Scope the agent to the sub-team folder

Configure your tool so the agent can access only:

```text
Track_B/03_scientific_postprocessing
```

If your agent tool asks for a working directory, project folder, allowed folder, or workspace root, set it to `Track_B/03_scientific_postprocessing`. Do not give the agent access to the whole Track B repository for this sub-team task.

### Step 3: Ask the agent to confirm its role

Ask the agent:

```text
Please read Track_B/03_scientific_postprocessing/CLAUDE.md and Track_B/03_scientific_postprocessing/00_SUBTEAM_GUIDE.md. Summarize your role, scope, restrictions, and workflow before doing anything else. Do not edit files until we approve a plan.
```

Check that the summary is faithful before continuing. The agent should understand that claims need computed evidence, not only visual impressions.

Before moving on, update the **Task 1** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 2: Inspect the Reference Dataset Structure Yourself

**Goal:** Build a human understanding of the data structure before asking the agent to analyze it.

This is the first moment of the data handoff. Treat `data/reference/` as the dataset you receive first, and understand it with your own eyes before asking the agent to analyze it. Inspect `data/reference/metadata.json`, `data/reference/raw_runs.csv`, and `data/reference/trajectories_sample.csv`, and get an idea of:

- which files exist;
- which file is summary-level and which is time-series-level;
- what one row represents in each file;
- how `run_id` connects the two files;
- which columns are input parameters and which are outputs or diagnostics;
- what `quicklook.py` plots;
- whether the reference quicklook figure shows clear trends.

Run from `Track_B/03_scientific_postprocessing`:

```bash
python -m pytest -q
python scripts/quicklook.py --dataset reference
```

Open the generated figure under `Track_B/03_scientific_postprocessing/outputs/reference/`.

You may ask the agent to explain what `quicklook.py` plots, but start with your own inspection and write down what you notice.

Before moving on, update the **Task 2** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 3: Build a First Reproducible Analysis on the Reference Dataset

**Goal:** Create a reproducible analysis pipeline for the reference dataset.

The analysis should produce figures, tables, and claims that can be regenerated from commands.

In a real project, this is the point where a notebook or quick manual plot often becomes fragile. Here, the goal is to turn the first dataset into a reusable analysis command before the second dataset arrives.

Work check-first. Before any implementation, ask the agent to propose:

- what outputs the analysis should produce;
- what minimal checks would show that the analysis actually worked;
- which values, tables, or figures should exist after the script runs.

Examples of checks:

- the expected output folder exists;
- the expected figures are generated;
- a Markdown summary is generated;
- the grouped table contains all solver labels;
- no claim is written without a computed value, table, or figure behind it.

Then ask the agent to create a reproducible analysis script, for example `scripts/analyze_data.py`, rather than a series of one-off manual steps.

A good target is a command like this, run from `Track_B/03_scientific_postprocessing`:

```bash
python scripts/analyze_data.py --dataset reference
```

The script might generate, under `outputs/reference/`, at least two figures, one Markdown table, and a short interpretation such as `outputs/reference/SUMMARY.md`, grounded in computed values.

Run your checks and confirm the expected outputs exist. Then ask the agent explicitly:

```text
Do the computed values and plots support the interpretation we are making? Is there any run, group, or trend that deserves further checking before we cite it?
```

For the reference dataset it is fine if nothing dramatic appears. The point is to build a pipeline you can reuse.

Before moving on, update the **Task 3** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 4: Apply the Analysis to the Second Dataset and Harden the Pipeline

**Goal:** Apply the same analysis to a new dataset and check whether the analysis pipeline supports defensible comparison.

This is the second moment of the handoff. You now receive `data/challenge/`, a second dataset with the same structure as the reference dataset. The goal is to run the same analysis, compare the evidence, and decide whether any additional checks are needed before making claims.

Possible outline:

- Adapt the Task 3 analysis script so it can analyze either dataset.
- Run the analysis on both datasets.
- Compare figures, grouped summary tables, and written summaries.
- Ask which run, solver group, parameter value, or trend deserves closer checking before it is used in a conclusion.
- Convert that observation into one or more reproducible checks.
- Update the analysis so checks, limitations, or interpretation changes are visible.

Example commands, if your script uses a `--dataset` option. Run from `Track_B/03_scientific_postprocessing`:

```bash
python scripts/analyze_data.py --dataset reference
python scripts/analyze_data.py --dataset challenge
```

Suggested checks include:

- missing or null values;
- duplicate `run_id` values;
- non-finite metrics;
- unexpected status values;
- inconsistent timing or run-duration information;
- whether each sampled trajectory covers the expected time interval;
- values that sit far from comparable runs;
- values that dominate a group summary;
- whether there are enough points before fitting or trusting a trend.

You do not need to implement every possible check. Choose checks motivated by what you saw when comparing the two datasets.

Possible outputs, if your checks identify records or groups that need extra attention, include:

- `outputs/challenge/flagged_runs.csv`
- `outputs/challenge/data_quality_report.md`
- `outputs/challenge/SUMMARY.md`

Suggested prompt to ask the agent before editing:

```text
What checks should we add before trusting the comparison between the reference and challenge datasets? For each check, explain what it tests, what output it should produce, what kind of issue it would catch or rule out, and how we will use the result in the final interpretation. Do not edit files yet.
```

Before moving on, update the **Task 4** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 5: Make the Result Visually Compelling

**Goal:** Turn the analysis into a clear visual product for the final presentation while keeping it reproducible and verified.

Before implementing, define:

- what the visual product is supposed to communicate;
- what command regenerates it;
- what files it should produce;
- what minimal check proves it was generated correctly.

Suggested directions:

- Build a phase-space or phase-diagram representation of the harmonic oscillator. If trajectory data are available, plot `x` versus `v`; if only aggregate data are useful, build a stability or quality map over method, timestep, and energy drift.
- Create a side-by-side reference-vs-challenge figure.
- Highlight runs or groups identified by your data-quality checks, if any.
- Create a Markdown or HTML report that embeds figures and tables.
- Add a CLI where the user selects dataset, solver, metric, and output folder.
- Animate selected trajectories with matplotlib.
- Build a compact analysis summary figure for the final talk.

Define the message, ask the agent for a small implementation plan, add checks or tests where appropriate, implement, regenerate the outputs, and run your check.

Before moving on, update the **Task 5** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Deliverable

A filled `DEMO_REPORT_TEMPLATE.md` saved inside `Track_B/03_scientific_postprocessing`. Use it to build your final 3-5 minute presentation: what the data were, what you built, what the reference-vs-challenge comparison showed, how you verified it, and what you would not overclaim.

Next: <a href="01_VERIFY.md" target="_blank" rel="noopener noreferrer">open 01_VERIFY.md</a>.
