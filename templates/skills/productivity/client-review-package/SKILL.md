<!-- GENERICIZED: 5×{AMOUNT}, 1×{CLIENT} | source: skills/productivity/client-review-package/SKILL.md -->
---
name: client-review-package
description: Build paginated HTML client-review packages before build — shared CSS/JS, sidebar nav, prev/next, i18n toggle, watermarked, legibility-audited, with dopamine motion.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [stakeholder-review, client-package, mockup-to-package, decision-cards, sign-off-gate]
    related_skills: [sketch, claude-design, popular-web-designs, buyer-rfp]
---

# Client Review Package

Use this skill when the user needs to produce a navigable HTML package for a client or stakeholder to review and sign off on before a build or other work proceeds. The package consolidates what was produced so far — mockups, screenshots, decision points, design rationale, backend proposals — into one self-contained artifact.

This skill is for the packaged review deliverable that the client opens to approve direction before work starts. Recent guidance (August 2026 session): packages should be **paginated into separate HTML pages per section** (not one endlessly scrolling document) to fix sidebar scroll-synced highlighting problems; design source files should be **rendered as live HTML/CSS tokens, never screenshotted**; when embedded mockups are in iframes, the i18n toggle must **propagate language choice to each iframe via postMessage + localStorage**; legibility should be **audited programmatically** (computed-style luminance check) not just visually; packages should include **dopamine micro-animations** (page-load fade-in, scroll reveal, stamp throb, toggle spring, progress fill, button press, hover lift) and a **multi-layer watermark** (HTML comment, hidden element, JS marker, SVG favicon comment, meta tag); and inline-English leaks in Arabic pages should be checked with `scripts/scan_language_leaks.py` rather than by eye.

See `references/design-tokens-extraction.md` for the design-token extraction workflow and the {CLIENT} design tokens as a worked example, `references/design-direction-from-logo.md` for resolving contradictory client design files (logo wins; verify Hijri dates and arithmetic from client assets), and `references/parallel-language-editions.md` for building a genuine (non-translation) parallel English edition.

## When to use

- Before a build starts and the client must approve UI/UX, feature set, aesthetic, and flagged decisions
- After a round of wireframes/mockups, first MVP, or any milestone where the client reviews completed work and communicates alterations
- When there are explicit decision points the client must make and the deliverable must make them easy to understand and act on
- When mockups exist but the client needs context alongside the visuals — rationale, backend proposals, defect remediation, phased plan

## When NOT to use

- Pure design exploration / throwaway variants — use `sketch`
- A single designed landing page or deck with no review/gate structure — use `claude-design`
- Extracting action items from a document — use `document-to-action-items` or `meeting-action-items`
- A formal design-token spec file — use `design-md`
- A buyer-side RFP / scope lock the client must review first — use `buyer-rfp`. Do not start this package in the same turn as an RFP draft. Stop until the user redlines or says issue.

## Core principle

**The page opens to content, not blank space.** On desktop, a fixed sidebar navigation + fixed main content area means the cover/title appears at the top of the viewport immediately. A sticky sidebar that occupies document flow pushes main content below the fold — that looks broken. Always verify the page top before delivering.

## Required components

Every client review package must contain these, in this order:

1. **Cover** — gradient banner, title, subtitle, meta (who, when, status, purpose). Status badge says "needs review/sign-off" when the package is the first gate.
2. **Navigation** — numbered sidebar. Desktop: fixed to viewport, `.app` gets `margin-left`. Mobile: overlay that slides in from left when toggle tapped.
3. **Context** — why this package exists, what the client will see, what the client must do.
4. **Mockups/screenshots** — embedded images with captions. Each screenshot captioned with what it demonstrates.
5. **Decisions** — each decision as its own card with: number badge, question, where it's raised, 2-3 options, the team's recommendation pre-selected/marked, and a "needs client sign-off" badge. Clickable options if interactive.
6. **Feature map** — items mapped to phase/priority with status (sign-off needed / deferred).
7. **Defect remediation** (if applicable) — what's broken, root cause, how the rebuild fixes it, how admin prevents recurrence.
8. **Backend / architecture proposal** — what's being built, stack, adapters, lock-in assessment, data ownership rationale. Not necessarily fully functional, but real and reviewable.
9. **Phases / plan** — phased plan with gates.
10. **Gate / summary** — what the client must approve to pass this pause, what happens after sign-off.

## Workflow

### 0. Extract design tokens from graphic design source files (if provided)

If the client provides graphic design source files, extract the tokens and render them as live HTML/CSS in the package — **never screenshot the source files**. See `references/design-tokens-extraction.md`.

### 1. Gather what exists

Read the RFP, audit, IDEA, and any prior plans. Identify:
- What mockups exist or need to be built
- What decisions the client must make (extract from RFP contested decisions, flagged items, open questions)
- What rationale the client needs to understand (design direction, backend approach, defect remediation, phased plan)
- What screenshots to capture (serve mockups, screenshot them)

**Fresh-build discipline (learned the hard way).** When the user hands you an execution plan for a NEW/alternate proposal and says "start from zero" or "don't use prior work", obey it literally — do NOT pull mockups, generators, or content from sibling/older project versions on disk, even when they look like a head start. A prior session's package is a DIFFERENT deliverable for a DIFFERENT proposal; copying it contaminates the alternate track and the user will correct you. Build the package fresh in the workspace the plan names. The one legitimate reuse is the plan + RFP + audit documents themselves (they are the handoff, not prior work).

### 2. Build mockups first (if not existing)

Use `sketch` for initial exploration. Then build the key screens as standalone HTML mockups — one per important screen. Arabic-first RTL if the product is Arabic-first. Each mockup: self-contained HTML, Cairo + system font, teal or brand accent, service-specific colours.

### 3. Serve and screenshot

Spin up a static server for the mockups directory. Navigate each mockup in the browser. Capture screenshots via `browser_vision` or the browser screenshot facility. Save to `assets/` in the package directory.

### 4. Assemble the package HTML

Single self-contained HTML file. Inline CSS in `<style>`, inline JS in `<script>`. Cairo for Arabic, IBM Plex Sans for Latin. CSS variables for tokens. Use:
- Fixed sidebar nav (desktop: pinned to viewport, `.app` gets `margin-left`). Mobile: overlay that slides in from left when toggle tapped.
- Numbered sections matching nav items
- Decision cards with clickable options
- Embedded screenshots (relative paths from same directory)
- Cover banner with gradient

### 5. Verify before delivery

Open the package in the browser. **Check the page top** — the cover/title must be visible at the top of the viewport without scrolling. If there's blank space above content, the layout is broken (usually sidebar `position: sticky` pushing content below fold). Fix: sidebar `position: fixed` + main content `margin-left` on desktop.

Take a screenshot of the package to verify visually. Confirm all screenshots load, all decision cards render, all sections present.

**Paginated packages — visual verification caveat.** When each section is a separate short HTML page (not one long scrolling document), `browser_vision` screenshot capture may return a black/blank image because the page content fits within the viewport with no scroll context — the viewport capture tool sees an empty frame. This is a tool-side limitation, not a page defect. For paginated packages, verify visually with `browser_snapshot` (full accessibility tree) + `browser_console` (computed styles, element counts, swatch/stamp/iframe presence) rather than relying on the screenshot alone. A longer page (e.g. a 12-card decisions page) will usually capture fine; short pages (cover, design-system section) are the ones that fail capture. Verify by checking that CSS is loaded (`document.querySelectorAll('link[rel=stylesheet]').length > 0`) and that key elements have the expected computed styles, not just that the screenshot is non-blank.

**Headless-Chrome screenshot QA for pixel-level review.** When you need an actual rendered image to review (RTL correctness, stamp clipping, overflow, motion states), capture pages with headless Chrome and inspect the PNG with vision analysis:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars --no-sandbox \
  --virtual-time-budget=8000 --window-size=1440,1600 \
  --screenshot=page.png "http://127.0.0.1:8080/ar/section-07.html"
```

- Use `--headless=new` (legacy `--headless` hangs on modern Chrome) and a `--virtual-time-budget` (~8000) so fonts/animations settle before capture.
- **Run captures sequentially, one per background process** — parallel Chrome instances contend and stall for minutes. Expect ~60s per page.
- **Set the window height taller than the content** (`--window-size=1440,1600+`) or the bottom of the page is cropped out of the screenshot; the vision reviewer will misread cropping as a layout bug.
- This is how the RTL-sidebar-placement bug, the clipped stamp badge, and the count-up-mid-animation total were all caught. The vision review reads "totals" from the image — a mid-count rAF animation shows a wrong number (e.g. 247.85 instead of 264.50), which is why price count-ups need the `setTimeout` fallback noted below.

**Serving the package — watchdog the static server.** A bare `python3 -m http.server ... &` background process can die (macOS process lifecycle, Hermes session-parent cleanup, transient port contention — the exact trigger is environment-dependent and not reliably isolable). When it dies, the port goes dark and all verification/traffic stops. Wrap the server in a restart loop so a death is recovered automatically:

```bash
while true; do
  python3 -m http.server <port> --directory /path/to/package
done
```

Run this loop in the background. Verify the port is live (`curl -sI http://localhost:<port>/<page>` → 200) after starting, and re-check after any idle period before relying on the server for browser-based verification. This is especially important for long evaluation passes where the server must stay up unattended.

### 6. Deliver

Serve from a static server, or ship the whole directory. The package should be openable directly (`file://` or `http://`). Send the directory to the client.

## Pitfalls

### Layout breaks on desktop: sidebar pushes content below fold
**Symptom:** Page opens to blank space; content only appears after scrolling down.
**Cause:** Sidebar is `position: sticky` (or `static`/`relative`) on desktop — it occupies document flow and pushes `<main>` below its height.
**Fix:** Sidebar `position: fixed; top:0;left:0;bottom:0; width:220px` on desktop (≥969px). `.app` gets `margin-left: 220px`. Mobile: sidebar `position: fixed; transform: translateX(-100%)` slides in from left when toggle tapped — overlay, doesn't block content flow.

### Bilingual text leakage in an Arabic page (D-03 defect)
**Symptom:** English words appear in Arabic UI text (e.g. "before the booking" in an Arabic heading, Latin city names in Arabic descriptions).
**Cause:** Copy written with English insertions, or locale files not reviewed.
**Fix:** All visible strings in Arabic pages must be Arabic (or Arabic-transliterated). City names, service names, statuses — all in Arabic. This is a core quality requirement, not a nice-to-have, for Arabic-first products.

**Audit programmatically, don't eyeball.** Grepping the file or skimming the rendered page misses leaks and over-reports legitimate terms. Use `scripts/scan_language_leaks.py <dir>` (strip `<script>/<style>/<head>`/comments, extract visible text, flag Latin words, drop the KEEP whitelist). It separates genuine leaks from legitimate proper nouns so you don't "fix" the wrong things.

**Distinguish a genuine leak from a legitimate term.** Do NOT translate: brand/company names (Bshiyat, SAASTECH.IO), font families (IBM Plex Sans Arabic/Latin, Google Fonts), frameworks (React Native, Expo, Fastify, PostgreSQL), API/file identifiers in backend tables (`services.ts`, `/api/v1/...`, `adapter`, `stub`), the contact identity (`critical@bshiyat.tech`), HTML entities (`&nbsp;`), or technical acronyms (P0..P5, RFQ, VAT, ZATCA, JWT, JSONB, D-01..D-07). Only words outside that set are real leaks. Real ones seen in practice: `ancestor` (mistranslation of "admin stub"), `Phase`/`Phases`, `Tuesday` (corruption of "تركية"), `Locale`, `canonical`, `cArabic-first` (typo), `البUILD`.

### Re-running a generator wipes manual fixes to generated HTML
**Symptom:** A manual fix to `section-11.html` (or any generated page) disappears after `generate_package.py` / `generate_en_package.py` runs.
**Cause:** The generators overwrite the HTML files from their inline Python source strings. Any edit made directly to the generated `.html` file is lost on regeneration.
**Fix:** Treat generated HTML as build output. To make a durable change, edit the generator's inline source strings and regenerate — or, if the fix is a one-off (a polish pass on already-shipped output), apply it to the generated file AND record in the handoff that re-running the generator will lose it. Never re-run a generator "to be safe" after a manual polish pass.

**Generator architecture that reduces this risk.** Prefer a content-file + renderer split: page copy lives in `content_ar.py` / `content_en.py` (META + BODY dicts), the renderer (`build_package.py`) wraps them in a shared shell. Two hard-won pitfalls with this pattern:
- **String-concatenation tokens inside triple-quoted strings do NOT execute.** `BODY["x"] = dict(html="""...''' + ICON_CLOCK + '''...""")` renders the literal text `''' + ICON_CLOCK + '''` — Python does not evaluate `+` inside a string literal. Fix: replace with a placeholder token (`@@ICON_CLOCK@@`) and have the renderer regex-substitute it from the module namespace before writing HTML.
- **Constants must be defined before the dicts that use them.** If `ICON_*`/`SVG_MAP_*` are defined at the bottom of the content file but referenced in `BODY` at the top, import raises NameError. Define assets before `BODY = {}`, and keep only ONE copy of the constants block (a stray duplicate at the file bottom shadows the top one and confuses patching).

### RTL grid auto-flow — do NOT add `html[dir="rtl"]` column overrides
**Symptom:** Arabic edition renders with the sidebar on the LEFT (or stage/side overlap).
**Cause:** An explicit override like `html[dir="rtl"] .deck{grid-template-columns:1fr 264px}` combined with `grid-column` placements on children. Grid auto-flows columns right→left in RTL by itself — the same `grid-template-columns: 264px 1fr` declaration puts the 264px sidebar on the right in Arabic and left in English automatically. The override double-reverses it.
**Fix:** Declare the grid once with logical order (sidebar as first child, `grid-template-columns: 264px 1fr`), and let the writing direction flip the flow. Remove RTL-specific grid overrides; `inset-inline-start/end` and logical properties handle the rest.

### Dual Hijri/Gregorian dates — verify against a converter, never trust source material
**Symptom:** A mockup shows "الأحد 16 أغسطس 2026 · 22 صفر 1447 هـ" — the Hijri date does not correspond to the Gregorian one.
**Cause:** The pairing was copied from the client's own design files. Even client-supplied design assets carry wrong dates (22 صفر 1447 is ~Sept 2025; 16 Aug 2026 is actually 3 ربيع الأول 1448 هـ). For a Saudi client this is a credibility killer — they WILL notice a wrong Hijri date.
**Fix:** Every Hijri/Gregorian pairing in a Saudi-facing package must be checked against a real Hijri calendar (web search / converter) before shipping. Fix all occurrences in BOTH language editions — the same wrong date hides in AR and EN copies.

### Price-integrity self-check — the package must not contain the defect it sells against
**Symptom:** On a live-in booking mockup, "pay in full" prices a 3-month contract ({AMOUNT} = {AMOUNT}×3×0.95) while the instalment breakdown prices a 6-month contract ({AMOUNT} + 4×{AMOUNT} = {AMOUNT}). Both payment options must price the SAME term.
**Cause:** Option rows and breakdown lines were written independently without reconciling the arithmetic.
**Fix:** Before delivery, run arithmetic reconciliation on every pricing mockup: full-payment total and instalment legs must equal the same term × unit price (check both the option labels and the breakdown rows). When the whole engagement is about fixing a pricing defect (D-01 class), shipping a mockup with internally inconsistent pricing is disqualifying. Also: format all money with thousands separators, and add a `setTimeout` fallback after any rAF count-up animation so a total can never sit half-counted on screen (background tabs and headless screenshots freeze rAF mid-count).

### Screenshot images don't load in the package
**Cause:** Package served from a different directory than `assets/`, or wrong relative paths.
**Fix:** Serve the package directory from a static server so `assets/*.png` resolves relative to `index.html`. Or use `file://` directly. Verify each `<img src>` is correct relative to the HTML file's location.

### Decision cards don't have a recommendation marked
**Cause:** All options presented as equal; client doesn't know what the team proposes.
**Fix:** The team's recommended option should be visually marked (selected state, checkmark, "recommended" label). Client can still pick another, but the default should be visible.

### No gate/next-steps section
**Cause:** Package shows visuals and decisions but doesn't say what the client must do to proceed.
**Fix:** Always include a gate section: what the client approves to pass this pause, what happens after sign-off. The package is a gate, not just a showcase.

## File layout (example)

```
pause-package/
├── index.html            # the review package (self-contained)
├── assets/
│   ├── 001-home.png
│   ├── 002-booking-funnel.png
│   ├── 003-order-tracking.png
│   ├── 004-cancellation.png
│   └── 005-admin.png
└── mockups/              # source mockups (optional to ship)
    ├── 001-home-booking-entry/index.html
    ├── 002-booking-funnel/index.html
    ├── 003-order-tracking/index.html
    ├── 004-cancellation-with-refund/index.html
    └── 005-admin-pricing-manager/index.html
```

## Serving the package for review

Static server from the package directory:
```
python3 -m http.server <port> --directory /path/to/pause-package
```
Then open `http://localhost:<port>/index.html`.

To stop: kill the server process. To serve again: restart.

The package also works via `file:///` directly if opened from the filesystem, as long as `assets/` is a sibling of `index.html`.

## Sharable to client

Ship the whole `pause-package/` directory to the client. They can open `index.html` locally. All assets are relative. No build step, no server needed on their side (though a static server is nicer for presentation).

## Related skills

- `buyer-rfp` — write and get the buyer RFP signed **before** this package. If the user asked for RFP first, stop; do not assemble mockups in the same turn.
- `sketch` — for producing initial mockup variants before building the package
- `claude-design` — for the visual quality bar of individual mockups and the package itself
- `popular-web-designs` — if the client has a preferred brand aesthetic to match
