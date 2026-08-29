<!-- GENERICIZED: 22×{CLIENT}, 3×{RELATIONSHIP} | source: skills/software-development/{CLIENT} -->
---
name: {CLIENT}
description: Use when building a plugin game for the {CLIENT} framework.
---

# {CLIENT} Plugin Development

Build games that COMPOSE the {CLIENT} rhythm-typing framework (`createSession` + hooks), never extend it. {CLIENT} (monster battler) is the first plugin; this skill carries what that build verified against the real bundle.

## Source of truth
- Handoff package: `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}` (README, PLUGIN_GUIDE, API_REFERENCE, dist/)
- CANONICAL BUNDLE: `dist/game.js` (ES module). Import it — never `bundle.js`.
- PITFALL: the shipped `dist/*.d.ts` are STALE vs the bundle (missing `onWrongKey`, describe an older judge). Author against the bundle surface: grep `dist/game.js`, not the `.d.ts`. Full verified surface: `references/handoff-api-truth.md`.

## Loading the module
- `dist/game.js` is an ES module: `<script src="vendor/{CLIENT}" type="module">` then `import { createSession, DEFAULT_THEME } from "./vendor/{CLIENT}"`.
- A classic inline `<script>` CANNOT see module exports (symptom: `Uncaught ReferenceError: DEFAULT_THEME is not defined`).
- FeedbackLayer does NOT deep-merge themes. Build the theme by spreading `DEFAULT_THEME` and overlaying your colors; a partial theme silently breaks rendering.

## Session wiring
`createSession({ container, content, bpm (20-120), difficulty, hooks, feedback: { theme } })` returns `{ judge, feedback, beatMap, rawBus, normBus, songTime(), destroy() }`.

## COMPOSE hooks with the feedback layer — or the framework animations NEVER fire (root-cause finding)
The framework's keycap depressions, particle bursts, and combo display are NOT automatic. `createSession` passes hooks only to the judge; `FeedbackLayer` is never subscribed to judgment events. The ONLY path for framework feedback is the plugin forwarding. If your `onHit`/`onMiss` handle everything internally (combo, HP, counter, battle-canvas FX) and never call the feedback layer, then keycap animations / particles are dead from the first review onward — the user sees "keyboard animations missing" and every press looks dead.
Fix: forward to the feedback layer FIRST in each hook, then do plugin logic:
```js
onHit(evt){ try{ session.feedback.renderHit(evt.judgment, evt.key, evt.delta); }catch(e){} /* plugin logic */ }
onMiss(evt){ try{ session.feedback.renderMiss(evt.char, evt.expectedKey); }catch(e){} /* plugin logic */ }
onNoteStale(note){ try{ session.feedback.renderStale(note); }catch(e){} }
onCombo(count,mult){ try{ session.feedback.renderCombo(count,mult); }catch(e){} }
```
Verified FeedbackLayer method names (from the vendored bundle): `renderHit`, `renderMiss`, `renderStale`, `renderCombo` — there is NO `renderWrong` / `renderComboBreak` / `renderStreak`; only forward the four that exist. This restores the framework's animation layer AND the keyboard press feedback.

## Judge menu-gate (load-bearing sequence)
During menus (attack/capture selection), keystrokes must NOT reach timing judgment:
- Menu-enter: `session.judge.detach()` → stop your tick loop → plugin-owned keydown listener on `document`.
- Menu-exit ORDER MATTERS: `session.judge.setStartTime(performance.now())` → resume tick → `session.judge.attach(session.normBus)` LAST.
- The judge's `tick()` is NEVER called by the framework — the plugin owns the tick cadence. Stop calling it in menus, or `onNoteStale` fires for every expired note (each breaking combo).
- `onChar` has an early guard (correct key too early → silent return) but NO late guard (correct key after window → miss). Without the re-baseline above, the first correct key after menu-exit is a guaranteed miss.

## Audio + autoplay policy
- Gesture gate: init + `resume()` the AudioContext in the Start button handler BEFORE `createSession` — browsers block contexts until a user gesture, and a blocked context makes wall-clock sync unbounded.
- Load/decode music in PARALLEL, never await it before starting the session; degrade to silent on failure.
- Re-anchor `session.judge.setStartTime(performance.now())` when audio actually starts.
- The judge's beat-grid derives from your track manifest, never the decoded file.

## Demo UX & content (user-locked for {CLIENT})
Explicit user corrections from the playable-battle review — encode them, don't re-derive:
- **Layout**: judgment counter (PERFECT/GREAT/GOOD/MISS) pinned to the very BOTTOM; HP bars in the lower area right ABOVE the counter; the virtual keyboard snug against the TOP border.
- **Approach rings begin at menu-select**: the instant the attack/capture choice (1/2) is made — menu-exit → re-baseline → tick → attach → rings. No dead gap between menu and rhythm.
- **Real words, not key sequences**: a repeating `asdfjkl` loop was rejected outright. Content must be coherent words; shuffle/randomize the pool per battle.
- **D — round = one word; the pause lives in the menu seam** (supersedes the earlier space-joined design: spaces are notes at uniform density — no real breath — and a genuine pause was PUNISHED as a miss). Each round's content is ONE word; when the word's notes resolve (`judge.state.isComplete`), `nextRound()` returns to the menu (`openMenu()` — judge detached, tick held): the between-words pause is genuinely free, and the next word starts on a fresh attack choice. `closeMenu()` rebuilds the session for the new word (destroy → `createSession` with next word → locked exit order). Hoist the theme to `window.__{CLIENT}Theme` so `closeMenu` can reuse it on rebuilds.
- **C — soft-fail spaces (mandatory net under D)**: intra-round trailing spaces still exist; in `onMiss`/`onNoteStale`, when `note.key === ' '` suppress HP drain + combo break. Without C, the natural rest at a word's edge is a damage source.
- **Word pool**: hand-curated 3–6 letter grade-school words (~300 is plenty). macOS `/usr/share/dict/words` is full of dictionary filler (scientific names, obscure strings) — do NOT supplement with it; a 300-word curated CORE beats a 30k-word noisy dict.
- **GH Pages subpath PATHS — strip the leading `/` EVERYWHERE, use a repo-relative prefix.** The bug class: `user.github.io/repo/demo/index.html` — any absolute `/assets/...` or `/demo/...` ref resolves to the domain ROOT, not the repo, → 404. It passes local dev (127.0.0.1 serves workspace root, so `/assets` works) and only dies on the live subpath. Apply ONE `const RP = "../"` (from `demo/index.html` to repo root — assets are a sibling of `demo/`) and prefix EVERY asset ref with it: image loads (`loadImg` must do `i.src = RP + path`, not `"/" + path`), `<img>.src` faces and the resolve-screen monster, and audio `fetch(RP + track)`. The JSON `words.json` (same dir as the page) is plain `"words.json"`. Do a sweep for `/`-prefixed refs before any public push — a single missed absolute path (e.g. `loadImg` silently prepending `/`) breaks the whole asset layer on subpath. Enemy extends this: NEVER hardcode a label next to a swapped {CLIENT} — wire the name UI to the config (`enemyName.textContent = CFG.enemy.name`) or you ship a BULWARK {CLIENT} labeled GEOMITE; and pick a foe with a DISTINCT silhouette (tall/dense column vs a small round player reads as "big enemy" at child size — a similar-shaped foe reads as clash). Plugin owns the single stats source: hide {CLIENT}'s `statsDisplay` and treat `FeedbackLayer.stats` as an untrusted hidden duplicate, never read it.
- **The judgment counter IS the real score** — wire `onHit`/`onMiss` to it, not just the HP bars. There must be exactly ONE counter. {CLIENT}'s FeedbackLayer renders its OWN top-left `statsDisplay` (a `Perfect: N / Great: N…` element) — hide it after EVERY session creation (`session.feedback.statsDisplay.style.display = "none"` in both `startBattle` and the `closeMenu` rebuild), or the user sees a duplicate counter.
- **NOTE-GRID must be decoupled & typable — the #1 real-browser regression fix.** A fast note grid kills real input: at 120 BPM (500ms/letter) with single-word rounds, the moment a child pauses >1s between letters, the tick loop stales every pending note → the round auto-completes → the judge detaches into the menu → **typing genuinely goes dead mid-word** (user: "no longer registers key presses at all", exactly one key then nothing). Fix: keep the EXCITING music BPM (e.g. 120) as flavor, but set the session's `bpm` to a typable child pace (e.g. 60 = 1000ms/letter). The judge's note grid and the music are independent — `createSession({ bpm })` drives only the notes. Verify with a HUMAN-pace sim (see Headless verification).
- **Real-browser vs headless-sim gap is the acceptance gate.** A beat-perfect synthetic sim playing to VICTORY is NOT proof the demo works — a real child does not type on the 500ms grid. A fixed-CADENCE or ring-aware sim can pass while real (irregular, slower) typing fails. To reproduce end-user input, add a `?human=1` sim that types at irregular 700–1200ms gaps; it should land CLEAN hits (not stale-kill) before you claim a fix. Per the user's standing rule: don't announce a fix until real input works on the served page, not just a sim.
- **Menu FIRST, word SECOND (user-locked start flow).** Start Battle → show the FIGHT/CAPTURE menu IMMEDIATELY, create NO session until the player chooses. The word must NOT start playing on its own after Start (user: "there's still a word that the game starts playing right away upon pressing the start battle button"). `startBattle()` ends with `openMenu()` directly (session still null); `closeMenu()` creates the session when `!session || S.sessionDone`; `openMenu()` must null-guard `if (session) session.judge.detach()` — the judge is detached or nonexistent, so nothing can run during the choice.
- **Next-key feed at the bottom — RELOCATE the framework's indicator, don't hide+rebuild (user-corrected).** The "floating orange squares" were the framework's OWN `expectedKeyIndicator` (the orange keycap above the target key); the user explicitly asked to MOVE that same element to the bottom strip, "literal same thing from {CLIENT}" — NOT hide it and build a custom feed. Fix: `repositionExpectedKey()` pins `session.feedback.expectedKeyIndicator` to `position:fixed; bottom:58px` (between HP bars and the judgment counter). Two gotchas that make it hold: (1) the wrap's `transform:translateX(-50%)` creates a CONTAINING BLOCK for fixed descendants — `position:fixed` resolves against the wrap, not the viewport — so `document.body.appendChild(ind)` first; (2) the framework rewrites `ind.style.top/transform` every frame (its `updateExpectedKeyIndicator`), so per-frame re-assert is not enough — use a `[data-{CLIENT}]{position:fixed!important; bottom:58px!important; top:auto!important; transform:translateX(-50%)!important}` CSS pin (`!important` beats inline). The indicator already does letter-by-letter press recoloring, which is exactly what the user wanted.
- **Canvas draw order — shadows FIRST.** Drawing ground shadows AFTER the sprites paints the shadow layer OVER the monsters (user: "shadow layer on top of {CLIENT} layer"). Draw the shadow ellipses before `drawImage`, sprites after; same canvas, one frame.
- **Keyboard flush — the REAL root cause is the bottom anchor, and the fix must NOT touch framework internals.** The framework's `keyboardContainer` is created with `position:absolute; bottom:0; height:55%` — anchored to the WRAP'S BOTTOM, so it floats mid-screen no matter where the wrapper sits. The internal-override hack `#{CLIENT} > div[style*="bottom"]{bottom:auto!important; top:0!important}` makes `keyboardRect.top=0` PASS but DESYNCS the framework's animation space (keycap flashes vanish, particles land off-origin) — it crossed the composition boundary. CORRECTED ({RELATIONSHIP} spec A: own by placement, not surgery): keep the wrap `top:0; height:100vh`, and add a runtime aligner that measures the keyboard SVG's `getBoundingClientRect().top` and shifts `wrap.style.top` so keyboard top = 0. Framework keeps full animation ownership; the plugin only moves the wrapper. Diagnose layout claims by measuring, never by looking: see the console-gate pattern below. Also zero framework child margins/padding (`#{CLIENT} > *{margin:0!important; padding:0!important; border-radius:0!important}`).
- **FX telegraphs: rings, not dots — and cull hard.** Stray small dots floating near a monster read as noise (user: "yellow dot circle" — reported repeatedly). Enemy attack telegraphs must render as a proper CHARGING RING at the monster (expanding stroke arc), NOT 5× 3px hit-spark dots; player-hit sparks anchor ON the enemy body, never floating over the ring/keyboard field. Cull everything aggressively — dots ≤250ms, ring ≤400ms, crit ≤700ms; anything lingering reads as broken. `fx.spawn` per-kind durations are the cull contract.
- **Console hygiene:** a `data:,` favicon (`<link rel="icon" href="data:,">`) kills the `/favicon.ico 404` line the user sees in console.
- **Fallback label text must match config too.** The static HTML fallback (`<b id="enemyName">GEOMITE</b>`) flashed the wrong name BEFORE the JS wired it — keep the fallback text equal to `CFG.enemy.name` (or empty), not just the JS assignment.
Full detail: `references/demo-ux-word-content.md`.

## Completion detection (single convergence point)
`onSongComplete` is dead — detect completion yourself. Put ONE check in your tick loop:
```js
session.judge.tick();
if (S.phase === "battle" && session.judge.state.isComplete && !S.sessionDone) nextRound();
```
- **Re-read `state` AFTER `tick()`** — `tick()` mutates the cursor; a pre-tick `isComplete` snapshot stays false and a stale-path completion freezes the game (the late-final-letter bug: child types the last letter past the window → `onMiss` → cursor completes → nothing advances → hard freeze mid-round, hit in minutes).
- One tick-loop check catches every completion path (hit / miss / stale). Per-hook checks are redundant — the original bug was exactly a hook (`onMiss`) missing its completion check.
- Verify the stale path headlessly by letting a round's last note LAPSE (stop the sim, no press): the round must advance to the menu. A visible diag div (`phase / cursor / isComplete`) read from `--dump-dom` gives ground truth faster than console greps.

## Headless verification (Chrome)
- `decodeAudioData` HANGS headless (no audio device) — measure decode precision with ffmpeg exact PCM sample counts instead.
- `--virtual-time-budget` advances flows; add a timeout to image loads so a 404 can never block a promise.
- Verify via `--dump-dom` (class toggles, HP text) + screenshots; the browser_* tool blocks localhost/private addresses.
- Drive full flows headlessly with query hooks: `?autostart=1` clicks Start after load; `?autofight=1` dispatches keydown/keyup for `judge.getExpectedNote()` (and presses menu key `1` when the menu is open). **PITFALL: a FIXED-CADENCE interval is a false-stall machine** — after a session rebuild (D rounds), the fresh session has a +1500ms lead-in, so fixed-interval presses land EARLY and the judge's early guard silently swallows them → the sim appears to stall mid-battle while the game is fine. Use a RING-AWARE sim: poll fast (~120ms) but only press when `session.judge.getSongTime() - expected.time > -200` (note nearly in-window). With it, a full 12-round battle plays to victory headlessly.
- **Dispatch test keys on `document`, NOT `window`.** RawBus listens on `window` (capture) while the plugin's menu-selection listener is on `document` — a `window.dispatchEvent` test key reaches the judge but MISSES the document-level menu listener, so the menu never advances and the sim dies at intro. `document.dispatchEvent(new KeyboardEvent(...))` bubbles to BOTH.
- **CONSOLE GATE for layout claims (binding after the 5-round keyboard saga).** Screenshot judgment cannot arbitrate position claims; make the served page MEASURE them. Add `assertLayout()`: `getBoundingClientRect()` on the keyboard/keyFeed/menu vs the expected value, log `[{CLIENT}] check: keyboardRect.top=0 → PASS | keyFeed.bottom=58px → PASS`, run on `setInterval` (~3s) while the battle is live. NO "done" until that console line is green on the SERVED URL the user tests, mid-battle — a victory-screen screenshot or a headless sim proves nothing for layout. Reading the line: `"$CHROME" --headless ... --enable-logging=stderr --dump-dom URL 2>&1 | grep '\[{CLIENT}\]'`.
- **Gate hardening ({RELATIONSHIP} + binding): rAF-sample + state-aware + animation-layer probe.** A 3s interval can miss frames the child occupies; run the check on the rAF loop (~every 15th frame ≈ 4×/sec) AND keep a 2s `setInterval` fallback so headless console greps always see the line (virtual time doesn't advance rAF reliably). Make it state-aware: keyFeed asserts only when `S.phase === "battle"`; keyboard always. Add the animation-layer probe so the gate can't pass while the framework layer is dead: assert `session.feedback.renderHit && renderMiss && renderCombo` present, and assert the relocated `expectedKeyIndicator` is at `bottom:58px` via `getBoundingClientRect()`. Full green line that arbitrates this round: `keyboardRect.top=0 → PASS | keyFeed.bottom=58px → PASS | feedback.renderHit/Miss/Combo present → PASS | expectedKey.bottom=58px → PASS`.
- **Debug `position:fixed` inside a transformed wrapper:** a wrapper with `transform` becomes a containing block for `position:fixed` descendants — fixed coordinates resolve against the wrap, not the viewport (a pinned element at `bottom:58px` measured 362px from viewport bottom). Move the element to `document.body` before pinning.
- `--virtual-time-budget` breaks setTimeout/rAF interplay mid-flight (a delayed-keydown harness's 1600ms setTimeout never fired). Simulate late-presses by LETTING THE WINDOW LAPSE (stop the sim, no press) instead of delayed keydowns.
- When a flow stalls silently, add a `mark("step")` diagnostic: a tiny fixed-position div appended to body, `mark()` after each awaited step, then `--dump-dom` and read the marker to find the exact throw point (it pinned `createSession` as the thrower via `ReferenceError: DEFAULT_THEME is not defined`). Strip all marks before shipping — a regex strip can leave stragglers; `grep -c 'mark('` after stripping.

## References
- `references/handoff-api-truth.md` — verified bundle API surface and stale-.d.ts detail
- `references/demo-ux-word-content.md` — user-locked layout/content/pause decisions
- `references/audio-pipeline.md` — track manifest, exact durations, tempo, CC0/CC-BY-SA provenance rules
