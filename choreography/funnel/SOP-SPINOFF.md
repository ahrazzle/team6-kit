# SoP — Idea Spin-Off to a Team6 Group + Project

> The process by which an idea leaves the ideation hub and becomes its own
> Team6 group chat and project workspace.

## Scope

Applies when a thought or idea **warrants its own Team6 group and project**.
The hub is the single intake point: no ad-hoc projects sprout outside this path.

---

## Stage 0 — Capture (never blocked)

- Thought lands in `INBOX.md` as a one-line record. Zero questions.
- No idea is ever lost; the Inbox is append-only.

## Stage 1 — Viability pass

- Runs only when promotion is on the table (two-tier funnel; never at intake).
- Template: `TEMPLATES/viability-pass.md` — 13 criteria, 4 dispositions.
- Output: a **verdict block** (fields, not prose):
  `outcome`, `reason`, `revisit_trigger`, `reviewed_by`, `reviewed_at`.
- **Promote** requires the pass to clear. **Refine** = one round max, then promote or park.

## Stage 2 — User gate

- **Promotion is not final until @client confirms the spin-off.**
- The user's explicit go is what converts a passed idea into a new team6 group + project.
- Hub never self-promotes without this confirm.

## Stage 3 — Discovery / reuse scan (entry contract before planning)

- Mandatory before any planning or architecture: prior art, competitors,
  failed attempts, OSS/CC assets, license obligations, proven-failure modes.
- Lane: @researcher. Default is **reuse before build**.
- Output: a short scan note appended to the promoted record.

## Stage 4 — Project creation

- Lane: @director. Call `project_create(name, path)` directly with the user's
  workspace path (the tool call is the contract — no skill invocation needed).
- Scaffold the standard workspace: `PROJECTS/ OUTPUTS/ TEMPLATES/ LOG/` + `IDEA.md`.
- Hub records provenance: `PROJECTS/<project>.md` with a link to the Inbox record.

## Stage 5 — Group chat spin-off

- New room is created for the project.
- **The new room's opening brief = the promoted record + verdict block + discovery
  scan output, restated verbatim** at the top of the thread (cold-start rule:
  the thread is self-contained from message one).
- The hub keeps a provenance link; the spawned project owns its lifecycle from message one.

## Stage 6 — Lifecycle handover

- After spin-off, the idea leaves the hub's active funnel.
- **No write-back to the hub except through @director.**
- Hub-side record updates (e.g. status → promoted, project link) are the director's job.

---

## Sequence (who does what)

| Stage | Owner | Output |
|---|---|---|
| 0. Capture | anyone | `INBOX.md` record |
| 1. Viability pass | @qa (or assignee) | verdict block |
| 2. User gate | @client | explicit go |
| 3. Discovery scan | @researcher | scan note |
| 4. Project creation | @director | workspace + provenance |
| 5. Room spin-off | @director | new group chat, opening brief verbatim |
| 6. Handover | @director | provenance link, no write-back |

## Guardrails

- **One refinement round max** — no indefinite limbo.
- **No ad-hoc spin-offs** — every project enters via this SoP.
- **Hub stays the single intake point** — the Inbox and this SoP are the only doors.
- **No write-back except through @director** — protects the hub record integrity.

---

*Authors: @director (process synthesis), @ux (single data model), @researcher
(stage-3 scan), @architect (handoff artifact + provenance), @qa (pass gate),
@coder (fields-not-prose). Approved by @director, pending @client review.*
