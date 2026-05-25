# Sub-team 02: Agentic Research-code Debugging

## Story

A researcher inherits a small harmonic-oscillator simulation used to compare numerical integrators. This resembles a familiar research-code handoff: the repository has tests, scripts, and plotting tools, and it appears to run, but the diagnostics are physically suspicious.

The task is to use an agent carefully: first inspect the code, then diagnose the issue, then verify the fix using tests and physical expectations.

This exercise is not primarily about fixing a Python bug. The main learning goal is to set up, constrain, and drive a coding agent so it makes safe, verified progress on a research-code task.

The harmonic-oscillator project is the substrate. The agent workflow is the lesson.

## What You Are Building

A good target is:

- one minimal verified fix;
- one test-first extension, such as a Verlet-style stepper;
- one clear statement of what the tests prove and what they do not.

Use <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a> as a working notebook. It is not only for the end of the day.

## Files to Know

- `00_SUBTEAM_GUIDE.md` - this guide.
- `01_VERIFY.md` - local verification commands for this sub-team.
- `DEMO_REPORT_TEMPLATE.md` - fill this in for your readout.
- `run_tests.sh` - Linux/macOS convenience wrapper; use the Python command in `01_VERIFY.md` on Windows.
- `src/` - source code for the oscillator, integrators, and diagnostics.
- `tests/` - pytest test suite.
- `scripts/` - scripts to run and visualize the simulation.
- `outputs/` - created by plotting scripts; do not commit generated files.

Shared commands: <a href="../02_COMMANDS_AND_VERIFY.md" target="_blank" rel="noopener noreferrer">../02_COMMANDS_AND_VERIFY.md</a>  
Local verification notes: <a href="01_VERIFY.md" target="_blank" rel="noopener noreferrer">01_VERIFY.md</a>

## Task 1: Set Up the Coding Agent

**Goal:** Establish the agent's role, scope, and guardrails before any code is inspected or modified.

Do both parts of this setup before asking the agent to inspect files.

### Step 1: Copy the role file into the sub-team folder

Run from the repository root, `Track_B/`, or copy the file manually in your file browser:

```bash
cp agent_role_templates/02_research_code_debugging_AGENT_ROLE_TEMPLATE.md 02_research_code_debugging/CLAUDE.md
```

On Windows PowerShell, run from the repository root, `Track_B/`:

```powershell
Copy-Item agent_role_templates\02_research_code_debugging_AGENT_ROLE_TEMPLATE.md 02_research_code_debugging\CLAUDE.md
```

If you are not using Claude Code, rename the copy to `AGENT_ROLE.md` instead, or paste the template contents into your tool's rules/system-prompt field.

### Step 2: Scope the agent to the sub-team folder

Configure your tool so the agent can access only:

```text
Track_B/02_research_code_debugging
```

If your agent tool asks for a working directory, project folder, allowed folder, or workspace root, set it to `Track_B/02_research_code_debugging`. Do not give the agent access to the whole Track B repository for this sub-team task.

### Step 3: Ask the agent to confirm its role

Ask the agent:

```text
Please read Track_B/02_research_code_debugging/CLAUDE.md and Track_B/02_research_code_debugging/00_SUBTEAM_GUIDE.md. Summarize your role, scope, restrictions, and workflow before doing anything else. Do not edit files until we approve a plan.
```

Check that the summary is faithful before continuing. The agent should understand that tests, scripts, plots, and physical expectations all matter.

Before moving on, update the **Task 1** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 2: Observe the Failing Behavior Yourself

**Goal:** Observe the failure directly before asking the agent for help.

This gives the team its own evidence from tests, scripts, and plots, rather than treating the agent as an oracle. The goal is to experience the problem as a researcher would when inheriting a codebase: the program may execute, but the scientific behavior still has to make sense.

Run from `Track_B/02_research_code_debugging`:

```bash
python -m pytest -q
python scripts/run_simulation.py
python scripts/plot_simulation.py
```

Open `Track_B/02_research_code_debugging/outputs/oscillator_diagnostics.png` after the plot command runs.

Write down, in your own words, what looks physically or numerically wrong. Only after this, ask the agent to inspect and explain the codebase.

Before moving on, update the **Task 2** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 3: Use the Agent to Diagnose, Fix, and Verify

**Goal:** Use the agent as a diagnostic partner while keeping the human in control of edits and verification.

The task is complete only when the proposed fix has been approved, applied, and verified.

In a real research group, this is the moment where the agent is useful but also risky. It can connect failing tests to source files quickly, but the human team still decides whether the proposed change matches the model and whether the verification evidence is strong enough.

Suggested workflow:

1. Ask the agent to inspect the codebase and explain what the main files do.
2. Paste the failing test output and describe what the plot shows.
3. Ask the agent to diagnose the failure pattern without editing files.
4. Ask the agent to propose the smallest possible fix.
5. Approve the edit only after the agent explains the intended change.
6. After the edit, ask the agent to summarize the actual diff.
7. Re-run the tests, run the numerical script, and regenerate the plot.
8. Record what you verified and what remains uncertain.

Run from `Track_B/02_research_code_debugging` after the fix:

```bash
python -m pytest -q
python scripts/run_simulation.py
python scripts/plot_simulation.py
```

Before moving on, update the **Task 3** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 4: Add a Verlet Stepper Using Test-first Development

**Goal:** Practise test-first extension of research code.

After Task 3 is verified, add a second numerical stepper using a test-first workflow. A good target is a velocity-Verlet or Verlet-style stepper that fits naturally into the existing integrator structure.

One reasonable route:

1. Ask the agent to inspect the existing integrator structure and propose how a Verlet-style stepper should fit into the codebase.
2. Ask the agent to propose one or more tests before implementation.
3. Review the proposed tests before allowing any edits.
4. Ask the agent to add the tests.
5. Run from `Track_B/02_research_code_debugging`:

   ```bash
   python -m pytest -q
   ```

   Confirm that at least one new test fails for the expected reason.

6. Only then ask the agent to implement the Verlet stepper.
7. Re-run from `Track_B/02_research_code_debugging`:

   ```bash
   python -m pytest -q
   python scripts/run_simulation.py
   python scripts/plot_simulation.py
   ```

8. Record what you verified and what is still not proven by the tests.

Before moving on, update the **Task 4** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 5: Extend the Research Tool

**Goal:** Turn the corrected code into a more useful research tool while keeping the same guardrails: scoped edits, test-first or check-first development, and verified outputs.

This is the open-ended creative task. There is no single required solution.

Suggested directions:

- Build a phase-space or phase-diagram representation of the harmonic oscillator. For example, plot `x` versus `v`, compare how different integrators distort the phase-space orbit, or build a stability/quality map over parameters such as `dt`, method, and energy drift.
- Add damping and verify that amplitude or energy decreases over time.
- Compare two numerical methods from the same initial condition.
- Add a parameter sweep over time step and plot an error metric.
- Add a command-line interface where the user can specify model parameters and solver choices, such as mass, spring constant, initial position, initial velocity, time step, number of steps, and solver name.
- Add a command-line option that regenerates the diagnostic plot for different parameter choices.
- Create a clearer diagnostic plot.
- Add a new output file, for example a CSV summary of several simulation runs.
- Add automated checks that prevent invalid parameter choices.

Whatever you choose, keep it scoped, test-first or check-first, verified, and clearly reported.

Before moving on, update the **Task 5** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Deliverable

A filled `DEMO_REPORT_TEMPLATE.md` saved inside `Track_B/02_research_code_debugging`.

Your report should explain how you set up the agent, what you observed before using the agent on the code, what the agent explained, what you diagnosed, what changed, how you verified it, what you added, and what should not be overclaimed.

## Scientific Background

The undamped 1D harmonic oscillator is:

```text
m x'' = -k x
```

Angular frequency:

```text
omega = sqrt(k / m)
```

Continuous-time total energy:

```text
E = (1/2) m v^2 + (1/2) k x^2
```

Use the tests, script output, and diagnostic plot to judge whether the numerical run is consistent with the analytical reference.

Next: <a href="01_VERIFY.md" target="_blank" rel="noopener noreferrer">open 01_VERIFY.md</a>.
