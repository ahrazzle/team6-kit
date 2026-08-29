<!-- GENERICIZED: 3×{CLIENT}, 9×{RELATIONSHIP} | source: skills/adversarial-review/references/session-20260820-{CLIENT} -->
# Session: {CLIENT} Architecture Live Review ({CLIENT})

A 7-agent team ({RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, {RELATIONSHIP}, user) defined the architecture for {CLIENT}, a kids' typing-rhythm game framework. {RELATIONSHIP} performed live adversarial review during the design discussion.

## Context

Unlike post-hoc review of a written output, this was **real-time adversarial intervention** during a group architecture session. The "output" was the emerging architecture itself — decisions made in the group chat that would determine downstream implementation.

## Interventions Made

### 1. Input Model Fork (Critical Architectural Question)
**The intervention:** Surprised that nobody had resolved what happens when a child types a wrong key. Two models existed — "wrong key advances beat-map" (rhythm game) vs "wrong key blocks progress" (traditional typing) — and every downstream decision (plugin contract, scoring, fail state, feedback) depended on which model was chosen.

**Why it mattered:** The team was about to scaffold an event bus and define a plugin API without knowing whether wrong keys should advance the beat-map or block progress. Building either system would have meant rebuilding it all if the other model was chosen.

**Resolution:** {RELATIONSHIP} provided the osu! precedent — wrong keys are ignored entirely (pedagogy holds), timing accuracy on correct keys determines the judgment (rhythm satisfaction preserved). The false binary dissolved.

**Lesson:** When you hear "we need to decide between X or Y" and X and Y lead to completely different architectures, stop everything and resolve that question first. No scaffolding, no API design, no prototyping until the fork is settled.

### 2. Framework-First Risk (Validate Before Abstract)
**The intervention:** Challenged the plan to build a plugin architecture before validating that any typing-rhythm game would actually engage kids. Argued for building one complete game first, proving engagement, then extracting the framework.

**Why it matters:** Building a framework before validating the core experience risks months of infrastructure for an unvalidated engagement hypothesis.

**Resolution:** Team compromised — build input + feedback layers first (the keystroke bus + animated keyboard), then build the first game as a plugin. This validates the architecture with a real game from day one without retrofitting from a monolith.

**Lesson:** Never abstract before you have at least two concrete examples. One example validates the experience. Two examples reveal what's common and what's specific.

### 3. Age Band Scaling (Demographic Precision)
**The intervention:** Flagged that "kids" is not a demographic. A 6-year-old hunt-and-pecking their first letters and a 12-year-old grinding WPM need fundamentally different architectures.

**Why it matters:** A framework that tries to serve all ages serves none. Key size, word complexity, reading level, session length, reward cadence all diverge.

**Resolution:** Team agreed to start with ages 7-10 as the first target.

**Lesson:** When the user says "kids" or "users" or "people," ask "which ones?" The answer determines the architecture.

### 4. Motivation Problem (Feedback as Bridge, Not Cosmetic)
**The intervention:** Called out that the engagement problem is not about flat 2D art or missing particle effects — it's about whether typing fast has *meaning* in the game world. Nitro Type works because real-time PvP gives speed meaning beyond typing, not because of car graphics.

**Why it matters:** If the team focused on visual polish without solving the motivation problem, they'd build a pretty thing kids try once and abandon.

**Resolution:** {RELATIONSHIP} reframed the feedback layer as "the bridge between correct input and 'I want to do it again'" — conceding that visual feedback is not cosmetic but the mechanism that makes motivation tangible.

**Lesson:** The most dangerous design failure is solving the wrong problem beautifully. Name the actual problem before designing the solution.

## Outcome

All four interventions landed. The input model fork resolution shaped the plugin contract and event bus design. The validate-before-abstract compromise shaped the work sequencing. The age band recommendation set the first target demographic. The feedback-as-motivation framing grounded the feedback layer design.

## Key Difference from Post-Hoc Review

In post-hoc review of a written output, the reviewer attacks a finished artifact. In live architecture review, the reviewer attacks the **assumptions and forks that, if left unresolved, cause the team to build the wrong thing.** The timing is different (during design, not after), but the adversarial function is the same: make the output stronger by subjecting it to the hardest possible scrutiny.
