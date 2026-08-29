<!-- GENERICIZED: 41×{CLIENT}, 5×{RELATIONSHIP} | source: skills/custom-domain-publishing/references/{CLIENT} -->
# {CLIENT} — Live Topology (verified {CLIENT}, updated through v6.13)

Reference state of the user's production domain. Validate against live DNS before trusting.

## Version state ({CLIENT})

- **Live = v6.11.5** (user-approved: shared terminal component on landing + Digital hero, universal command map, no-js guard removed server-side so the landing terminal is visible by default).
- **Staging = v6.13.1** (latest unapproved: height revert to sleek-short terminals, `/enter` alias added, LLM prompt no longer forces "scheduled: intro call" on every answer, Physical topbar has {CLIENT} switcher, Digital wordmark/CTA in Geist Mono). Staging LLM needs `OPENROUTER_API_KEY` in the {CLIENT} project's **production** env scope (Vercel env scopes are production/preview/development only; the staging subdomain's project still uses its own 'production' scope).
- Env swaps revert approved fixes — after ANY live↔staging swap, re-verify every fix against served bytes (see SKILL.md staging section). A "rollback done" claim is false until the served bytes prove it.

## DNS (Cloudflare zone 25f48466ebd44bd98dc5728021bbeb36, token = "Edit zone DNS" scoped)

| Record | Type | Target | Proxied |
|---|---|---|---|
| {CLIENT} | CNAME | {CLIENT} | yes |
| www | CNAME | {CLIENT} | yes |
| staging | CNAME | cname.vercel-dns.com | no |
| acctraining | CNAME | {RELATIONSHIP}.github.io | yes |
| quran | CNAME | {RELATIONSHIP}.github.io | yes |
| {CLIENT} | CNAME | cname.vercel-dns.com | no |
| _vercel (TXT ×3) | TXT | apex + www + staging verification values | — |
| MX/TXT/DKIM | — | Google Workspace — NEVER touch | — |

## Hosting map

| Surface | Serves | Host |
|---|---|---|
| {CLIENT} + www | {CLIENT} corporate site: division gateway (mirror layout — Digital=[content|terminal], Physical=[pipeline|content]; interactive terminal + sourcing pipeline flank the center divider) → clean paths /digital, /physical | Vercel project `{CLIENT}` (prj_g27G8Lvqan5gATvQMXx8JpHG2b6L), CLI deploys from `{CLIENT}` |
| staging.{CLIENT} | Same corporate site — REVIEW COPY, always the latest unapproved build | Vercel project `{CLIENT}` (prj_zcZuSzilfYCOh2cRLzEuZNOg16SD), `vercel --project {CLIENT} --prod --yes` |
| acctraining.{CLIENT} | {CLIENT} (title/brand "{CLIENT}"; {CLIENT} internal-only) | GitHub Pages repo {RELATIONSHIP}/acc-training, cname=acctraining.{CLIENT} |
| {CLIENT} | {CLIENT} proposal | Vercel project `{CLIENT}`, git-linked push-to-deploy |

## Deploy path for the corporate site

- Private repo: github.com/{RELATIONSHIP}/{CLIENT} (git source of truth)
- Build dir: `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}`
- **Pre-deploy guard runs FIRST on every deploy**: `bash scripts/predeploy-guard.sh index.html` — fails unless root carries `.gw-hero` + `#askterm` (the gateway), preventing a division page masquerading as the root.
- Deploy: `vercel deploy --prod --yes` (CLI auth self-refreshes; API tokens expire ~24h). Same-commit `?v=` CSS bump mandatory.
- **Wrong-project trap**: `vercel --prod` deploys to the LINKED project — the repo links to `{CLIENT}` (production). Staging builds MUST use `vercel --project {CLIENT} --prod`. A fix that "didn't land" on staging once deployed to production instead.
- Quarantined subdirs: `logos/`, `mats/` (baked checkerboards) — build only from `assets/`
- STATE.md lives in the build dir — resumability protocol: executor writes at milestones, resumer validates against disk first

## USER RULES (superseded rule explicitly reversed {CLIENT})

- **STAGING-FIRST (NEW, MANDATORY):** all new versions deploy to staging.{CLIENT} and wait for user review BEFORE promoting to main. The old rule "every new draft pushes live automatically — NO approval step" is REVOKED after the gateway was clobbered by a cross-page copy on production. Main stays production-stable until explicit approval.
- "jj" = silent mode.
- Corporate code stays PRIVATE (Vercel, never public Pages).
- Public naming: "{CLIENT}" (/digital), "{CLIENT}" (/physical); "{CLIENT}" is internal-only.
- Portfolio links on site: {CLIENT} + acctraining. subdomains must stay linked and 200.
- The site must "blow people away" — the interactive terminal responder + pipeline tracker are the flagship proof elements (see marketing-site-flagship-interactions.md).

## Design direction (user-set bar)

- Exemplars: aalo.com, palantir.com (incl. /platforms/gotham + foundry), anduril.com, bshiyat.com. Component sources: threeui, beautifului, beui, rareui, transitions.dev, shadcn, ui-skills, coss.com/ui, designsystemchecklist, reui, emilkowal.ski.
- **Font tone is division-specific (user correction, {CLIENT}):** "{CLIENT}" wordmark + the cyan CTA button on the Digital page use **Geist Mono** (sleek/futuristic — the user rejected the "thick and blocky" face there as out of tone). Rostex (blocky, from mats/rostex) suits the **Physical** side only. Geist Sans + Mono remain the base system; Rostex is NOT used for the Digital wordmark/CTA.
- Naming locked: {CLIENT} (/digital) and {CLIENT} (/physical) consistently everywhere.
- Container rule (blanket): below the hero, every dark surface is a contained card (shared `.card-dark` / `.card-warm` in system.css) — no full-bleed bands inside the light page; light-theme cards use `--line-strong` (≥1.5:1 contrast floor).
- **Targeted deltas over skill-driven broad refreshes.** The user rejected a full ui-ux-pro-max/landing-page-design rebuild ("no visible improvements from skill, many past improvements undone") — apply the skill's discipline for new sections, but never blanket-refresh a heavily tuned site. Screenshot pairs (main vs staging) ship with every review request.
- Terminal = shared component `assets/js/{CLIENT}` (data-driven command map; universal commands incl. /info → /digital/#benefits, /game → {CLIENT} demo, /call → tel). Physical inner page gets NO terminal — its own interactive element comes later.
- Terminal height: user preferred the SHORT, sleek terminal over a taller one ("looked sleeker when it was short") — keep term-body compact (~150px min / 320px max), pipeline matched to it.
- Gateway layout: two halves sacrosanct (user rejected 3-column spine); Enter links are the only nav surfaces; terminal click = focus only.
