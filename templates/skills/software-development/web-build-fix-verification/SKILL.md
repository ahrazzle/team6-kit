<!-- GENERICIZED: 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/web-build-fix-verification/SKILL.md -->
---
name: web-build-fix-verification
description: "Use when verifying served web-build fixes. Assert live-page."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [verification, web, browser, qa, fix-loop, served, announce-and-hope]
    related_skills: [dogfood, systematic-debugging, long-run-deployment-discipline]
---

# Web Build Fix Verification

## When to Use
Iterating on a served web app/build that a real user tests and reviews. Any time a fix is announced for a layout, animation, or behavior claim on a live page.

## Core Doctrine
**A fix is not done until it is verified on the served page, in the state the user actually occupies.** Headless sims, local-file checks, and end-state screenshots cannot arbitrate layout or behavior claims. This is the "no announce-and-hope" rule: never report a fix as live until the served bundle proves it.

## The Served-Page Assertion Gate
For any positional/layout/behavior claim, ship a deterministic console assertion that runs on the served URL (the exact page the user tests):

- Console line like `[app] check: keyboardRect.top=0 -> PASS/FAIL`
- **Sample on the animation-frame loop** that drives the live state (every N frames), not a slow timer — covers the frames the user actually occupies
- **State-aware**: assert battle-only elements only during battle, always-present elements always. "PASS" must mean green across the states the user occupies
- **Assert the element the user sees**, not the first selector match — a wrong node prints green lines over a broken screen
- Keep the gate in the page after shipping; the user's next test becomes a pass/fail line instead of another review round

## Evidence Freshness
Before trusting any "here's the proof" screenshot or result:

- **mtime check**: the screenshot must be NEWER than the source it documents. A stale shot proves nothing and can even show the pre-fix state
- **served == source**: `curl URL | shasum` vs `shasum local_file` — catches cache divergence and silently-dead dev servers
- **Capture the MID-state, not the end state**: a victory/result screen documents none of the layout fixes
- Include URL + state + timestamp in the receipt

## Pitfalls

1. **"Move X to location Y" = relocate X.** If the user says move an existing element (e.g. a next-key indicator) to a new spot, MOVE that element. Do NOT hide it and build a replacement — the user said "literal same thing" and a rebuilt surface is a misread that costs a full review cycle.

2. **Don't CSS-hack framework-rendered nodes.** Reaching into a framework's DOM by inline-style fingerprint (e.g. `div[style*="bottom"]{bottom:auto!important; top:0!important}`) crosses the composition boundary and desyncs the framework's internally-computed animation coordinates — keycap flashes vanish, particles land off-target. Position + animation must be owned by the SAME layer. If the framework can't be configured for a position, place the wrapper and let the framework keep ownership, or own the whole element yourself. Never split position and animation across layers.

3. **Non-invocation first (Occam's razor).** When a framework feature "doesn't render" (keycap animations, particle bursts), grep whether the handler is ever CALLED before blaming CSS, clipping, or z-order. A plugin hooks object that handles events itself but never forwards to the framework (`session.feedback.renderHit(...)`) makes the feature dead by non-invocation. Compose, don't replace.

4. **Headless sims type on fixed cadence** and miss gesture/timing-dependent bugs (stale-note stalls, late-key swallows, autoplay-policy dead input). They cannot validate feel or real typing; only the served page can.

## User Workflow (embed this user's standard)

- "Determine the root cause and don't ask me for another review until it's fixed." A fix round is NOT complete until the served-page gate is green in the state the user tests.
- A repeated-ask loop (same complaint N rounds) is a verification-process failure, not a CSS bug — fix the gate, not just the pixel.
- Root-cause every symptom before announcing; a claim that a headless sim passed is not a claim the user's browser will pass.
- After a real-user test, report only what is confirmed on the served page. No "it should work now" cycles.

## Support
- `references/{CLIENT}` — full case study: a 5-round keyboard/animation loop, each failure mode, and the receipts that finally broke it.
