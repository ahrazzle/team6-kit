<!-- GENERICIZED: 3×{CLIENT} | source: skills/software-development/deploy-gate-discipline/SKILL.md -->
---
name: deploy-gate-discipline
description: Use when a site deploys via a staging gate. Verify bytes.
---

# Deploy Gate Discipline

SOP for sites that run a **staging-first review gate**: every version goes to a staging domain, the user reviews, and only an explicit approval promotes to production. Born from an {CLIENT} incident run (Aug 2026) where one unauthorized direct-to-live push caused a full environment-swap recovery round, and repeated "verified in code, broken in served reality" disputes.

## The rules

1. **Staging-first, always.** Every version deploys to a staging domain for user review before anything touches live. Promotion ONLY on explicit user approval. One unauthorized direct-to-live push triggers an entire incident round (env swap, stale-state disputes, trust loss).
2. **Name the target on every deploy.** Never run a deploy command without stating which surface it targets (staging vs live). No deploy without explicit target + second-agent confirmation.
3. **Version every asset reference.** CSS/JS refs carry `?v=<bump>` incremented in the SAME commit as the change. Unversioned stylesheets against new HTML = the stale-layout-vs-new-html class (recurring "run-together text" / "still old layout" complaints). Versioning images alone is insufficient — the layout-carrying CSS is the critical one.
4. **Verify claims against served bytes.** Any claim about deployed state is only valid from a cache-busted fetch of the current versioned ref (`curl -s "https://…/?cb=<sha>"` / `?v=`). Local source reads and teammate claims have repeatedly contradicted served reality; served bytes and the user's screenshots are truth, local reads are hypotheses. A grep for a class NAME proves presence, not rendering — use computed style / live-browser click for behavior.
5. **Separate staging and production as distinct deploy targets.** Staging is often a separate platform project (e.g. Vercel `{CLIENT}` vs `{CLIENT}`). `vercel --prod` from repo root targets the LINKED project only; deploying staging requires an explicit `--project <staging>` flag. Wrong-project deploys "succeed" while the visible surface keeps serving stale bytes. Env vars are per-project AND per-environment — a key scoped to production does not exist on staging; add it explicitly.
6. **Pre-deploy guard.** A cheap marker check before any push: fail the deploy unless the root page carries expected structural markers (e.g. `gw-hero`, `askterm`). Catches cross-page copy accidents (a division page copied over the gateway) that otherwise clobber production.

## Critical-UI visibility (no-js inversion)

Never gate flagship UI visibility on a JS runtime step (e.g. `.no-js .term{opacity:0;visibility:hidden}` with JS removing the class). When class-removal races or fails in the user's browser, the flagship stays invisible — the recurring "container missing" complaint. Ship critical UI **visible by default**; JS only enhances (auto-type, commands, LLM wiring).

## Shared component + data-driven maps

Build reusable UI once as a config-driven component (theme, command set, mount point) and mount it in multiple places — never copy markup per surface; copies drift and one gets fixed while the other doesn't. For command surfaces, define the map as DATA driving both dispatch and help output, so "command works but help doesn't list it" drift is structurally impossible.

## Pitfalls

- Stale-cache disputes recur until every verification is cache-busted by default — make `?cb=`/`?v=` the default probe, not the tiebreaker.
- A successful platform deploy can leave the visible surface on stale bytes — always re-probe the actual domain, not the deployment URL.
- Scoped CSS fixes beat broad selectors: a `font-family` change on `.btn` hits every button on the page; scope to the brand classes the user actually named.
- Rotation of approved builds: when a rollback or env swap is ordered, re-verify BOTH surfaces (live and staging) with independent probes — claims of "swap done" were false twice in one incident because the deploy hit the wrong project.

See `references/deploy-gate-patterns.md` for concrete recipes (cache-busted probes, pre-deploy guard, Vercel staging/prod specifics, incident vignettes).
