<!-- GENERICIZED: 2×{CLIENT} | source: skills/web-release-gates/references/{CLIENT} -->
# {CLIENT} Site Incident Log (reference)

Symptom → root-cause map from the {CLIENT} build (Aug 2026). Use to recognize
the failure classes fast; the SKILL.md body carries the durable rules.

## 1. Unauthorized live push (the staging-first violation)
- Symptom: user saw live change while room iterated on staging; user asked "why are we changing live?"
- Root: one push went to live without review (`vercel --prod` on a staging-intended commit).
- Aftermath: full environment untangle — live had v6.5, staging had v6.8, approved was v6.3.
- Marker: `/api/ask` endpoint live = v6.5; absent = v6.3.

## 2. Cross-page copy clobber
- Symptom: landing page replaced by the division page (`cp digital/index.html index.html`).
- Marker: root HTML carries `.d-hero` instead of `.gw-hero` / `#askterm`.
- Fix class: pre-deploy guard greps root for its expected marker and fails otherwise.

## 3. Stale-CSS-vs-new-HTML (the cache class)
- Symptom: "weird text" / run-on labels (`SPECspecificationC34 grade`) that the served source doesn't contain.
- Root: CSS file URL unversioned; browser holds old CSS against new HTML for the TTL (4h).
- Marker: fetch CSS with `?cb=<sha>` — the rule exists but the user's browser never got it.
- Fix: version ALL css/js refs (`?v=<sha>`), bump in the SAME commit as the layout change.

## 4. False rollback report
- Symptom: room declared "live = v6.3" but live bytes still served `/api/ask` (200 with real LLM answer).
- Root: rollback deployed from a mixed worktree.
- Marker: `git checkout <commit> -- .` leaves files tracked later (e.g. `api/ask.mjs`) on disk; they ship.
- Fix: remove files not in target tree (`git rm -r --cached` + `rm -rf`), verify zero residue, then deploy; verify live by grep after.

## 5. Environment-scoped secrets
- Symptom: `/api/ask` answers on production but 503 "Assistant not configured" on staging.
- Root: Vercel env vars are per-environment; key scoped to production only.
- Fix: `vercel env add OPENROUTER_API_KEY staging` after any fresh staging baseline.

## 6. Hollow class / computed-style gap
- Symptom: "containers still look like plain rectangles" after a fix was "verified live".
- Root: QA grepped for the class name in CSS; the class was padding-only (the depth rules existed but were missing/overridden).
- Fix: gate checks computed style (border-radius + background + shadow) and the BASE rule, not the media-query override.

## 7. Click-surface regression after restructure
- Symptom: clicking the terminal navigates to the division page instead of focusing input.
- Root: the whole `.half` was an anchor; a restructure re-glued the surfaces.
- Fix: click = instrument (focus, stopPropagation), separate `.enter` anchor = navigation; re-verify after ANY move.

## 8. Adopted accident (three-column spine)
- Symptom: accidental 3-column render; room adopted it as a design.
- Root: misread "terminal got more vertical space" as "terminal should be its own column". User clarified: two halves sacrosanct, flavour elements get columns INSIDE each half.
- Lesson: ground-truth the DOM and ask the user what they actually liked before adopting an accident.
