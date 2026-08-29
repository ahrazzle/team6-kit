<!-- GENERICIZED: 10×{CLIENT} | source: skills/devops/staging-first-web-deployment/references/{CLIENT} -->
# {CLIENT} deploy playbook — incident classes and verification

Session-derived from the {CLIENT} build. Concrete failures and the exact patterns that resolved them.

## Incident classes (each happened, each is preventable)

### 1. Staging-first violation → environment swap
- v6.5 was pushed to live WITHOUT user review. Everything after (click fix, commands, layout experiments) went to staging only, leaving live stuck on v6.5 while the room iterated. User caught it.
- Fix: deploy-target lock (explicit target + second-agent confirm), and the staging-first loop above.

### 2. False "rollback done" claim
- Live was reported as v6.3 after rollback, but served bytes showed v6.5 (`/api/ask` returned 200, not 404). The rollback never landed or was overwritten.
- Fix: verify the served bytes of the specific marker (`/api/ask` → 404 = v6.3 tree; `cmd==='/enter'` presence = v6.5+). Never trust a rollback report.

### 3. Cross-page copy clobber
- `cp digital/index.html index.html` in a batch command replaced the landing page with the division page at root. The user's "the one thing I loved is gone."
- Fix: pre-deploy guard grepping for root markers (`gw-hero` + `askterm`). Guard now catches its own class.

### 4. Stale CSS vs new HTML (unversioned stylesheet)
- Pipeline labels rendered run-together (`SPECspecificationC34 grade`) because `gateway.css` was referenced WITHOUT `?v=` — browsers held the old CSS against new HTML for up to 4h.
- Fix: version EVERY stylesheet ref (`/gateway.css?v=<sha>`), bump in the SAME commit as the CSS change. Images had `?v=` all along; stylesheets were the gap.

### 5. Hidden-by-class terminal (no-js flash guard inversion)
- Landing terminal invisible (`visibility:hidden; opacity:0`) because `<body class="no-js">` was never removed: the shared component didn't remove it, and the init script raced the deferred component load.
- Fix: serve visible by default (remove the hiding rule), JS only enhances. The component removes `no-js` on init AND the init script retries until `window.{CLIENT}` exists.

### 6. Wrong-project deploy
- `vercel deploy --prod` from the repo deployed to the production project, not staging. Fix looked like it didn't land.
- Fix: `vercel --project {CLIENT} --prod` for staging. Separate projects, explicit project flag.

### 7. Grid row-height loop
- A 3-column grid's row ballooned to 1624px because `.gw-divider{height:120%}` inside a grid with auto rows loops (120% of the auto-sized row feeds the row height). Physical half pushed below the fold.
- Fix: `height:100%` + `overflow:hidden` on the hero, and ensure divider is a direct grid child, not nested inside a column.

### 8. Nested-anchor click bug
- `<a class="half">` wrapping the terminal made every click navigate; `stopPropagation` on the panel never helps because the anchor's native default is what fires. Requires `preventDefault()` or structural change to `<div>`.
- Fix: panel → `<div>`, only the "Enter …" text is an anchor. Verify by clicking in a live browser, not by grepping handlers.

### 9. Off-by-one-weight (base-rule inheritance)
- User pointed at a concrete orange button and said "use this font." We applied Geist 500, but the reference renders at 600 — the base `.btn` rule in system.css sets `font-weight:600`, overriding the scoped 500. A whole review round burned on a one-value diff.
- Fix: when matching a reference element, read its COMPUTED style (family + weight + case + tracking), not the class you think it uses. See the Point-at-a-Concrete-Element principle in user-preference-capture.

### 10. Exact-URL vs bare-path asset dispute
- One audit reported Armstrong font woff2 as 404; another reported 200. Both were true on different URLs — the 404 was a bare path guess, the 200 was the exact path the served `@font-face` references.
- Fix: grep the served HTML for the referenced path, then fetch THAT exact URL. The referenced one decides whether the user sees the font.

### 11. LLM unconditional system-prompt instruction
- The showcase-assistant prompt REQUIRED "→ scheduled: intro call" on every answer; the model appended it even to "what does {CLIENT} do?" — read as pushy, user asked what was injected.
- Fix: keep the honesty-guard spine, but make conversational add-ons CONDITIONAL ("append only when the user expresses genuine interest or asks for next steps"). Contact info (email/phone) belongs IN the prompt so the assistant can answer contact questions.

### 12. Painted-size vs token-value dispute
- "Top-right button text too small" — the fix bumped 12px→14px (CSS token), but the room argued whether that was enough by comparing tokens and screenshots.
- Fix: measure painted text height in a live browser (`document.createRange().selectNodeContents(el).getBoundingClientRect().height`). Equal painted heights settle it; token reads and stale screenshots don't.

## Verification commands (cache-busted)

```bash
# Served bytes, never local source
curl -sL "https://<host>/?cb=<short-sha>" -o /tmp/check.html
curl -sL "https://<host>/system.css?cb=<short-sha>" | grep -c "marker-rule"

# LLM endpoint surface check (404 = removed, 200 = live)
curl -s -X POST https://<host>/api/ask -H "Content-Type: application/json" -d '{"q":"test"}' -w "\n%{http_code}\n"

# Versioned ref present in served HTML
curl -sL "https://<host>/?cb=x" | grep -oE '(gateway|system|digital|physical)\.css\?v=[a-z0-9]+'
```

## Environment topology ({CLIENT})

- Production project: `{CLIENT}` (Vercel team a-4677s-projects), deployed via `vercel deploy --prod --yes` from repo root.
- Staging project: `{CLIENT}` — `vercel --project {CLIENT} --prod --yes`, domain staging.{CLIENT} (Cloudflare CNAME + `_vercel` TXT verification).
- OpenRouter key: scoped per project env (`OPENROUTER_API_KEY`), never in repo/client.
- Pre-deploy guard: `scripts/predeploy-guard.sh` at repo root, run before every deploy.
