# Track C — KTH Agent Skills

The KTH agent skills produced in this track now live in their own
standalone, installable repository:

## 👉 [github.com/kth-sci/kth-agent-skills](https://github.com/kth-sci/kth-agent-skills)

They were extracted from this event repo so they can be installed,
versioned, and improved independently of the Agenthon 2026 materials.

## What's there

Reusable agent skills + CLIs that let an AI agent (Claude, or anything
that understands the [Agent Skills specification](https://agentskills.io/specification))
operate KTH IT services from one command line, via the Claude Chrome
extension:

| Skill | Service |
| ----- | ------- |
| `kth` | Main entry skill — KTH SSO / session |
| `kth-findity` | Travel expenses (Findity / Hogia) |
| `kth-efh` | Unit4 e-invoices (Inwise / EFH) |
| `kth-wisum` | Purchasing / orders (WISUM) |
| `kth-intra` | Intranet navigation (intra.kth.se) |
| `kth-canvas` | Canvas LMS read + Markdown export |
| `kth-prisma` | VR / Vetenskapsrådet (Prisma) grant applications |
| `kth-service-onboarding` | Meta-skill — add a new KTH service |

## Install

```bash
git clone https://github.com/kth-sci/kth-agent-skills
cd kth-agent-skills
./install.sh
```

See that repo's `README.md` for the full walkthrough, the
discovery-then-script methodology, and the safety model (irreversible
writes stay with the user — the agent prepares, you click the final
submit/approve button).

---

> ⚠️ **Educational reference only.** KTH IT policy may not permit
> automation of every service — use at your own risk and check with
> KTH IT if in doubt. AI agents make mistakes; verify every action,
> especially anything irreversible.
