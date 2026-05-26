# Track C: Agent Quickstart — KTH IT Service Skills

> **For AI agents** (Claude Code, or any agent that reads CLAUDE.md).
> Give this file to your agent to get started.

## What this repo is

A collection of **reusable AI agent skills** for automating KTH IT services:

| Skill | Service | What it does |
|-------|---------|-------------|
| `kth` | KTH SSO | Login + MFA, session management, routing to sub-skills |
| `kth-findity` | [Findity](https://hogia.findity.com/app/) | Travel expenses: upload receipts, create reports, OCR |
| `kth-efh` | [Unit4 EFH](https://agrprodweb01.ug.kth.se/agrprod/) | E-invoice handling: query tasks, view invoices |
| `kth-wisum` | [WISUM](https://www.wisum.its.umu.se/KTH/) | Purchasing: search products, manage carts, checkout |
| `kth-intra` | [Intranet](https://intra.kth.se/) | Internal news, HR info, service directory |
| `kth-service-onboarding` | (meta) | How to add a NEW KTH service as a skill |

## Prerequisites

1. **Claude Code** installed ([claude.ai/download](https://claude.ai/download))
2. **Claude Chrome extension** installed and connected to Claude Code
   - Install from: https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome
   - The extension lets the agent see and interact with your Chrome browser
3. **KTH account** with Microsoft Authenticator MFA set up
4. **Python 3** + **curl** on PATH

## Setup

```bash
# 1. Clone the repo
git clone -b track-c git@github.com:kth-sci/sci-agenthon-2026.git
cd sci-agenthon-2026

# 2. Install CLIs + skills
./install.sh        # symlinks CLIs + skills, seeds config templates

# 3. Edit your KTH identity
$EDITOR ~/.config/kth-cli/config.env   # name, unit, delivery address

# 4. Start Claude Code WITH Chrome extension enabled
claude --chrome
```

**Important**: always start Claude Code with `claude --chrome` so the
agent can use the Chrome extension tools (`mcp__claude-in-chrome__*`)
for browser automation.

## How the agent should work

Read `CLAUDE.md` first — it describes the architecture and operating principles.

### Step 1: Login (once per ~7-day session)

```
Agent: Load skill `kth`, then navigate Chrome to https://www.kth.se/social/?login
User: Complete MFA + tick "Keep me signed in"
Agent: Verify session via javascript_tool on intra.kth.se
```

### Step 2: Use a service

Tell the agent what you want. Examples:

- **"Upload my receipts to Findity"** → agent loads `kth-findity` skill, captures bearer via `javascript_tool` fetch intercept, uses the 3-step upload API
- **"Check my pending invoices"** → agent loads `kth-efh` skill, runs `kth efh count`
- **"Search WISUM for a USB-C hub"** → agent loads `kth-wisum` skill, runs `kth wisum search "usb-c hub"`
- **"Order Simin's forwarded cart"** → agent loads `kth-wisum`, drives the checkout wizard via Chrome extension

### Step 3: Add a new service

Tell the agent: "I want to automate [service URL]". The agent loads `kth-service-onboarding` and walks through:
1. Navigate to the service in Chrome
2. Discover API endpoints via `read_network_requests`
3. Probe endpoints via `javascript_tool` + `fetch()`
4. Write a SKILL.md + optional CLI wrapper
5. Test it

## Key architecture principle: discovery-then-script

**Phase 1 (discovery)**: Use Chrome extension's `computer` tool (screenshot + click) to explore a new page. Slow, interactive — that's expected for first contact.

**Phase 2 (script)**: Write JS via `javascript_tool` that does everything without screenshots. Capture auth by intercepting `window.fetch`. Call APIs via in-page `fetch()`. This is the fast path — no round-trip screenshots.

**Phase 3 (CLI)**: Wrap the API calls in a `bin/kth-*` CLI for reuse outside the browser.

**The goal**: after discovering a service once, every repeat operation is a **scripted one-shot**.

## Discovered API patterns (copy-paste ready)

### Findity bearer capture (run in page context via javascript_tool)

```javascript
// Override fetch to intercept the bearer token
const origFetch = window.fetch;
window._b = null;
window._origF = origFetch;
window.fetch = function(input, init) {
  if (init && init.headers) {
    let auth = null;
    if (init.headers instanceof Headers) auth = init.headers.get('Authorization');
    else if (typeof init.headers === 'object') auth = init.headers['Authorization'];
    if (auth && auth.startsWith('Bearer ') && !window._b) window._b = auth.slice(7);
  }
  return origFetch.call(this, input, init);
};
// Then click something in the SPA to trigger an API call → window._b is set
```

### Findity receipt upload (3-step, all from javascript_tool)

```javascript
// Step 1: Upload PDF
const resp = await fetch(pdfUrl);
const blob = await resp.blob();
const upload = await window._origF('/api/v1/expense/content?organizationId=' + orgId, {
  method: 'POST', headers: {'Authorization': 'Bearer ' + bearer, 'Content-Type': 'application/pdf'}, body: blob
});
const contentId = (await upload.json()).id;

// Step 2: OCR scan
const scan = await (await window._origF('/api/v1/expense/content/' + contentId + '?action=scan&organizationId=' + orgId, {
  method: 'PUT', headers: {'Authorization': 'Bearer ' + bearer}
})).json();
const sr = scan.scanResult;

// Step 3: Create expense
await window._origF('/api/v1/expense/expenses', {
  method: 'POST',
  headers: {'Authorization': 'Bearer ' + bearer, 'Content-Type': 'application/json'},
  body: JSON.stringify({
    organizationId: orgId,
    expenseReportId: reportId,
    categoryId: sr.categoryIds[0],
    verification: {
      type: 'ReceiptVerification',
      amount: sr.amount, taxAmount: sr.taxAmount, currency: sr.currency,
      description: 'Your description here',
      purchaseDate: sr.purchaseDate + 'T12:00:00Z',
      receiptAttachment: {id: contentId},
      customFields: [/* project, unit, account fields */]
    },
    reimbursementCurrency: 'SEK'
  })
});
```

### KTH session check (via javascript_tool on intra.kth.se)

```javascript
// Returns true if logged in, false if session expired
!document.querySelector('a')?.textContent?.match(/Logga in|Log in|Sign in/)
```

## Important rules

1. **Never auto-submit money-moving actions.** The agent prepares; the user clicks Slutför / Submit / Ekonomisk attest.
2. **3-second delay between Findity API calls** to avoid rate limiting.
3. **Bearer tokens expire** — re-capture via fetch intercept when you get HTTP 401.
4. **User config lives at `~/.config/kth-cli/`** — never committed to git.

## File structure

```
bin/                    CLIs (pure curl/API, no browser dependency)
skills/                 Agent skill definitions (SKILL.md per service)
config/                 Template files for user config
install.sh              Symlinks + config seeding
CLAUDE.md               Architecture + operating principles (read this!)
```
