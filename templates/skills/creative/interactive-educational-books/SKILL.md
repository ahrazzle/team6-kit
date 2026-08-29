<!-- GENERICIZED: 2×{AMOUNT}, 1×{CLIENT}, 2×{HABIT}, 1×{RELATIONSHIP} | source: skills/creative/interactive-educational-books/SKILL.md -->
---
name: interactive-educational-books
description: Build interactive educational books with clickable terms.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, education, interactive, book, clickable-terms, page-navigation]
    related_skills: [claude-design, popular-web-designs]
---

# Interactive Educational Books

Build self-contained HTML books that go beyond static text — interactive term definitions, accuracy badges, page-by-page navigation, and {HABIT}-friendly readability.

**Trigger:** User asks for a book, reference guide, educational artifact, or "compiled" collection that will be read on-screen and benefits from interactivity.

## Core Patterns

### 1. Page-by-Page Navigation

One `page-view` div per page. Single navigation state variable. No scroll-based detection (it fights click navigation).

```html
<div class="page-view active" id="page-title">...</div>
<div class="page-view" id="page-toc">...</div>
<div class="page-view" id="page-recipe-1">...</div>
```

```javascript
const pages = ["page-title", "page-toc", "page-recipe-1", ...];
let currentPage = 0;

function goToPage(pageId) {
  const idx = pages.indexOf(pageId);
  if (idx >= 0) currentPage = idx;
  updatePage();
}

function nextPage() { if (currentPage < pages.length - 1) { currentPage++; updatePage(); } }
function prevPage() { if (currentPage > 0) { currentPage--; updatePage(); } }

function updatePage() {
  document.querySelectorAll(".page-view").forEach(p => p.classList.remove("active"));
  document.getElementById(pages[currentPage]).classList.add("active");
  document.getElementById("prevBtn").disabled = currentPage === 0;
  document.getElementById("nextBtn").disabled = currentPage === pages.length - 1;
  document.getElementById("pageCounter").textContent = `Page ${currentPage + 1} of ${pages.length}`;
  window.scrollTo({ top: 0, behavior: "smooth" });
}
```

**Pitfall:** Do NOT add IntersectionObserver or scroll-based page tracking. It conflicts with click navigation — clicking to page 5 then scrolling slightly jumps back to page 1.

### 2. Clickable Terms with Modal

Two-class system so JS and CSS can target separately:

```html
<span class="term clickable-term" data-term="curcumin">curcumin</span>
```

- `.term` — JS selector target (functional)
- `.clickable-term` — CSS styling (visual highlight)

```javascript
document.querySelectorAll(".term").forEach(el => {
  el.addEventListener("click", function() {
    const key = this.getAttribute('data-term');
    openTermModal(key);
  });
});
```

Modal HTML (place once before `</body>`):

```html
<div id="term-modal" class="term-modal" role="dialog" aria-modal="true">
  <div class="term-modal-content">
    <button class="term-modal-close" aria-label="Close">&times;</button>
    <h3 id="modal-title"></h3>
    <p id="modal-definition"></p>
    <p id="modal-source"></p>
  </div>
</div>
```

**Pitfall:** If JS looks for `.term` but HTML only has `.clickable-term`, zero elements match. Clicks do nothing. Always use both classes.

### 3. Evidence/Accuracy Badges

When content makes health, scientific, or factual claims, label confidence explicitly:

```html
<span class="evidence-badge evidence-high">High</span>
<span class="evidence-badge evidence-moderate">Moderate</span>
<span class="evidence-badge evidence-traditional">Traditional</span>
```

- **High** — multiple RCTs, meta-analyses, regulatory approval
- **Moderate** — limited human trials, strong preclinical, clinical tradition
- **Traditional** — historical/cultural use, minimal modern research

**Pitfall:** Never claim "over {AMOUNT} peer-reviewed studies" or "comparable to prescription medications" unless you can cite the specific comparison study. Soften to "extensively studied," "research has documented," or "modest reduction."

### 4. {HABIT} Readability

- Body text: 18px+ (1.125rem minimum)
- Line height: 1.6+
- High contrast: dark charcoal (#2a2018) on warm cream (#faf6ee)
- Generous spacing between steps
- Large tap targets (44px minimum)
- Text size controls (A-/A/A+) in fixed position, always visible
- Page navigation with large Previous/Next buttons

### 5. Ingredient Quantities

Every ingredient gets a quantity badge:

```html
<li><span class="ingredient-dot gold"></span> basmati rice <span class="ingredient-qty">1 cup</span></li>
```

Without quantities, it's an ingredient list, not a recipe.

### 6. Visual Placeholders for Unsourced Media

When an image or diagram doesn't exist yet, create a placeholder with a prompt inside:

```html
<div class="diagram-placeholder">
  <p><strong>Diagram prompt:</strong> Curcumin molecule → liver (glucuronidation blocked by piperine) → bloodstream. Clean medical illustration, coral/teal/gold palette.</p>
</div>
```

This signals to the user that a custom asset is needed and tells another model exactly what to generate.

## File Structure

```
book-name/
├── index.html          # Complete self-contained book
├── {CLIENT}        # Design system
├── terms-popup.js      # Clickable terms modal logic
├── terms_complete.json # Term definitions database
└── image-manifest.json # Image references (optional)
```

**Pitfall:** Keep it to ONE html file. Multiple index*.html files in the same directory confuse both agents and users.

## Content Woven Between Steps

For educational books, context between instructional steps keeps readers engaged during waiting periods:

- **Health** — how the ingredient affects the body
- **History** — origins, trade routes, cultural spread
- **Islamic/Religious** — authentic scholarly connections (hadith, Quranic references) where they genuinely exist
- **Fun Fact** — interesting tidbits, etymology
- **Cultural** — traditions, ceremonies, daily practices
- **Science** — mechanisms, studies, bioavailability

**Pitfall:** Don't force theology onto traditions where it doesn't exist. Present origins honestly, highlight authentic connections where real.

## Verification Checklist

Before delivering:

- [ ] All page navigation works (click + keyboard arrows)
- [ ] No duplicate clickable terms within the same page/section
- [ ] No hourglass/stopwatch emojis cutting into UI (use plain text for step times)
- [ ] Clickable terms use BOTH `.term` and `.clickable-term` classes
- [ ] Modal HTML exists in the file (not just CSS)
- [ ] Terms database keys match `data-term` values exactly (lowercase, underscores)
- [ ] Evidence badges on all health/factual claims
- [ ] Ingredient quantities on all recipe ingredients
- [ ] Skip link for accessibility
- [ ] Text size controls functional
- [ ] Only ONE index.html in the workspace

## Pitfalls

1. **Class mismatch** — JS targets `.term`, HTML has `.clickable-term`. Clicks do nothing.
2. **Scroll + click navigation conflict** — IntersectionObserver fights goToPage(). Use one system.
3. **TOC links styled as clickable terms** — TOC is navigation, not content. Don't wrap TOC text in term spans.
4. **Hourglass emojis** — `⏱` and `⏳` cut into adjacent UI elements. Use plain text: "30 min soak" not "⏱ 30 min soak".
5. **Health overclaiming** — "{AMOUNT} studies," "comparable to prescriptions," "anti-cancer effects" without human trials. Soften language.
6. **Evidence badge inflation** — Most traditional remedies are "Traditional" evidence, not "Moderate." Be honest.
7. **Missing modal HTML** — CSS for `.term-modal` exists but the div is never added to the body. JS has nothing to show.
8. **Ingredient lists without quantities** — "basmati rice" is not a recipe. "1 cup basmati rice" is.
