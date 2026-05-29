---
name: consult-antigravity
description: Use when the user asks to "consult antigravity", "ask antigravity", "ask agy", "what does antigravity say", "run antigravity on this", "have antigravity write/generate/check X", "generate an image with nanobanana", or otherwise delegate a coding task, question, or image generation to Google's Antigravity CLI (the `agy` command) installed on this Mac. Also trigger on "use antigravity to ...", "let agy do ...", "second opinion from antigravity / Gemini-via-agy", "compare with antigravity", or any "nano banana / nanobanana / Gemini image generation" request. agy is Google's agentic coding tool (Gemini-backed) and may have a nanobanana plugin installed for image generation. Skip when the user wants Claude itself to do the work, or names a different tool (e.g. "ask codex" → consult-codex). The Antigravity IDE itself is not scriptable from here; this skill only wraps the `agy` CLI.
---

# Consulting Google Antigravity CLI `agy` (macOS)

This skill lets Claude delegate a coding task, question, or image-generation request to Google's Antigravity CLI (`agy`) on this Mac, then relay the result back. agy is Google's agentic coding tool (Gemini-backed). If the `nanobanana` plugin is installed it exposes image generation via the `generate_image` MCP tool / `/generate` slash command.

## Where it lives

- Binary: `~/.local/bin/agy` (absolute: `/Users/sellberg/.local/bin/agy`) — version 1.0.2 at time of writing.
- State dirs (created on first run):
  - `~/.gemini/antigravity-cli/` — conversations, brain transcripts, scratch, plugins
  - `~/.gemini/config/` — global config, `mcp_config.json`, plugins
- Plugin skills (if installed): `~/.gemini/config/plugins/nanobanana/skills/`
- Auth: Google account (interactive on first run; cached after)

Use the absolute path when invoking from Claude's Bash tool — it runs a non-login shell where `~/.local/bin` may not be on PATH.

## When to use this skill

Trigger when the user wants Antigravity's output specifically. Phrases:

- "ask antigravity …", "consult antigravity about …", "ask agy …"
- "what does antigravity / agy / Gemini-via-agy say about …"
- "have antigravity write / generate / review …"
- "get a second opinion from antigravity"
- "use agy to do …"
- "generate an image with nano banana / nanobanana / Gemini image"
- "make a poster / mockup / illustration with agy"

Skip when the user names a different tool (Codex → consult-codex) or wants Claude itself to handle it.

## The two reality constraints

1. **agy `--print` does not emit text to stdout on non-TTY shells.** When Claude calls agy from any shell wrapper, the response IS generated but NOT printed. agy ignores `--dangerously-skip-permissions` for this — it has its own permission model.

2. **agy stores every conversation locally.** The response — including any tool-call outputs — is in:
   `~/.gemini/antigravity-cli/brain/<conversation-uuid>/.system_generated/logs/transcript.jsonl`
   The newest directory by mtime under `brain/` after agy exits is the call you just made.

The working pattern uses these two facts: invoke agy, ignore stdout, read the latest transcript.

## How to invoke

### Pattern A — text-only consultation

```bash
AGY=/Users/sellberg/.local/bin/agy
BRAIN="$HOME/.gemini/antigravity-cli/brain"
work=$(mktemp -d -t agy-q)
cd "$work"
"$AGY" --print "<your prompt>" </dev/null   # output captured by bash, ignore it

# Find the newest brain dir (the call we just made)
conv=$(ls -1dt "$BRAIN"/*/ 2>/dev/null | head -1)
tr="${conv}.system_generated/logs/transcript.jsonl"

# Extract the final PLANNER_RESPONSE.content (the agent's reply)
python3 - <<PY
import json, sys, pathlib
p = pathlib.Path("$tr")
last = None
for line in p.read_text().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if obj.get("type") == "PLANNER_RESPONSE" and obj.get("content"):
        last = obj["content"]
print(last or "")
PY
```

The final response text is the last `PLANNER_RESPONSE` step with a non-empty `content` field. Earlier `PLANNER_RESPONSE` steps may have empty `content` but populated `tool_calls` — those are intermediate reasoning steps.

If `jq` is available, this is equivalent and shorter:

```bash
jq -r 'select(.type == "PLANNER_RESPONSE" and .content != null and .content != "") | .content' "$tr" | tail -n 1
```

### Pattern B — image generation via nanobanana

If the `nanobanana` plugin is installed (`agy plugin list` to confirm), it exposes a `generate_image` MCP tool and a `/generate` slash command (also reachable via natural language). Requires `NANOBANANA_API_KEY` set to a Gemini API key (separate from agy's Google login — get one at https://aistudio.google.com/apikey). Optional: `NANOBANANA_MODEL` (default `gemini-3.1-flash-image-preview`; use `gemini-3-pro-image-preview` for Nano Banana Pro).

```bash
export NANOBANANA_API_KEY="<gemini api key>"
export NANOBANANA_MODEL="gemini-3-pro-image-preview"  # optional, picks Nano Banana Pro
AGY=/Users/sellberg/.local/bin/agy
"$AGY" --print 'Use the /generate command to create a PNG image. Subject: <describe the image>. Confirm with the saved filename.' </dev/null
```

The generated image lands at one of:
- `~/.gemini/antigravity-cli/brain/<conv-uuid>/<name>_<timestamp>.png` (raw)
- `~/.gemini/antigravity-cli/scratch/<name>.png` (the agent's default save target; it has write permission there)

agy does NOT have write permission to arbitrary paths. It will NOT save into the user's project dirs directly. Copy the file yourself afterwards:

```bash
cp ~/.gemini/antigravity-cli/scratch/<name>.png "<final destination>"
```

To find the just-generated image, look at the latest brain dir's transcript for a `GENERATE_IMAGE` step — its `content` field includes "Generated image is saved at `<full path>`".

### Pattern C — file generation in a writable workspace

agy will only write files to paths it has permission for. The default-allowed write locations are under `~/.gemini/antigravity-cli/`:

- `scratch/`
- `browser_recordings/`
- `html_artifacts/`
- `knowledge/`
- `worktrees/`

For tasks that write project files, copy the output from one of these paths into the target location after agy completes.

## Flags reference (agy 1.0.2)

| Flag | Purpose | Notes |
|---|---|---|
| `--print` / `-p` / `--prompt` | One-shot non-interactive mode | Always set for "consult" use |
| `--print-timeout 5m0s` | Per-run wall-clock cap | Default 5m, bump for image gen / complex tasks |
| `--add-dir <dir>` (repeatable) | Add a dir to the workspace | Use to expose project dirs as read-only context |
| `--sandbox` | Terminal-tool restrictions | Add for extra safety |
| `--log-file <path>` | Override debug log location | Useful when triaging silent failures |
| `--conversation <uuid>` | **RESUMES** an existing conversation | Passing a fresh UUID hangs agy. Do NOT use to create new conversations |
| `--dangerously-skip-permissions` | Inherited from other CLIs | agy IGNORES this. Do not bother |

## State-corruption recovery

If agy starts exiting 0 with no transcript and the CLI log under `~/.gemini/antigravity-cli/log/` is 0 bytes, the likely cause is a corrupt config file. Check:

```bash
ls -l ~/.gemini/config/mcp_config.json
# If 0 bytes, fix:
echo '{}' > ~/.gemini/config/mcp_config.json
```

Also kill any orphaned `agy` and `language_server` processes (the shared Antigravity language server can hold state between runs):

```bash
pkill -f '^/Users/sellberg/\.local/bin/agy' 2>/dev/null
pkill -f 'language_server' 2>/dev/null
true
```

## Reporting the answer back

After agy finishes:

1. Read the latest `transcript.jsonl`.
2. Extract the final `PLANNER_RESPONSE.content` as the agent's reply.
3. If image-gen was used, locate the file via the `GENERATE_IMAGE` step's "Generated image is saved at …" content and copy it to where the user wants.
4. Attribute the answer: "Antigravity says …" or "Agy produced …".
5. Preserve attribution. Do not silently merge agy's output into your own voice.

## Caveats

- agy's `-c` / `--continue` resumes the **most recent conversation in this cwd** (per `~/.gemini/antigravity-cli/cache/last_conversations.json`). For independent threads, use separate cwds (the patterns above already `cd` into a fresh scratch dir).
- agy is Google's product. Sending the user's code or prompt through it sends data to Google. Mention this if the prompt contains anything sensitive (e.g. student personal data — the SK1110 grading directory contains personnummer).
- The Antigravity **IDE** Electron desktop app, if installed, has no usable CLI. Do not try to script it.
- The Nano Banana plugin generates JPEG bytes even when the filename is `.png`. If a strict-PNG consumer cares, run a conversion step (`sips -s format png in.png out.png` works on macOS).
- agy's response sometimes does not address the user's request literally — it may decide to ask a clarifying question or take a detour. Read the final `PLANNER_RESPONSE.content` before assuming success.
- First-ever invocation triggers an interactive Google login flow that will not work under Claude's Bash tool. If `~/.gemini/` does not yet exist, ask the user to run `agy --print "hello"` once in their own terminal to authenticate before this skill can be used.

## Quick reference

```bash
# Verify install + version + plugins
/Users/sellberg/.local/bin/agy --version
/Users/sellberg/.local/bin/agy plugin list

# Text consultation — read transcript after, ignore stdout
AGY=/Users/sellberg/.local/bin/agy
BRAIN="$HOME/.gemini/antigravity-cli/brain"
work=$(mktemp -d -t agy); cd "$work"
"$AGY" --print 'your prompt' </dev/null
conv=$(ls -1dt "$BRAIN"/*/ | head -1)
tr="${conv}.system_generated/logs/transcript.jsonl"
jq -r 'select(.type=="PLANNER_RESPONSE" and .content!="" and .content!=null) | .content' "$tr" | tail -n 1

# Image generation (requires NANOBANANA_API_KEY)
export NANOBANANA_API_KEY="<key>"
export NANOBANANA_MODEL="gemini-3-pro-image-preview"
/Users/sellberg/.local/bin/agy --print 'Use /generate to create a PNG: <subject>. Confirm with the filename.' </dev/null
ls -t ~/.gemini/antigravity-cli/scratch/*.png | head -1
```
