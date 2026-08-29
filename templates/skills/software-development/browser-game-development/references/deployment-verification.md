<!-- GENERICIZED: 7×{CLIENT} | source: skills/software-development/browser-game-development/references/deployment-verification.md -->
# Deployment Verification Pattern

## Problem

After pushing fixes to GitHub, the served files may differ from local source due to:
1. GitHub Pages deployment lag (2-3 minutes)
2. Browser caching of old versions
3. Git not actually containing the rebuilt bundle

## The Pattern That Destroys Trust

1. Fix code locally
2. Commit and push
3. Announce "fixed and pushed"
4. User tests → still broken
5. Everyone confused because "the code is correct"

This pattern repeated 4+ times in the {CLIENT} project. Users lose confidence rapidly.

## Correct Workflow

```bash
# 1. Rebuild the bundle from current source
npx esbuild src/index.ts --bundle --outfile=dist/bundle.js --format=esm

# 2. Commit and push
git add -A && git commit -m "Fix: ..." && git push

# 3. Wait 3 minutes for GitHub Pages propagation

# 4. Verify in the RAW GitHub source (what GitHub Pages serves)
curl -s https://raw.githubusercontent.com/USER/REPO/main/dist/bundle.js | grep "fix_pattern"

# 5. Or verify in the GitHub Pages URL
curl -s https://USER.github.io/REPO/main/dist/bundle.js | grep "fix_pattern"

# 6. Only announce "fixed" AFTER verifying the served file contains the fix
```

## Why This Matters

- **GitHub Pages propagation**: Takes 2-3 minutes. During this time, users see stale content.
- **Browser caching**: Even after propagation, browsers may cache old versions. Cache-busting (`?v=3`) forces new fetch.
- **Git vs served mismatch**: The bundle in `dist/bundle.js` may not have been rebuilt after source changes. Always rebuild before commit.

## User Communication

When deploying fixes:
1. "Fix pushed, waiting 3 minutes for propagation..."
2. "Verified the fix is in the served bundle."
3. "Hard refresh (Cmd+Shift+R) or try incognito to bypass cache."

## Cache Busting Strategies

```html
<!-- In HTML head -->
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">

<!-- Versioned bundle import (bump version on each fix) -->
<script type="module">
  import { Game } from './dist/bundle.js?v=3';
</script>
```

## Deterministic Layout Assertions (the anti-screenshot gate)

When a layout/position claim has failed more than once ("keyboard not against top" burned four asks), screenshots stop arbitrating. Put a console assertion IN the page and make "done" conditional on it:

```js
function assertLayout(){
  const out = [];
  const kbd = document.querySelector("#{CLIENT} [style*='bottom']") || document.querySelector("#{CLIENT} svg");
  const r = kbd.getBoundingClientRect();
  out.push(`keyboardRect.top=${Math.round(r.top)} → ${r.top <= 4 ? "PASS" : "FAIL"}`);
  // state-aware: only assert the feed while a word is actually in flight
  if (S.phase === "battle"){
    const kf = document.getElementById("keyFeed").getBoundingClientRect();
    const dist = Math.round(innerHeight - kf.bottom);
    out.push(`keyFeed.bottom=${dist}px → ${Math.abs(dist - 58) <= 10 ? "PASS" : "FAIL"}`);
  }
  console.log("[{CLIENT}] check: " + out.join(" | "));
}
// rAF-sampled, not a 3s timer — a timer can miss the broken frames a player occupies
let n = 0;
function gate(){ if ((++n % 15) === 0) assertLayout(); requestAnimationFrame(gate); }
requestAnimationFrame(gate);
```

Binding rules that came out of the {CLIENT} verification-loop failure:
1. The assertion runs on the **served URL the user actually tests** (e.g. `127.0.0.1:8770/demo`), mid-battle — never the local file, never the victory screen.
2. **State-aware**: feed/position assertions fire only in the phase they apply to; the keyboard check runs always.
3. A fix is not announced until the console line is green on that URL. Green over a broken frame is worse than no gate — it erodes trust the same way a stale screenshot did.

## Human-Pace Sims (why "works headless" lies)

A fixed-cadence autofight sim types every note before the timing window closes, so it NEVER exercises the stale/miss paths a real player hits. When a bug report says "input dies mid-word", repro with:
- a **human-pace sim**: irregular 600–1200ms gaps between presses, dispatched on the real document/window path (`document.dispatchEvent(new KeyboardEvent("keydown", {key}))`); or
- a **ring-aware sim**: poll at 120ms, press only when the expected note's `delta > -200` (the window has nearly opened).

Also remember: under `--virtual-time-budget`, `setTimeout` chains and rAF interplay can stall — prefer real-time headless (`--timeout=N`) for timer-dependent flows, and check the served page's console output (grep `[{CLIENT}]`), not just the source.

## {CLIENT} Lessons

- **Two bundle filenames (bundle.js vs game.js)**: the demo imported `./dist/game.js` but builds wrote `dist/bundle.js`, so the served game.js stayed stale after every "rebuild + push" — even when the rebuild itself was correct. Docs also pointed at the 404 bundle.js, breaking a forker's first command. Lesson: one canonical bundle filename; grep the demo's actual import before writing build commands/docs; verify served bytes at the exact filename.
- **TypeScript in inline scripts**: The demo.html had `const preemptTimes: Record<string, number>` which worked on local server but broke on GitHub Pages. Browsers don't parse TypeScript.
- **Bundle not rebuilt**: Source was fixed but bundle.js wasn't rebuilt before commit. Users saw old code.
- **Multiple "fixed" announcements**: Each fix was announced as live before verifying the served file. Trust eroded.
- **Orphaned events between games**: Old judge/bus not torn down properly, causing MISS events to leak into the next game.
- **Keypresses during lead-in**: With a 3-second lead-in, early keypresses registered as MISS instead of being ignored.

## Verification Checklist

Before announcing a fix is live:
- [ ] Bundle rebuilt from current source
- [ ] Code committed and pushed
- [ ] Waited 3 minutes for propagation
- [ ] Verified fix pattern exists in served file via curl
- [ ] No TypeScript annotations in inline scripts
- [ ] Tested in incognito/private window
- [ ] Checked browser console for errors
