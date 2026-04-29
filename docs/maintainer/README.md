# Maintainer skill

This directory contains the project's maintainer-facing knowledge base — encoded as a Claude skill. Its purpose is to give an agent (local or cloud-scheduled) full context for triaging issues, reviewing PRs, cutting releases, and writing user-facing replies in the project's voice.

The skill is the same one packaged at `~/.claude/skills/mhrv-rs-maintainer/` on the maintainer's machine. This in-repo copy exists so cloud-scheduled agents (which run in a fresh sandbox without local skills) can read the same reference material.

## Read order

Start with `SKILL.md` — the orientation, conventions, and pointers. Then read references lazily as relevant to the current task:

- `references/architecture.md` — apps_script vs Full mode, MITM CA, tunnel-node, AUTH_KEY/TUNNEL_AUTH_KEY/DIAGNOSTIC_MODE, SNI rewriting
- `references/issue-patterns.md` — 15 recurring issue patterns + diagnostic procedures + canonical reply structures + quick triage table
- `references/diagnostic-taxonomy.md` — 6 candidate causes for the placeholder body, DIAGNOSTIC_MODE disambiguator
- `references/workflow-conventions.md` — reply marker, Persian/English match rule, changelog format, commit messages, close reasons
- `references/release-workflow.md` — Cargo.toml → tag → Telegram pipeline
- `references/contributors.md` — w0l4i, 2bemoji, ipvsami, dazzling-no-more, euvel + frequent Persian reporters
- `references/roadmap.md` — v1.8.x queue, v1.9.0 xmux, v1.9.x+ longer-horizon
- `references/persian-templates.md` — 6 ready-to-adapt Persian reply templates + standardized phrases

## Updating

When the maintainer's local skill is updated (e.g., new issue pattern, refined Persian template), copy the changes here and commit. The local skill at `~/.claude/skills/mhrv-rs-maintainer/` is the source of truth; this in-repo copy mirrors it.

## Why this exists in the repo

Cloud-scheduled DOPR agents clone the repo fresh on each fire. They have no access to the maintainer's local home directory. Embedding the skill in `docs/maintainer/` means the cloud agent can read the same canonical context as the local maintainer — same diagnostic taxonomy, same Persian templates, same conventions — and produce replies indistinguishable from a local DOPR session.
