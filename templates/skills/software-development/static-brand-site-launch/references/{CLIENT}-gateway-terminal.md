<!-- GENERICIZED: 1×{AMOUNT}, 8×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/static-brand-site-launch/references/{CLIENT} -->
# {CLIENT} gateway + interactive terminal — working recipe (v6.x, 2026-08)

Session-specific detail for the {CLIENT} reference build. Companion to `references/{CLIENT}`.

## Universal terminal command map (single source of truth)

Data array drives BOTH dispatch and `/help` — no drift. Aliases grouped to one record:

| Command(s) | Action |
|---|---|
| `/help`, `help` | list all commands (rendered from same array) |
| `/digital`, `digital` | nav `/digital/` |
| `/physical`, `physical` | nav `/physical/` |
| `/home`, `/back`, `/reset` | nav `/` (landing) |
| `/portfolio`, `portfolio` | nav `/digital/#proof` (relative anchor) |
| `/contact`, `/book`, `/mail`, `/email` | mailto:info@{CLIENT} |
| `/faq`, `faq` | nav `/digital/#faq` |
| `/info`, `info` | nav `/digital/#benefits` (verify the anchor exists before shipping) |
| `/game`, `game` | nav {CLIENT} (configurable constant) |
| `/github`, `github` | nav github.com/{RELATIONSHIP} |
| `/call`, `/phone` | tel:416-500-4462 |

All page anchors relative (no staging hostname hardcoding). Raw non-slash text → POST `/api/ask` (LLM showcase assistant with honesty guard spine).

## Shared component shape

`assets/js/{CLIENT}` — IIFE exposing `window.{CLIENT}(cfg)`:
- cfg: `{root, api, commands, hint, gameUrl, intro, readyLine, focusDelay}`
- command map as data (see above), LOOKUP built from aliases
- `respond()`: slash → lookup → nav/mailto/tel; else fetch LLM, typeLine output
- `help()` renders from the map array
- click handler: `preventDefault + stopPropagation + focus()` (giant-anchor belt-and-braces)
- auto-type intro: types cfg.intro char-by-char (34ms), then "✓ <readyLine> — type a command below", focuses input
- `prefers-reduced-motion`: render final state instantly, no auto-type

Mount on landing (dark navy) and Digital page (dark navy) with different intro lines; same module, config differs.

## Gateway structure that survived review

- 2 halves sacrosanct (Digital left / Physical right, `grid-template-columns:1fr 1fr`)
- Digital half = `[content stack | terminal]`; Physical half = `[pipeline | content]` — flavour elements flank the center divider, content stacks on the outer edges (true mirror)
- Implemented via `.half{display:grid;grid-template-columns:1fr 1fr}` + `.half-stack` order rules: `.half.digi .half-stack{order:0}` (stack outer-left, terminal toward center), `.half.phys .half-stack{order:2}` (pipeline toward center, stack outer-right). A blanket `order:1` on half-stack produces the NON-mirrored layout (flavour on outer edges) that the user rejected.
- ENTER CTAs: real `<a class="enter">` underneath each stack (label → logo → headline → subtext → ENTER), Digital one bright cyan + glow (rgb({AMOUNT}) measured) so it's not contrast-invisible on navy; Physical orange.
- Panels are `<div class="half digi|phys">` — NEVER `<a class="half">` (giant-anchor bug).
- Mobile ≤820px: halves stack, flavour columns hidden.

## Incidents logged this session

1. **Root clobber:** `cp digital/index.html index.html` replaced the landing page on production ("the one thing I loved is gone"). Recovery: `git show <good-commit>:index.html > index.html`, redeploy, verify markers. Permanent guard: `scripts/predeploy-guard.sh` greps root for `.gw-hero` + `#askterm`, fails deploy otherwise.
2. **False rollback claim:** "live = v6.3" reported but bytes still served v6.5 (`/api/ask` 200). Lesson: verify served bytes, not claims. Real rollback: `git checkout <v6.3-sha> -- .` then `git rm` the leftover `api/ask.mjs` (checkout does NOT delete paths absent from the commit).
3. **Giant-anchor click bug** shipped 3×: panel `<a>` wrapping terminal → every click navigated. Fixed structurally (panel div), verified by clicking in a live browser (path stays `/`, focus termline).
4. **Stale-CSS vs new-HTML:** user's "weird text" and "old static terminal still there" were often cached renders of the OLD CSS against new HTML. Fix: versioned CSS refs in same commit + cache-bust probes (`?cb=`). Also: "terminal gone from landing" = cache; hard-refresh clears.
5. **Static vs interactive terminal on one page:** Digital hero had a static `d-device` console visual AND the interactive mount was appended mid-page. User: "static terminal still in old spot, that's where interactive should be." Fix: remove static visual, mount interactive at that position (after hero), delete standalone section, verify exactly one `#askterm` + zero `d-device`.
6. **Grid row-height loop:** `.gw-divider{height:120%}` in auto-row grid ballooned the row to 1624px; also the divider/spine had been nested inside the digi half by markup surgery. Fixed: height:100% + overflow:hidden + all columns as direct grid children + balanced divs.
7. **3-column misread:** team adopted an accidental 3-column render as the design; user clarified the layout was still 2 halves, the flavour elements just had more vertical room. Rebuilt as 4-columns-in-2-halves (mirror).
8. **Hollow-card false alarm:** grep saw padding-only `@media` overrides and called `.card-warm` hollow; full base rules had the real treatment. Verify with computed style or the full base rule, not the first grep hit.
9. **LLM on the front door:** unauthenticated chatbot on a consulting site = cost/injection/brand-reality risks; consensus = "showcase assistant" (explains what {CLIENT} does, routes to consultation, honesty guard spine), server-side key via Vercel env var, rate cap (10/min → 429), never client-side key.
