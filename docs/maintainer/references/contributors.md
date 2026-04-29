# Contributor ecosystem

The project's substantive contributors fall into a few specialty domains. Knowing who-does-what lets you tag the right reviewer, weight feedback appropriately, and route new design decisions to the people most likely to have informed opinions.

## Project owner

### @therealaleph

Maintainer. Operates Claude in real-time during DOPR cycles. Reviews/approves all comments via the `[reply via Anthropic Claude | reviewed by @therealaleph]` marker. Final authority on architectural decisions, release timing, what merges. Persian/English bilingual.

When you reply to issues, you're signing those replies in their name. Don't promise things you can't deliver. If you're uncertain about a decision, say so and flag for the maintainer rather than committing to a path.

## Core community contributors

These are the users whose reports and PRs have shaped the project's roadmap. When designing features that touch their domain, tag them for review.

### @w0l4i

**Domain**: deep diagnostic feedback, architectural insight, persistence on hard bugs.

**Notable contributions**:
- Drove the v1.8.1 → v1.8.2 → v1.8.3 evolution of decoy detection. Reported the false-positive in v1.8.1 that led to the 4-cause taxonomy (then 5-cause, then 6-cause).
- Reported the Persian-localized quota body case after multiple failed hypotheses (third-party relay → Iranian VPS appliance → Hetzner DE → Apps Script account locale).
- Suggested the v1.8.x "per-deployment auto-throttle" feature (AIMD style) with detailed rationale.
- Suggested the v1.9.0 xmux roadmap items: byte-range slipstreaming across deployments, MTU/packet-size optimization, per-deployment burst limits.

**How to engage**:
- Take their reports seriously even when initial framing is wrong — they self-correct fast as data comes in
- Their setups tend to be advanced (multiple deployments, Hetzner VPS, Full mode) — don't condescend with basic-tier explanations
- Tag them as a core reviewer for v1.9.0 xmux design issue when filed
- They write in English; reply in English

### @2bemoji

**Domain**: roadmap design discussions, particularly for QUIC blocking and DNS optimization.

**Notable contributions**:
- Drove the design of `block_quic` 3-state UI toggle (off / drop / reject with ICMP unreachable for instant Happy Eyeballs failover) in #361 / #377
- Surfaced the mobile-accessibility framing for `block_quic` (config-only is "Linux desktop only" for users who can't easily edit Android's `/data/data/...` config)

**How to engage**:
- Tag for Android UI batch decisions, especially anything touching QUIC / DNS / network-layer toggles
- Tag for v1.9.0 xmux design as a core reviewer
- English communication

### @ipvsami / Sam Ashouri

**Domain**: advanced Full mode setups, dual-VPS topologies, account suspension reports.

**Notable contributions**:
- Reported the Iranian-VPS xray entry topology in #420 (Iranian VPS as xray entry, German VPS as tunnel-node exit) — drove the dual-routing-xray design discussion
- Reported the Google account flag pattern in #421 (phone-less new accounts, "action required" notifications, Workspace landing HTML on flagged deployments) — drove the v1.8.x detection for cause #6 in the diagnostic taxonomy

**How to engage**:
- Solid Full mode user, comfortable with VPS/xray/network routing; explanations can assume that level
- Tag for v1.9.0 xmux design as a core reviewer
- English communication

### @dazzling-no-more

**Domain**: code contributor — substantive Rust PRs.

**Notable contributions**:
- PR #121 (`--remove-cert` flag for clean CA teardown)
- PR #359 (Google Drive queue tunnel mode — community-testing, hasn't merged yet, awaiting cleanup confirmation)
- PR #438 (H1 container keepalive + 431 oversized headers + clearer port-collision message — merged in v1.8.3)
- PR #439 (DoH bypass for Cloudflare/Google/Quad9/etc. on TCP/443 — merged in v1.8.3)

**How to engage**:
- Reliable code quality; PRs tend to be self-contained with tests + clean diff
- Address review feedback substantively — they iterate on PRs based on reviewer comments
- Has been a steady contributor for multiple release batches; their PRs effectively scale the project beyond what one maintainer can ship
- Tag for v1.9.0 xmux design as a core reviewer (could potentially contribute the implementation)
- English communication

### @euvel

**Domain**: code contributor — Apps Script (Code.gs) features.

**Notable contributions**:
- Designed the spreadsheet-backed response cache (#400 design discussion → PR #443 implementation)
- All 5 review suggestions from the design discussion implemented in PR #443: TTL-aware caching, 35 KB body-size gate, header rewriting on hit, circular buffer for O(1) writes, Vary-aware compound cache keys

**How to engage**:
- First substantive contribution; if quality continues, will become a steady contributor
- Apps Script JavaScript expertise; consider tagging for any future Code.gs changes
- English communication

## Frequent issue reporters (Persian-speaking userbase)

These users post issues frequently. Each has slightly different patterns of reporting and slightly different setups; recognizing the user can save you re-asking diagnostic questions they've already answered in prior threads.

### @hamed0937

Iranian user, heavy Full-mode + Termius-on-Android setup. Reports are detailed but sometimes scattered — recurring TUNNEL_AUTH_KEY / port-mismatch issues. Persian replies.

### @drerfancoding

Iranian user with European VPS. Multiple-deployment Full-mode setup. Common bug: `script_id` (singular) vs `script_ids` (plural) typo. Persian replies.

### @armanfallah82, @Z-Rajaei, @Xsycho666, @ganjiali37, @P3D4AM, @amizx494, @mrpotato67, @sinamationir, @massomi, @habibu5555

Various Iranian users with mixed setups. Tend to report 504/decoy issues. Most resolve via the standard pattern-1/pattern-3/pattern-13 workarounds. Persian replies (use English-Persian mix as the user does).

### @poryiar13, @Alimnsx

VPS-questions reporters. Want to set up Full mode but uncertain about provider selection. Pattern-12 replies.

### @amintoorchi (xdevteam)

Maintains a community-mirrored set of Iranian-CDN download links for the project's binaries (xdevteam.liara.space). Pending: SHA-256 verification before docs link to those mirrors. See #422.

## Adjacent projects + people

### @masterking32

Original Python project (`masterking32/MasterHttpRelayVPN`). mhrv-rs is the Rust port; we cherry-pick stability/feature commits from masterking32 periodically. PR #438 in v1.8.3 was a batch of three such cherry-picks. Not a direct contributor here, but the project's design parent.

### @denuitt1

Maintainer of `denuitt1/mhr-cfw` — Cloudflare Workers backend that aims to be Apps Script-compatible. Independent project, not officially endorsed. Tracked in #380 / #393 for compatibility audit (queued v1.8.x). Not a direct contributor here.

### @g3ntrix, @mehrad-mz

Authors of forks/branches on the Python project that occasionally have valuable commits to cherry-pick (see #430 for the audit list).

### @kanan-droid

Reported the git-from-Iran-when-filtered workaround patterns in #333. Suggested user-trust-store-aware routing patterns. Not a code contributor but informed multiple roadmap items.

## Tagging conventions

When tagging in a comment:

- Reviewer requests: "@dazzling-no-more — would you mind reviewing this approach?"
- Cross-references: "see [#404](https://github.com/therealaleph/MasterHttpRelayVPN-RUST/issues/404) where @w0l4i described this"
- Recognition: "this drove the design — thanks @euvel for the detailed initial proposal"
- For v1.9.0 xmux design issue specifically (when it's filed): tag @w0l4i, @2bemoji, @ipvsami, @dazzling-no-more, @euvel as core reviewers

Don't ping people gratuitously; each ping should have a clear ask or recognition.

## Project history context

The project predates this repo as `masterking32/MasterHttpRelayVPN` (Python). The Rust port was started for performance + cross-platform binary distribution. Apps Script protocol stayed compatible across both, and we periodically cherry-pick from upstream Python. v1.7.x represented the initial port stabilization; v1.8.x is the "DPI evasion + diagnostics + community-contribution batch"; v1.9.0 will be the xmux flagship.

For historical issue context, the canonical "long" issues are:
- #313 — Iran ISP throttle, primary tracking issue, ~50+ comments
- #300 — SABR cliff, primary tracking for video streaming limit
- #310 — VPS setup help, primary tracking for setup questions
- #333 — VPS / Full mode / Iranian-network workarounds
- #420 — dual-VPS topology, primary tracking for advanced Full mode
- #382 — Cloudflare error patterns
- #325 — community-shared deployment workflow
- #361 / #377 — Android UI batch + QUIC blocking design
- #369 — v1.9.0 xmux design (RFC, not yet filed as the formal design issue)
