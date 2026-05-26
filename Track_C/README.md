# agenthon — a collection of agent skills for KTH services

A reference repository of **AI-agent skills** that drive KTH (Royal
Institute of Technology, Stockholm) IT services from a single command
line. Doubles as an **educational repo** for KTH faculty and staff who
want to learn the agent-skills pattern: how to take any SAML- or
Shibboleth-protected web service, reverse-engineer its endpoints, and
turn it into a CLI an AI agent can drive.

---

## ⚠️ Disclaimer — please read

This repository is **educational**. It demonstrates how an AI agent can
be taught to operate KTH IT services using the
[Agent Skills](https://agentskills.io/specification) format and the
[agent-browser](https://github.com/vercel-labs/agent-browser) tooling.

Before you use any of it on a real KTH account:

1. **KTH IT policy may not permit automation** of every service this
   repo touches. The services in scope (Findity, Unit4 EFH, WISUM, the
   intranet) explicitly forbid bot traffic in some places, and ToS
   on a per-service basis can change without notice. **Use is at your
   own risk and may violate institutional policy.** If you're unsure,
   check with KTH IT before running anything against your live account.

2. **AI agents make mistakes.** Even when an agent is "sure" about
   what it's doing, it can mis-classify, mis-paste, or misunderstand a
   form field. **Every action this repo performs needs to be verified
   by a human** — and especially anything irreversible:
   - purchase orders (`kth wisum checkout`)
   - invoice approvals (`kth efh approve`)
   - sent emails
   - anything that moves money or commits you to a counterparty.

3. **Money-moving clicks always stay with the user.** Every CLI in this
   repo refuses to auto-click final-submit buttons. The agent prepares
   the form, opens the visible browser window, and *you* click. This
   isn't just policy — Unit4/Telerik's ASP.NET WebForms architecture
   makes pure-CLI replay of those clicks structurally impossible
   anyway, but it's also the right design.

4. **This is not affiliated with KTH IT.** It is an independent
   research/automation experiment. There is no warranty. There is no
   support contract. The author(s) of this repo are not responsible
   for orders you place, invoices you approve, or any other state
   change you cause.

5. **No PII in commits, please.** The user-config directory
   (`~/.config/kth-cli/`) is intentionally outside the repo so your
   personal preferences (KTH ID, projects you can charge, default
   delivery address) never leak. Don't commit your real
   `config.env` or `project-accounts.yaml` upstream.

If those conditions don't fit your situation, don't use this code.
Read it as documentation only.

---

## What you get

A handful of `kth …` commands and matching agent skills, plus the
discovery patterns that produced them. Today's surface:

| Command                              | Service                              | Architecture |
| ------------------------------------ | ------------------------------------ | ------------ |
| `kth login` / `kth status`           | KTH SSO (login.ug.kth.se AD FS)      | browser auth |
| `kth ab <args>`                      | agent-browser passthrough             | browser      |
| `kth efh count` / `tasks` / `summary` | Unit4 EFH — pending invoice tasks    | pure curl (read) |
| `kth efh invoice <vernr>`            | Unit4 EFH — fetch one invoice + attachments | curl after one browser discovery |
| `kth wisum search "<q>"`             | WISUM — product catalog search       | pure curl (ASMX JSON) |
| `kth wisum cart` / `add` / `favorites` | WISUM — cart + favorites           | pure curl |
| `kth wisum carts` / `select` / `cleanup` | WISUM — multi-cart management    | browser (cart UI) |
| `kth wisum checkout`                 | WISUM — drive checkout to Slutför    | browser (stops before submit) |

Every command has a `--help`.

---

## Quick start

```bash
git clone https://github.com/<your-fork-or-source>/agenthon.git
cd agenthon
./install.sh                                  # installs agent-browser, seeds user config

# Edit the seeded preferences with your KTH affiliation:
$EDITOR ~/.config/kth-cli/config.env

# (Optional) Edit your invoice project-routing rules:
$EDITOR ~/.config/kth-cli/project-accounts.yaml

# One-time MFA bootstrap (Microsoft Authenticator):
kth login

# Verify:
kth status                                    # → session: ok
kth wisum search "usb cable" --per-page 5
kth efh count
```

That's it. The browser profile under `~/.config/browser-profile/` holds
your warm SSO session and is shared by every CLI on your account.

---

## Architecture, in three principles

The whole repo is built on three operating principles. Internalising
them is the most useful takeaway from reading this code.

### 1. Discovery in the browser, runtime in curl

Most KTH-internal services don't have a documented public API. To
build a CLI for one, you do this loop:

1. Open the service in the visible browser (`kth ab open <url>`).
2. Start a HAR recording (`kth ab network har start /tmp/X.har`).
3. Perform the target action by hand (click the menu, submit the
   form, whatever).
4. Stop the HAR. Parse it for `POST` / `PUT` requests that returned
   real data.
5. Replay those requests with `curl` using the warm-profile cookies.
   If it works, you've found the JSON surface.

`kth efh tasks` and `kth wisum search` are both pure-curl commands
discovered exactly this way. Browser used once for capture; never
again at runtime.

### 2. Irreversible writes stay in the browser

Some endpoints can't be safely replayed from curl. Examples:
- Unit4/EFH's *Ekonomisk attest* button POSTs to `ContentContainer.aspx`
  with a server-encrypted `__VIEWSTATE` blob. The blob is signed with
  KTH's machine key; we don't have it. Pure-curl replay is structurally
  impossible.
- WISUM's checkout *Slutför* button works the same way.

Plus, **even when replay is mechanically possible**, money-moving and
state-changing actions deserve a real human click. So every CLI in
this repo:

- Drives the headed browser through everything *up to* the
  irreversible click.
- Brings the window to the foreground.
- Prints a clear "USER ACTION REQUIRED — verify and click X" message.
- Never clicks X itself.

### 3. User-specific state stays outside the repo

The repo is a reusable artifact. Your name, KTH ID, KTH unit, default
delivery address, and project-routing rules go in
`~/.config/kth-cli/`. The repo only ships templates with placeholders.

This keeps the repo shareable. It also means that when KTH IT
inevitably rotates a server-side identifier or your group code
changes, you update one file in `~/.config/kth-cli/` instead of
patching code.

---

## Repository layout

```
agenthon/
├── README.md                ← this file
├── CLAUDE.md                ← agent-facing brief (operating principles, current state)
├── install.sh               ← one-shot installer
├── .gitignore
│
├── bin/                     ← the CLI binaries (Bash + Python)
│   ├── kth                  Top-level dispatcher. Sources user config.
│   ├── kth-efh              Unit4 EFH wrapper (curl JSON + browser drill).
│   ├── kth-efh-parse        Python EI02 HTML parser + project-router.
│   └── kth-wisum            WISUM wrapper (ASMX JSON + browser checkout).
│
├── config/                  ← templates only (no real user data)
│   ├── kth-cli.example.env
│   └── project-accounts.example.yaml
│
└── skills/                  ← agentskills.io-compliant skill folders
    ├── kth/                 main entry skill (auth, routing)
    ├── kth-findity/         travel-expense skill
    ├── kth-intra/           intranet portal skill
    ├── kth-efh/             e-invoice skill (+ SOP, source PDFs in references/)
    ├── kth-wisum/           WISUM skill (+ received-cart SOP)
    └── kth-service-onboarding/   meta-skill: how to add a new service
```

External, user-owned state:

```
~/.config/kth-cli/
├── config.env               your defaults — name, KTH unit, delivery address
└── project-accounts.yaml    your EFH project-routing rules

~/.config/browser-profile/   shared Chromium profile (cookies for KTH, Frontiers, …)
```

---

## Setup, in detail

### Requirements

- macOS or Linux (tested on macOS 15.4)
- bash 3.2+ (macOS default works)
- python3 (for the small parsing helpers and JSON encoding)
- `curl`, `jq` (not strictly required), `osascript` (macOS only, for window activation)
- one of `npm` / `brew` / `cargo` to install agent-browser
- A KTH account with SSO + Microsoft Authenticator (this is the
  hard prerequisite — nothing here works without it)

### What `install.sh` does

1. Installs [`agent-browser`](https://github.com/vercel-labs/agent-browser)
   via npm/brew/cargo if missing.
2. Runs `agent-browser install` to fetch Chrome for Testing.
3. Symlinks every executable in `bin/` into `~/.local/bin/`.
4. Creates `~/.config/browser-profile/` (the shared profile dir).
5. **Seeds `~/.config/kth-cli/config.env` from
   `config/kth-cli.example.env` if missing**. It never overwrites an
   existing user config.
6. **Seeds `~/.config/kth-cli/project-accounts.yaml` from
   `config/project-accounts.example.yaml`** the same way.
7. Symlinks `skills/kth*/` into `~/.claude/skills/` so Claude Code
   sees them.

Running `install.sh` repeatedly is safe — every step is idempotent.

### Editing your config

```bash
$EDITOR ~/.config/kth-cli/config.env
```

The seeded template documents every variable. The ones that matter for
day-to-day use:

| Variable                  | Purpose                                                                 |
| ------------------------- | ----------------------------------------------------------------------- |
| `KTH_USER_NAME`           | Your display name on KTH/WISUM. Default Godsmärkning / parcel label.    |
| `KTH_USER_ID`             | Your 4-letter KTH ID (e.g. `WEIO`). Usually auto-detected at runtime.   |
| `KTH_WISUM_ENHET`         | Default KTH unit for WISUM checkouts. Run `kth wisum enheter` to list.  |
| `KTH_WISUM_ADDRESS`       | Default delivery address. Run `kth wisum addresses` to list.            |
| `KTH_WISUM_GODSMARKNING`  | Default parcel label (defaults to `$KTH_USER_NAME`).                    |
| `KTH_EFH_PROJECT_ACCOUNTS`| Path to your project-routing rules YAML.                                |
| `KTH_PROFILE_DIR`         | Override the shared browser-profile dir (rare; only for isolation).     |

### Editing your project-routing rules

Used by `kth efh summary` to propose which KTH project to charge an
invoice to. See `config/project-accounts.example.yaml` for the schema.
Briefly:

```yaml
version: 1
owner: "Your Name (KTHID)"
rules:
  - id: short-rule-id
    when: "When does this rule apply, in prose?"
    project: "12345"                  # Unit4 project number
    cost_centre: "SCI-XYZ"
    label: "Human-readable label"
    keywords: [match, against, invoice, text, lowercase]
default:
  project: "..."
  label: "Generic fallback"
```

`kth efh summary <vernr>` scans the invoice's supplier + line items for
your keywords and proposes the first rule that matches.

### Login

```bash
kth login
```

A headed Chromium window opens at the KTH SSO page. The wrapper
auto-ticks "Keep me signed in" (which extends MSISAuth from ~12h to
~7d if KTH allows it). Complete username → password → Authenticator
push. The wrapper polls for completion and exits when you've landed
back on a `*.kth.se` page.

After login, every other command works headless and silent.

---

## Building a new agent skill — the educational walkthrough

This is the part for KTH faculty / staff who want to add their own
service. We'll walk through what we did for WISUM, because that's the
cleanest case (JSON ASMX endpoints) and ends with a usable CLI in ~150
lines of shell.

### Step 0 — Decide if it's worth automating

Before you write code, answer two questions:

1. Will I use this more than five times? If no, just use the web UI.
2. Is at least one read-only operation (search, list, status) safely
   automatable, even if writes are off the table? If yes, a curl-based
   read CLI is still useful by itself.

Useful candidates inside KTH today:

- Daisy (course administration) — heavy WebForms, low value for solo use.
- Canvas — has a documented API; skip the reverse-engineering.
- The KTH timetable service — useful read-only.
- KTH RES (travel) — like Findity, already partly covered.
- KTH eduSign — too short an interaction to bother.

### Step 1 — Open the service via the warm profile

```bash
kth ab open https://service.kth.se/...
```

If the redirect chain bounces through `login.ug.kth.se` and lands
silently (no MFA prompt), your warm KTH SSO is doing the work. If it
asks for credentials, the service uses a separate IdP — make a note
of which one (Shibboleth at `saml-5.sys.kth.se`, AD FS at
`login.ug.kth.se`, or external) and adapt.

### Step 2 — Identify what the service actually exposes

Two ways:

**Static** — visit `<service>.asmx`, `<service>/api/`, `<service>?WSDL`,
`/swagger`, `/.well-known/openid-configuration` in the visible browser.
A surprising number of ASP.NET services expose introspection endpoints.
For WISUM, hitting
`https://www.wisum.its.umu.se/KTH/ws/TreeWebService.asmx/jsdebug` gave
us the full list of methods + their signatures via the auto-generated
JS proxy.

**Dynamic** — start a HAR recording and click around.

```bash
kth ab network har start /tmp/discover.har
# … perform the action by hand in the visible window …
kth ab network har stop /tmp/discover.har
```

Open the HAR file and look for `POST` / `PUT` requests with JSON
bodies. Those are your API. Anything that posts to `*.aspx` with
`__EVENTTARGET` / `__VIEWSTATE` is an ASP.NET WebForms postback —
it's typed as "needs the browser to replay", not curl.

### Step 3 — Reproduce one endpoint with curl

Export the warm profile's cookies into a Netscape jar:

```bash
kth ab --json cookies get | python3 -c '
import json, sys
data = json.load(sys.stdin).get("data", {}).get("cookies", [])
print("# Netscape HTTP Cookie File")
for c in data:
    d = c.get("domain", "")
    if "your-service-host" not in d: continue
    # … rest of the export logic; see bin/kth-wisum refresh_cookies()
' > /tmp/svc-cookies.txt
```

Then replay one of the POSTs:

```bash
curl -sS -b /tmp/svc-cookies.txt \
  -H 'Content-Type: application/json; charset=utf-8' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -X POST -d '{"foo": "bar"}' \
  'https://service.kth.se/api/SomeMethod'
```

If it returns the same JSON you saw in the browser, you have a CLI.

### Step 4 — Write `bin/kth-<service>`

Model on `bin/kth-wisum` or `bin/kth-efh`. The conventions:

1. **Source `~/.config/kth-cli/config.env`** at the top so user
   preferences flow through.
2. **Resolve the profile dir** the same way (`KTH_PROFILE_DIR`,
   defaulting to `~/.config/browser-profile`).
3. **Export cookies on demand** (`refresh_cookies` function) and
   re-export automatically on HTTP 4xx (the cookie may have rotated).
4. **One sub-command per verb.** Dispatch via `case "$cmd" in`.
5. **Browser-driven verbs** open the headed window and stop before
   any irreversible click.
6. **Pure-curl verbs** never spawn a browser at runtime.

Add the new command to `bin/kth`'s dispatch:

```bash
case "$cmd" in
  …
  yournew)
    exec "$(dirname "$0")/kth-yournew" "$@"
    ;;
esac
```

### Step 5 — Write the SKILL.md

Create `skills/kth-<service>/SKILL.md` per the
[Agent Skills spec](https://agentskills.io/specification):

```markdown
---
name: kth-yourservice
description: One-paragraph description of what this skill does and
  when an agent should reach for it. Include the URL, the SSO
  mechanism, and the keywords a user might say. Required.
compatibility: Requires `kth` CLI + a warm KTH SSO session.
metadata:
  service: yourservice
  start_url: https://...
---

# KTH <Service> — service skill

## When to use this skill
…

## Verbs
…

## API used (under the hood)
…

## What this skill should never do
- never auto-submit money-moving / state-changing actions
- never commit cookie jars
```

Add the service to the roadmap table in `CLAUDE.md`.

### Step 6 — Record what you learned to memory

If you discovered something architectural (a new IdP, a quirky widget
framework, a session-renewal endpoint, a write-endpoint topology),
write a short memory entry to
`~/.claude/projects/.../memory/<short-name>.md`. Future agent sessions
read these before they re-burn the same hours.

See the existing entries for shape:

- `project_kth_mfa_methods.md` — KTH only allows Microsoft Authenticator.
- `project_efh_writes_are_aspnet_postbacks.md` — why Unit4 writes can't be curl-replayed.
- `project_wisum_telerik_combobox_recipe.md` — how to set a Telerik RadComboBox via DOM.
- `feedback_discovery_then_curl.md` — the overarching strategy.
- `feedback_irreversible_writes_stay_in_browser.md` — the safety rule.

The format is YAML frontmatter + short prose body, indexed in
`MEMORY.md`. Index lines are read at every session start, so keep them
under ~150 chars.

---

## Common patterns and gotchas

Things that have already bitten us, recorded so the next person
doesn't.

### Telerik RadComboBox needs a real DOM click

`item.select()` via JS throws postback errors inside agent-browser
eval. The working pattern is:

```javascript
const cb = $find('ctl00_main_…_ddlYourCombobox');
cb.findItemByText('Option Label').get_element().click();
```

See `project_wisum_telerik_combobox_recipe` memory.

### ASP.NET WebForms wizard navigation

"Nästa steg" / "Föregående steg" buttons in Telerik are RadButtons.
`$find('btn').click()` throws; the working alternative is:

```javascript
document.getElementById('ctl00_main_btnNextStep').querySelector('a').click();
```

See `project_wisum_wizard_advance_needs_real_clicks` memory.

### `Spara` resets your form

WISUM's "Spara" commits the form's *current* `__VIEWSTATE` and goes
read-only. If you set a Telerik combobox value via JS but didn't wait
for the auto-postback, Spara saves the pre-postback (empty) value.
Don't click Spara during automated checkout — go straight to Nästa
steg.

### bash 3.2 doesn't support `${var@Q}`

macOS ships with bash 3.2. The `@Q` quoting expansion is bash 4.4+.
For shell-quoting strings into a heredoc, use Python instead:

```bash
js_safe=$(printf '%s' "$value" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
```

### `${3:-{}}` is parsed as default `{`, then literal `}`

bash's parameter-expansion default-value parser terminates on the
first `}`. So `${3:-{}}` is *not* "default to `{}`" — it's "default to
`{`, then literal `}` concatenated". This caused real outages. Use
explicit defaults:

```bash
local body="${3-}"
[ -z "$body" ] && body='{}'
```

### `set -e` + `set -o pipefail` kills functions silently

`ls $dir/*.html 2>/dev/null | head -1` returns non-zero when the glob
doesn't match. Inside `set -o pipefail`, this propagates and `set -e`
exits — silently, mid-function. Always guard:

```bash
result=$(ls $dir/*.html 2>/dev/null | head -1 || true)
```

### KTH AD FS expires MSISAuth in ~12 h

The cookie that backs your KTH SSO has a hard ~12 hour lifetime. The
"Keep me signed in" checkbox on the AD FS login page extends it to
~7 days *if KTH IT enabled the feature for your tenant*. The wrapper
auto-ticks it at `kth login`. There is no programmatic way to bypass
the MFA prompt past the absolute lifetime — that's by design.

---

## Memory: making lessons stick across sessions

This repo deliberately makes use of Claude Code's per-project memory
system. Findings about KTH's auth model, individual service
architectures, and personal preferences are stored as small markdown
files at:

```
~/.claude/projects/-Users-…-agenthon/memory/
├── MEMORY.md                              ← index, ~150-char lines
├── project_kth_mfa_methods.md
├── project_kth_keep_me_signed_in.md
├── project_kth_oidc_client_id.md
├── project_efh_writes_are_aspnet_postbacks.md
├── project_efh_activity_context_session_bound.md
├── project_wisum_telerik_combobox_recipe.md
├── project_wisum_wizard_advance_needs_real_clicks.md
├── feedback_discovery_then_curl.md
├── feedback_irreversible_writes_stay_in_browser.md
└── user_wants_centralized_mfa.md          ← user-preference type
```

Three types of memory:

- **project** — facts about the current service / repo (auth limits,
  API quirks, configured projects).
- **feedback** — user-validated rules of thumb. "Always do X. Never do
  Y. The reason is …".
- **user** — preferences and context about the operator
  (collaboration style, goals, expertise).

When you add a new skill and learn something non-obvious, write a
memory entry. The cost is one extra file per session; the value is
that you don't relearn the same lesson three months later.

---

## Security and privacy

| What                                       | Where it lives                                | Treat it as          |
| ------------------------------------------ | --------------------------------------------- | -------------------- |
| KTH SSO cookies (MSISAuth, etc.)           | `~/.config/browser-profile/Default/Cookies`   | as sensitive as your KTH password |
| Service-specific session cookies           | `~/.config/browser-profile/.cookies-*.txt`    | same — never commit, never email |
| Your name + KTH ID                         | `~/.config/kth-cli/config.env`                | low-sensitivity, but personal     |
| Your project codes                         | `~/.config/kth-cli/project-accounts.yaml`     | might be considered internal     |
| Downloaded invoice PDFs / attachments      | `./efh-invoice-<vernr>/`                      | financial records — handle accordingly |
| HAR captures (during discovery)            | `/tmp/*.har`                                  | contain bearer tokens, delete after use |

Everything personal-or-sensitive lives outside the repo. The repo's
`.gitignore` is defensive — it blocks the old in-repo profile path —
but the real safety comes from never committing
`~/.config/kth-cli/` or `~/.config/browser-profile/`.

---

## Contributing

This is primarily a personal/educational repo, but useful PRs are
welcome:

- New service skills (especially ones that follow the
  discovery-then-curl architecture).
- Memory entries that record real architectural findings.
- Better installer ergonomics, especially on Linux.
- Anything that improves the disclaimer or the safety story.

Please **don't** PR your real `config.env` or project-routing rules.
That's the whole point of keeping them outside the repo.

---

## Acknowledgements

- [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)
  — the underlying browser-automation CLI that makes the
  discovery-then-curl loop ergonomic.
- [agentskills.io](https://agentskills.io/specification) — the spec
  that defines the SKILL.md format.
- KTH's published invoice-management documentation, which lives in
  `skills/kth-efh/references/pdf/` (downloaded via the warm profile,
  used here only as context for the SOP). Original copyright KTH;
  redistributed for educational reference.

---

## License

No formal license is included in this repository; treat the code as
read-only educational material unless / until a license is added. If
you adopt parts of it, also adopt the disclaimer at the top of this
file in any derivative work — the safety story is the load-bearing
part of the design.

---

## One more time, just in case

> This is an **educational** repo. **AI agents make mistakes.**
> **Verify everything before any irreversible action.** **KTH IT
> policy may not permit automating these services.** **Use at your
> own risk.**

