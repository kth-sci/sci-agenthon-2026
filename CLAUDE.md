# SCI Agentathon 2026

Agentic AI hackathon for KTH SCI school faculty and researchers.  
**Date:** Tuesday, 26 May 2026, 09:00–17:00  
**Venues:** Salongen (KTH Library, KTHB) for plenaries · Teknikringen 8 for track rooms

## Event overview

The agentathon runs two coding sessions separated by a cross-track lunch update, ending with live demos from every sub-team. Around 45 enrolled participants split across three tracks, each exploring a different family of agentic problems.

## Repository layout

```
sci-agenthon-2026/
  CLAUDE.md                                   # this file
  Agentathon_2026_Participant_instructions.pdf
  Agentathon_2026_Program.pdf
  Track_B/                                    # Research and HPC workflow agents
  Track_C/                                    # Open agent exploration (free exploration)
```

## The three tracks

### Track A — Course syllabus to teaching assistant
**Lead:** Artem Kulachenko, Jonas Sellberg  
**Room:** Salongen, KTH Library (KTHB)  
Sub-teams build grading/feedback agents and student-facing Q&A agents from course syllabi.

### Track B — Research and HPC workflow agents
**Lead:** Marco Laudato (laudato@kth.se)  
**Room:** Faxén, Fluid Mechanics lab, Teknikringen 8, floor 1  
Sub-teams choose a direction: orchestration on the cluster, agentic debugging, or an interactive post-processing agent.

### Track C — Open Agent Exploration
**Lead:** Wei Ouyang (wei.ouyang@scilifelab.se)  
**Room:** Hållfasthetslära seminarierum, Teknikringen 8D, floor 1  
Open exploration, no fixed tutorial. Natural home for administrative workflows (eISP, scheduling, document review), retrieval-augmented knowledge agents, and lab automation. See `Track_C/`.

## Toolchain

| Tool | Role |
|------|------|
| Claude Desktop + Cowork mode | Excel, PowerPoint, Word, and browser integrations |
| Claude Code (`npm install -g @anthropic-ai/claude-code`) | Command-line agentic coding |
| Superpowers skills (claude.com/plugins/superpowers) | Extended Claude capabilities |
| Claude for Chrome extension | Browser read/fill/navigate tasks |
| OpenAI Codex (optional fallback) | `npm install -g @openai/codex` |
| VS Code / JetBrains + Claude Code extension | IDE integration (optional) |

## Workspace rules

- Store intermediate files in the shared OneDrive folder for cross-account collaboration.
- Private scratch work goes in a `scratch/` subfolder inside your sub-team folder (ignored at collection time).
- Never paste personal data, API keys, or passwords into prompts or shared files.

## Schedule at a glance

| Time | Activity |
|------|----------|
| 08:30–09:15 | Arrival in Salongen |
| 09:15–10:15 | Morning plenary: welcome, agent intro, live demo, track intros, sub-team formation |
| 10:15–12:00 | Coding session 1 in track rooms |
| 12:00–13:15 | Lunch + cross-track 3-minute status updates |
| 13:15–15:45 | Coding session 2 — converge on a demoable result |
| 15:45–16:00 | Move to Salongen, set up demos |
| 16:00–16:45 | End-of-day live demos (one per sub-team) |
| 16:45–17:00 | Wrap-up, lessons learnt, next steps |

## Contacts

- Track A: artem@kth.se
- Track B: laudato@kth.se
- Track C: wei.ouyang@scilifelab.se
