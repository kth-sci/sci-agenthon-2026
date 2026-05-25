# Facilitator Guide: Track B

This guide is for the Track B lead. Keep `_facilitator/` separate from the participant reading order.

## Track-level Message

Track B is not about demonstrating that an AI agent can write code. It is about learning how to embed an agent in a research-computing workflow where assumptions become visible, checks become explicit, and outputs can be regenerated.

Useful sentence:

```text
The artifact matters less than the verification evidence and the limitation statement.
```

## Suggested Room Flow

### Track Start

- Show <a href="../00_START_HERE.md" target="_blank" rel="noopener noreferrer">../00_START_HERE.md</a>.
- Explain the three sub-team options briefly:
  - cluster/log/workflow interests: 01;
  - code/debug/test interests: 02;
  - data/figures/interpretation interests: 03.
- Invite optional roles from <a href="../01_COMMON_GUIDE.md" target="_blank" rel="noopener noreferrer">../01_COMMON_GUIDE.md</a>.
- Point everyone to <a href="../02_COMMANDS_AND_VERIFY.md" target="_blank" rel="noopener noreferrer">../02_COMMANDS_AND_VERIFY.md</a>.
- Remind teams to update their demo reports continuously.

### Human-first Observation

Each team should run the starter commands before asking for fixes.

Intervention questions:

- What did you observe before the agent helped?
- Which command produced that evidence?
- What should the agent not be allowed to do yet?

### Agent Diagnosis and First Fix

Push teams into inspect, plan, approve, edit, verify.

Intervention questions:

- Did the agent propose a plan before editing?
- Did the group approve the actual change?
- What is the smallest check that confirms progress?

### Lightweight Checkpoint

Ask each group to write five lines in the demo report:

```text
Verified so far:
Current blocker:
Next check:
Files changed:
One thing we will not overclaim:
```

### Stretch or Hardening

Favor smaller verified artifacts over broad ambition.

- 01: add one validator check or log parser rather than a full HPC system.
- 02: add one test-first integrator or physical guardrail rather than a large refactor.
- 03: add one data-quality check and update the interpretation rather than a full dashboard.

### Demo Preparation

Ask every group:

- What one command will you run or show?
- What file or figure will it regenerate?
- What limitation will you state?

Use <a href="DEMO_RUBRIC.md" target="_blank" rel="noopener noreferrer">DEMO_RUBRIC.md</a> to help teams tighten the story.

## When a Group Is Stuck

Offer one nudge at a time:

1. What command output do you have?
2. Which file does that output point to?
3. What would a minimal check look like?
4. Ask the agent to propose three hypotheses without editing.

## When a Group Is Moving Fast

Ask them to pause and write:

```text
Verified facts:
Assumptions:
Files changed:
Command to regenerate:
Limitation:
```

## Closing Reflection

End by asking:

```text
What is one guardrail or reproducibility artifact you could add to your real research workflow next week?
```
