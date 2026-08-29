<!-- GENERICIZED: 1×{CLIENT} | source: skills/web-release-gates/SKILL.md -->
---
name: web-release-gates
description: Use when promoting web builds to production.
---

# Web Release Gates

Discipline for promoting static web builds between staging and production. Born from a multi-week site build where the same failure classes recurred: unauthorized live pushes, stale-CSS-vs-new-HTML bugs, false rollback reports, and environment-scoped secrets silently breaking staging.

Session-specific symptom→cause markers (commit hashes, exact grep probes): see `references/{CLIENT}`.

## The review loop

**build → staging → QA + visual pass on staging → USER review → promote to live.**

- The user reviews a QA-passed staged artifact, never a raw build, and never a live deployment.
- **Never deploy to live without explicit user sign-off on the staged version** — even when an earlier standing directive said "auto-deploy every draft". Standing directives get superseded; check the current instruction before each promote.
- **Deploy-target lock:** every deploy command names an explicit target (live vs staging) AND gets a second-agent confirm before running. One unauthorized push caused a full round of environment untangling.
- **Live = last approved version; staging = current working version.** When the user orders a swap ("live back to X, staging to Y"), verify BOTH surfaces after, with byte-level probes.

## Cache-busting (the stale-CSS class)

Layout complaints that "came back" after a fix are usually this: CSS changed while the stylesheet URL stayed the same, so browsers with a long cache TTL serve old CSS against new HTML. Symptoms: run-on text, old layout, "weird text" the source doesn't contain.

- **Version every CSS/JS reference** (`/gateway.css?v=<deploy-sha>`) — images alone are not enough; the asset class that changes layout is the one that must be versioned.
- **Bump the version in the SAME commit as the CSS change** — never after. A layout change without a version bump ships a stale-layout window.
- Verify deployments by fetching through a cache-buster (`?cb=<sha>`) so "stale bytes vs live bytes" stops being a room argument.

## Pre-deploy guard

A cross-page copy (`cp digital/index.html index.html`) silently replaced the site root. Guard the whole class:

- Before any push, verify the root file carries its expected marker (grep for the gateway/landing marker) and FAIL if it matches a different page type. A `scripts/predeploy-guard.sh` tested for both pass and fail makes it permanent.
- Extend later: check each page's own marker so division-to-division copies are caught too.

## Rollback hygiene

- **`git checkout <commit> -- .` does NOT remove files in the worktree but not in that commit** — a tracked file added later (e.g. `api/ask.mjs`) survives the checkout and ships in the "rolled back" deploy. For a clean rollback: remove files not in the target tree (`git rm -r --cached` + `rm -rf`) and confirm zero residue before deploying.
- **Verify rollbacks by bytes, not claims.** After any rollback/promote, probe the live surface yourself: fetch the page, grep for markers that distinguish versions (endpoint presence, command set, title). A "rollback done" report was proven false by live bytes still serving the old version.

## Environment-scoped secrets

Platform env vars (Vercel, Netlify) are scoped per environment. A function that works on production can 503 on staging because the key isn't scoped there (`vercel env add <KEY> staging`). After any fresh staging baseline, add the staging-scoped secrets or expect the "Assistant not configured" class of failure.

## QA gates: check computed style, not class presence

A fix was "verified live" because the CSS contained the class name — but the class was padding-only, so the visual defect survived. Rules:

- Verify what the class DOES: computed style (border-radius + background + shadow present), the base rule not the media-query override, contrast floors (border color ≥ threshold vs background). A grep for the class name proves nothing about rendering.
- Visual pass reads pixels; the gate reads computed style — both are required, neither is substitutable.

## Pitfalls

- Interaction-surface splits: one element doing two jobs (terminal that navigates AND accepts input) — split them: click = instrument behavior (focus), separate anchor = navigation. Re-verify after any restructure; the click bug returned when the terminal moved columns.
- Layout "accidents" that look good: before adopting an accidental render as a design, ground-truth it against the DOM and confirm with the user what they actually liked — often it's spacing, not structure.
- Serving a private-repo requirement: confirm repo visibility (GitHub API) before any push — "private" is a constraint from the user, not a default.
