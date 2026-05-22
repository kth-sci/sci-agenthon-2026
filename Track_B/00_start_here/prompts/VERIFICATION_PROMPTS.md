# Verification prompts (optional examples)

These are **optional** example phrasings for the mid-day verification checkpoint. Your
agent should already be scoped to your sub-team folder and operating off its role
document (see [`../README.md`](../README.md)).

Try asking in your own words first. Use these only if you want a model phrasing — the
**role document is the source of authority**, not this file, so do not paste anything
that does not match what you actually built.

## Sub-team 01 — HPC simulation workflow

Your message should ask the agent to re-read the README, list what is done versus
outstanding against the Level 1 goal, run the workflow (or closest equivalent)
end-to-end, and flag anything it cannot actually verify.

> *Example:* Please re-read `Track_B/01_hpc_simulation_workflow/README.md` and the
> work we have done so far. List what is done and what is outstanding against the
> Level 1 goal. Then run a dry-run of the workflow end-to-end and report the result.
> Flag anything you cannot actually verify.

## Sub-team 02 — Research-code debugging

Your message should ask the agent to re-read the README, list what is done versus
outstanding, re-run the tests, and flag any test that passes only because of mocking,
skipping, or weak assertions.

> *Example:* Please re-read `Track_B/02_research_code_debugging/README.md` and the work
> we have done so far. List what is done and what is outstanding. Then run
> `python -m pytest -v tests` from inside the sub-team folder and report the result.
> Flag any test that passes only because of mocking, skipping, or assertions that do
> not really check the intended behaviour.

## Sub-team 03 — Scientific post-processing

Your message should ask the agent to re-read the README, list what is done versus
outstanding, regenerate the summary figure end-to-end from the source data in a fresh
shell, and flag anything that looks suspicious or hand-edited.

> *Example:* Please re-read `Track_B/03_scientific_postprocessing/README.md` and the
> work we have done so far. List what is done and what is outstanding against the
> Level 1 goal. Then regenerate the summary figure end-to-end from the source data in
> a fresh kernel or shell, and describe what the figure shows. Flag anything that
> looks suspicious or hand-edited.
