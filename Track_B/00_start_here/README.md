# Start here — Track B front door

This is the first folder to open in SCI Agentathon 2026 Track B. The `00_` prefix is
intentional: read this before anything else.

## What's in here

- `agent_role_templates/` — per-sub-team role-document templates. The role document
  is the **source of authority** for your agent.
- `prompts/` — **optional** example phrasings and checkpoints for kickoff, mid-day,
  and the demo. They are not mandatory copy-paste scripts, and they do not replace the
  role document.

## Setting up your agent (see also below)
Your sub-team's README repeats these steps as its Task 1, with the exact paths.

Before you start the agent on a sub-team, you must **manually copy** that sub-team's
role template into the sub-team folder:

1. Copy the matching template from `agent_role_templates/` into your sub-team folder,
   renamed to `CLAUDE.md` (Claude Code) or `AGENT_ROLE.md` (any other agent tool). If
   your tool uses a "system prompt" or "rules" field, paste the template contents
   there instead.
2. Scope your agent so it has access **only to your sub-team folder**.
3. Ask the agent to read the role document first and summarise back its role, scope,
   restrictions, and workflow before doing anything else.

### Availability note about role templates

Tailored role templates are provided for sub-teams 01, 02, and 03. Do not reuse a
sub-team's template for another sub-team unless the track lead tells you to adapt it.

## Ground rules

- Work only inside your assigned sub-team folder unless the track lead says otherwise.
- Do not assume access to Dardel, external APIs, credentials, or private data.
- Do not commit generated files (figures, outputs, run artefacts).

## Next action

**Pick your sub-team and follow that sub-team's README:**

- [01 HPC simulation workflow](../01_hpc_simulation_workflow/README.md)
- [02 Research-code debugging](../02_research_code_debugging/README.md)
- [03 Scientific post-processing](../03_scientific_postprocessing/README.md)
