<!-- GENERICIZED: 8×{CLIENT} | source: skills/deployment-verification-discipline/references/{CLIENT} -->
# {CLIENT} Site Deployment Incidents — Timeline & Lessons

Source: the {CLIENT} build (Vercel static site, private repo, two projects: `{CLIENT}` production + `{CLIENT}` staging). Each incident below is a real event that produced a rule in the parent skill.

## 1. Stale CSS vs new HTML (run-on pipeline text)
- User reported `SPECspecificationC34 grade` run-on text. Root cause: HTML gained new spans (full labels) but the CSS filename was unversioned; the browser held the old CSS (4-hour cache TTL) against the new HTML.
- Images had `?v=3`; stylesheets had nothing. The asset class that changes layout was the one class without versioning.
- Fix: versioned CSS refs `?v=<deploy-sha>` on every page, same commit as the change.
- Lesson → Rule 2 (version every asset reference).

## 2. False "fixed" claims vs served bytes
- Repeatedly, a teammate claimed a fix was live; served bytes or the user's screenshot proved otherwise (the `no-js` terminal hide, the v6.5 rollback that never landed, the hollow-card grep false alarm).
- The served bytes and user screenshots were right every time; the local-source read was wrong repeatedly.
- Fix discipline: cache-busted curls of the served HTML/CSS + live-browser interaction tests.
- Lesson → Rule 1 (verify served bytes), Pitfall 1.

## 3. Unauthorized live push (v6.5 without review)
- A deploy meant for staging went to live without user review, breaking the staging-first rule. The user caught it; the room then spent a full round unwinding (swap live back to last-approved v6.3, staging to the working version).
- Lesson → Rule 8 (explicit target + second-agent confirmation), Rule 9 (staging-first loop).

## 4. Rollback silently reverted approved fixes
- The environment swap (live → v6.3, staging → v6.5) restored baselines but silently reverted the click-split fix, the Enter-link contrast fix, and the layout spec that the user had already approved — all three had to be re-applied in a later composite round.
- Lesson → Rule 4 (record what a baseline contains), Pitfall 4.

## 5. `git checkout <sha> -- .` left straggler files
- Rolling back to v6.3 left `api/ask.mjs` on disk (tracked at HEAD, absent from v6.3); the deploy "succeeded" but `/api/ask` still answered 200. The clean rollback required `git rm` + removing the dir, then redeploy.
- Lesson → Rule 5 (clean-tree checkout).

## 6. Staging is a separate Vercel project
- `vercel --prod` from the repo deploys to the linked `{CLIENT}` project; `staging.{CLIENT}` is served by the separate `{CLIENT}` project. Deploys to staging need `--project {CLIENT}`.
- Env vars are project-scoped: staging's `/api/ask` returned 503 "Assistant not configured" until the OpenRouter key was added to the staging project's env.
- Lesson → Rule 6 (separate staging and production projects).

## 7. The `no-js` flash-guard became a permanent hide
- The landing terminal was hidden by `<body class="no-js">` + `.no-js .term{opacity:0;visibility:hidden}` until JS removed the class. When the shared-component refactor stopped removing it (or the init raced the deferred script), the flagship terminal stayed invisible — user reported "container missing from landing page".
- Fix: removed the `no-js` class from the served HTML and deleted the hiding CSS rule entirely. Terminal is visible by default; JS only enhances.
- Lesson → Rule 3 (never gate critical UI on a JS runtime step).

## 8. Pre-deploy guard caught its own class
- A sync overwrote root `index.html` with a terminal-less base; the guard (`grep` for `.gw-hero` + `#askterm` in root before deploy) failed the deploy and caught the accident before it shipped.
- Lesson → Rule 7 (pre-deploy guard).

## 9. Grep-for-class ≠ renders
- "The container classes are hollow (padding only)" was a false alarm: the grep hit the `@media(max-width:720px)` padding overrides sitting after the full base rules. Computed-style verification (radius 24px, gradient, shadow, border) proved the classes render as cards.
- Lesson → Pitfall 2 (check computed style, not class presence).
