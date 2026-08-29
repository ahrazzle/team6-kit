<!-- GENERICIZED: 5×{CLIENT}, 6×{HABIT} | source: skills/creative/interactive-html-publication/references/{CLIENT} -->
# {CLIENT} Build Notes

Session: {CLIENT} | Project: {CLIENT} — "{HABIT} {HABIT}"

## What Was Built

A 10-recipe digital book with:
- Page-by-page navigation (12 pages: title, TOC, 10 recipes)
- 29 clickable terms with modal definitions
- 38 context blocks (health/history/Islamic/cultural/science/funfact)
- 9 Unsplash hero images (black seed returned 0 results)
- 6 custom SVG visuals (Silk Road map, nitric oxide pathway, curcumin absorption, spice routes, timeline, body diagram)
- Text size controls (A-/A/A+)
- Print/PDF export stylesheet
- Masculine aesthetic (deep teal/burgundy/gold, bold typography, direct language)
- {HABIT} accessibility (18px+ body text, high contrast, large clickable targets)

## Key Technical Decisions

1. **Page navigation**: Used `div.page-view` with `display: none` / `.active` class. Fixed bottom nav bar with Previous/Next buttons. Keyboard navigation with Arrow keys and Space.

2. **Clickable terms**: `<span class="clickable-term" data-term="..." title="...">` with JS modal popup. Avoid wrapping inside HTML tags.

3. **API integration**:
   - Unsplash: `https://api.unsplash.com/search/photos` with `client_id` param
   - Grokipedia: `from grokipedia_api import GrokipediaClient` (NOT `grokipedia`)

4. **Custom SVGs**: Generated as separate `.svg` files, embedded with `<img src="...">`. Simplified paths for trade routes, anatomical diagrams, chemical processes.

5. **Masculine palette**: Deep teal (#2a7a82), burgundy (#6a2030), gold (#b88a3a). Coral as accent only. No pastels.

6. **{HABIT} readability**: Minimum 18px body text, 1.6+ line height, generous white space, large clickable targets.

## File Structure

```
{CLIENT}
├── index.html          # Main book (67KB)
├── {CLIENT}        # Design system (28KB)
├── ASSETS/
│   ├── *.svg           # Custom visuals
│   ├── *_hero.jpg      # Unsplash images
│   ├── unsplash_images.json
│   └── grokipedia_terms.json
├── IDEA.md             # Project scope
├── PHYSICAL_AUDIT.md   # {HABIT} accessibility audit
└── *.py                # Build scripts
```

## Lessons Learned

1. **Grokipedia module name**: Package is `grokipedia_api`, not `grokipedia`. Import fails silently if wrong.

2. **Unsplash rate limit**: 50 requests/hour for free tier. Cache results locally.

3. **Page navigation scroll**: Use `window.scrollTo({ top: 0, behavior: "smooth" })` AFTER making new page visible.

4. **Print stylesheet**: All `.page-view` must be `display: none` except `.active`, otherwise blank pages print.

5. **Clickable term wrapping**: Don't wrap terms inside HTML tags. Only replace in text content.

6. **Image hotlinking**: Unsplash images can be hotlinked directly via URLs.

## User Preferences Captured

- Masculine aesthetic: bold, angular, direct. No pastels, no whimsy.
- {HABIT} readability: large text, high contrast, page-by-page navigation.
- Islamic context: authentic connections only, no forced theology. No faces of Islamic figures.
- Content woven between steps: health, history, Islamic, cultural, science, funfact.
- Pantry-availability icons: 🟢 pantry staple, 🟡 easy to find, 🔴 specialty store.
