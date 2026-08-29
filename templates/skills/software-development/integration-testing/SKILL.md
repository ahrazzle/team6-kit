<!-- GENERICIZED: 3×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/integration-testing/SKILL.md -->
---
name: integration-testing
description: "Integration tests for browser-based multi-component systems."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, integration, browser, pipeline, wiring, end-to-end]
    related_skills: [systematic-debugging, test-driven-development]
---

# Integration Testing

## Overview

Unit tests prove components work in isolation. Integration tests prove they work together. In multi-component browser systems (input bus → judge → feedback layer → DOM), passing unit tests can still hide broken wiring that only appears when the full pipeline runs.

**Core principle:** If your system has multiple components that pass data through each other, unit tests are necessary but not sufficient. You need at least one test that drives the entire pipeline from user input to visual output.

## When to Use

**Always when:**
- System has 3+ components in a pipeline (A → B → C → DOM)
- Components are tested individually but the system fails in production
- Timing matters (event-driven systems, animation frames, debouncing)
- DOM elements are created/destroyed across sessions (games, SPAs, widgets)
- User reports "it works in tests but not when I actually use it"

**Use this ESPECIALLY when:**
- You've fixed the same class of bug 3+ times
- Each fix reveals a new problem in a different place
- The user says "this is disgusting" or "still broken"
- Unit tests pass but the deployed version fails

## The Iron Law

```
NO DEPLOYMENT WITHOUT A FULL PIPELINE TEST
```

If you can't drive the complete flow from input to output in a test, you haven't proven the system works.

## Common Wiring Bugs That Unit Tests Miss

### 1. Timing Bugs
- A method is called AFTER the bus starts listening instead of BEFORE
- A timestamp is absolute (`performance.now()`) but compared against relative time (`note.time`)
- An animation frame callback fires before the previous frame finishes

**Test:** Drive the pipeline with a simulated input at a known time. Assert the output matches expected timing.

### 2. Teardown Sequence Bugs
- References are nulled in the wrong order (orphaned event listeners)
- A new instance is created without destroying the old one (DOM accumulation)
- A cleanup timer expires while the system is inactive (stale highlights)

**Test:** Run the system through a full lifecycle (start → play → end → restart). Assert no orphaned state persists.

### 3. DOM Accumulation
- Multiple SVG/canvas elements stack up because old ones aren't removed
- Event listeners from previous sessions fire into new sessions
- Absolute-positioned containers overlap because `destroy()` was never called

**Test:** After a full lifecycle, assert the DOM has exactly one instance of each element.

### 4. Bundle vs. Source Mismatch
- The served bundle doesn't match the source code
- Build artifacts (`.d.ts`, `.map`) are committed but the bundle isn't
- Cache-busting query parameters are missing or stale

**Test:** After deployment, fetch the served bundle and assert it contains the expected exports and methods.

## The Feedback Loop

Before deploying, create a test that drives the full pipeline:

1. **Simulate user input** — keyboard events, mouse clicks, touch
2. **Run the complete flow** — input → processing → judgment → rendering
3. **Assert on output** — DOM state, visual feedback, console logs
4. **Run the lifecycle** — start → play → end → restart
5. **Assert cleanup** — no orphaned listeners, no accumulated DOM, no stale state

## Browser-Based Testing Options

### Option A: Headless Browser (Playwright/Puppeteer)
```javascript
const page = await browser.newPage();
await page.goto('http://localhost:8000/demo.html');
await page.click('#start-btn');
await page.keyboard.press('a');
// Assert on DOM state
const comboText = await page.textContent('.combo-display');
expect(comboText).toBe('1');
```

### Option B: DOM Simulation (jsdom)
```javascript
import { JSDOM } from 'jsdom';
const dom = new JSDOM(`<!DOCTYPE html><div id="stage"></div>`);
global.document = dom.window.document;
global.window = dom.window;
// Initialize your system and drive it
```

### Option C: Console Log Capture
```javascript
const logs = [];
const originalLog = console.log;
console.log = (...args) => logs.push(args.join(' '));
// Run the system
console.log = originalLog;
// Assert on logs
expect(logs.some(l => l.includes('PERFECT'))).toBe(true);
```

### Option D: Screenshot Comparison (for visual bugs)
```javascript
await page.screenshot({ path: 'after-start.png' });
// Compare against reference image
```

## Lifecycle Test Pattern

For systems with start/stop cycles (games, media players, widgets):

```javascript
test('full lifecycle: start → play → end → restart', async () => {
  // Start game 1
  await startGame();
  await pressKey('a');
  await pressKey('b');
  expect(getCombo()).toBe(2);

  // End game 1
  await endGame();
  expect(getKeyboardCount()).toBe(1);
  expect(getEventListeners()).toHaveLength(1);

  // Start game 2
  await startGame();
  await pressKey('c');
  expect(getCombo()).toBe(1); // Not 3 — new game

  // Assert no accumulation
  expect(getKeyboardCount()).toBe(1);
  expect(getContainers()).toHaveLength(1);
});
```

## Deployment Verification

After pushing to a static host (GitHub Pages, Netlify, Vercel):

```bash
# Fetch the served bundle and verify it contains expected code
curl -s https://example.com/bundle.js | grep -c "expectedMethod"

# Fetch the served HTML and verify cache-busting
curl -s https://example.com/demo.html | grep "bundle.js?v="

# Check for console errors (if you have a headless browser)
npx playwright test e2e.spec.js
```

## Pitfalls

**Don't trust unit tests alone.** A system with 100% unit test coverage can still fail in production because the wiring between components is untested.

**Don't deploy without verifying the served bundle.** The bundle on the server may not match your local build. Always fetch and verify after pushing.

**Don't ignore the teardown sequence.** The order matters: stop bus → null references → destroy DOM → set inactive. Wrong order = orphaned events.

**Don't assume one test is enough.** A single integration test that drives the full pipeline catches 80% of wiring bugs. Add lifecycle tests for systems with start/stop cycles.

## Real-World Impact

From the {CLIENT} framework session:
- Unit tests: 46/46 passing (beat-map generator, event bus)
- Integration bugs found in production: 7+ (timing, DOM accumulation, orphaned listeners, bundle mismatch)
- Each bug required a separate push to fix
- A single integration test would have caught all of them before deployment

## References

- `references/{CLIENT}` — Concrete examples from the {CLIENT} rhythm-typing framework session
