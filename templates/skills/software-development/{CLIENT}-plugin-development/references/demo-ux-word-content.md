<!-- GENERICIZED: 9×{CLIENT} | source: skills/software-development/{CLIENT} -->
# Demo UX & word-content detail ({CLIENT} playable battle, {CLIENT})

## The user's five corrections (verbatim intent, from the review round)
1. Move UI elements: perfect/great/good/miss counter to the very bottom, health bars to the lower area of screen right above it, virtual keyboard snug against the top border.
2. Approach rings begin immediately before the user presses 1 or 2 for attack/capture (i.e. rings start the moment the menu selection is made — no dead gap between menu and rhythm).
3. Don't repeat `asdfjkl` — randomize the key sequence at the very least.
4. Keys must form coherent words, not gibberish — otherwise the typing practice is meaningless. A dictionary-word compilation is acceptable.
5. Pause between words so the child senses real words being typed.

## Round-3 corrections (the "Good:/Bad:" live-test review)
Good (kept): key presses register (after the note-grid fix), duplicate counter gone, music playing.
Bad (fixed in this round):
- **Menu-first start flow** — a word was playing immediately on Start, with attack/capture buttons only appearing ~1s later. Fix: `startBattle()` ends with `openMenu()` directly and creates NO session; `closeMenu()` creates the session on `!session || S.sessionDone`; `openMenu()` null-guards `if (session) session.judge.detach()`.
- **Next-key feed — RELOCATE the framework's indicator, don't hide+rebuild (user-corrected).** The user asked to move the framework's own floating orange expected-key indicator to the bottom — "literal same thing from {CLIENT}" — NOT hide it and build a custom feed. `repositionExpectedKey()` pins `session.feedback.expectedKeyIndicator` at `position:fixed; bottom:58px`. Two gotchas: (1) the wrap's `transform` is a containing block for `fixed` descendants → `document.body.appendChild(ind)` first or `bottom:58px` measures against the wrap (was 362px from viewport); (2) the framework rewrites `ind.style.top/transform` every frame → a per-frame re-assert isn't enough, use `[data-{CLIENT}]{position:fixed!important; bottom:58px!important; top:auto!important; transform:translateX(-50%)!important}` CSS pin. The indicator already does letter-by-letter press recoloring — exactly the "literal same thing from {CLIENT}" ask. Keep the in-keyboard keycap highlight too (eye-to-key mapping); the bottom strip is the "child sees the next word forming" surface.
- **Shadow layer over sprites** — ground shadows drawn AFTER `drawImage` paint over the monsters. Fix: draw shadow ellipses FIRST, then sprites.
- **Keyboard flush — corrected after root-cause round: NO internal overrides, runtime aligner.** The `div[style*="bottom"]` hack made `keyboardRect.top=0` PASS but desynced the framework's animation space (the composition-boundary violation). Keep the wrap `top:0; height:100vh` and add `alignKeyboardToTop()` on an interval: measure the keyboard SVG's `getBoundingClientRect().top`, shift `wrap.style.top` by `(0 - svgTop)`. Framework keeps animation ownership; plugin moves only the wrapper. Measured result: `keyboardRect.top=0 → PASS` WITHOUT the hack.
- **Favicon 404 in console** — `<link rel="icon" href="data:,">` kills it.
- **Fallback label** — static HTML `<b id="enemyName">GEOMITE</b>` flashed the pre-swap name before JS wiring; fallback text must equal `CFG.enemy.name` (or be empty), and JS assigns it at battle start.

## Layout implementation
- `#counter` → `position:absolute; bottom:10px` (pinned to very bottom)
- `#hud` (HP bars) → `bottom:120px` (lower area, above the counter)
- `#{CLIENT}` (keyboard) → `top:0` + internal margin/padding zeroed (flush against top border)
- `#combo` float → `bottom:200px` (above HP, below monsters)
- Reset counter text to "0" on battle start; increment in `onHit` (perfect→#cPerfect, great→#cGreat, good→#cGood) and `onMiss` (→#cMiss). The counter is the real score, not garnish.

## Ring timing
Rings must begin at menu-select, not at session creation. In `closeMenu()` after the load-bearing exit order:
```
session.judge.setStartTime(performance.now());
startTick();
session.judge.attach(session.normBus);
S.phase = "battle";
session.feedback.startRings && session.feedback.startRings();  // rings begin NOW
```

## Word pool generation (proven recipe)
- Source: hand-curated CORE list (~300 grade-school words, 3–6 letters, lowercase alpha).
- DO NOT merge in macOS `/usr/share/dict/words`: it produced 33k words of scientific names (sicyos, truvat, tekke), proper nouns, and dictionary filler. Every attempt to filter it (vowel-run bans, consonant-run bans, q/x/z bans) still leaked noise. The curated CORE is the only quality anchor; a small clean pool beats a huge noisy one.
- BPM mapping: `bpm / 5 ≈ WPM`; at 120 BPM a 5-letter word ≈ 24 WPM — child-friendly zone.

## Word pauses — D/C model (supersedes the space-joined design)
The first version joined 14 random words with spaces, trusting `BeatMapGenerator`'s "spaces become notes" behavior. QA proved that WRONG:
1. Spaces are notes at the SAME uniform density as letters (500ms at 120 BPM) — no breath exists.
2. A real pause is PUNISHED: the space note's window closes → `onMiss`/`onNoteStale` → combo break + enemy attack. The natural rest the user asked for was a damage source.

The locked fix (both plugin-side, zero framework surface):
- **D (primary)**: each round's content is ONE word (`S.roundWords[i]`, no spaces). When the word's notes resolve (`session.judge.state.isComplete`), `nextRound()` increments the round and calls `openMenu()` — the pause between words lives in the menu seam where the judge is detached, so it is genuinely free. Next word starts on a fresh attack choice (FIGHT/CAPTURE).
- **closeMenu() rebuild**: when `S.sessionDone` (or no session yet, menu-first flow), destroy the old session and `createSession({ content: S.roundWords[S.roundIndex], ... feedback: { theme: window.__{CLIENT}Theme } })` — hoist the theme to a window var in `startBattle` so the rebuild can reuse it. Then the locked exit order (setStartTime → tick → attach LAST) + rings.
- **C (mandatory net)**: `onMiss(evt)` / `onNoteStale(note)` suppress HP drain + combo break when `note.key === ' '` — trailing spaces at a word's edge are survivable.

## Note-grid decoupling (the input-dead regression fix)
Root cause of "no longer registers key presses at all": 120 BPM (500ms/letter) + single-word rounds → a child pausing >1s between letters lets `tick()` stale every pending note → round auto-completes → judge detaches into menu → typing genuinely dead mid-word.
Fix: session `bpm: 60` (1000ms/letter — typable child pace) while the music stays at 120 BPM as mood. The judge's note grid and the music are independent; `createSession({ bpm })` drives only the notes. Product reframe (contract §5): "typing game with rhythm", not "music-locked rhythm game" — the audio-clock calibration machinery is dead weight once notes don't derive from the audio clock.

## Words.json fetch — GH Pages subpath-safe
`words.json` lives NEXT TO `index.html`; fetch it with `fetch("words.json")` (relative). An absolute `/demo/words.json` resolves to `user.github.io/demo/words.json` under Pages → 404. Relative-to-page works at server root AND under the `/repo/demo/` subpath. This class of bug passes local preview and only appears on the live subpath — the verification gate must probe the served URL's fetch.

## Repo-relative asset prefix (all assets, not just words.json)
`loadImg` prepending `"/" + path` breaks EVERY asset on the GH Pages subpath. Use ONE `const RP = "../"` (from `demo/index.html` to repo root — `assets/` is a sibling of `demo/`) and prefix every asset ref: `i.src = RP + path` inside `loadImg`, `RP + CFG.enemy.{CLIENT}` for the HUD faces and the resolve-screen monster, `fetch(RP + CFG.track)` for audio. Sweep for `/`-prefixed refs before any public push — a single missed absolute path breaks the whole asset layer on subpath.

## Root-cause round findings ({CLIENT} evening)
- **Framework animations were dead by NON-INVOCATION, not CSS.** The demo's hooks handled `onHit`/`onMiss` entirely on their own and never called `session.feedback.renderHit/renderMiss/renderStale/renderCombo` — so keycap depressions, particles, and the combo display NEVER fired, from the first review to the root-cause round. The plugin guide's manual wiring spells it out: the plugin must FORWARD judgment events to the feedback layer. Verified method names from the vendored bundle: `renderHit(judgment,key,delta)`, `renderMiss(char,expectedKey)`, `renderStale(note)`, `renderCombo(count,mult)` — there is NO `renderWrong`/`renderComboBreak`/`renderStreak`. Forward FIRST, plugin logic after; wrap in try/catch so a framework hiccup can't break the battle.
- **The `div[style*="bottom"]` hack was the desync.** Crossing the composition boundary (CSS override of framework internals) made the layout assert pass while the framework's animation coordinates went stale. The held fix: runtime `alignKeyboardToTop()` shifting `wrap.style.top` so the keyboard SVG top = 0 — plugin moves the wrapper only.
- **Debugging a `position:fixed` element that ignores `bottom`:** a transformed ancestor (`transform:translateX(-50%)` on the wrap) becomes a containing block for fixed descendants. `appendChild` to `document.body` fixes the coordinate space.
- **The gate earned its keep by naming the failure** (expectedKey.bottom=362px → FAIL) where a screenshot "looks fine" would have passed. Keep the gate in the page even after a round passes — it is the drift canary for the next layout change.

## Verification technique (headless full-flow)
- Query hooks in the demo page: `?autostart=1` clicks Start after 300ms; `?autofight=1` runs a ring-aware interval that presses menu key `1` when `S.phase === "menu"` and dispatches keydown/keyup for `judge.getExpectedNote().key` when in battle, only when the note is in-window (`getSongTime() - expected.time > -200`) — a fixed 260ms cadence lands EARLY after D-rebuilds (fresh +1500ms lead-in) and the judge's early guard silently swallows it (false stall).
- `?human=1`: types at irregular 700–1200ms gaps to reproduce real child input; the acceptance gate is that it lands CLEAN hits (no stale-kill), not that a perfect-cadence sim wins.
- Headless run: `--headless=new --autoplay-policy=no-user-gesture-required --virtual-time-budget=60000 --dump-dom "…?autostart=1&autofight=1"` then grep `id="resolve" class="on"`, `id="cGood">`, `id="enemyHpText"`.
- `--virtual-time-budget` breaks setTimeout/rAF interplay (a delayed-keydown harness's 1600ms setTimeout never fired) — simulate late presses by LETTING THE WINDOW LAPSE (stop the sim, no press), then read the phase via a diag div.
- The `mark()` diagnostic: append a tiny div (`#diag`, fixed bottom-left, 10px mono), call `mark("step")` after each awaited step in the async start path, dump-dom, read the marker chain. In this session it isolated the throw to `createSession` (`ReferenceError: DEFAULT_THEME is not defined`) after images/audio had all succeeded. Strip all marks before shipping; `grep -c 'mark('` after the regex strip (a regex can leave stragglers that hard-fail the page with `mark is not defined`).
