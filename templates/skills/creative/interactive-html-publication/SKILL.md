<!-- GENERICIZED: 1×{HABIT}, 1×{RELATIONSHIP} | source: skills/creative/interactive-html-publication/SKILL.md -->
---
name: interactive-html-publication
description: "Build interactive HTML books or digital publications."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
---

# Interactive HTML Publication

Build standalone, multi-page HTML documents with navigation, interactive elements, and accessibility features.

## When to Use

- User asks to build a "book," "manual," "guide," or "publication" in HTML
- Content requires page-by-page navigation (not endless scrolling)
- Need interactive elements like clickable terms, tooltips, or modals
- Accessibility requirements (text sizing, high contrast, keyboard nav)
- Print/PDF export needed

## Core Patterns

### 1. Page-by-Page Navigation

Structure each "page" as a `div.page-view` with a single active page:

```html
<div class="page-view active" id="page-title">...</div>
<div class="page-view" id="page-toc">...</div>
<div class="page-view" id="page-recipe-1">...</div>
```

CSS:
```css
.page-view { display: none; animation: pageFadeIn 0.4s ease; }
.page-view.active { display: block; }
```

JS navigation:
```javascript
const pages = ["page-title", "page-toc", "page-recipe-1", ...];
let currentPage = 0;
function goToPage(pageId) { const idx = pages.indexOf(pageId); if (idx >= 0) currentPage = idx; updatePage(); }
function prevPage() { if (currentPage > 0) { currentPage--; updatePage(); } }
function nextPage() { if (currentPage < pages.length - 1) { currentPage++; updatePage(); } }
function updatePage() {
  document.querySelectorAll(".page-view").forEach(p => p.classList.remove("active"));
  document.getElementById(pages[currentPage]).classList.add("active");
  document.getElementById("prevBtn").disabled = currentPage === 0;
  document.getElementById("nextBtn").disabled = currentPage === pages.length - 1;
  document.getElementById("pageCounter").textContent = `Page ${currentPage + 1} of ${pages.length}`;
  window.scrollTo({ top: 0, behavior: "smooth" });
}
```

Keyboard support:
```javascript
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); nextPage(); }
  if (e.key === "ArrowLeft") { e.preventDefault(); prevPage(); }
});
```

Fixed bottom nav bar with Previous/Next buttons and page counter.

### 2. Clickable Terms with Definitions

Wrap terms in spans with `data-term` and `title` attributes:

```html
<span class="clickable-term" data-term="curcumin" title="The bioactive yellow pigment in turmeric...">curcumin</span>
```

CSS:
```css
.clickable-term {
  border-bottom: 1px dotted var(--teal);
  cursor: pointer;
  color: var(--teal-deep);
  font-weight: 600;
  transition: all 0.2s;
}
.clickable-term:hover {
  background: rgba(74, 159, 168, 0.1);
  border-bottom-color: var(--coral);
}
```

JS modal popup:
```javascript
document.querySelectorAll('.clickable-term').forEach(term => {
  term.addEventListener('click', function() {
    const termName = this.getAttribute('data-term');
    const definition = this.getAttribute('title');
    document.getElementById('modal-title').textContent = termName;
    document.getElementById('modal-definition').textContent = definition;
    document.getElementById('term-modal').style.display = 'block';
  });
});
```

### 3. Text Size Controls

Fixed position buttons (A- / A / A+) that toggle CSS classes on `<html>`:

```javascript
function setTextSize(size) {
  document.documentElement.classList.remove("text-small", "text-medium", "text-large");
  document.documentElement.classList.add(`text-${size}`);
  document.querySelectorAll(".text-controls button").forEach(b => b.classList.remove("active"));
  document.getElementById(`ts-${size}`).classList.add("active");
}
```

CSS variables for each size:
```css
html.text-small { --text-base: 1rem; --text-lg: 1.125rem; ... }
html.text-medium { --text-base: 1.125rem; --text-lg: 1.25rem; ... }
html.text-large { --text-base: 1.25rem; --text-lg: 1.5rem; ... }
```

### 4. Print/PDF Export

Hide navigation and non-active pages in print:
```css
@media print {
  .page-nav, .text-controls, .page-view:not(.active) { display: none !important; }
  .page-view.active { display: block !important; }
  body { background: white; font-size: 14pt; }
  .context-block, .step { break-inside: avoid; }
}
```

For a dedicated PDF export button, use the same print stylesheet with `window.print()`.

### 5. API Asset Integration

**Unsplash API** (images):
```python
import requests
access_key = 'YOUR_KEY'
url = 'https://api.unsplash.com/search/photos'
params = {'query': 'turmeric root', 'per_page': 5, 'client_id': access_key}
r = requests.get(url, params=params)
data = r.json()
for item in data.get('results', []):
    print(item['urls']['regular'])  # full-size image URL
```

**Grokipedia API** (term definitions):
```python
from grokipedia_api import GrokipediaClient
client = GrokipediaClient()
result = client.search('Black seed')
# result['results'][0] contains title, snippet, etc.
```

Note: Grokipedia module is `grokipedia_api` (not `grokipedia`). Install via pip if missing.

### 6. Custom SVG Visuals

Generate inline SVG for:
- Trade route maps (simplified paths with city nodes)
- Anatomical diagrams (body outlines with target organs)
- Chemical process flows (step-by-step boxes with arrows)
- Historical timelines (horizontal line with event dots)

Keep SVGs as separate `.svg` files and embed with `<img src="...">` or inline them directly.

## Design Preferences (User-Specific)

When the user requests a "masculine" aesthetic:
- **Typography:** Bold, angular display fonts. Strong geometric lines. No delicate/flowing elements.
- **Colors:** Deep teal, burgundy, gold — rich and commanding. Coral as accent only. No pastels.
- **Language:** Direct, authoritative, instructional. "Do this" not "you might consider." Active voice. Strong verbs.
- **Imagery:** Botanical precision over decorative flourishes. Scientific diagrams. Maps. Anatomical illustrations.
- **Layout:** Structured, architectural, grounded. Clear hierarchy. No whimsy.

When targeting **{HABIT} readers**:
- Body text minimum 18px, line height 1.6+
- High contrast (dark text on light background)
- Generous white space
- Large clickable targets
- Page-by-page navigation (not scrolling)
- Text size controls (A-/A/A+)

## Pitfalls

1. **Module naming:** Grokipedia package is `grokipedia_api`, not `grokipedia`. Import fails silently if wrong.

2. **Unsplash rate limit:** 50 requests/hour for free tier. Cache results locally. Don't re-fetch on every build.

3. **Page navigation state:** If using `window.scrollTo` on page change, ensure it fires AFTER the new page is visible (use `behavior: "smooth"`).

4. **Print stylesheet:** All `.page-view` elements must be `display: none` except `.active`, otherwise blank pages print between content.

5. **Clickable term wrapping:** Don't wrap terms inside HTML tags (e.g., don't replace "curcumin" inside `<h2>...</h2>`). Only replace in text content, not in tag attributes or nested elements.

6. **Image hotlinking:** Unsplash images can be hotlinked directly via their URLs. No need to download unless offline use is required.

## Verification Checklist

- [ ] All pages navigate correctly (forward and backward)
- [ ] Keyboard navigation works (Arrow keys, Space)
- [ ] Text size controls change the entire document
- [ ] Clickable terms open a modal/popup with definition
- [ ] Print/PDF export shows only the active page
- [ ] Images load (check for broken URLs)
- [ ] Responsive on mobile (text doesn't overflow, buttons reachable)
- [ ] No faces of Islamic figures in any visual (per Islamic rules)
