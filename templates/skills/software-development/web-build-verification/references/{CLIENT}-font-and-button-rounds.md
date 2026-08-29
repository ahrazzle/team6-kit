<!-- GENERICIZED: 2×{AMOUNT}, 2×{CLIENT}, 4×{RELATIONSHIP} | source: skills/software-development/web-build-verification/references/{CLIENT} -->
# {CLIENT} font & button rounds (v6.18 → v6.20)

Session detail for the class-level lessons in SKILL.md §11f.

## The Armstrong font round (v6.18)

- User supplied font dir: `wrk/mats/armstrong_3/` — `Armstrong.otf`, `Armstrong Oblique.otf`, `Armstrong-Extrabold.otf`, `FONT LICENSE.txt`, `Preview/`. Quarantined source; converted copies → `assets/fonts/armstrong-regular.woff2` ({AMOUNT} B) + `armstrong-extrabold.woff2` ({AMOUNT} B).
- Served HTML declared `@font-face{font-family:'Armstrong';font-weight:400;src:url(/assets/fonts/armstrong-regular.woff2)}`; scoped rule `.btn-cyan,.btn-ghost-dark{font-family:'Armstrong';font-weight:400;...}` was live.
- **Probe dispute:** I probed `/assets/fonts/Armstrong-Regular.woff2` (constructed, wrong case) → 404, declared the font broken. Correct probes (`armstrong-regular.woff2`, exact from served `@font-face`) → 200. Lesson: probe the verbatim URL from the served document; case matters. The 404-vs-200 dispute was my probe bug, resolved by the exact-URL check.
- Weight inventory: only 400 (Regular) and Extrabold exist in the package — no intermediate. Room's "sleek = 500-600" contract could not be satisfied in-family; the choice was 400 (possibly thin) or Extrabold (rejected register).
- Outcome: user rejected Armstrong entirely ("nevermind, looks bad") and pointed at the Physical page's `btn-orange` "Request a sourcing quote" button as the styling target.

## "Use the font from that button" (v6.18.1 → v6.18.2)

- First attempt: `.btn-cyan,.btn-ghost-dark{font-family:var(--font-sans);font-weight:500;letter-spacing:normal;text-transform:none}` — family + register matched, but the reference `.btn-orange` COMPUTES to 600 via the base `.btn` rule in `system.css` (`font-weight:600`), not via `.btn-orange` itself.
- Room dispute: 500 (sleek contract) vs 600 (faithful to reference). Resolution: user pointed at a concrete artifact → replicate its full computed spec → bump to 600. Design-contract amendment adopted: **when the user references a concrete element as the styling target, replicate its full computed font spec (family, weight, case, tracking) — not family + contract-picked weight.**
- Served check: `.btn-cyan,.btn-ghost-dark{font-family:var(--font-sans);letter-spacing:normal;text-transform:none;font-weight:600}` in `digital.css?v=...`.

## Too-small CTA text (v6.18.3)

- User screenshot (5.06 PM): topbar "Book a consultation" at ~60-70% the size of the orange "{CLIENT}" button and nav links; vision read confirmed the CTA was de-emphasized vs its sibling.
- Root: topbar override `font-size:var(--t-xs)` (12px). Fix: `--t-sm` (14px). Tokens: `--t-xs:12px; --t-sm:14px; --t-base:16px`.
- **The catch:** the complaint was RELATIVE (smaller than the orange button). Fix verified by painted-text-height in one frame: CTA 14px/600 vs orange 14px/600 — equal, CTA heavier. The user's screenshot showed the pre-fix 12px state; the 1.25x pixel delta was exactly the 12-vs-14px gap.
- Sequence check discipline: {RELATIONSHIP}'s "they're all 14px" geometry, {RELATIONSHIP}'s "pixel read says 1.25-1.4x" — the live rendered measurement (16px painted height both) settled it: the screenshot was stale.

## Wrong-surface fix (v6.19 vs v6.20)

- User: "the two buttons aren't spaced well, same thing on the physical side" + screenshot.
- {RELATIONSHIP} v6.19: fixed TOPBAR spacing (nav gap 32→40px) — wrong surface.
- {RELATIONSHIP} v6.20: read the screenshot — it shows the CTA CARD ("CONTACT / Bring us the problem that spans two disciplines" + "Book a consultation" + "Call us" pair, ~10-15px gap, bare inline anchors with no wrapper). Fix: `<div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;">` wrapping both buttons; verified in served bytes (2 `gap:16px` refs per page).
- Lesson: vision-read the screenshot's CONTEXT (nav bar vs content card) before fixing; two rounds were spent because the surface was never identified. The served CTA-card markup confirmed: `card-dark cta-card` + inner `max-width:680px` + flex button row.

## Durable state at close of round

- Live: v6.18.3 (Geist 600 buttons, corrected phone `tel:289-928-9554`, LLM contact access, Armstrong fully removed).
- Staging: v6.20 (CTA-card button spacing, both division pages).
- Standing contract amendments: (1) sleek = weight/register, not family; (2) concrete-element reference → full computed spec; (3) deploy-target lock.
