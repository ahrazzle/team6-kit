<!-- GENERICIZED: 1×{AMOUNT}, 7×{CLIENT}, 2×{RELATIONSHIP} | source: skills/productivity/user-preference-capture/SKILL.md -->
---
name: user-preference-capture
description: "Encode user approval signals into durable design principles."
version: 1.0.0
author: {RELATIONSHIP}, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [user-preferences, design-review, positive-reinforcement, approval-patterns, ux]
    related_skills: [requesting-code-review]
---

# User Preference Capture Skill

> When a user reviews work and expresses approval (or disapproval), study the patterns and encode them as explicit design principles. This turns subjective feedback into durable, reusable guidance for future sessions.

## When to Use

- A user says "I like X", "good job", "that's clever", "huge stamp of approval", "absolutely loving this" during a review
- A user corrects a design oversight ("this is a clear design oversight", "you should have caught this")
- A user explicitly asks to study success patterns ("learn from what success looks like", "positive reinforcement training")
- After any MVP review where the user provides feedback on what worked and what didn't

**Don't use for:** Generic praise without substance. "Great job" with no specifics doesn't qualify — you need the *reasoning* behind the approval.

## Prerequisites

- User has reviewed work and provided approval/disapproval with reasoning
- You can identify the specific patterns, techniques, or decisions that earned approval

## How to Run

### Step 1: Catalog the Approval

When the user expresses approval, capture:
- **What** earned approval (the specific feature, pattern, or decision)
- **Why** it earned approval (the user's reasoning — what problem it solves, why it's better than alternatives)
- **The principle** (the general rule that can be applied to future work)

### Step 2: Distinguish Pattern Types

| Pattern Type | Description | Example |
|-------------|-------------|---------|
| **Visualization** | Making abstract concepts tangible | Root letters slotted into templates like algebra |
| **Explanation** | Tidy bundled explanation systems | One-line grammatical explanation with expandable details |
| **Progressive Disclosure** | Collapsed by default, expandable on demand | Grammar section hidden until tapped |
| **Interaction Model** | Bidirectional or single-gesture interactions | Arabic ↔ English word highlighting |
| **Source Management** | Single source at a time with switcher | One {CLIENT} visible, dropdown to switch |
| **Accuracy Standard** | Quality over quantity | "Teach a little right, not a lot wrong" |
| **Data Integrity** | Verification against source | Pull total root occurrences, not filtered subsets |

### Step 3: Encode as Principles

Write principles in this format:

```
## [Principle Name]
**What:** [Specific pattern]
**Why:** [User's reasoning]
**Apply when:** [Trigger condition]
**Example:** [Concrete instance from this session]
```

### Step 4: Distribute by Role

The orchestrator ({RELATIONSHIP}) assigns targeted memory per agent based on their function:
- **Design/UI agents** → visualization, interaction, progressive disclosure patterns
- **Frontend agents** → interaction models, technical workarounds, accuracy standards
- **Research agents** → dataset quality, verification methods, accuracy standards
- **Architecture agents** → source-identity, extensibility, data model patterns
- **QA agents** → edge cases, trust-destroyer identification, verification patterns

**Do NOT** have every agent memorize every pattern. That is redundancy, not role-specific learning.

### Step 5: Verify Against Future Work

When starting new work, check the encoded principles:
1. Does this design follow the approved interaction models?
2. Are we showing one source at a time with a switcher?
3. Is the explanation system tidy and bundled?
4. Is accuracy prioritized over coverage?
5. Is progressive disclosure used for depth layers?

## Pitfalls

**Mechanical rule application.** When the user gives a new directive, it overrides previous standing rules. Understand intent, don't enforce old rules mechanically. The user approved the team's work and told them to keep going — that reactivated work mode; it didn't mean "stay silent."

**Blanket replication.** Every agent committing the same praise list to memory is a hierarchy failure. The orchestrator assigns targeted memory per role.

**Missing the "why".** Capturing "user liked X" without the reasoning produces cargo-cult design. Always capture the principle behind the approval.

**Overgeneralizing from one instance.** One approval of a visualization technique doesn't mean "always visualize." It means "when an abstract concept can be made tangible through spatial/templating metaphors, do so."

## Examples From Practice

### Visualization
**What:** Root letters slotted into morphological template (e.g., ر-ح-م → رَحْمَان)
**Why:** "Like algebra — almost everyone has learned algebra"
**Apply when:** Showing how roots transform into words
**Example:** wazn display in {CLIENT} study pane

### Progressive Disclosure
**What:** Grammar section collapsed by default, expandable on tap
**Why:** "Best of both worlds between simplicity and focus vs depth and robust features"
**Apply when:** A feature adds depth but could overwhelm the primary flow
**Example:** wazn card with expand/collapse toggle

### Single Source Display
**What:** One {CLIENT} visible at a time, dropdown to switch
**Why:** "Users should just be shown a single {CLIENT} source at a time"
**Apply when:** Multiple sources ({CLIENT}, translation) exist for the same content
**Example:** study pane header switcher (Jalalayn ↔ Ibn Kathir)

### Accuracy Over Coverage
**What:** Manual annotation for 29 words rather than algorithmic derivation for all {AMOUNT} ayahs
**Why:** "Better to teach a little of a right thing than a lot of the wrong"
**Apply when:** Scaling a feature where accuracy matters (especially educational content)
**Example:** wazn annotation — manual for Al-Fatihah, defer MASAQ for full Quran

### Sleek = Weight and Register, Not Family-Shopping
**What:** "Sleek" is a WEIGHT + register signal (light-medium geometric sans, light tracking), not a mandate to try a new font family. The {CLIENT} button font loop ran four attempts before landing: Geist Mono (rejected as technical), Manrope 700 (rejected as "thick"), Space Grotesk 500 (accepted briefly), Armstrong (rejected "looks bad"), final = Geist 600.
**Why:** The user said "sleek" and kept correcting the WEIGHT, not the family. Dropping from 700 to 500 was the fix that landed — a new family each round was the wrong lever.
**Apply when:** The user asks for "sleek / futuristic / thin / elegant" styling. First check weight and register on the CURRENT choice before switching families. Capture the family's available weights (a supplied display face may only have Regular 400 + Extrabold, no intermediate — Extrabold recreates the rejected "thick" register).
**Example:** Space Grotesk 500 (light-medium) accepted; Manrope 700 and Armstrong Extrabold rejected as heavy.

### Point-at-a-Concrete-Element = Replicate the FULL Computed Spec
**What:** When the user references a concrete element as the styling target ("use the font from this button", pointing at an actual button), replicate its FULL computed font spec — family AND weight AND case AND tracking — not just the family with a contract-picked weight. {CLIENT}: user pointed at the orange "Request a sourcing quote" button; we applied Geist at 500, but the reference renders at 600 — an off-by-one-weight round followed.
**Why:** The user reads button styling as a complete artifact, not a family choice. They have corrected weight even when the family was right.
**Apply when:** Any instruction of the form "use the style/font from X" where X is a visible artifact. Inspect X's computed style (family, weight, text-transform, letter-spacing) and replicate all of it unless told otherwise.
**Example:** `.btn-cyan,.btn-ghost-dark` → Geist 600, no transform, normal tracking — byte-identical to the `btn-orange` reference.

## Output Format

After capturing, broadcast to the team:

```
Encoded user preferences:
- [Principle 1]
- [Principle 2]
- [Principle 3]
```

Or save to a project's design principles document if one exists.
