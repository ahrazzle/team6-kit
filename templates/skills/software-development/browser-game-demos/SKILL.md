<!-- GENERICIZED: 1×{AMOUNT}, 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/browser-game-demos/SKILL.md -->
---
name: browser-game-demos
description: "Build browser game demos with Canvas/SVG animations."
version: 1.0.0
author: {RELATIONSHIP}, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [game-dev, canvas, svg, animation, browser, demo, es-modules]
    related_skills: [p5js, sketch]
---

# Browser Game Demos

> Build interactive browser-based game prototypes with HTML5 Canvas, SVG, and modern animation patterns. Covers the workflow from local dev server to GitHub Pages deployment.

## When to Use

- Building typing games, rhythm games, or any keyboard-interactive browser demo
- Need particle effects, ripples, spring physics, or specular highlights
- Deploying ES module-based frontends to GitHub Pages
- Prototyping game feedback systems (combo, judgment, scoring)

## Prerequisites

- Python 3 (for local HTTP server) or Node.js
- ES modules (`<script type="module">`) — browsers block these over `file://`
- A bundler for production builds (esbuild recommended)

## Workflow

### 1. Local Dev Server (Required)

ES modules don't work over `file://` due to CORS. Always serve:

```bash
python3 -m http.server 8765
# or
npx serve .
```

Verify with `curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/demo.html` — expect 200.

**Preview pane caveat**: If `open_preview`/`read_preview` fails repeatedly, switch to terminal verification (curl + browser console checks) rather than retrying the same failing tool.

### 2. Bundle for Production

```bash
npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm
```

### 3. GitHub Pages Deployment

`dist/` is commonly gitignored. If your bundle lives there, the deployed page will silently fail (blank screen, no errors).

**Fix**: Remove `dist/` from `.gitignore` before committing the bundle, or build as a post-commit hook.

**Check**: Always verify the deployed URL returns 200 for both HTML and bundle:
```bash
curl -s -o /dev/null -w "%{http_code}" https://user.github.io/repo/dist/bundle.js
```

## Demo UX Patterns

### Onboarding Overlay
- Show on first load with step-by-step instructions
- Include a CTA button that both dismisses AND starts the game
- Allow Space to dismiss
- Keep it dismissible — don't force re-reading

### Character Sequence Display
- Render the beat-map as a row of keycap-shaped boxes
- Current target: highlighted, scaled up, glowing
- Hit keys: green
- Missed keys: red
- Upcoming keys: dimmed

### Layout
- **Top-bottom orientation** for complex UIs (keyboard stage on top, controls below)
- Side-by-side wastes vertical space and compresses the play area

### Controls That Work
- Every input field must be read live when the action fires — don't cache values at init
- Single CTA button (e.g., "Start Game") preferred over multi-step flows
- Regenerate state on each action (don't reuse stale data)

## Animation Patterns

### Ripple Emanation (Highest Impact)
Concentric circles expanding outward from a point — like dropping a stone in water. Perfect for keypress feedback.

```typescript
interface Ripple {
  x: number; y: number;
  startTime: number; duration: number;
  maxRadius: number; color: string;
  opacity: number;
}

// Render multiple concentric rings with easing
private renderRipples(ctx: CanvasRenderingContext2D): void {
  // For each ripple, draw 3 rings at progress, progress+0.1, progress+0.2
  // Use easeOutQuad for natural deceleration
  // Add radial gradient fill for inner glow
}
```

**Key insight**: Perfect hits get a second, larger ripple for extra satisfaction. The ripples should be visible across the keyboard surface, not just at the point of impact.

### Spring-Physics Key Depression
Keys should overshoot their target depth and bounce back — mimicking a mechanical switch.

```css
@keyframes {CLIENT} {
  0%   { transform: translateY(0) scale(1); filter: brightness(1); }
  30%  { transform: translateY(4px) scale(0.95); filter: brightness(0.85); }
  60%  { transform: translateY(2px) scale(0.97); filter: brightness(0.9); }
  80%  { transform: translateY(3px) scale(0.96); filter: brightness(0.88); }
  100% { transform: translateY(2px) scale(0.96); filter: brightness(0.88); }
}
```

Re-trigger by removing the class, forcing reflow (`element.getBoundingClientRect()`), then re-adding.

### Specular Highlight Sweep
A diagonal streak of light sweeping across the surface — brief (400ms), subtle, gives physical depth.

```typescript
const gradient = ctx.createLinearGradient(startX, 0, startX + streakWidth, height);
gradient.addColorStop(0, 'transparent');
gradient.addColorStop(0.5, `rgba({AMOUNT},${alpha})`);
gradient.addColorStop(1, 'transparent');
```

### Confetti Burst
Rectangular particles burst outward on celebration events. Use sparingly (50% density) to avoid overwhelming the scene.

## Rendering Architecture

### Hybrid SVG + Canvas
- **SVG layer**: Keyboard (crisp keycaps, ARIA labels, CSS animations)
- **Canvas overlay**: Particles, ripples, specular sweeps (stacked with `pointer-events: none`)
- **z-index**: SVG keyboard (1) < Canvas (2) < Combo display (3) < Plugin UI (4) < Expected-key indicator (5) < ARIA live region (10)

### Judgment-Driven Feedback
```typescript
switch (judgment) {
  case 'perfect':
    emitRipple(cx, cy, 'perfect');      // Large vivid ripple
    emitBurst(cx, cy, 'perfect');       // Full particle burst
    emitBurst(cx, cy, 'confetti', 0.5); // Confetti at half density
    addEdgeGlow(primary, intensity, 300);
    addShake(shakeIntensity * 0.5, 150);
    emitSpecularSweep();                 // Light sweep
    break;
  case 'great':
    emitRipple(cx, cy, 'great');        // Medium ripple
    emitBurst(cx, cy, 'great', 0.7);    // Moderate burst
    addEdgeGlow(secondary, intensity * 0.5, 200);
    break;
  case 'good':
    emitRipple(cx, cy, 'good');         // Small ripple
    emitMutedFlash(cx, cy);             // Muted feedback
    break;
  case 'wrong':
    emitRipple(cx, cy, 'wrong');        // Tiny red ripple
    emitWrongKeyBurst(cx, cy);          // Deliberately underwhelming
    shakeKey(keyId);                    // No screen shake
    break;
}
```

## Pitfalls

1. **ES modules over file://** — Always use a local server. The browser console will show CORS errors.

2. **Stale input values** — Read `.value` at action time, not at page load.

3. **Port conflicts** — If `Address already in use`, kill the old process: `lsof -ti :8765 | xargs kill -9`

4. **Spring animation won't re-trigger** — Must remove class, force reflow, then re-add.

5. **Silent GitHub Pages failure** — If `dist/` is gitignored, the deployed page loads but does nothing. No console error.

6. **Preview pane timeout** — If `read_preview` fails 3+ times with identical errors, switch to terminal verification. Don't retry.

## See Also

- `references/animation-patterns.md` — Detailed recipes for ripple, particle, spring, and specular effects
