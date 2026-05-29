---
name: consult-codex
description: Use when the user asks to "consult codex", "ask codex", "what does codex say", "run codex on this", "have codex generate/write/check X", or otherwise delegate a coding task or question to the OpenAI Codex CLI installed on this Mac. Also trigger on phrases like "use codex to ...", "let codex do ...", "second opinion from codex", or "compare with codex". Codex is a non-Anthropic agent that can answer questions, write code, generate files, and review existing code. Skip when the user wants Claude itself to do the work, or when they explicitly name a different tool (e.g. "ask antigravity" or "ask gemini").
---

# Consulting OpenAI Codex CLI (macOS)

This skill lets Claude delegate a task or question to the OpenAI Codex CLI (`codex`) running locally on this Mac, then relay the answer back. Codex is OpenAI's agentic coding tool — it can reason, write code, edit files, and run shell commands.

## Where it lives

- Binary: `/opt/homebrew/bin/codex` (Homebrew, Apple Silicon)
- Config dir: `~/.codex/`
- Auth: ChatGPT login (cached in `~/.codex/`)

`codex` is normally on PATH in interactive shells, but Claude's Bash tool runs a non-login shell, so always invoke by **absolute path** to avoid surprises.

## When to use this skill

Trigger when the user wants Codex's output specifically. Phrases:

- "ask codex …", "consult codex about …"
- "what does codex say about …"
- "have codex write / generate / review …"
- "get a second opinion from codex"
- "use codex to do …"

Do NOT trigger when:

- The user is asking Claude directly ("what do you think")
- The user names a different tool (Antigravity, Gemini, etc.) → use the matching skill
- The user wants the Codex desktop app (no equivalent here — there isn't one on Mac)

## How to invoke

Codex runs **non-interactively** via `codex exec`. The exact pattern (bash):

```bash
/opt/homebrew/bin/codex exec \
    --skip-git-repo-check \
    -s <sandbox-mode> \
    -C <working-dir> \
    -o <output-file> \
    --color never \
    "<the prompt>" </dev/null
```

Always close stdin with `</dev/null` (or pipe the prompt in) so codex never blocks waiting for input.

**Two invocation patterns:**

- **Short prompt as positional arg:** pass the prompt as the final argument, redirect stdin from `/dev/null`. Single-quote the prompt to keep the shell from interpreting it.
- **Long prompt with quotes / newlines:** feed the prompt itself via stdin using a heredoc, omit the positional argument. Codex reads `[PROMPT]` from stdin when not given as an argument. This is the **safer default** for any prompt longer than one line or containing quote characters.

```bash
# Pattern 1 (short prompt, no embedded quotes)
out=$(mktemp -t codex-answer.XXXXXX)
/opt/homebrew/bin/codex exec --skip-git-repo-check -s read-only \
    -C "${TMPDIR:-/tmp}" -o "$out" --color never \
    'your one-line prompt' </dev/null

# Pattern 2 (prompt via stdin — preferred for non-trivial prompts)
out=$(mktemp -t codex-answer.XXXXXX)
/opt/homebrew/bin/codex exec --skip-git-repo-check -s read-only \
    -C "${TMPDIR:-/tmp}" -o "$out" --color never <<'PROMPT'
Multi-line prompt with "quotes" and whatever else.
Required content: ...
PROMPT
```

### Required and recommended flags

| Flag | Meaning | When to use |
|---|---|---|
| `--skip-git-repo-check` | Allow running outside a git repo | Always set — many project dirs are not git repos |
| `-s read-only` | Codex cannot write files or run mutating commands | DEFAULT — use for pure "consult" questions |
| `-s workspace-write` | Codex can edit files in `-C <dir>` (and any `--add-dir` paths) | Only when the user explicitly wants code or a file produced |
| `-s danger-full-access` | No sandbox | Never set unless user explicitly requests it |
| `-C <dir>` | Working root for Codex | Set to a **scratch dir** (`$(mktemp -d -t codex-task)`) for one-off generation tasks; set to the project dir only when the user wants Codex to operate ON the project |
| `-o <file>` | Write the final agent message to this file | Always set — this is how you reliably capture the answer |
| `--color never` | Strip ANSI escapes | Always set when capturing output |
| `-m <model>` | Pick a model | Omit unless the user names one |
| `-c <config>` | Pick an effort | Use model_reasoning_effort="high" unless specified |
| `--add-dir <dir>` | Additional writable directory (repeatable) | Use to expose a project dir read-only-ish alongside a scratch root |

### The two default modes

**Mode A — pure question (read-only):**

```bash
out=$(mktemp -t codex-answer.XXXXXX)
/opt/homebrew/bin/codex exec --skip-git-repo-check -s read-only \
    -C "${TMPDIR:-/tmp}" -o "$out" --color never \
    '<prompt>' </dev/null
cat "$out"
```

**Mode B — generate a file (workspace-write in a scratch dir):**

```bash
work=$(mktemp -d -t codex-job)
out="$work/_codex-summary.txt"
/opt/homebrew/bin/codex exec --skip-git-repo-check -s workspace-write \
    -C "$work" -o "$out" --color never <<'PROMPT'
<multi-line prompt that asks Codex to write a specific filename in the current directory>
PROMPT
ls -la "$work"
cat "$out"
```

Always tell Codex **the exact filename** it should produce, and tell it the file goes in the current working directory. Codex picks its own name otherwise.

## Capturing output reliably

- Codex's last agent message goes to the `-o` file. Read that file with the Read tool, not stdout — stdout also contains streamed reasoning lines that are noisy.
- Codex sessions can take 30–180 seconds for simple tasks because it streams reasoning. Run via `run_in_background: true` and wait for the completion notification rather than blocking with a long timeout.
- If the call exits non-zero or returns nothing, check the tail of stdout/stderr — `Logged in using ChatGPT` is informational success, not an error.

## Reporting the answer back

After Codex finishes:

1. Read the `-o` file with the Read tool.
2. If Mode B, also list the produced files in the working directory.
3. Quote or summarize Codex's answer to the user, attributing it: "Codex says …" or "Codex produced …".
4. Do NOT silently merge Codex's output into your own voice. The user asked for Codex's view specifically; preserve attribution.
5. If Codex produced code or a file, offer to copy/move it into the user's current project on request — do not move it automatically.

## Caveats

- Codex is an agent, not a chat. Even short prompts trigger a multi-step reasoning loop. Expect latency.
- Codex defaults will load `~/.codex/config.toml` — the user may have personal config there. Use `--ignore-user-config` only if the user explicitly wants a clean run.
- Codex can run shell commands inside its sandbox. The `-s read-only` flag blocks file mutations but not network or read calls. For true isolation, run in a scratch dir under `$(mktemp -d)`.
- This skill is the wrapper around the CLI. It does not give Codex any tools beyond what `codex exec` itself has.
- macOS `mktemp` requires either no template or a template ending in `XXXXXX`. The patterns above use `-t <prefix>` which appends a random suffix; either form is fine.

## Quick reference

```bash
# Pure consultation
out=$(mktemp -t codex.XXXXXX)
/opt/homebrew/bin/codex exec --skip-git-repo-check -s read-only \
    -C "${TMPDIR:-/tmp}" -o "$out" --color never 'your question' </dev/null
cat "$out"

# File generation in a scratch dir
w=$(mktemp -d -t codex-job)
/opt/homebrew/bin/codex exec --skip-git-repo-check -s workspace-write \
    -C "$w" -o "$w/_summary.txt" --color never \
    'write a file called foo.svg with ...' </dev/null
ls "$w"
```
