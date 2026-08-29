<!-- GENERICIZED: 2×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/event-bus-architecture/SKILL.md -->
---
name: event-bus-architecture
description: "Layered event bus for real-time input systems."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [events, architecture, input, timing, precision, real-time]
    related_skills: [test-driven-development, systematic-debugging]
---

# Event Bus Architecture

## When to Use

- Building input systems where timing precision matters (rhythm games, musical instruments, accessibility tools)
- Designing layered event processing pipelines
- Any system where raw events need normalization before consumption
- Systems where multiple consumers need to react to the same input events

## Core Pattern

```
Raw Source → Raw Bus → Normalized Bus → Judge/Consumer → Plugin Hooks
```

### Layer 1: Raw Bus
- Captures events from the OS/hardware source
- **Captures timestamp at the moment the event fires** — inside the raw handler, not downstream
- Exposes raw event objects with metadata (key, code, modifiers, timestamp)
- Decoupled from downstream via structural typing (any object with `onEvent(fn)` works)

### Layer 2: Normalized Bus
- Consumes raw events
- Normalizes for layout, modifiers, shift/caps lock
- Filters out key repeats — only genuine new presses are emitted
- Produces clean character events with both normalized char and raw event reference

### Layer 3: Judge/Consumer
- Consumes normalized events
- Evaluates against expected state (beat-map, game state, etc.)
- Maintains cursor position, combo, score
- Emits judgment events to subscribers

### Layer 4: Plugin Hooks
- Fan-out registry dispatches events to all registered plugins
- Each plugin receives the same events
- Plugins render their own scenes or react to judgments

## Critical Rule: Capture Timestamps at Source

The single most important timing guarantee in the framework.

**Capture `performance.now()` inside the raw DOM/event handler itself** — the first handler that runs when the OS delivers the event. Propagate that timestamp through all downstream layers. Never re-capture time later in the pipeline.

**Why:** Event-loop jitter between raw capture and later handlers adds milliseconds of variance. For ±25ms precision (rhythm games), even 5-10ms of jitter is significant. Normalization layers add processing time; capturing there measures processing speed, not input timing.

## Design Principles

1. **Immutability at infrastructure layer** — Beat-maps are read-only. The judge advances a cursor *over* the beat-map, never mutates it.
2. **Separation of concerns** — Input, feedback, and game logic are decoupled layers. The feedback layer is shared infrastructure; plugins emit judgments, the feedback layer renders them.
3. **Wrong keys are silently ignored** — In typing-rhythm hybrids, wrong keys don't advance the beat-map, don't break combo, don't trigger feedback. Only the correct key + timing matters.
4. **Hybrid rendering** — SVG for crisp accessible keycaps with ARIA labels, Canvas overlay for particle effects and screen shake. Stacked with `pointer-events: none` so keystrokes reach the input layer.

## Common Pitfalls

- **Canvas sharing conflict** — If two plugins draw to the same 2D context, they overwrite each other. Fix: stack independent canvas layers with `pointer-events: none` on plugin canvases.
- **Feedback layer theme conflicts** — Direct DOM/canvas access from multiple plugins causes theme conflicts. Fix: the feedback layer accepts a **theme descriptor** (color palette, particle style, animation intensity) rather than raw access.
- **Missing event flow in contract** — Plugin hooks need an emitter-to-consumer pipeline so plugins know what drives their hooks. Define the full flow: `RawBus → NormalizedBus → BeatClockJudge → PluginHooks`.
- **Timing integration gaps** — `setStartTime()` must be called BEFORE the bus starts listening, or the first keypresses have wildly wrong timestamps. Unit tests pass but the full pipeline breaks because they test components in isolation.
- **Double-start duplicate listeners** — Clicking Start twice creates two judges, two normBuses, two rawBuses, all logging and responding. Guard: `if (gameActive) return;` at the top of `startGame()`.
- **Negative radius in animation loops** — Ripples/effects with future start times or expired lifetimes can produce negative radii. Clamp: `Math.max(0, now - r.startTime)` and `Math.max(0, ...)`.

## Web Deployment Pitfalls

### The "Committed ≠ Served" Gap

**Pitfall:** Fixing local source, announcing "live," user tries, bug persists because the served bundle differs from local source.

**Root cause:** Build pipelines, CDN caching, browser caching, and deployment lag all decouple "committed" from "served."

**Rule:** After every push, verify fixes in the **actual served file** — not local source, not commit history.

```bash
# Verify fix is in the SERVED bundle (not local source)
curl -s https://raw.githubusercontent.com/user/repo/main/dist/bundle.js | grep "the_fix"
curl -s https://user.github.io/repo/dist/bundle.js | grep "the_fix"
```

**If it's not in the served file, it doesn't exist.** The user executes the served bundle, not your local source.

### Browser Cache Invalidation

**Pitfall:** Browser caches stale JavaScript bundles. User hard-refreshes, still gets old code.

**Fix:** Add a version query parameter to asset imports. Increment on every deploy.

```html
<!-- Without cache busting — browser may serve stale bundle -->
<script type="module" src="./dist/bundle.js"></script>

<!-- With cache busting — forces fresh fetch -->
<script type="module" src="./dist/bundle.js?v=3"></script>
```

Also add cache-control meta tag:
```html
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">
```

### TypeScript in Inline Scripts

**Pitfall:** TypeScript annotations (`: Type`) in inline `<script>` blocks break browsers silently. Browsers serve HTML as-is; TypeScript must be transpiled.

**Rule:** Never put TypeScript type annotations in inline `<script>` blocks. Use `.ts` files bundled by esbuild/webpack, or write plain JS in HTML.

```html
<!-- BREAKS — browsers don't understand TypeScript -->
<script>
  const preemptTimes: Record<string, number> = { easy: 1500 };
</script>

<!-- WORKS — plain JavaScript -->
<script>
  const preemptTimes = { easy: 1500 };
</script>
```

## References

- [{CLIENT} Event Bus Implementation](references/{CLIENT}) — concrete example for rhythm-typing game
