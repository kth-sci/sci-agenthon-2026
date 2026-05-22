# Sub-team 02 - Agentic research-code debugging

## What this exercise teaches

This exercise is not primarily about fixing a Python bug. The main learning goal is
to **set up, constrain, and drive a coding agent** so it makes safe, verified
progress on a research-code task.

The small harmonic-oscillator project in this folder is the substrate. The agent
workflow is the lesson.

The deliverable is a filled `DEMO_REPORT_TEMPLATE.md` saved inside this folder.

## Repo layout

This folder is self-contained after Task 1.

- `README.md` - this file
- `VERIFY.md` - exact setup and verification commands for Windows PowerShell and Linux/macOS
- `DEMO_REPORT_TEMPLATE.md` - fill this in for your readout
- `run_tests.sh` - Linux/macOS test wrapper; see `VERIFY.md` for cross-platform commands
- `src/` - source code for the oscillator, integrators, and diagnostics
- `tests/` - pytest test suite
- `scripts/` - scripts to run and visualise the simulation
- `outputs/` - created by `plot_simulation.py`; gitignored, do not commit

The agent role document lives outside this folder, in:

```text
../00_start_here/agent_role_templates/
```

You copy it into this folder during Task 1.

## Task 1 - Set up the coding agent

**Goal:** Establish the agent's role, scope, and guardrails before any code is inspected
or modified. This makes the agent workflow reusable in future research-code projects.

1. From this folder, copy:

   ```text
   ../00_start_here/agent_role_templates/02_research_code_debugging_AGENT_ROLE_TEMPLATE.md
   ```

   into this folder and rename the copy:

   - to `CLAUDE.md` if you are using Claude Code or Claude Desktop, OR
   - to `AGENT_ROLE.md` for another agent tool, OR
   - paste the file contents directly into your tool if it expects rules or role instructions in the interface.

2. Configure your tool so the agent has access **only to this folder**:

   ```text
   Track_B/02_research_code_debugging/
   ```

3. Ask the agent to read the role file first and summarise, in its own words:

   - its role;
   - its scope;
   - its restrictions;
   - its workflow.

4. Check that the summary is faithful before continuing.

5. Do **not** edit code yet.

Before moving on, update the **Task 1** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 2 - Observe the failing behaviour yourself before the agent inspects the code

**Goal:** Observe the failure directly before asking the agent for help. This gives the
team its own evidence from tests, scripts, and plots, rather than treating the agent as
an oracle.

Run the code and see the failure with your own eyes before asking the agent to
inspect the codebase.

The goal is to first experience the problem as a researcher would: through tests,
script output, and a diagnostic figure.

1. Run the tests. See `VERIFY.md` for the exact command.

2. Run the numerical driver:

   ```bash
   python scripts/run_simulation.py
   ```

3. Generate the diagnostic plot:

   ```bash
   python scripts/plot_simulation.py
   ```

4. Open the plot:

   ```text
   outputs/oscillator_diagnostics.png
   ```

5. Write down, in your own words, what looks physically or numerically wrong.

6. Only after this, ask the agent to inspect and explain the codebase.

Before moving on, update the **Task 2** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 3 - Use the agent to diagnose, fix, and verify

**Goal:** Use the agent as a diagnostic partner while keeping the human in control of
edits and verification. The task is complete only when the proposed fix has been
approved, applied, and verified.

1. Ask the agent to inspect the codebase and explain what the main files do.

2. Paste the failing test output and describe what the plot shows.

3. Ask the agent to diagnose the failure pattern **without editing files**.

4. Ask the agent to propose the smallest possible fix.

5. Approve the edit only after the agent explains the intended change.

6. After the edit, ask the agent to summarise the actual diff.

7. Re-run the tests, run the numerical script, and regenerate the plot.

8. Record what you verified and what remains uncertain.

Before moving on, update the **Task 3** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 4 - Add a Verlet stepper using test-first development

**Goal:** Practise test-first extension of research code. Before implementing a new
stepper, define what behaviour the new code must satisfy and verify it with tests.

After Task 3 is verified, add a second numerical stepper using a test-first workflow.

This task is intentionally more structured than Task 5. The goal is to practise
asking an agent to extend research code without letting it jump directly to an
implementation.

1. Ask the agent to inspect the existing integrator structure and propose how a
   Verlet-style stepper should fit into the codebase.

2. Ask the agent to propose one or more tests **before** implementation.

   The tests should define measurable expected behaviour. For example, they may compare
   trajectories, errors, or diagnostic quantities against a reference computed from the
   existing model.

3. Review the proposed tests before allowing any edits.

4. Ask the agent to add the tests.

5. Run the tests and confirm that at least one new test fails for the expected reason.

6. Only then ask the agent to implement the Verlet stepper.

7. Re-run all tests and regenerate any relevant diagnostic output.

8. Record what you verified and what is still not proven by the tests.

Before moving on, update the **Task 4** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 5 - Extend as much as you like

**Goal:** Turn the corrected code into a more useful or impressive research tool while
keeping the same guardrails: scoped edits, test-first or check-first development, and
verified outputs.

This is the open-ended creative task. There is **no single required solution**.
The cooler, better-verified implementation wins.

Work test-first:

1. Ask the agent to propose an extension.

2. First ask the agent to create or modify tests that define the expected behaviour
   of that extension.

3. Run the tests and confirm that at least one new test fails for the right reason
   before implementation.

4. Only then ask the agent to implement the code.

5. Re-run verification and update `DEMO_REPORT_TEMPLATE.md`.

Some directions you could take are listed below. These are examples only.

- Add damping and verify that the amplitude decreases over time.
- Compare two numerical methods from the same initial condition.
- Add a parameter sweep over time step and plot an error metric.
- Add a command-line interface where the user can specify model parameters and solver choices, for example:
  - mass;
  - spring constant;
  - initial position;
  - initial velocity;
  - time step;
  - number of steps;
  - solver name.
- Add a command-line option that regenerates the diagnostic plot for different parameter choices.
- Create a clearer diagnostic plot.
- Add a new output file, for example a CSV summary of several simulation runs.
- Add automated checks that prevent invalid parameter choices.

Whatever you choose, keep it **scoped, test-first, verified, and clearly reported**.

Before moving on, update the **Task 5** section of `DEMO_REPORT_TEMPLATE.md`.

## Deliverable

Fill in:

```text
DEMO_REPORT_TEMPLATE.md
```

and save the completed report inside this folder.

Your report should explain:

- how you set up the agent;
- what you observed before using the agent on the code;
- what the agent explained about the codebase;
- what you diagnosed;
- what you changed;
- how you verified it;
- what you added in Task 4;
- what you attempted in Task 5, if applicable;
- what should not be overclaimed.

## Scientific background

The undamped 1D harmonic oscillator is:

```text
m x'' = -k x
```

Angular frequency:

```text
omega = sqrt(k / m)
```

Period:

```text
T = 2 pi / omega
```

Continuous-time total energy:

```text
E = (1/2) m v^2 + (1/2) k x^2
```

Analytical position for initial condition `(x0, v0)`:

```text
x(t) = x0 cos(omega t) + (v0 / omega) sin(omega t)
```

Use the tests, script output, and diagnostic plot to judge whether the numerical run
is consistent with this reference.
