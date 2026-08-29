<!-- GENERICIZED: 1×{AMOUNT}, 6×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/static-brand-site-launch/references/{CLIENT} -->
# {CLIENT} Site Case History ({CLIENT} / {CLIENT})

Session-specific detail behind the class rules in SKILL.md. Reference for failure signatures and verification gates.

## Failure modes encountered (in order)

1. **Baked checkerboard in "master" logo files.** Multiple copies of the same logos existed with different provenance: some RGB with baked light checkerboard, one with a BLACK checkerboard layer under the white, some clean RGBA. Two same-named files in `logos/` vs `assets/` had different hashes and different properties. Resolution: hash-compare all candidates, quarantine non-clean directories (`logos/`, `mats/`), build only from verified `assets/`.

2. **White-on-white glass cards.** A `.glass` component (translucent white + white text) designed on the dark gateway was reused on the light body background → invisible cards, unreadable text. Fix: scoped `.on-light.glass` variant. Rule: components declare surface contract explicitly.

3. **Single-shell SPA router failure cascade.** One index.html serving three URLs via JS (pathname match + legacy hash rewrite + replaceState). Symptom: `/digital` returned 200 but rendered as neither arm when JS hiccuped; identical `<title>` for all routes; canonical split across schemes. Fix: v4 rebuild as real multipage static — three files, plain links, no routing code at all.

4. **Clean URLs 404ing under hash-only routing.** Hash-based navigation meant typed/shared plain URLs died. Interim fix was vercel.json rewrites + pathname fallback; final fix was the multipage rebuild which needs none.

5. **Stale CSS vs new HTML (the run-on text class).** User screenshot showed `SPECspecificationC34 grade` collapsed text. The layout rule (`.route-row{display:flex;gap:8px}`) existed in served CSS but the user's browser held the OLD unversioned `gateway.css` (4h TTL) against the NEW HTML. Root cause: images got `?v=3` in the same pass, stylesheets got nothing. Fix: version every CSS/JS ref (`?v=<sha>`), bumped in the SAME commit as the layout change (never after), plus a `?cb=` cache-bust on every gate probe. This class caused at least two "weird text" reports that were not broken in source.

6. **Interactive terminal read as raw CLI log dump.** Even after the responder worked and the pipeline labels were fixed, the user's screenshot showed: concatenated `try /build…/fund…/source…` string, an orphaned `c34 steel`, a floating `$ /build supply chain` ghost line, and a detached input box. Two distinct causes:
   - The ghost `$ /build supply chain` was the AUTHOR'S OWN functional-test input persisted in the seed state — real interaction residue shipped as static seed content. Never test by typing into the live DOM and then ship it.
   - The concatenated "try" line and bare acronyms were raw scaffolding with no presentation pass. Fix (v5.3.6): seed exactly three clean lines (styled hint `type /help to see what i can do`, auto-typed `$ {CLIENT} deploy --emerging-tech --funded`, `✓ capability demo ready`), full pipeline labels, input styled as a dark inset mono field with cyan border/focus ring.
   - The `—help` em-dash bug: an em-dash where a CLI flag needs `--help` renders as broken-looking text and was the first thing visitors saw.

7. **Desktop-only widget cost mobile Lighthouse twice.** The responder script and then the auto-type intro each ran on mobile despite the terminal being CSS-hidden, dropping mobile perf 93 → 78 both times (15 and 15 points). Fix: gate the SCRIPT by viewport (`matchMedia('(max-width: 820px)').matches` early-return) AND `defer`, and gate any auto-play animation identically. CSS visibility alone never stops a script from parsing and executing.

8. **Full-bleed dark bands inside a light page ("containers look awkward").** sc2/sc3 showed the four middle bento cards clean but the quote strip, "How It Works," and the contact CTA edge-to-edge full-bleed dark bands clashing against the light body. Fix (v5.5): blanket rule — below the hero, EVERY dark surface is a contained card (`.tagline-card`, `.how-card`, `.cta-card`, radius 20px, navy border, same rhythm as the mid-page cards). Fixing 1 of 4 bands just leaves the inconsistency the user flagged; apply the rule blanket from the start.

9. **Digital hero emptiness = composition, not texture.** sc1: flat navy wall, ~70% dead viewport, everything crammed upper-left. The engineering-grid overlay was invisible on navy (it reads on Physical's light page, not on dark). Fix (v5.5): 2-column hero (`grid-template-columns:1fr minmax(300px,420px)`) with a **right-side rendered terminal device** (tilted perspective, traffic lights, `{CLIENT} assess --agentic-ai` demo lines, blinking caret) + a **light-stroke grid at `rgba({AMOUNT},.06)`** so it reads on navy. Texture alone doesn't fill dead space; composition does.

10. **Wrong-base rebuild silently dropped the terminal.** The responder edit was written to the pre-terminal v5 base and copied over the root, overwriting the terminal-carrying `23cac17` build; the served gateway lost the terminal. Recovered by `git show 23cac17:index.html` → rebuild responder on that base → re-verify. Lesson: `git log -S "term-head" -- .` to find the commit carrying a feature before extending it.

11. **"No way to navigate between divisions."** User's explicit ask. Fix (v5.4/v5.5): persistent orange `{CLIENT} ↗` button in the `/digital/` header (and cyan mirror in `/physical/`), plus a footer "Explore the other division" switcher on both pages for scroll-past users. Verify the switcher is in the served HTML of every sub-page.

## Verification gates that caught things

- Sign-off gate: every public route curl'd for status + title after each deploy (apex, www, subdomains, asset URLs).
- Disk-level checks before sign-off: file mtime + sha256 vs manifest — a room member flagged an "identical hash" as suspicious stale reuse; it turned out to be a deterministic transform reproducing byte-identical output from the same input. Verify claims against disk before accepting either interpretation.
- PIL probes: `im.mode`, `im.size`, corner alpha values settle logo disputes in seconds.
- Live-asset audit: pull served bytes off production and hash-compare to workspace copies.
- Cache-busted probes: every gate curl appends `?cb=<deploy-sha>`; every production asset ref carries `?v=<deploy-sha>` bumped in the same commit as the change. Three "stale bytes vs live bytes" disputes happened while deploys were correct — each was a probe hitting a cached copy.
- Mobile emulation gate (binding): 390px screenshot per surface + mobile Lighthouse against live URL, run for ALL surfaces (not just the one being worked on). Desktop-only QA is how a "horrible on mobile" site shipped.
- One-primary-CTA check: verify hrefs differ — a duplicated `mailto:` under two labels ("Book a consultation" / "Email us") shipped once.

## Deploy specifics

- Vercel: CLI deploy lands on project linked via `.vercel/project.json` in the workdir — a reused directory silently deploys to the OLD project. Token expiry (~24h): `vercel whoami` without `--token` refreshes.
- Apex domain verify required adding a second TXT value to `_vercel.<domain>` in Cloudflare; then POST `/v9/projects/{id}/domains/{domain}/verify`.
- Cloudflare apex: CNAME flattening works (CNAME at root, proxied:true).
- GitHub Pages cname change: `gh api repos/{org}/{repo}/pages -X PUT`; DNS CNAME to `{RELATIONSHIP}.github.io` proxied; build takes ~60s.
- Deploy mechanism is `vercel --prod` CLI, NOT git-push — record which one the project uses in STATE.md.

## Workflow lessons

- Micro-stage protocol: each stage = one bounded batch ending in STATE.md write + report. Persist state so any session can resume after cutoff (this session survived multiple timeouts this way).
- Deterministic rebuilds produce identical hashes — not evidence of staleness by itself; check mtime too.
- User-supplied "open source building material" may be wrong-grain (Flatlogic = admin dashboards, not brand sites); extract patterns if the user names something specific, otherwise use the exemplar set.
- The two-tree trap: with `vers/vN` mirrors, edits silently land in the wrong copy. Confirm the canonical path against STATE.md before editing; STATE.md must name the exact real path. One room member's fix "didn't survive contact with the disk" because it was applied to the stale mirror.
- When a user screenshot contradicts the source, suspect the CACHE first (unversioned refs), then the reference chain (page pointing at a retired asset), then the seed state (test residue) — in that order.
