<!-- GENERICIZED: 1×{AMOUNT}, 10×{CLIENT}, 11×{RELATIONSHIP} | source: skills/autonomous-ai-agents/project-handoff-takeover/references/{CLIENT}-{CLIENT} -->
# Worked Example — {CLIENT} / {CLIENT} Takeover ({CLIENT})

Concrete instance of this skill. Incoming: user said "take it across the finish line, make an execution plan, report for review" for `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}/wrk/3ft6/previousclaude`.

## The artifact
- {CLIENT} = "{CLIENT}" education program (money, incentives, first-principles reasoning, psychology).
- {CLIENT} = skill-mapping webapp; simulation engine **done and validated** (158 skills, 12 branches, 72 activities, 15 states; validated vs 5 synthetic lifetimes). Interface was an engineer's sketch.
- Also in workspace: `3rdF.html` landing page (34KB) + `skill_activity_outcome_loop.png/svg`.

## Recon findings (verified on disk, not from docs)
- **No git repo.** Build brief's step 1 (`git init` before redesign) never ran. Old prototype uncommitted = one-way door.
- `handoff/design/` **empty** — the handoff's design step (step 2) never started. The documented sequence stopped exactly at the handoff line (last writes Aug 5).
- `handoff/` contained three docs: `01-DATA-CONTRACT.md` (locked data layer), `02-DESIGN-BRIEF.md` (design brief), `03-BUILD-BRIEF.md` (build rules + done-definition = 15 states list + verify gates).
- 16 prototype version folders (`v1` … `v16 freeflow`, `webapp v7 (self verify)`, `handoff prepped`) = user-made backups. Untouched.
- One absolute-path reference to old location (`/Users/{RELATIONSHIP}/Documents/{RELATIONSHIP}/...`) in a markdown doc only — portability clean.
- Claimed "npm run verify green" in brief — flagged as *to be re-run*, not assumed.

## Plan shape that worked
- P0 Baseline: re-run verify+validate (record real output) → `git init` + baseline commit → one-way door closed.
- P1 Design: handoff design step never ran → {RELATIONSHIP} designs from brief bound to data contract → {RELATIONSHIP} arch review → **user gate: does a stuck skill read as an instruction (remedy beside the number)?**
- P2 Build (brief's de-risking order): type the contract → design system → skill detail → daily loop → orientation → guarded paths.
- P3 Verification: verify green after every change; two known walk drifts preserved (Recovery 20/19, Nutrition 10/9); all 15 states render incl. degenerate cases (Marta {AMOUNT} SP frozen with NO remedy → must not render "needs " with nothing after; Ada all-four remedies → must not render useless copy); add a persona exercising the two unreachable states (`cashedSp`, `inadmissible`); DEPLOY.md demo paths; no localStorage.
- P4 Release: landing page review/deploy (GitHub Pages + cache-busting), README stale-number fixes (13→14 rules, gate/edge counts, SP figures).
- Ownership: {RELATIONSHIP} recon/license, {RELATIONSHIP} arch, {RELATIONSHIP} design, {RELATIONSHIP} build, {RELATIONSHIP} QA, {RELATIONSHIP} orchestration. User checkpoints: plan → design review → done-report with command output.

## Why it fit the class
The takeover skill's core moves all fired: verify-on-disk, find + quote the documented done-definition, close the git safety gap as Phase {CLIENT}, run claimed-green gates, split primary ({CLIENT} rebuild) vs secondary (landing/deploy), checkpoint with user at decision gates, preserve-quirks rule.