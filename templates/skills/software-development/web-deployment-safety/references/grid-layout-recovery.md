<!-- GENERICIZED: 1×{CLIENT} | source: skills/software-development/web-deployment-safety/references/grid-layout-recovery.md -->
# Grid layout escapes + git recovery — measured case study ({CLIENT} gateway, v6.7)

Real debugging transcript from converting a two-panel gateway to a deliberate three-column
composition (terminal spine between two doors). Both failure modes below cost multiple
deploy cycles; the fixes are verified.

## Failure 1: grid row ballooned to 1624px (intended 900px)

Symptom: the right-hand column's content sat ~870px below the left column's; the grid row
was `grid-template-rows:1624.5px` instead of `~100vh`.

Root cause (two compounding bugs):

1. **Percentage height on an auto-sized grid row loops.**
   `.gw-divider{position:absolute;top:-10%;height:120%}` — with the row height
   auto-sized, the divider's `120%` forced the row taller, which fed the percentage
   again → row grew to 1624px and the divider itself measured 1949px.
   Fix: `height:100%` + `.gw-hero{overflow:hidden}`.

2. **The spine + divider were nested INSIDE the left half** (a restructure bug), so
   `hero.children` was `[field, half digi]` — the spine and Physical half were not
   direct grid children, and the grid sized the row from the wrong content.
   Fix: reorder to `field → half digi → gw-spine → gw-divider → half phys` all as
   direct children of `.gw-hero`.

Verification that the fix landed (1600×900 viewport):

```
gridTemplateRows: 900px
kids: ,half,gw-spine,gw-divider,half
digiMid:450 physMid:450 spineMid:450   <- all three centered on the same midpoint
digiTop:195 physTop:181 diff:-14       <- stacks aligned
```

Debugging path that worked: scan `hero.querySelectorAll('*')` for elements taller than
expected (found `gw-divider h=1949`), then check `hero.children` order — both pointed at
the same structural bug.

## Failure 2: anchor/div imbalance after panel conversion

Converting `<a class="half">` panels to `<div>`s left a stray `</a>` (the old panel
closer) and an unclosed `<div>`; the browser tolerated it but the layout broke subtly.
Count pairs in the hero block:

```
div opens:19 closes:18 balance:+1
a opens:2 closes:3 balance:-1   <- extra </a> before </section>
```

Fix: remove the stray `</a>`, add the missing `</div>`; re-count until 19/19 and 2/2.

## Git recovery from a corrupted rebase

A v6.2 "revert + fixes" commit lost the favicon and system.css fixes during
`git pull --rebase` conflict resolution (`git checkout --theirs` picked the wrong side;
a later `git rebase --continue` failed with "could not read log file").

Working recovery:

```bash
git reset --hard origin/main                      # known-good remote state
git checkout 07ac049 -- index.html digital/index.html physical/index.html \
  system.css gateway.css digital.css physical.css favicon.svg   # intended base
# re-apply only the intended delta, then VERIFY markers before committing:
bash scripts/predeploy-guard.sh index.html        # guard must pass
grep -c 'foot-divisions' index.html               # must be 0 (removed)
grep -c 'flex-direction:row' system.css           # must be 1 (footer brand)
```

A clean `git status` after conflict resolution is NOT proof of a correct tree —
verify the actual markers.

## Lessen the pain next time

- Commit small deltas; the corrupt-commit happened because one commit mixed a revert
  with three independent fixes.
- Keep the pre-deploy guard in the repo root and run it before EVERY push, not just
  before production deploys — it catches wrong-tree state early.
- When a rebase goes sideways (stuck `rebase-merge` dir, "could not read log file"),
  abort and rebuild directly rather than continuing to fight the rebase.

## Failure 3: adopting an accidental layout without user-intent ground truth (v6.8)

After the 3-column spine fix landed, the room (this agent included) endorsed adopting the
accidental 3-column render as a deliberate redesign based on the screenshot — then the
user corrected: the screenshot they had liked was NOT 3 columns. It was the 2-half
layout where the terminal and sourcing pipeline had gained generous **vertical space**.
The structure they wanted was the 2 halves staying sacrosanct, with each flavour element
as its own column INSIDE its half.

The corrected structure (user spec, verified working):

```
.gw-hero { display:grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); }  /* 2 halves */
.half    { display:grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); }  /* 2 inner cols */
/* Digital half = [.half-stack content | .term-col terminal]
   Physical half = [.pipe-col pipeline | .half-stack content] */
```

- The half boundary never breaks; the flavour columns carry the vertical room the user
  liked. Mobile: halves stack, flavour columns hidden.
- Carry the vertical-centering work over from the previous structure (both `.half-stack`
  midpoints at the same Y — check with `getBoundingClientRect()`).
- **The click-split contract must survive the move.** After relocating the terminal back
  inside the Digital half, re-verify in a browser: terminal click → focus only, pathname
  unchanged; the "Enter the division" anchor → navigates. Same regression class as the
  original giant-anchor bug.

Lesson: when a user says "I liked that screenshot", confirm whether they liked the
STRUCTURE or the SPACE before building a structural redesign. Ground-truth the served
DOM and the user's words; a render that looks good is not a design mandate.
