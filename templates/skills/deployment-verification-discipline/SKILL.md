<!-- GENERICIZED: 5×{CLIENT} | source: skills/deployment-verification-discipline/SKILL.md -->
---
name: deployment-verification-discipline
description: Use when verifying deployed sites or subagent claims.
---

# Deployment Verification Discipline

Hard-won rules from a live-site project where the recurring failure class was **"verified in code, broken in served reality"** — the local build and the repo looked correct while the user's browser showed the old, broken, or missing state. The served bytes and the user's screenshot were right every time; the local-source read was wrong repeatedly.

## The rules

1. **Verify served bytes, never local source.** Every "fixed / deployed / rolled back" claim is proven with a cache-busted curl of the live or staging URL (HTML + CSS + JS), and where interaction matters, a live-browser click/type test. "It's in the repo" means nothing until the served artifact shows it. Grep the served HTML/CSS for the exact marker, class, or rule you claim to have shipped.

2. **Version every asset reference, not just images.** CSS/JS `<link>`/`<script>` refs need `?v=<deploy-sha>` (or monotonic number), bumped in the SAME commit as the layout change. Images-only versioning leaves stale-CSS-against-new-HTML rendering bugs (run-on text, missing layout rules, invisible cards) alive for the full cache TTL. Users do not run cache-busters; their browser runs on `?v=`. This is the completing clause of any cache-buster verification contract: your `?cb=` curls prove the server, the `?v=` refs prove the browser.

3. **Never gate critical UI on a JS runtime step.** A `no-js` flash-guard class that hides a flagship element until JS removes it becomes a permanent hide when the class-removal loses the race (defer ordering, cached script, JS error). Serve critical UI visible by default on first paint; JS only *enhances* (auto-type, commands, live data), never *reveals*. If a class must gate, remove it server-side in the served HTML, not client-side at runtime.

4. **Record what a baseline contains, not just its SHA.** When an environment is rolled back to an older commit, every fix built after that commit is silently reverted too. A deploy-target lock must record the baseline's approved-fix list, or the next round re-ships bugs the user already complained about (three times, in this project's history).

5. **Clean-tree checkout for rollbacks.** `git checkout <sha> -- .` leaves files that exist at HEAD but not at <sha> (e.g. a newly added `api/` dir) on disk; deploying from that mixed state ships the wrong tree — and the deploy "succeeds" while serving the wrong version. After any rollback checkout: verify `git ls-tree <sha> --name-only` matches the worktree, remove stragglers, then deploy.

6. **Separate staging and production projects.** On Vercel, `vercel --prod` deploys to whatever project the directory is linked to; staging is often its own project (`{CLIENT}`) with its own domain. Confirm which project serves which domain and target explicitly (`vercel --prod --project {CLIENT}`) before claiming a deploy landed anywhere. Env vars are also project-scoped — a staging deploy that works on production may 503 on staging until the key is added there too.

7. **Pre-deploy guard.** Before any push, verify the root document carries its expected page marker (e.g. gateway section id + terminal id) and fail the deploy if it matches a different page. This catches `cp digital/index.html index.html`-class cross-page copy accidents that have clobbered live sites. The guard should check per-page markers (`.gw-hero`, `.d-hero`, `.p-hero`), not just presence.

8. **No deploy without an explicit target + second-agent confirmation.** "Push to live" and "push to staging" act on the same pipeline; one unauthorized push to live without review caused an entire incident round. The target must be named and confirmed before the command runs.

9. **Staging-first review loop.** Build → staging → QA + visual pass on staging (computed-style checks, not just class presence) → user review → promote to main. The user reviews a QA-passed artifact, never a raw build, and never catches bugs the gates should have caught.

## Verifying subagent-claimed deliverables

Subagent completion reports are self-reports, not verified facts — the same failure class as local-source reads: the agent's logs and screenshots looked right while the served artifact was broken. A build round came back "15/15 checks pass" with screenshots while the served island rendered solid black with no objects and the creature reduced to two dots.

1. **Treat every subagent screenshot as evidence of one state, not the truth.** Captures can conflict (two green-island shots at 14:49, black island in the "final verified" shot at 14:56). When they disagree: check file mtimes to identify the latest state, then verify against the LIVE served build — the served artifact is ground truth, never the agent's chosen screenshot.
2. **Automated interaction checks do not catch visual regressions.** A headless 15/15 pass proves logic, not rendering. If the deliverable is visual (scene, layout, UI), run your own vision-model pass on the ACTUAL render — the served page, not the subagent's PNG.
3. **The served build is the deliverable, not src.** A fix that passes `npm run build` but regresses the served page (stale dist, crossfade that never fires, labels with no objects behind them) is not a fix. Verify in the served build; rebuild + hard-refresh before claiming.
4. **Reject with evidence, re-dispatch with a narrow brief.** Send the orchestrator's own screenshot + DOM diagnostics (canvas mounted? SVG opacity stuck at 1? labels present but no geometry?) and demand before/after proof in the next round. One narrow fix round beats a re-architect.
5. **When in-app preview/browser tools are unavailable, drive headless Chrome via CDP** — see `scripts/headless-cdp-serve-check.mjs` for the proven probe (spawn Chrome with `--remote-debugging-port`, fetch `/json`, WebSocket CDP, `Page.captureScreenshot` + `Runtime.evaluate`). Screenshot the real served page AND read DOM/computed-style diagnostics in the same run.

## The repeated-fix loop — kill it with a deterministic assertion gate

When the same UI fix is announced "done" multiple times and each time the live page still shows it broken (observed: a "keyboard flush to top" request stayed broken across 5 announced-fixed rounds), it is no longer a CSS bug — it is a verification-loop failure. Headless sims and victory-screen screenshots cannot arbitrate a LAYOUT claim; only a capture of the SERVED live page in the state under test can.

1. **Make the success criterion a number, not a screenshot judgment.** Assert geometry with a console line that runs on the served URL mid-state: `[{CLIENT}] check: keyboardRect.top=0 → PASS/FAIL`. A fix is not announced until that line is green on the page the user actually tests. This converts whack-a-mole into a pass/fail gate by construction.
2. **Simulate the real user's input pattern, not a fixed cadence.** A headless sim typing on a fixed interval passes while a real user's irregular pacing breaks the game (a beat-locked note grid + a fixed-cadence sim "won" while real slow typing triggered the stale-kill and input went dead mid-word). If the user is a child or slow typer, simulate irregular 700–1200ms gaps and test the degraded path too.
3. **Receipts must be fresh AND show the state under test.** A screenshot's mtime must be ≥ the source file it documents (a 9-minute-older PNG was presented as proof of a fix that shipped 9 minutes later), and it must capture the mid-battle/interaction state — a victory/end screen documents none of the layout being verified.
4. **Wrapper-positioning claims need element-level checks.** `top:0` on the wrapper container does not move a child's own internal offset (framework-rendered keyboards carry their own top padding). Assert the keyboard ELEMENT's `getBoundingClientRect().top`, not the wrapper's.
5. **Absolute paths work on localhost, break on the hosted subpath.** A dev server that serves the workspace root resolves `/demo/words.json` and `"/" + asset` — GitHub Pages serves under `/repo/` and 404s them. This class only surfaces on the real URL, so verify the live-served fetch and prefer relative / repo-relative paths from the start.

## Pitfalls

- **"Fixed" claims from a local build are worthless** until served bytes AND a live-browser test confirm. This class of false claim repeated six+ times in one project.
- **Grep for class names in markup/CSS proves nothing about rendering.** Check computed style (border-radius + background + shadow present) or look at pixels — "class exists" ≠ "class does something".
- **Cache disputes** between team members ("stale vs live") are resolved by deterministic probes: `?cb=<deploy-sha>` on every verification curl, so the argument cannot happen.
- **A rollback swap restores baselines but silently reverts approved fixes** — re-apply the approved fix set on top of the restored baseline, and verify each fix in the served bytes of the restored environment.
- **Planning without artifacts reads as stalled.** When the user is waiting on an MVP/deliverable and design verdicts are resolved, dispatch the build lane immediately — the user tests artifacts, not documents; design polish iterates on a working build.
- **For user visual corrections (fonts, spacing, alignment, mirror symmetry), load `design-feedback-iteration`** — sleek = weight/register not family-shopping, replicate the FULL computed spec of a referenced element, and screenshot complaints may be stale renders (verify served bytes + live render before rebuilding).

## References

- `references/{CLIENT}` — the full incident timeline that produced these rules (stale CSS run-on, environment swap, no-js hide, staging-project split, unauthorized live push).
- `references/{CLIENT}` — case study: subagent-verified MVP whose served build rendered a black island (mtime forensics, evidence hierarchy, fix-round pattern).
- `scripts/headless-cdp-serve-check.mjs` — screenshot + DOM diagnostics of any served URL via headless Chrome CDP (proof of served reality when in-app preview/browser tools are unavailable).
