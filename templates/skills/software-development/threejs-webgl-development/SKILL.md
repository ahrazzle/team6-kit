<!-- GENERICIZED: 1×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/threejs-webgl-development/SKILL.md -->
---
name: threejs-webgl-development
description: "Build WebGL/three.js browser apps: 3D scenes and worlds."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [threejs, webgl, browser, 3d, interactive, scene, kids]
    related_skills: [browser-game-development, static-webapp-verification]
---

# Three.js / WebGL Browser App Development

> Build interactive 3D browser apps — worlds, scenes, companions, explorable
> islands — with three.js and vanilla DOM chrome. Complements
> `browser-game-development` (which is Canvas 2D / SVG / TypeScript and explicitly
> excludes WebGL). Route all three.js work here.

## When to use

- Any three.js / WebGL scene: interactive worlds, creature companions, 3D data
  views, orbit-camera demos, kid apps with a "world instead of menus" UX.
- Architecture walls that recur: offline-first (vendor three.js locally, no CDN),
  mobile performance budgets (<100 draw calls), context-loss resilience,
  self-hosted fonts, no third-party SDKs.

## Vendoring three.js locally (offline-first)

No CDN on the hot path — a kid app must work offline after first load:

```bash
npm init -y && npm install three@0.160.0
cp node_modules/three/build/three.module.js assets/lib/three.module.js
```

Then an importmap in the page (no bundler needed):

```html
<script type="importmap">
{ "imports": { "three": "../assets/lib/three.module.js" } }
</script>
<script type="module" src="main.js"></script>
```

Self-host fonts the same way (Baloo 2 / Fredoka for kids; DM Serif only on the
adult marketing surface), preloaded in `<head>`. Zero runtime-fetched assets.

## Critical three.js pitfalls (each cost a real debugging cycle)

### 1. `renderer.context` does not exist in r160 (silent boot death)

`renderer.context` is gone. `renderer.getContext()` exists, but under headless
SwiftShader the GL context is NOT an EventTarget — `gl.addEventListener` throws
`TypeError: gl.addEventListener is not a function`. The context-loss events fire
on the **canvas element** itself, and that works across real GPU + software
rasterizers:

```js
canvas.addEventListener("webglcontextlost", (e) => { e.preventDefault(); this.lost = true; }, false);
canvas.addEventListener("webglcontextrestored", () => { this.lost = false; this.renderer.compileAsync(this.scene, this.camera); }, false);
```

### 2. Chained `.scale.set().position.setY()` returns a Vector3, not the mesh

`new THREE.Mesh(...).scale.set(...).position.setY(...)` — `scale.set()` returns
the Vector3, so `.position` is undefined → `Cannot read properties of undefined
(reading 'setY')` deep inside a builder. One-liner chains on newly created
objects are a trap. Write explicit statements:

```js
const canopy = new THREE.Mesh(geo, mat);
canopy.scale.set(2.6, 2.0, 2.6);
canopy.position.setY(4.6);
```

### 3. `readPixels` returns all zeros on a painted canvas

three.js defaults to `preserveDrawingBuffer:false` — the buffer is cleared after
compositing, so `gl.readPixels` in a QA harness reads zeros and you'll chase a
phantom "blank canvas" bug. The screenshot is the paint evidence:
`Page.captureScreenshot` → PNG → PIL pixel-bucket analysis (count sky/water/land/
creature color families; assert the expected composition, not a uniform screen).

### 4. Same-name variables across scope in a render loop

`const c = this.creature.position;` then later `c.position.y = ...` — `position`
is already the Vector3, so `c.position` is undefined. In `_tick`, keep one alias
and mutate `c.x / c.y / c.z` directly; rotation lives on the GROUP
(`this.creature.rotation.y`), not the position vector.

### 5. Camera drag vs tap vs hold — one input state machine

A kid app needs tap (poke), drag (orbit), and hold (feed) on one surface.
Disambiguate in `pointerdown/move/up`:
- `drag.moved = true` once movement exceeds ~14px → orbit only, never a tap.
- Hold timer (~650ms) fires feed; set `_suppressTap` so the pointerup is not
  ALSO interpreted as a tap.
- Clear the hold timer on move/up; `clearTimeout` on pointercancel.

### 6. Raycast the world you actually see

Raycast hits can be occluded by a domed terrain mesh: the island dome sits
between camera and creature, so a tap at the creature's screen position hits
`island` first. Order matters and the terrain is a valid target — assert via the
app's own raycast probe before trusting a tap coordinate. Project world→screen
for test taps: `cam.position.clone().copy(worldPos).project(cam)` →
`x=(v.x*0.5+0.5)*innerWidth, y=(-v.y*0.5+0.5)*innerHeight`.

## Patterns that work well

### Instant-alive loading (kid apps: never a blank screen)

Stage-0: a pure CSS/SVG creature (breathing keyframes, blinking eyes, pointer-
following pupils via CSS vars) alive on cold load with zero JS. three.js mounts
behind it; on the first rendered frame the SVG crossfades out over ~400ms — the
swap reads as the creature "waking up", not a page change. Audio unlocks on the
first user gesture (autoplay rules).

### Mobile performance budget

- `renderer.setPixelRatio(Math.min(devicePixelRatio || 1, isMobile ? 1.5 : 2))`
- No shadow maps; blob shadows (transparent circle under the creature) are cheap
  and read fine at kid scale.
- Low-poly primitives + flat shading; a whole island scene lands ~20 draw calls
  (budget: <100).
- `setAnimationLoop` for the render loop; `resize` sets size with `false` to
  avoid resetting the CSS size.

### Content as a discriminated union (data, not code forks)

When units of content have different interaction shapes (fact card vs math
challenge vs vocab word), model them as ONE JSON array discriminated on `kind`
and branch the UI ONCE: `if (pack.kind === "challenge") {...} else {...}`.
New kinds are additive — no per-subject forks, no new engine paths. Keep
`verification` / `source` / `readingLevel` fields on every unit so the content
bank carries its own honest ledger.

### Compiled content lags the source-of-truth ledger

When the content bank is owned by a SEPARATE teammate (a research/QA ledger like
UNIT-BANK.md), your compiled `packs.json` goes stale the moment that ledger
updates — even if the visible facts don't change (e.g. `pending` → `verified`
with a pinned source URL). That is a DATA re-run, not a code change: recompile
from the current ledger, then verify against the SERVED bytes
(`curl` the served packs.json and assert status/counts), never the disk copy —
QA checks the served artifact, not your report or your local file. Keep
`verification`/`source` in lockstep so "0 pending" is true of what actually
ships.

### Design tokens may land AFTER the build — audit, don't assume

In the team pipeline the design-token spec can arrive post-build as the "hard
reference." When it does, run a systematic compliance sweep against the SERVING
app and report the mismatch list rather than assuming conformance. The checks
that burn real rounds: font-size floors (nothing under 22px for kid-readable
copy — buttons, prompts, feedback, journal, onboarding; chip/badge labels are
usually exempt chrome but flag the exemption), ≥56px tappable targets, and
silhouette rules (creature growth = decoration only — body scale stays 1.00,
"same creature, more decorated, never bigger"). Verify each fix in the live
browser, not by grep.

## Verification

- Static localhost server (`python3 -m http.server PORT`), then real-browser
  CDP verification — see `static-webapp-verification` →
  `references/headless-chrome-cdp-harness.md` (working Chrome flags: SwiftShader
  trio, `--remote-allow-origins=*`, fresh `--user-data-dir`; error capture with
  stack traces; tap simulation; screenshot pixel-bucket proof).
- Zero `Runtime.exceptionThrown` / `Log.entryAdded` errors at the END of the
  interaction suite — check once after all clicks, not just on load.
- Expose a harmless QA hook (`window.__world = world`) during verification so the
  harness can probe raycasts and live positions; strip it at ship.

## References

- `references/kid-world-mvp-architecture.md` — worked example: {CLIENT} island MVP (scene structure, pack schema, storage seam, hold-to-feed input machine)
