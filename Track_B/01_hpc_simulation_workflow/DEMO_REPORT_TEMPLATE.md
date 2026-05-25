# Demo Report: Sub-team 01 (HPC workflow preparation)

Use this during the exercise. Update the relevant section after each task so the final demo is grounded in what the group actually observed.

## Team Members

-

## Task 1: Agent Setup

- Which agent tool did you use?
- Which role file did you copy into `Track_B/01_hpc_simulation_workflow`?
- How did you scope the agent to `Track_B/01_hpc_simulation_workflow`?
- What role, scope, restrictions, and workflow did the agent summarize?

## Task 2: Workflow Exploration

- What parameters are swept, and how many runs are there?
- What command appears to run a single simulation?
- What command appears to run the local sweep?
- What is the job script trying to do?
- What do the sample logs suggest?
- Which issues look local, and which would only be verifiable on a real cluster?
- After your own exploration, what did the agent clarify about the scripts or codebase?

## Task 3: Participant-built Validator

- Which checks did you implement in `scripts/validate_package.py`?
- What command did you run to execute the validator?
- Which checks passed, warned, or failed?
- What evidence did the validator report?
- What did the validator reveal before any workflow repair?

## Task 4: Local Reproducibility

- What minimal fixes did the agent propose, and which did you approve?
- Which validator results changed after the fixes?
- What happened when you ran the dry-run and the full local sweep?
- Which commands did you run after the fixes?
- What outputs were produced?
- What is verified locally, and what remains a cluster assumption?

## Task 5: Hardening, Diagnosis, or Packaging

- What creative hardening or diagnosis artifact did you build?
- What is it meant to communicate or catch?
- What command regenerates it, and what file does it produce?
- What check or command verifies it?
- How does it help another researcher reuse or inspect the workflow?

## Final Demo Outline

- What will you show in 3-5 minutes?
- Which command will you run or show?
- What should the audience not overclaim?

## Links

Paths to the key files, reports, or figures inside `Track_B/01_hpc_simulation_workflow`.

-

Next: return to <a href="00_SUBTEAM_GUIDE.md" target="_blank" rel="noopener noreferrer">00_SUBTEAM_GUIDE.md</a> or open <a href="../02_COMMANDS_AND_VERIFY.md" target="_blank" rel="noopener noreferrer">../02_COMMANDS_AND_VERIFY.md</a>.
