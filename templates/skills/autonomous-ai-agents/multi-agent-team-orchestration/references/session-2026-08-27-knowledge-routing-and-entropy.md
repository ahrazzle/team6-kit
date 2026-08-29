<!-- GENERICIZED: 12×{CLIENT} | source: skills/autonomous-ai-agents/multi-agent-team-orchestration/references/{CLIENT}-knowledge-routing-and-entropy.md -->
# Session {CLIENT} — Knowledge Routing, Entropy Doctrine, Liveness Checks

Control room session that established the routing/doctrine layer on top of the existing
absorption machinery. The SKILL.md carries the doctrine; this is the session detail.

## The jumble the user felt

Team6 had accumulated many stores ({CLIENT}, {CLIENT}, memory, SOUL.md, Command, Control,
{CLIENT}, {CLIENT}) with no single rule saying which one a new piece of knowledge falls
into. Fix = one routing reflex (see SKILL.md), seeded into every profile's memory as a
pointer (not a copy): "route per mct6/ROUTING.md". Load-path matters: IDEA.md never
auto-loads; `AGENTS.md` at the workspace root does (auto-injected at session start), and
each profile's memory carries the one-line pointer for sessions outside the workspace.
Self-seed per profile with consolidation to fit the memory budget.

## Room index (regenerable)

`OPERATIONS/gen-room-index.py` scans `<project>/wrk/<code>` under the Hermes root, skips
asset dirs (mats, assets, PROJECTS, …), maps display names, emits the ROUTING.md table
(20 rows observed: control, command, 3ft6, {CLIENT}, aet6, gc1, {CLIENT}, ckt6,
vaultofsouls, ift6, kat6, mbt6, mst6, nvt6, rpt6, rht6, t6gc, tst6, tjgc1, xpt6).

## {CLIENT} liveness (check5) design

Two-condition rule so hiatus never pages:
- A (stale): kanban.db mtime OR {CLIENT} git last-commit > 72h (same expiry as
  ventures.yaml `next_action_verified`)
- B (drive-expected): ≥1 active venture with a fresh in-room commitment
- A∧B → alert naming the venture/owner; A without B → silent log-only; unreadable
  manifest → ALWAYS alert (registry that decides "expected" is broken)
- Registry is {CLIENT}'s own ventures.yaml — never the store being judged (circular
  dependency trap)
- `dark_since` column = `next_action_verified + 72h`, derived, recomputable
  retrospectively (survives the watcher itself being down) — the "state of affairs from
afar" reconstruction read. Group dark-above-active ONLY on `state==active && dark_since`;
parked/never-verified ventures keep their own quiet section (intentional park ≠ stall).

## Verified constraint: no programmatic path into Hermes group rooms

Checked {CLIENT}: `hermes send` targets external platforms only (none configured —
`hermes send --list` = "No messaging platforms configured"); `hermes peer dm` delivers
into a bot's canonical DM, not a group room; group rooms are desktop-plugin-owned with
no CLI/API write path. The manual copy-paste step for feeding transcripts into rooms is
STRUCTURAL, not a gap — do not re-check or try to automate it.

## Transport-only transducer pattern (Discord bot)

Bot = record + transcribe + emit text, nothing more (stateless, testable). All routing,
tagging, confidentiality, consent logic lives DOWNSTREAM in an ingestion handler — one
place to get policy right, and routing rules change without touching a long-running
process. Consent/legal flags (recording disclosure, client-data confidentiality) are
BUILD requirements scoped in the brief, not policy suggestions.

## ui-ux-pro-max recap (why scoped stays scoped)

Proof run ({CLIENT} v6) rejected by user — broad skill-driven refresh regressed tuned
work; reverted to v5.8.1. Decision-rules layer still sound for targeted single-decision
queries. Absorbed component sources carry the same constraint: proof on ONE live surface
(component-level, served output) before the catalog counts as live.
