<!-- GENERICIZED: 2×{AMOUNT}, 10×{CLIENT}, 12×{RELATIONSHIP} | source: skills/software-development/web-build-verification/references/{CLIENT} -->
# {CLIENT} late rounds (v6.13 → v6.16): served-value disputes & the tone loop

Session detail behind SKILL.md §11e. All values verified against served staging bytes on {CLIENT}.

## 1. The 200px-vs-320px height dispute

- Context: after the user approved v6.13 (height revert from v6.12's taller terminal), two auditors disagreed on the served `.term-body` max-height. {RELATIONSHIP} claimed served showed `min-height:150px; max-height:320px`; {RELATIONSHIP} read `max-height:200px`.
- Settlement: one cache-busted fetch of the CURRENT versioned ref (`gateway.css?v=521b04` — read from the served HTML, fetched with fresh `?cb=`): `.term-body{max-height:200px}`. No `320px` anywhere in the served file. {RELATIONSHIP}'s "stale cache" explanation was wrong — the value simply wasn't in the deployed CSS (local file differed from what was deployed).
- Outcome: the user's intent (short sleek terminal) WAS satisfied — 200px is the pre-v6.12 value. The dispute was purely about claimed numbers; served bytes settled it.
- Rule extracted: any claim about a served value is only valid from a cache-busted fetch of the current versioned ref. "Stale cache" is itself a claim, not evidence.

## 2. Conflicting favicon-hash audit

- My earlier verification: favicon SHA-256 `cccf1c9600891e564627bb35cba538aab3d025cb`, {AMOUNT} bytes, byte-identical (`cmp -s` passes) to `assets/svg/{CLIENT}`.
- {RELATIONSHIP} reported `a720f157…` — a different hash. Both could not be the current served truth.
- Re-fetch (fresh `?cb=` on both URLs): `cccf1c96…` both, {AMOUNT} bytes both, `cmp` IDENTICAL. The standing claim held; the other number was a stale read (possibly from before a redeploy).
- Rule extracted: conflicting auditor hashes → re-fetch fresh once, publish the winner, and note the loser was stale. Never leave two conflicting verification numbers in the record.
- Technique worth keeping: favicon-as-brand-asset verification = `shasum` both + `cmp -s` — byte-identity, not approximation.

## 3. Same class ≠ same render (CTA container asymmetry)

- User: "these two containers at the bottom of each division page are different sizes" (screenshots {CLIENT} 13:32).
- Byte check: BOTH pages carried `cta-card` (1 each) — class unified, but `card-dark` counts differed: Digital 3, Physical 1.
- Vision reads of the two screenshots: Digital CTA ~60–70% viewport width, Physical ~90–95% (one read) / ~40–45% (other read) — the exact percentages disagreed between vision passes, but BOTH agreed the widths differed.
- Root cause ({RELATIONSHIP}'s fix): Digital's CTA had `card-dark cta-card` + inner `max-width:680px` wrapper; Physical had inline `max-width:min(100% - 48px, 900px)` with no inner wrapper. Same class, different structure and width cap.
- Fix that landed (v6.14.1): shared `cta-card` width rule in `system.css` (`max-width:min(100% - 48px, 680px)`, margin-inline auto), Physical's inline 900px cap corrected to 680px. Verified: both 680px.
- Rule extracted: class unification ≠ structural unification. Verify per-page rendered width/structure; count class occurrences per page as the cheap tell for extra wrapping.

## 4. The "sleek" font loop (user correction)

- User ask 1 (v6.15): "use a different sleeker font for those three buttons" — after Geist Mono had been applied to Digital wordmark + CTAs.
- Attempt 1: Manrope 700 ({RELATIONSHIP}: "sleek geometric sans, 700 weight"). User: "I said sleek, you chose a thick font."
- Attempt 2 (v6.16): Space Grotesk 500 — accepted tone. User also asked: "use the {CLIENT} logo for the favicon please" (done, byte-identical).
- The correction that landed was NOT a new family — it was dropping to weight 500. Geist Mono read technical (mono + uppercase + wide tracking); Manrope 700 read heavy; Space Grotesk 500 reads futuristic + legible.
- Standing design contract (ratified by room, {RELATIONSHIP}): for {CLIENT}, "sleek" = weight 500–600 geometric sans, light tracking, sentence case — NOT bold, NOT mono, NOT heavy. "Sleek" is a weight/register signal, not a family-shopping exercise.
- Verified served state (v6.16): `@font-face` Space Grotesk 400/500 self-hosted; scoped rule `.btn-cyan,.btn-ghost-dark{font-family:'Space Grotesk';font-weight:500;letter-spacing:0.03em;text-transform:none}`; `.btn-orange` zero overrides.

## 5. Brand-scoped treatment (the scoping correction)

- {RELATIONSHIP}'s first v6.15 attempt used a broad `.btn` rule — would have applied Geist Mono to the orange "{CLIENT} ↗" switcher (Physical-brand element).
- {RELATIONSHIP} narrowed it to `.btn-cyan` + `.btn-ghost-dark` (Digital-brand buttons only): 2× "Book a consultation" + 1× "Explore the practice". Served CSS carries a comment documenting the intent: "Scoped to the cyan/ghost Digital buttons only — the orange {CLIENT} switcher keeps its identity."
- Rule extracted: inside a shared component system with two brands, treatments are scoped to the target brand's classes, and the sibling brand's element is verified untouched in the same pass.

## 6. Dead anchor target (`/info` command)

- User asked for `/info` → `https://{CLIENT}#benefits`. Byte check: `id="benefits"` grep = 0 on the served Digital page — the anchor did not exist; the command would land dead.
- Also: the spec hardcoded the production hostname; relative `/digital/#benefits` resolves on both staging and live. {RELATIONSHIP}'s flag was correct and confirmed by the anchor-existence check.
- Rule extracted: verify anchor IDs exist on the target page before wiring nav commands; use relative URLs.

## 7. Working state at session end (for continuity)

- Live: v6.14.1 (approved push). Staging: v6.16 (Space Grotesk 500 buttons + {CLIENT} favicon) awaiting review.
- Standing: deploy-target lock (explicit `--target=live|staging` + second-agent confirm); design contract "sleek" rule; staging-first loop.
- Known non-blocking review items: Space Grotesk 500 legibility at nav-button scale ({RELATIONSHIP}); favicon legibility at 16–32px tab scale ({RELATIONSHIP} — simplified silhouette is the known fallback).
