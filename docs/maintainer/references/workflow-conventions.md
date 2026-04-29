# Workflow conventions

These are the writing conventions, formatting rules, and tone guidelines for everything that goes into the public repo or out to users. Internalize these — they're applied to every issue reply, every commit message, every changelog, every PR description.

## The reply marker

Every substantive issue or PR comment ends with this exact footer:

```
---
<sub>[reply via Anthropic Claude | reviewed by @therealaleph]</sub>
```

That's a literal Markdown horizontal rule, then the `<sub>...</sub>` line. The `[reply via Anthropic Claude | reviewed by @therealaleph]` text is verbatim — same brackets, same pipe, same case, same `@therealaleph` mention.

**Why this exists**: the maintainer (@therealaleph) is operating Claude in real-time and approves each post implicitly by sending it. The marker signals to the user that Claude wrote the prose but a human reviewed it. This is true and it's also a courtesy — users in this community know this convention and rely on it.

**Don't omit it**, don't translate "reviewed by" into Persian, don't paraphrase the format. The marker is the same regardless of whether the rest of the reply is in Persian or English.

**Where it doesn't go**: very short comments like "Dup of #423." or "Closing as resolved." or close-comments via `gh issue close --comment "..."`. The marker is for substantive replies. Trivial close comments don't need it.

## Persian or English: match the user

The repo's userbase is majority Persian-speaking. Writing in their language matters — both for clarity (technical context lands better) and for respect (assuming everyone wants English is wrong).

**Match what the user wrote**:
- User wrote in Persian → reply in Persian
- User wrote in English → reply in English
- User wrote a mix → match the dominant language; if it's roughly even, prefer Persian since most mixed-language Iranian users default to Persian for nuance and English for technical terms

**Things that always stay in original Latin form**, regardless of reply language:
- Code blocks (Rust, JSON, bash, JS — all stay as-is)
- Command-line examples (`gh issue close N`, `cargo build`, `docker run ...`)
- Technical identifiers: `AUTH_KEY`, `TUNNEL_AUTH_KEY`, `script_id`, `parallel_concurrency`, `disable_padding`, `tunnel_doh`, `bypass_doh_hosts`, `DIAGNOSTIC_MODE`, `passthrough_hosts`, `google_ip`, `mode: "full"` / `mode: "apps_script"`
- Filename references: `Code.gs`, `CodeFull.gs`, `config.json`, `tunnel-node`, `mhrv-rs.exe`, `MhrvVpnService.kt`, `domain_fronter.rs`
- URLs and links
- The reply marker
- Issue references like `#404`, `#313`
- HTTP status codes (`502`, `504`, `403`)
- Unicode shrugs like `:)` and emoji where they were in original

**Don't**:
- Translate command names or function names
- Mix Persian text into code blocks (unless user did so in their own paste)
- Use machine-translation for the Persian — write it natively. If you can't, ask the maintainer

**Persian register**: write at "polite professional" level — `می‌فرمایید` over `می‌گی`, `لطفاً` (please), full pronouns when needed. Iranian Github users tend to write fairly formally; match that. Use Persian punctuation conventions: `،` (Persian comma), `؛` (Persian semicolon), `؟` (Persian question mark) — though comma in lists is acceptable as `،` or `,` per style preference.

## Caveman mode: maintainer-only

The maintainer's `/caveman` skill installs a tone for maintainer-facing chat: terse, drop articles, "fix bug in foo" not "I fixed the bug in foo". **That mode applies ONLY to your replies in chat to the maintainer.** It must NOT appear in:

- GitHub issue replies (Persian or English, full sentences)
- GitHub PR comments
- Commit messages
- Tag/release notes
- Changelog entries
- Code comments (full sentences in code comments are fine and expected)

The voice in public artifacts is warm, full-prose, and deliberately not terse. Iranian users especially read carefully and the brevity of caveman mode reads as cold or dismissive. Use full sentences. Explain reasoning. Be patient.

## Changelog format

Every release has a file at `docs/changelog/vX.Y.Z.md`. The format is strict:

```markdown
<!-- see docs/changelog/v1.1.0.md for the file format: Persian, then `---`, then English. -->
• [bullet 1 in Persian, with markdown links to issue numbers]
• [bullet 2 in Persian]
• [bullet 3 in Persian]
---
• [same bullet 1 in English, written natively, not machine-translated]
• [same bullet 2 in English]
• [same bullet 3 in English]
```

Conventions:

- **Use `•` (U+2022 bullet)**, not `-` or `*`. The Persian half uses bullets because Markdown unordered lists don't render naturally with Persian RTL text in the GitHub Releases page.
- **Issue/PR links**: full GitHub URLs in markdown form: `[#404](https://github.com/therealaleph/MasterHttpRelayVPN-RUST/issues/404)`. Don't use bare `#404` in changelogs — they don't auto-link in the Persian section.
- **Same content both halves** — they cover the same bullets, in the same order. Not necessarily verbatim translation; the Persian is written for Persian readers and may use slightly different framing.
- **Length**: each bullet should describe what changed AND why it matters. "Added DoH bypass" is too thin; "DoH lookups now route around the Apps Script tunnel via plain TCP, saving the ~2s UrlFetchApp roundtrip per name without losing privacy (DoH is already encrypted)" is the right depth.
- **Credit contributors**: if a PR landed from a community contributor, say so by name + handle. Persian: `از @euvel`. English: `by @euvel`.
- **Backwards-incompatible changes**: rare for this project, but flag prominently if any. Add `**شکستگی سازگار**` / `**Breaking change**` prefix.

The starter template is at `assets/changelog-template.md`.

## Commit messages

Format:

```
<type>: vX.Y.Z — <short summary>

<longer prose body explaining the why and the changes>

[optional: bullet list of specific changes]
```

Types in regular use:
- `feat:` — new feature, user-visible (most common)
- `fix:` — bug fix
- `chore(releases):` — auto-fired CI commit refreshing prebuilt binaries
- `chore:` — version bump, dep update, etc.
- `docs:` — documentation-only changes
- `ci(workflow-name):` — workflow file changes
- `feat(area):` — feature scoped to a specific subsystem (e.g., `feat(code.gs):`, `feat(drive):`)

Example commit message:

```
feat: v1.8.3 — sheet cache + DoH bypass + H1 keepalive + 431 + clearer errors

Three substantive PRs from contributors landed for this release:

- #443 by @euvel: optional spreadsheet-backed response cache in Code.gs.
  Implements all 5 review suggestions from the design discussion (#400):
  TTL-aware caching, 35 KB body-size gate, header rewriting on hit,
  circular buffer for O(1) writes, Vary-aware compound keys.

- #439 by @dazzling-no-more: bypass Apps Script tunnel for known DoH
  endpoints on TCP/443. Cloudflare/Google/Quad9/AdGuard/NextDNS/OpenDNS/
  ...
```

Conventions:
- **Subject line under 75 chars** (GitHub truncates longer)
- **Body wrapped at ~75-80 chars** for terminal-readability
- **Don't sign with `Co-Authored-By: Claude`** when committing as the maintainer — the project's convention is human-authored commits with the marker reserved for issue/PR replies, not commits. (Different projects have different conventions; this one keeps the public history simple.)
- **PR-merge commits**: when merging PRs via `gh pr merge --merge`, use `--subject` and `--body` to write the merge commit. Format is the same — type prefix, short summary, body explaining what shipped and credit.

## Issue close reasons

Always pass `--reason`:

- `--reason completed` — the user's problem was resolved (their fix worked, or our fix shipped + they confirmed). For close comments, brief acknowledgement is fine; full marker not required.
- `--reason "not planned"` — duplicate, architectural limit, won't-fix, or stale and unrecoverable. Always link to the canonical thread when closing as duplicate.

For close comments, always include the destination issue if duplicate:

```
gh issue close N --reason "not planned" --comment "Closing as duplicate of #420 — full discussion + workarounds there."
```

## File names for reply markdown

Convention: write reply markdown to `/tmp/r-<issue>-<topic>.md` before posting via `gh issue comment N --body-file /tmp/r-<issue>-<topic>.md`.

Examples:
- `/tmp/r-404-w0l4i-quota.md` — reply to #404 about w0l4i's quota observation
- `/tmp/r-414-decoy.md` — reply to #414 about the decoy body
- `/tmp/r-pr-merged.md` — generic "merged + included in vX.Y.Z" PR thank-you reply

**Why use files instead of inline `--body`**: the inline `--body` argument runs through zsh, which interprets backticks (\`code\`) and `$()` substitutions. Issue replies frequently contain bash command examples with these patterns. The file approach sidesteps the quoting hell entirely. Use it by default.

The exception is very short replies like `Dup of #423.` — those can use `--body "Dup of #423."` directly.

## Tone

- **Warm but technical**. Iranian users in particular often write apologetically ("sorry for using AI for the translation", "sorry to bother") — answer them as you'd want to be answered: with care, with technical depth, with explicit acknowledgment that their report is valuable.
- **Don't promise fixes you can't deliver**. The Iran ISP throttle is not something we can fix; saying "we're working on it" is OK, "we'll fix it next release" is not.
- **Don't pretend certainty**. v1.8.1's over-confident "AUTH_KEY mismatch" message in the decoy detection cost us trust with @w0l4i. v1.8.2 + v1.8.3 are explicitly less assertive ("could be one of the following four/six causes...") because being honest about uncertainty is the better long-term move.
- **Acknowledge community contributions liberally**. When a contributor's report shaped a roadmap item, say so by name. When a PR lands, thank them in the merge commit + PR comment + changelog. The project runs on goodwill.
- **Don't apologize excessively** but do correct yourself when wrong. The "g.workstream.ir is third-party / Iranian VPS / Hetzner" iteration in #404 had two wrong hypotheses; each correction acknowledged the previous error and moved on. That's the right pattern.

## Persian translation specifics

When writing Persian replies:

- **Half-spaces (ZWNJ — `‌`)** in compound words: `می‌خواهم` (not `میخواهم` or `می خواهم`), `نمی‌توانم` (not `نمیتوانم`)
- **Persian numerals**: optional but common in formal writing — `۲۰،۰۰۰` instead of `20,000`. Code/commands always Latin numerals.
- **English technical terms in Persian text**: leave them in Latin script with surrounding Persian particles. Example: `از طریق Apps Script روی Google` (not transliterated)
- **Quotation marks**: Persian uses `«...»` rather than `"..."` for prose. Code/commands use `"..."` regardless.
- **The reply marker stays in English** as established. Don't translate `reviewed by` to Persian.

## DOPR cycle structure

When triaging a batch of issues/PRs, work through them in this order:

1. **Read everything first** — list PRs, list recently-updated issues, scan headlines. Don't reply to issue 1 before knowing what issues 2-15 contain. Often there are clusters that should be addressed together (e.g., five users all hit the v1.8.0 decoy on the same day).
2. **Triage by pattern** — match each issue to a pattern from `issue-patterns.md`. Issues that match a pattern get pattern-canonical replies (with specifics drawn from the user's actual log lines). Issues that don't match a pattern get individual attention.
3. **Substantive PRs first** — if a PR has tests passing and looks mergeable, merge it. Then your subsequent issue replies can reference "shipped in vX.Y.Z" instead of "queued for next release".
4. **Reply in batches but not as templates** — write each reply to address that user's specific log lines, config quirks, or terminology. Templated replies are easy to spot and erode trust.
5. **Close cleanly** — if an issue was a duplicate, close at the end of your reply with the close-comment pointing to canonical thread. If it's awaiting user verification, leave open with last comment from you.
6. **Cut releases when work lands** — don't accumulate fixes across multiple work sessions. Each session that lands user-visible code → one tag → one release.
