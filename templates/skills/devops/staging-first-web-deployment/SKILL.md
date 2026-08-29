<!-- GENERICIZED: 3×{CLIENT} | source: skills/devops/staging-first-web-deployment/SKILL.md -->
---
name: staging-first-web-deployment
description: Use when deploying or iterating a user-reviewed website.
---

# Staging-First Web Deployment

For any client-facing or user-reviewed site, the default process is:

**build → staging → QA + visual pass on staging → user review → promote to main.**

Never deploy a new version directly to the live domain without explicit user approval. One unauthorized push costs the whole team a round of forensic untangling — the user WILL catch it. Born from the {CLIENT} site build where a single staging-first violation caused a full environment-swap incident and several "verified in code vs served reality" disputes.

## The loop

1. **Build** against the current staging baseline (revert/scratch decisions included).
2. **Deploy to staging** (a SEPARATE Vercel project from production — `vercel --project <staging-project> --prod`).
3. **QA + visual pass on staging** before the user ever sees it. The user reviews a QA-passed artifact, not a raw build.
4. **User review** — screenshot artifacts and main-vs-staging pairs help them see what changed.
5. **Promote to main** only on explicit approval, with the guard + version bump in the same pass.

## Pre-deploy guard (mandatory)

Before any push/deploy, run a marker check that fails if the root file is the wrong page. The canonical failure: `cp page2/index.html index.html` silently clobbers the landing page at the site root.

```bash
#!/usr/bin/env bash
# scripts/predeploy-guard.sh — root MUST be the gateway/landing page
set -e
ROOT="${1:-index.html}"
[ -f "$ROOT" ] || { echo "GUARD FAIL: $ROOT missing"; exit 1; }
if grep -q 'class="gw-hero"' "$ROOT" && grep -q 'id="askterm"' "$ROOT"; then
  echo "GUARD OK: root is the gateway"
else
  echo "GUARD FAIL: root is NOT the gateway — refusing deploy"
  exit 1
fi
```

Test it on BOTH the good file and a fake wrong-page file before trusting it. Wire it into the deploy stage permanently — it catches the highest-probability silent clobber class.

## Served-bytes verification (the truth)

- Every claim about the deployed state comes from a **cache-busted fetch** (`curl -sL "https://host/path?cb=<sha>"`), never the working tree.
- "Verified in code" has repeatedly failed this class of task. The served bytes are the truth; local source has been wrong mid-session.
- If a teammate's audit disagrees with your claim, re-fetch with a fresh cache-buster — the dispute class is the trap, not the value.
- After any rebase/conflict during a rollback, verify the final tree's markers — conflict resolution can silently drop the fixes you're restoring.
- **Exact-referenced-URL checks.** For asset disputes (font 404 vs 200, missing image), fetch the EXACT URL the served page references — grep the served `@font-face`/`src` for the path, don't guess a bare path. Two agents can both be right on different URLs, and only the referenced one matters for the user.
- **Painted size beats CSS tokens.** For "text too small" / "buttons differ in size" complaints, measure the actual rendered geometry in a live browser — `getBoundingClientRect()`, or `document.createRange().selectNodeContents(el).getBoundingClientRect()` for painted text height. CSS token values (14px vs 12px) and scoped-rule reads don't settle what the user sees; the painted render does.
- **Check COMPUTED style, not just the scoped rule.** Base-rule inheritance silently overrides scoped values (a `.btn` base sets weight 600 while your override says 500) — off-by-one-weight disputes come from reading the override as the whole truth. `getComputedStyle(el)` is the arbiter.

## Versioned asset refs — SAME commit as the change

- Images usually get `?v=` cache-busts; stylesheets that carry layout often don't. That gap ships stale CSS against new HTML (run-together text, "old terminal" ghosts).
- Any deploy that changes CSS/JS must bump the version param on those refs in the same commit.
- Browsers hold 4h+ TTLs; a version bump is the only thing that reaches them without hard-refresh.

## Deploy-target lock

- No deploy command runs without an explicit target (`--project <staging>` vs production project) and a second agent's confirmation.
- Staging and production are separate Vercel projects — deploying to the wrong project looks exactly like "the fix didn't land."
- Record what each target's baseline contains, not just which commit.

## Pitfalls

- **Vercel env vars are per-project.** A key scoped to production is invisible to staging's serverless functions (503 "not configured"). Add via a linked temp dir: `vercel link --project <staging>` then `vercel env add NAME production`.
- **Vercel CLI tokens expire (~24h).** Deploy fails "Not authorized" → run `vercel whoami` WITHOUT `--token`; the CLI auto-refreshes. Never reuse a cached token across days.
- **Don't gate critical UI on a JS-removed class.** The `no-js` flash-guard becomes a permanent hide if the removal JS doesn't run (init race, deferred-script ordering). Serve the flagship visible by default; JS only enhances (auto-type, commands).
- **"Scratch that change" reverts need the same served-bytes verification** as the original change — a claimed revert that never landed is as bad as the original bug.
- **Same-commit discipline:** CSS change + `?v=` bump + pre-deploy guard all in one pass, or the review loop burns a round.

## Reference

- `references/{CLIENT}` — concrete {CLIENT} deploy incident classes, guard history, and verification commands.
