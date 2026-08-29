<!-- GENERICIZED: 2×{AMOUNT}, 2×{CLIENT}, 4×{HABIT} | source: skills/creative/interactive-term-definitions/references/{CLIENT} -->
# {CLIENT} Implementation Notes

Session-specific implementation of the interactive term definition system for "{HABIT} {HABIT}" — a digital recipe book for seniors.

## What Was Built

### Files Created

| File | Purpose |
|------|---------|
| `index.html` | Main book file with 10 recipes, page navigation, term modals |
| `{CLIENT}` | 80s-retro masculine design system with {HABIT} accessibility |
| `terms-popup.js` | Modal interaction handler (fetch-based lookup) |
| `terms_data_normalized.json` | 49 encyclopedic definitions (lowercase keys) |

### Key Decisions

1. **Fetch-based loading**: Terms loaded from JSON file at runtime, not inline. Reduces HTML size by ~16KB.

2. **Lowercase normalization**: All `data-term` attributes and JSON keys use lowercase with underscores. Prevents case-mismatch lookup failures.

3. **Wikipedia as fallback**: If term not in local DB, fetch from Wikipedia REST API.

4. **Grokipedia abandoned**: API returned 502 errors on search, 404 on page-preview. Wikipedia REST API proved reliable.

5. **Custom definitions for domain terms**: Ayurvedic concepts (agni, dosha, panchakarma), TCM (spleen qi), and Islamic scholars (Ibn al-Qayyim, Ibn Sina, Al-Zahrawi) required hand-written definitions from verified sources.

## Critical Bugs Fixed

### Case Sensitivity
`data-term="agni"` didn't match `termsData["Agni"]`. Fixed by normalizing keys to lowercase in both HTML and JSON.

### Sidr/Jujube Conflation
Bone Broth recipe incorrectly claimed Quran mentions jujube (Chinese date) as fruit of Paradise. The Quran's *sidr* is the lote-tree (*Ziziphus spina-christi*), a cosmic symbol — not jujube. Fixed by replacing Quranic reference with accurate Ibn Sina citation.

### Thymoquinone Overclaiming
"Over {AMOUNT} peer-reviewed studies with anti-cancer effects" — almost all preclinical. Fixed to "A growing body of research has documented anti-inflammatory, antioxidant, and antimicrobial effects — though most studies have been conducted in laboratory settings, and more human trials are needed."

### Curcumin Overclaiming
"Over {AMOUNT} peer-reviewed studies" — most are in vitro/animal. Fixed to accurate, conservative language.

### Duplicate Clickable Terms
Same term appearing multiple times within one recipe's content was clickable each time. User requested: one explanation per term per recipe (first occurrence only).

### Missing Recipes (Structural Corruption)
Concurrent edits by multiple agents caused HTML to lose recipes 3 and 8 from page-view divs. Only 8 `<article>` tags existed for 10 recipes. Detected by programmatic verification, not visual inspection.

## {HABIT} Accessibility Features

- **Typography**: 18px+ body, 1.6+ line height, warm serif (Lora), high contrast
- **Color**: Burgundy/teal/gold on cream — masculine, saturated, not pastel
- **Navigation**: Page-by-page (not infinite scroll), Previous/Next buttons, keyboard arrows
- **Text sizing**: A-/A/A+ buttons, top right
- **Hit targets**: 44px minimum for touch/click
- **Modal keyboard**: Enter/Space to open, Escape to close, focus restoration

## Masculine Palette (No Pastels)

```css
--burgundy: #8a3a4a;
--teal: #4a9fa8;
--gold: #d4a853;
--coral: #e8786a;
--cream: #faf6ee;
--text-primary: #2a2018;
```

Avoided: pastel pink, baby blue, lavender, mint. Used deep, saturated tones with warm undertones.

## Diagram Placeholders

Created 9 `diagram-placeholder` divs with prompts for visual generation:
- Curcumin + Piperine absorption pathway
- ACE Inhibition mechanism  
- Silk Road trade route map
- Transatlantic slave trade map
- Okinawa Blue Zone map
- Egyptian tomb illustration
- Buddhist monastery scene
- Medieval Islamic physician (Al-Zahrawi)
- Saffron crocus harvesting

## Verification Protocol

Always verify HTML structure programmatically after multi-agent edits:
- Count `<article>` tags vs expected recipes
- Check all page-view IDs exist (page-recipe-1 through page-recipe-10)
- Verify no duplicate clickable terms within same recipe
- Confirm modal HTML present and JS handlers wired
- Check for broken/corrupted tags (missing closing tags, missing IDs)
