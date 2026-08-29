# Viability Pass

> Gate promotion. Filter before build. Capture stays open.

**Use this when:** An idea is being considered for promotion — not on raw capture.

**Capture rule (two-tier funnel):**
- Raw idea capture = one line, zero questions, never blocked.
- This pass runs only when promotion is on the table.

**How to use:**
- Answer each criterion to your best honest ability.
- "Unsure" is a valid answer if you say *what would resolve it*.
- A criterion that can't be answered isn't automatically a kill — note which one, and which disposition it pushes toward.

---

## Criteria (13)

### 1. What is this, in one sentence?

No jargon, no audience inside the sentence. Plain English. If you can't say it plainly, you don't have it yet.

### 2. What problem or opportunity does it address, and for whom?

Specific user or stakeholder — not "people," "companies," or "the market." If the honest answer is "it's cool," that's a hobby, not an idea.

### 3. Why now?

What changed that makes this worth touching *today* rather than six months ago or six months from now? Timing can be a catalyst, a tech threshold, a market shift, a constraint relaxation, or a personal moment. "No particular reason" is honest and valid — it just lowers the urgency bar.

### 4. What already exists in this space, and what's reusable?

Prior art, competitors, failed attempts, public domain / OSS / CC assets you could build on. Default is "reuse before build" — building from scratch is the most expensive way to be wrong. Name license exposure if it matters. Name proven-failure modes if you know them. This is not gatekeeping — it's not "it exists so we can't," it's "what's the cheapest honest relationship to what's already there."

### 5. What's in scope for v1, and what's explicitly out?

Boundaries prevent scope creep from the first conversation. The out-list is as important as the in-list. If everything's in, nothing's in.

### 6. What are the 2–4 assumptions that, if wrong, kill the idea?

Load-bearing bets. Each should be testable. If you can't name what would prove you wrong, you don't have an idea — you have a belief.

### 7. What's the smallest credible version?

Not "MVP" as a label — the smallest thing that delivers enough core value that someone would actually use it, pay for it, or care. Below that line, you're building a demo that teaches you nothing.

### 8. What's the rough resource shape?

People (who'd drive it, rough commitment level), tech (existing vs. new), time (order of magnitude: weeks / months / quarters), and whether it touches an active venture or stands alone.

### 9. What are the downsides and risks?

Not just technical. Reputation, audience fit, maintenance burden, opportunity cost, regulatory or policy exposure if relevant. The idea with no downsides is usually one where you haven't looked hard enough.

### 10. Where does this live relative to existing work?

Inside an active venture (e.g. an existing product, client engagement, or
internal platform)? Extends one? Competes with one? Stands alone? If it
competes with an active venture, that's a decision the venture owner sees —
not something buried.

### 11. Who wants this and why?

Not "who would use it" — who here cares enough to drive it or advocate for it. An idea nobody in the group will own is a parking candidate, not a promotion candidate.

### 12. What would success look like, and how would we know?

A tangible signal with a rough timeline. Not "it becomes popular." Something observable: user adoption, revenue, completed pilot, validated assumption, shipped artifact. If we can't name the signal, we can't call it success.

### 13. What are the kill criteria?

Conditions under which we stop. This is what makes the pass honest. No kill criteria = no real test, just a default-commitment treadmill. Can be time-based, assumption-based, or signal-based.

---

## Dispositions

- **Promote** — clears the pass, becomes a real project brief, enters the build queue.
- **Park** — interesting but not now, or missing critical answers. One-line reason + revisit trigger (date, event, new information). Not a graveyard — a waiting room with a reason.
- **Kill** — fundamentally misaligned, not viable, or nobody will own it. One line on why. No drama.
- **Refine** — core is there but one or two answers are too weak to pass. One round back with a specific question to answer. One round max, then promote or park.

**Refinement round rule:** One round maximum. After that, promote or park. No indefinite limbo.

---

## Verdict block (structured — fields, not prose)

```
---
outcome: promote | park | kill | refine
reason: <one line>
revisit_trigger: <date | event | "none">
reviewed_by: <who ran the pass>
reviewed_at: <timestamp>
---
```

- `outcome` — one of the four disposition labels, verbatim.
- `reason` — one line, the single best sentence on why.
- `revisit_trigger` — a date, an event description, or `"none"` for kill.
- Fields are discrete so the hub surface can filter/sort parked ideas by revisit date, kill reason, and outcome without parsing prose.

---

## Edge cases

- An idea that fails one criterion but is otherwise strong → Refine, not Kill, unless the failed criterion is load-bearing.
- An idea that's clearly a hobby → Kill, with reason "hobby, not project" or similar — honest, not cruel.
- An idea that's been parked before and is back → re-run the pass; don't assume the old verdict.
- An idea that's a near-duplicate of an existing project or parked idea → note the duplicate, disposition accordingly, don't write it twice.

---

## After the pass

- **Promote** → hand the brief to @director for project creation.
- **Park** → the idea stays in the hub with its verdict; `revisit_trigger` is the only thing that brings it back.
- **Kill** → stays in the hub as a record; nothing revives it unless the reason is explicitly overturned.
- **Refine** → one round back to the originator with the specific question; then re-run.

---

**Authors:** @qa (criteria, dispositions, verdict block), @architect (two-tier funnel), @researcher (prior-art criterion), @ux (verdict-as-record), @coder (fields-not-prose). Approved by @director.
