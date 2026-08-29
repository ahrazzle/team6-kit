<!-- GENERICIZED: 2×{AMOUNT}, 6×{CLIENT}, 6×{HABIT}, 13×{RELATIONSHIP} | source: skills/creative/book-creation/SKILL.md -->
---
name: book-creation
description: Build paginated HTML books with multi-agent team.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent-book, paginated-html, {HABIT}-readability, team6, islamic-content, evidence-honesty]
    related_skills: [claude-design, client-review-package, popular-web-designs]
---

# Book Creation (Team6 Multi-Agent)

Build paginated HTML books using Team6's multi-agent workflow. This skill covers the full lifecycle: research → design → build → QA, with specific conventions for {HABIT} readability, Islamic authenticity, health evidence honesty, and interactive features.

## When to use

- User asks for a "book," "recipe book," "mini book," or similar HTML deliverable
- Multi-agent team ({RELATIONSHIP} orchestrator, {RELATIONSHIP} architecture, {RELATIONSHIP} design, {RELATIONSHIP} build, {RELATIONSHIP} research, {RELATIONSHIP} QA) is involved
- The book targets {HABIT} readers (60+) who need large type, high contrast, and intuitive navigation
- Content requires Islamic authenticity with honest sourcing
- Health/medical content requires evidence-level labels (High/Moderate/Traditional)

## When NOT to use

- Single-page landing pages or decks — use `claude-design`
- Stakeholder review packages with decision gates — use `client-review-package`
- Pure research or writing tasks — use appropriate domain skill

## Core principles

### 1. IDEA.md is canonical — verify against it, not summaries
The user's `IDEA.md` is the single source of truth. When rebuilding or updating, **read the file** — never trust a teammate's summary of what it contains. Multiple QA failures in this project came from agents rebuilding from memory instead of the actual file.

### 2. File-level QA, not claim-level QA
When reviewing a teammate's work, **read the actual files** (`read_file`, `search_files`). Do not accept status reports like "✅ 48 ingredients now have amounts" without verifying. Claimed fixes repeatedly did not exist in the live HTML.

### 3. Recipe lists change — always check the finalized list
Recipe lists go through multiple iterations for safety ({HABIT} drug interactions), geographic diversity, and evidence honesty. The finalized list is locked in IDEA.md. Never rebuild from an old version — always check the current IDEA.md first.

### 4. Class names must match between JS and HTML
When implementing interactive features (clickable terms, navigation, modals), the CSS selectors in JavaScript must exactly match the class names in HTML. A mismatch means the feature is completely non-functional and users see no error.

### 5. Navigation tracking systems must not conflict
If you have click-based page navigation, do NOT add scroll-based detection that updates the same state variable. They will fight and the page counter will jump erratically.

### 6. Evidence honesty in health claims
Never claim "X peer-reviewed studies" without verifying the actual count. Most herbal research is in vitro/animal — human clinical trials are far fewer. Use evidence badges (High/Moderate/Traditional) on every health claim. Specific claims to avoid or soften:
- Curcumin: ~{AMOUNT} total studies but most are not human RCTs
- Thymoquinone: ~{AMOUNT} studies but almost all preclinical
- Hibiscus: ~8 mmHg SBP reduction, not "comparable to prescriptions" (which achieve 10-20 mmHg)
- Sage: small safety/tolerability trials, not large efficacy studies

### 7. Islamic authenticity — no forced theology
Present cultural origins honestly. Do not fabricate Islamic connections for Ayurvedic/Buddhist-rooted recipes. Highlight genuine connections (Black Seed hadith, Quranic honey verse, Ibn al-Qayyim references). Distinguish between Islamic, Ayurvedic, and Buddhist traditions where they overlap. Always verify hadith numbers against authoritative sources.

### 8. {HABIT} accessibility is non-negotiable
- Body text: 18px minimum, 1.6+ line height, warm serif font
- High contrast (WCAG AAA preferred)
- Page-by-page navigation (not infinite scroll)
- Text size controls (A-/A/A+)
- No intense physical demands in recipes (flag heavy lifting, long active simmering)
- "Where to Find Ingredients" section for each recipe
- Pantry-availability icons (🟡🔴)

### 9. Visuals must be actual visuals, not placeholders
The user explicitly wants images, diagrams, maps, anatomical illustrations — not placeholder boxes with "Botanical illustration of X" text. Source from Unsplash, Wikimedia Commons, or create SVG diagrams. If an image cannot be sourced, leave the container blank with a prompt for the user to generate.

### 10. Term clickability requires full implementation
Clickable terms need:
- Matching class names between JS selector and HTML
- Modal HTML structure present in the page
- Full encyclopedic definitions (not 50-character tooltips)
- Keyboard accessibility (Enter/Space to open, Escape to close)
- Wikipedia or local JSON fallback for terms not in database

## Workflow

### Phase {CLIENT}: Research & Ideation
- {RELATIONSHIP} researches ingredients, health evidence, Islamic connections
- {RELATIONSHIP} proposes recipe list with geographic spread and safety analysis
- Present to user for approval before building

### Phase {CLIENT}: Design System
- {RELATIONSHIP} builds CSS design system with tokens (colors, typography, spacing)
- Masculine aesthetic: bold, angular, saturated — no pastels
- 80s retro as accent, not foundation
- Evidence badges, context block styling, clickable term styling

### Phase {CLIENT}: Build
- {RELATIONSHIP} assembles HTML from {RELATIONSHIP}'s design system + {RELATIONSHIP}'s research
- Page-by-page navigation with Previous/Next buttons and keyboard support
- Clickable terms with modal system
- Ingredient quantities (not just names)
- Evidence badges on every "Why This Heals" callout
- Safety warnings for hot liquids, heavy lifting, drug interactions
- "Where to Find Ingredients" section per recipe

### Phase {CLIENT}: QA
- {RELATIONSHIP} reads actual files (not summaries)
- Verifies: recipe list matches IDEA.md, quantities present, hadith numbers correct, evidence claims honest, Islamic connections authentic, clickable terms functional (class names match, modal HTML present), no conflicting navigation systems
- Reports specific line numbers and exact issues

### Phase {CLIENT}: Iterate
- Fix only what QA flagged
- Re-verify fixes in actual files (not claims of fixes)
- Do not rebuild from scratch unless the foundation is broken

## Required components

1. **Title page** — decorative frame, title, subtitle, attribution ("Compiled for...", "by...")
2. **Table of Contents** — numbered list with subtitles, clickable navigation
3. **Recipe pages** — one per page, each with:
   - Header (number, title, subtitle, meta: prep time, difficulty, serves)
   - Tags (pantry availability, health benefits, warnings)
   - "Why This Heals" callout with evidence badge
   - Ingredient list with quantities and pantry icons
   - "Where to Find Ingredients" section
   - Step-by-step method with woven context blocks (health, history, Islamic, cultural, science, funfact)
   - Unsplash image or SVG diagram
   - "Back to Contents" link
4. **Footer** — book title, attribution, disclaimer
5. **Navigation** — Previous/Next buttons, page counter, keyboard arrows
6. **Text size controls** — A-/A/A+ buttons
7. **Clickable terms** — modal with full definitions, Wikipedia fallback

## File layout

```
workspace/
├── IDEA.md              # Canonical source — always check this
├── index.html           # The book
├── {CLIENT}         # Design system
├── terms-popup.js       # Clickable terms system
├── terms_complete.json  # Local term definitions database
├── PHYSICAL_AUDIT.md    # {HABIT} safety audit
└── ASSETS/              # Images, diagrams
```

## Pitfalls

### Rebuild regresses recipe list
**Symptom:** Live HTML has old recipes (Ashwagandha, Chyawanprash) instead of finalized ones (Saffron, Hibiscus, Sage).
**Cause:** Agent rebuilt from memory or old file instead of current IDEA.md.
**Fix:** Always read IDEA.md first. Never trust summaries of what it contains.

### Clickable terms don't work
**Symptom:** Clicking highlighted terms does nothing.
**Cause:** JS uses `.term` selector but HTML uses `class="clickable-term"`. Or modal HTML is missing from page.
**Fix:** Use both classes (`class="term clickable-term"`). Add `<div id="term-popup">` modal HTML before `</body>`.

### Evidence badges missing or dishonest
**Symptom:** "Why This Heals" has no evidence label, or claims are overstated.
**Cause:** Agent used inflated study counts or omitted badges entirely.
**Fix:** Add `<span class="evidence-badge evidence-moderate">Moderate</span>` to every heals callout. Verify all study counts.

### Navigation counter jumps
**Symptom:** Page counter changes when scrolling, fighting with click navigation.
**Cause:** Both click-based `goToPage()` and scroll-based detection update `currentPage`.
**Fix:** Use only ONE navigation tracking system. Remove scroll-based detection.

### Ingredient quantities missing
**Symptom:** Ingredient list shows only names, no amounts.
**Cause:** Agent stripped quantities during a rebuild.
**Fix:** Include quantities in HTML: `<span class="ingredient-qty">1 cup</span>`.

### Hadith number wrong
**Symptom:** Black seed hadith cited as Bukhari 5687 instead of 5688.
**Cause:** Typo not caught in QA.
**Fix:** Verify all hadith numbers against authoritative sources before delivery.

### Subtitle inconsistency
**Symptom:** IDEA.md says one subtitle, HTML says another.
**Cause:** Subtitle changed during iteration but not synced everywhere.
**Fix:** Use the latter/more recent subtitle consistently across all files.

## Related skills

- `claude-design` — visual quality bar for individual pages
- `client-review-package` — stakeholder review workflow (different purpose)
- `popular-web-designs` — brand aesthetic matching
