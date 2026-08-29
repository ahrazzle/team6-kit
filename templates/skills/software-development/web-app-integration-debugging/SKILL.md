<!-- GENERICIZED: 5×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/web-app-integration-debugging/SKILL.md -->
---
name: web-app-integration-debugging
description: "Debug web app integration, cache, and event lifecycle bugs."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, web, integration, browser, console, cache, lifecycle]
    related_skills: [systematic-debugging, test-driven-development, dogfood]
---

# Web App Integration Debugging

## Overview

Debugging web applications where visual inspection is unavailable, the gap between "fix committed" and "user sees fix" needs explicit verification, or multi-component integration bugs hide between unit-tested components.

**Core principle:** Verify served files match source before debugging. Browser caching causes more "broken" reports than actual bugs.

## When to Use

- User reports "the fix isn't working" after a verified push
- Unit tests pass but integration is broken
- No visual access to the rendered page (preview pane broken, headless)
- Console shows orphaned events, duplicate listeners, or lifecycle bugs
- Multi-component systems where data flows through several layers

## Phase {CLIENT}: Verify Served Files Match Source

**ALWAYS do this first.** Browser caching is the #1 cause of "fix not working."

```bash
# Compare served file hash with git source
curl -s https://example.com/file.js | md5
git show HEAD:file.js | md5

# Check cache headers
curl -sI https://example.com/file.js | grep -i "cache-control\|last-modified\|age"
```

GitHub Pages: `cache-control: max-age=600` (10 min). If hashes differ, wait. If they match, user's browser is caching.

**Cache-busting for future updates:**
```javascript
// Add version query parameter
import { X } from './bundle.js?v=3';
```
```html
<!-- Add no-cache meta tag -->
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">
```

**User-side bypass:** Open incognito/private window.

**The verification fetch itself must be cache-busted.** CDN/edge caches serve stale CSS/HTML too. "Stale bytes vs live bytes" disputes waste rounds when agents curl a bare URL and disagree. Every verification request appends a cache-buster:

```bash
curl -s "https://site.com/gateway.css?cb=$(git rev-parse --short HEAD)"
# or a fixed per-deploy tag that the served HTML actually references: ?v=521b04
```

An agent's curl is only authoritative if it carries the current versioned ref. When resolving a 404-vs-200 dispute, probe the **EXACT URL written in the served `@font-face` / `src` / `href`** — never a bare path that happens to exist (a cached page can hold an old manifest and hit a 404 window).

**Versioned asset references in production HTML — not just images.** When HTML changes but a stylesheet filename doesn't, browsers hold the old CSS against the new HTML for the whole cache TTL (4h on common configs) → run-on text, invisible containers, "weird text" reports that aren't in the source. Every asset class that carries layout (CSS, JS) must get `?v=<deploy-sha>` bumped in the SAME commit as the change. Images-only versioning is the classic half-fix.

## Phase {CLIENT}: Console-Driven Diagnosis

When you can't see the page, the browser console reveals everything:

1. **Inject logging at pipeline boundaries** — log every event with timestamps
2. **Look for patterns in sequences** — orphaned events between state transitions indicate lifecycle bugs
3. **Check for JS exceptions** — `IndexSizeError`, `TypeError` pinpoint exact failing lines
4. **Count event sources** — two identical events per action = duplicate listeners

**Key insight:** Events appearing *between* state transitions (e.g., `MISS pressed="t"` right after `Game Over`) are almost always orphaned handlers from the previous state, not current logic bugs.

## Phase {CLIENT}: Integration Test Pattern

When unit tests pass but the wire is broken, write a headless test driving the full pipeline:

```typescript
// Real components, not mocks
const rawBus = new RawBus();
const normBus = new NormalizedBus(rawBus);
const judge = new BeatClockJudge(beatMap, { difficulty }, hooks);

// Wire together
normBus.onChar((evt) => judge.onChar(evt));
normBus.start();
rawBus.start();

// Set start time BEFORE bus starts listening
const startTime = performance.now();
judge.setStartTime(startTime);

// Inject events at specific times
rawBus.inject('h', 'KeyH', 'keydown', targetTime);
```

This catches timing, ordering, and lifecycle bugs that unit tests miss.

## Common Bug Patterns & Fixes

### Duplicate Event Listeners
**Symptom:** N starts = N identical events per action.
**Fix:** Null old references. Use closure capture guard (see below).

### Timing Clock Divergence
**Symptom:** Two clocks drift apart (e.g., tick loop uses local `startTime`, judge uses `_startTime` set 300ms later).
**Fix:** Set all clocks once, before processing begins, referencing the same variable.

### Negative Animation Values
**Symptom:** `IndexSizeError: radius provided (-59.77)` in canvas rendering.
**Cause:** Animation start time set in future (`performance.now() + 80`) → negative elapsed → negative radius.
**Fix:** `const elapsed = Math.max(0, now - startTime);`

### Stale Visual State
**Symptom:** Visual highlights persist after game ends.
**Cause:** Cleanup clears tracking Map but not DOM elements.
**Fix:** Call `keyboard.reset()` that clears all visual state, not just internal tracking.

### Orphaned Event Handlers (Closure Capture)
**Symptom:** Old judge fires MISS events into new game.
**Cause:** Hooks reference shared `judge` variable, not the specific instance.

```javascript
// BUG: old hooks fire into new game
function startGame() {
  judge = new BeatClockJudge(beatMap, { difficulty }, {
    onMiss: (key, expectedKey) => debugPlugin.onMiss(key, expectedKey),
  });
}

// FIX: capture specific instance
function startGame() {
  const newJudge = new BeatClockJudge(beatMap, { difficulty }, {
    onMiss: (key, expectedKey) => {
      if (judge !== newJudge) return; // Bail if replaced
      debugPlugin.onMiss(key, expectedKey);
    },
  });
  judge = newJudge;
}
```

### Giant Anchor Wrapping a Panel
**Symptom:** Clicking anywhere in a card/panel navigates, despite a `stopPropagation` handler on the inner element.
**Cause:** The whole panel is an `<a href=...>`; `stopPropagation` does NOT cancel anchor default navigation — only `preventDefault()` does, and clicks on children hit the anchor first.
**Fix:** Structural — make the panel a `<div>` and keep only the real CTA as the anchor (or `preventDefault()` on inner clicks). "Verified in code" is not enough: reproduce the click on the LIVE URL, because the DOM that shipped may differ from the source that was reviewed.

### Flash-Guard Inversion (invisible critical UI)
**Symptom:** A flagship element (hero terminal, main CTA) is reported "missing" — markup present in HTML, hidden by CSS.
**Cause:** `.no-js .term{opacity:0;visibility:hidden}` gates visibility on a JS-runtime class removal that races or never fires. Visibility is inverted: visible only if JS runs, instead of visible by default with JS as enhancement.
**Fix:** Serve critical UI visible by default (strip `no-js` from the served HTML server-side, or don't gate on it at all). JS only adds behavior (auto-type, commands) — never the thing that reveals the UI.

### Hollow Container Classes (class present, no treatment)
**Symptom:** QA greps the class name in markup AND CSS, both pass, but the element renders as a flat rectangle.
**Cause:** The class exists but carries only `padding` — no border-radius/background/shadow. Grep verifies the fix was *attempted*, not that it renders. Media-query overrides sitting after the base rule can also make a full rule read as padding-only.
**Fix:** The gate checks computed style (border-radius + background + shadow present) or a live-browser pixel read — not class-name presence. Put contrast floors in tokens (`--line-strong` ≥1.5:1 vs background) so "can't see the outline" is a failing check, not a subjective finding.

### Cross-Page Copy Accident (clobbered root)
**Symptom:** A page suddenly renders as a different page (e.g. a division page at the site root) — often after a "small" sync/copy.
**Cause:** `cp digital/index.html index.html` — a copy aimed at the wrong target.
**Fix:** Pre-deploy guard in the deploy stage: grep the root HTML for markers that identify it (`.gw-hero`, `#askterm`) and fail the deploy if absent. Test the guard both ways (passes on the real root, refuses the clobber). Same class as any `cp` between pages — per-page marker checks catch those too.

### Baseline Swap Reverts Approved Fixes
**Symptom:** After an environment rollback/restore, previously-approved fixes silently disappear ("we fixed this twice already").
**Cause:** Restoring a baseline commit reverts everything after it — including approved fixes that were never promoted.
**Fix:** When swapping environments, record what each target's baseline contains (the approved-fixes list), and fold re-approved fixes back into the restored baseline BEFORE the next build — not after the user notices. The deploy-target lock should record what a target's baseline contains, not just which commit.

## Phase {CLIENT}: Verify Before Announcing

**Never announce "fixed" until verified in served file:**
```bash
curl -s https://raw.githubusercontent.com/user/repo/main/dist/bundle.js | grep -c "fixPattern"
```

If the fix pattern isn't in the served file, the user can't see it yet.

## References

- `references/web-app-debugging.md` — Extended cache verification, console debugging recipes, and pattern catalog.
- `references/served-reality-incidents.md` — Concrete "verified in code / broken in served reality" incident catalog ({CLIENT} site, 2026-08): giant-anchor click, flash-guard inversion, hollow container classes, cross-page copy, stale CSS vs new HTML, contested 404/200 — plus the curl commands that ended each dispute.
