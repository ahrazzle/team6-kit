<!-- GENERICIZED: 3×{CLIENT} | source: skills/software-development/static-webapp-verification/SKILL.md -->
---
name: static-webapp-verification
description: "Verify static web apps via headless DOM and screenshot QA."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [qa, testing, playwright, static-app, browser, verification]
---

# Static Web App Verification (headless)

## When to use

You built (or were handed) a static HTML/web artifact — a training tour, report,
dashboard, mockup, or any single-page app that runs from `file://` or a plain
static host — and you must prove it actually works before shipping. Use this
instead of (or in addition to) exploratory `browser_*` QA: it is deterministic,
re-runnable, and catches the class of bug that manual clicking and DOM reads miss.

Overlap note: `dogfood` covers manual exploratory QA with the browser toolset.
This skill is the programmatic harness — better when you have many views ×
settings to cover and need repeatable assertions.

## The core lesson

**Automated DOM assertions can be fully green while the app is silently broken.**
In one real session: 50/50 checks passed, yet three features were dead on a fresh
load (a reveal button, a step-advance button, and map pins) because a text
transform had wiped their event listeners — and a double-transform ("Forma Forma
Build") read fine to a regex but looked broken to a human. The cross-checks that
caught all three:
1. Drive **real interaction clicks** (not just presence assertions) in the
   **default mode** of the app — the mode where transforms/renders actually run.
2. **Screenshot + vision review** of real renders. Vision sees what assertions
   don't: controls below the fold, listener-dead buttons, mangled compound words.

## Workflow

### 1. Get a browser
`playwright-core` + the cached Chromium headless shell (macOS):
```
mkdir -p /tmp/pwtest && cd /tmp/pwtest && npm init -y >/dev/null && npm i playwright-core --no-fund --no-audit
CHROME=$HOME/Library/Caches/ms-playwright/chromium_headless_shell-<ver>/chrome-headless-shell-mac-arm64/chrome-headless-shell
# find it:  find ~/Library/Caches/ms-playwright -name headless_shell
```
Launch with `chromium.launch({ executablePath: CHROME })`. Load the artifact via
`file://` — keep app scripts as plain `<script>` tags (not ES modules) so there
is no CORS restriction on `file://`.

### 1b. Zero-install alternative: headless Chrome CLI (canvas pages, localhost)

When the target is a localhost/private address that the interactive browser
tooling refuses, or you want a deterministic re-runnable check of a CANVAS-heavy
page, drive the system Chrome binary directly — it executes JS, runs rAF loops,
and dumps real DOM:

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --disable-gpu --no-sandbox --virtual-time-budget=8000 \
  --dump-dom "http://127.0.0.1:PORT/page.html" 2>/dev/null > /tmp/dom.html
"$CHROME" --headless=new --disable-gpu --virtual-time-budget=9000 \
  --window-size=1400,3000 --screenshot=/tmp/page.png \
  "http://127.0.0.1:PORT/page.html" 2>/dev/null
```

- `--virtual-time-budget` fast-forwards async `boot()`/image loads so dynamic
  content is present in the dump.
- **Have the page write render-completion markers into the DOM** — a stats line
  ("rendered 51 monsters × 8 cols"), tile counts, a recipe-identity line. Parsing
  those from the dumped DOM proves canvases PAINTED, not just that HTTP 200.
- Capture console errors: `--enable-logging=stderr 2>&1 | grep -i uncaught` —
  a fetch SyntaxError kills the whole script block and the dump silently shows
  the static shell.
- Save the screenshot to the project `OUTPUTS/` as a durable review artifact.

**Pitfalls learned (real session):**
- A page under a subdirectory + relative `fetch("data.json")` resolves to
  `/subdir/data.json` → 404 → entire boot dies. Use root-absolute paths
  (`/assets/...`) on the spike server.
- One JS error in a render function (e.g. a bad selector) kills ALL subsequent
  renderers because nothing is try/catch'd — check console errors BEFORE trusting
  any counts in the dump.
- Verify dynamic DOM markers with a tolerant regex (`id="check"[^>]*>(.*?)</span>`)
  — nested spans defeat naive `grep -o`.
- **A background `http.server` can wedge — and even a clean restart dies between turns.** Session handle dies (poll → not_found) while the PID still listens: `nc -z` succeeds but curl returns 000, and restart fails with "Address already in use" — kill by `lsof -ti:PORT`, confirm "port free". BUT a background-terminal server is SESSION-SCOPED: it dies when the turn ends, so a server the user tests across turns silently goes down ("server is down now. please run again" — happened twice in one session, each time the old PID was wedged AND a fresh background start died at the next turn boundary). For a user-facing localhost server, run a **detached double-fork daemon** with pidfile + idempotent start: `scripts/detached_static_server.py <root> [port]` survives session teardown, and re-invoking it is a no-op while the port is live. Full sequence in `references/headless-chrome-cdp-harness.md`.
- **Grep Chrome stderr through a noise filter first.** `CVDisplayLink`,
  `address_sorter`, `sqlite_persistent`, `FromSockAddr` lines are harmless
  macOS headless noise — filter them before trusting an error grep.

### 2. Instrument error capture
```js
const errors = [];
page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
page.on("pageerror", e => errors.push(String(e)));
```
Assert `errors.length === 0` at the END, after all interactions — an error partway
through a session is easy to miss if you only check once.

### 3. Per-view render pass via hash deep-linking
If the app supports `#viewId` navigation (add it if it doesn't — it is free and
enables this whole pattern), iterate every view id and assert a content marker:
```js
for (const v of VIEWS) {
  await page.evaluate(x => { location.hash = "#" + x; }, v);
  await page.waitForTimeout(40);
  check("renders " + v, await page.locator("#main h1").count() === 1);
}
```
A missing marker means a block renderer threw mid-view. This catches exceptions
in seconds that manual clicking takes minutes to find.

### 4. Real interactions in the default mode
After toggling a setting back and forth, RE-VERIFY the interactive pieces in the
mode a fresh visitor lands in. Dead-listener bugs live in the transform path:
click reveal buttons, advance steppers, flip toggles, and assert the state change.

### 5. Matrix pass
For settings that persist (theme, naming mode, …): run the full view list × each
setting combination, e.g. `views × light/dark × modeA/modeB`. Loop and count
failures rather than stopping at the first.

### 6. Persistence across reload
Set a preference by clicking its control, `page.reload()`, and assert it was
re-applied. If the app restores the preference in an early inline `<script>`
(before first paint), that also verifies no flash-of-wrong-mode.

### 7. Visual cross-check
Take screenshots and have vision read them. Target a specific element by clipping
to its bounding box:
```js
const box = await page.locator(".acc-titlebar").boundingBox();
await page.screenshot({ path: "titlebar.png", clip: { x: box.x-8, y: box.y-8, width: box.width+16, height: box.height+16 } });
```
Vision caught, in one session: a theme toggle pushed below the fold by a long nav
(a "persistent chrome" control the user would never find), the dead listeners,
and the double-transform — all invisible to the assertion pass.

### 8. Deterministic layout assertions — the console gate

Screenshot-judgment arbitration fails on repeat: a layout fix is announced as verified, the user re-tests, and the same element is still misplaced — a keyboard flush was re-requested **five times** in one real session, each round "verified" by a screenshot that couldn't actually arbitrate a position claim. When a LAYOUT claim is the deliverable, make the served page measure itself:

```js
function assertLayout(){
  const kbd = document.querySelector("#wrap [style*='bottom']");
  const r = kbd.getBoundingClientRect();
  const ok = r.top <= 4;
  console.log(`[app] check: keyboardRect.top=${Math.round(r.top)} → ${ok ? "PASS" : "FAIL"}`);
}
setInterval(assertLayout, 3000);   // runs while the app is live
```

- Announce rule: **no "done" until the console line is green on the SERVED URL the user tests, mid-interaction** — never a victory/end screen, never a headless-sim result, never a screenshot judgment. A measurable success criterion kills the announce-if-broken cycle by construction.
- Read the line headlessly: `"$CHROME" --headless=new --enable-logging=stderr --dump-dom URL 2>&1 | grep '\[app\]'`.
- This is the same determinism discipline applied to audio/note-grid timing — apply it to any UI seam that has burned more than one user ask.
- **Gate hardening (rAF-sample + state-aware + probe the layer).** A 3s interval can miss the frames the user actually occupies. Run the check on the rAF loop (~every 15th frame ≈ 4×/sec) AND keep a 2s `setInterval` fallback so headless console greps always see the line (virtual time doesn't advance rAF reliably). Make it state-aware: layout elements that only exist during an interaction (e.g. a battle feed) assert only while that state is active; persistent elements assert always. Probe the FUNCTIONAL layer, not just geometry — assert the animation/feedback methods exist (`fb.renderHit && fb.renderMiss`) and the relocated element is at its expected offset, so a green `top=0` can't mask a dead animation layer.
- **Debug `position:fixed` that ignores your coordinates:** a wrapper with a `transform` (e.g. `translateX(-50%)`) becomes a containing block for `position:fixed` descendants — fixed coordinates resolve against the WRAP, not the viewport (a pinned element at `bottom:58px` measured 362px from the viewport bottom). Fix: `document.body.appendChild(el)` before pinning, and use a `[data-pin]{position:fixed!important; ...}` CSS rule (`!important` beats the framework's per-frame inline style rewrites).


## Known failure modes this harness catches (real cases)

- **innerHTML-based text transform kills listeners.** Rewriting `el.innerHTML`
  with a transformed copy destroys the event listeners added at render time.
  Fix: transform text nodes IN PLACE with a `TreeWalker` over `SHOW_TEXT`, or
  transform at render time before attaching listeners. Assert interactions still
  work after any transform runs.
- **Non-idempotent find/replace double-transforms.** A rule `Build → "Forma
  Build"` re-matches its own output ("Forma Forma Build"). Fix with negative
  lookbehind (`(?<!Forma\s)\bBuild\b`) or by wording the canonical source so
  output never re-matches. Add a guard assertion: scan all rendered views for the
  doubled compound.
- **"Persistent chrome" control pushed below the fold.** A pinned toggle in a
  sidebar gets pushed out of view once nav grows. Make the nav scroll internally
  (`overflow-y: auto; flex: 1`) and assert the control's bounding box is inside
  the viewport.
- **`textContent` vs CSS text-transform.** `textContent` returns the pre-CSS
  string ("Autodesk Forma" not "AUTODESK FORMA"), so assertion regexes must
  match the source string, not the rendered case.
- **`getComputedStyle` on a missing element** throws `parameter 1 is not of type
  'Element'` — pick a selector that exists on the current view, or guard it.
- **Browser caching serves stale bundle after deployment.** App works on
  localhost but breaks on GitHub Pages / static hosting. The browser caches the
  old `bundle.js` and serves it even after a new deploy. Fix: add a cache-control
  meta tag `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">`
  and a version query parameter on the bundle import
  (`import { ... } from './dist/bundle.js?v=3'`). Bump the version on each deploy.
  Verify by checking the served bundle URL contains the expected version and the
  response has `cache-control: no-cache`.
- **Root-absolute paths vs GH Pages subpath — the fix INVERTS per host.** The
  1b pitfall above ("use root-absolute paths on the spike server") is only true
  on a server that serves the workspace root. On a GH Pages project repo the
  page lives at `user.github.io/repo/demo/`, so `/assets/...` resolves to the
  DOMAIN root → 404, while a page-relative `fetch("words.json")` and a
  repo-relative `const RP = "../"` prefix (from `demo/` to the repo root)
  resolve correctly on BOTH hosts. Sweep for leading-`/` refs before any public
  push — including inside loader helpers: one `i.src = "/" + path` inside a
  `loadImg()` silently breaks the whole asset layer on subpath while passing
  local preview.
- **Stale screenshot receipt.** A verification screenshot is only evidence if
  its mtime is ≥ the source it documents. One QA pass rejected an entire fix
  round because the PNG was 9 minutes OLDER than the `index.html` it claimed to
  show (it depicted the pre-fix state). Before presenting a fix round as
  visually verified: re-shoot from the live page, check `ls -la` timestamps of
  artifact vs source, and never reuse a screenshot captured earlier in the
  session.

## Template

`templates/headless-qa-harness.js` — known-good starter harness (error capture,
per-view pass, interaction checks, matrix loop, persistence, screenshots). Copy
and adapt; do not hand-type the boilerplate each time.

For WebGL/canvas or localhost pages (interactive tooling refuses private
addresses), skip playwright: drive system Chrome directly over CDP with
`scripts/cdp_browser_probe.py` — see `references/headless-chrome-cdp-harness.md`
for the working flag set (Chrome >= 152 needs `--remote-allow-origins=*`, fresh
`--user-data-dir` per run, SwiftShader trio for WebGL, `--no-proxy-server`),
stack-trace error capture, localStorage seeding order, and why `readPixels`
returns zeros on three.js canvases (screenshots are the paint evidence).

## References

- `references/headless-chrome-cdp-harness.md` — CDP WebSocket verification recipe for WebGL/localhost pages: working Chrome flags, error capture, tap simulation, paint proof
- `scripts/cdp_browser_probe.py` — re-runnable probe: launch headless Chrome, load URL, report console issues + diagnostics + screenshot
- `scripts/detached_static_server.py <root> [port]` — detached double-fork daemon for a localhost static server that must survive session teardown (pidfile + idempotent start)
- `references/{CLIENT}` — real bug log from {CLIENT} framework ({CLIENT}), with root causes and fixes for 10 bugs
- `references/rhythm-game-patterns.md` — core architecture patterns for rhythm games: event flow, approach rings, timing windows, common pitfalls
- `references/multi-note-approach-highway.md` — osu!/Stepmania-style multi-note approach rings: rendering, color/opacity ramps, difficulty scaling
- `references/visual-state-cleanup.md` — why stop() must clear ALL visual state (DOM/SVG), not just tracking data structures
