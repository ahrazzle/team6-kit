<!-- GENERICIZED: 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/game-feedback-animations/SKILL.md -->
---
name: game-feedback-animations
description: "Rhythm game feedback — approach rings, spring, ripples."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [web]
metadata:
  hermes:
    tags: [animation, canvas, game-dev, feedback, rhythm-game]
    related_skills: [p5js, claude-design]
---

# Game Feedback Animations

> Canvas/SVG animation patterns for rhythm games and juicy feedback. Born from building {CLIENT}, validated through 46+ tests.

## When to Use

- Building rhythm games, typing games, music games
- Implementing "approach" mechanics (osu!/Stepmania-style)
- Creating particle effects, ripples, expanding/contracting animations
- Adding spring-physics feel to UI elements
- Rendering multiple simultaneous animated elements on canvas

## Core Patterns

### 1. Approach Ring System

Rings shrink toward a target as the note approaches. Player times input to when ring matches target size.

**Preempt time scales with difficulty:** easy: 1500ms, medium: 1000ms, hard: 600ms, expert: 350ms.

**Color ramp:** white (far) → cyan → green → yellow (near). **Opacity ramp:** 30% → 100%.

**Judge interface:** `getNextNotes(count: number)` returns `{ note, timeUntilHit }[]`.

### 2. Spring-Physics Key Depression

Keys overshoot and bounce like mechanical switches. Use `cubic-bezier(0.34, 1.56, 0.64, 1)` with keyframes that go past target then settle. Re-trigger by removing class → force reflow → re-add.

### 3. Ripple Emanation

Expanding concentric circles from keystroke position.

**Critical bug:** When staggering ripples (second at `now + 80`), next frame computes negative elapsed → `easeOutQuad(negative)` returns negative radius → `IndexSizeError`.

**Fix:** `const elapsed = Math.max(0, now - r.startTime);`

### 4. Multi-Note Highway

Render 2-3 upcoming approach rings simultaneously. Player tracks a stream, not a single highlight.

## Pitfalls

1. **Negative radius** — always clamp `elapsed` to `Math.max(0, ...)`
2. **Double-start** — guard with `if (gameActive) return;` at top of start function
3. **Stale highlights** — clear animation state in BOTH `reset()` AND `stop()`
4. **Browser caching** — use `?v=3` query param on bundle import, increment each deploy
5. **TypeScript in inline scripts** — browsers don't support it, strip all `: type` annotations
6. **Premature start** — don't call `feedbackLayer.start()` on page load, only inside `startGame()`
7. **Verify served files** — curl the raw GitHub URL after deploy, don't trust local source

## References

- [Approach Ring Math](references/approach-ring-math.md)
- [GitHub Pages Deployment](references/github-pages-deploy.md)
