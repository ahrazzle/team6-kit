<!-- GENERICIZED: 1×{HABIT}, 1×{RELATIONSHIP} | source: skills/multi-page-html-design/SKILL.md -->
---
name: multi-page-html-design
description: "Use when the user asks for multi-page HTML documents."
version: 1.0.0
author: {RELATIONSHIP} (Team6)
license: MIT
platforms: [linux, macos, windows]
tags: [design, html, multi-page, navigation, prototype, creative, artifact, reference]
---

# Multi-Page HTML Document Design

Design multi-page HTML documents — recipe books, guides, handbooks, references — as self-contained local artifacts with page navigation, visual placeholders, interactive term systems, and audience-aware constraints.

## When To Use

- Recipe books or formula collections
- Reference guides or handbooks
- Multi-chapter educational materials
- Interactive documents with glossaries
- Documents requiring external visual assets
- Audience-specific design (seniors, cultural/religious constraints)

**Do not use for:** single-page landing pages, marketing sites, or pure token spec files.

## Page Navigation System

**Never use endless scrolling for multi-page documents.** Use a page-view system.

### HTML Structure

```html
<div class="page-view active" id="page-title">...</div>
<div class="page-view" id="page-toc">...</div>
<div class="page-view" id="page-chapter-1">...</div>
```

### Navigation Controls

```html
<nav class="page-nav">
  <button id="prevBtn" onclick="prevPage()">Previous</button>
  <span class="page-counter" id="pageCounter">Page 1 of 12</span>
  <button id="nextBtn" onclick="nextPage()">Next</button>
</nav>
```

### JavaScript

```javascript
const pages = ["page-title", "page-toc", "page-chapter-1"];
let currentPage = 0;

function goToPage(pageId) {
  const idx = pages.indexOf(pageId);
  if (idx >= 0) currentPage = idx;
  updatePage();
}

function prevPage() { if (currentPage > 0) { currentPage--; updatePage(); } }
function nextPage() { if (currentPage < pages.length - 1) { currentPage++; updatePage(); } }

function updatePage() {
  document.querySelectorAll(".page-view").forEach(p => p.classList.remove("active"));
  document.getElementById(pages[currentPage]).classList.add("active");
  document.getElementById("prevBtn").disabled = currentPage === 0;
  document.getElementById("nextBtn").disabled = currentPage === pages.length - 1;
  document.getElementById("pageCounter").textContent = `Page ${currentPage + 1} of ${pages.length}`;
  window.scrollTo({ top: 0, behavior: "instant" });
}

document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); nextPage(); }
  if (e.key === "ArrowLeft") { e.preventDefault(); prevPage(); }
});
```

### CSS

```css
.page-view { display: none; animation: pageFadeIn 0.3s ease; }
.page-view.active { display: block; }

.page-nav {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: var(--surface);
  border-top: 3px solid var(--accent);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1000;
}
```

## Visual Placeholder Containers

When an image, diagram, or visual asset needs external generation, **do not leave empty space or broken images**. Create a placeholder with a detailed prompt.

### HTML

```html
<div class="diagram-placeholder">
  <p class="diagram-prompt">
    DIAGRAM: Nitric oxide pathway — dietary nitrates → nitric oxide → vasodilation → lower blood pressure.
    Clean diagram with arrows. Medical illustration style, coral/teal/gold palette.
  </p>
</div>
```

### CSS

```css
.diagram-placeholder {
  background: linear-gradient(135deg, var(--surface-alt), var(--surface-muted));
  border: 3px dashed var(--accent);
  border-radius: 8px;
  padding: 2rem;
  margin: 1.5rem 0;
  text-align: center;
}

.diagram-prompt {
  font-size: 0.9rem;
  line-height: 1.6;
  font-style: italic;
  color: var(--text-secondary);
}

.diagram-prompt::before { content: "🎨 "; font-size: 1.2rem; }
```

### Prompt Writing Rules

- Specify TYPE: DIAGRAM, MAP, ILLUSTRATION, PHOTOGRAPH
- Describe SUBJECT clearly
- Specify STYLE: "medical illustration," "aged parchment," "botanical"
- Specify PALETTE if applicable

## Interactive Term Systems (Glossaries)

**Do not use `title` tooltips** — limited to ~50 chars, no mobile support, inaccessible.

### HTML

```html
<span class="term clickable-term" data-term="curcumin" title="Brief fallback definition">curcumin</span>

<div id="term-popup" class="term-modal">
  <div class="term-modal-content">
    <button class="term-popup-close">&times;</button>
    <h3 id="term-title"></h3>
    <p id="term-definition"></p>
  </div>
</div>
```

### JavaScript

```javascript
const termsData = {
  "curcumin": "The bioactive yellow pigment in turmeric...",
  "piperine": "The active compound in black pepper..."
};

document.querySelectorAll(".clickable-term").forEach(el => {
  el.addEventListener("click", () => {
    const term = el.getAttribute("data-term");
    document.getElementById("term-title").textContent = term;
    document.getElementById("term-definition").textContent = termsData[term] || "Definition not found.";
    document.getElementById("term-popup").classList.add("active");
  });
});

document.querySelector(".term-popup-close").addEventListener("click", () => {
  document.getElementById("term-popup").classList.remove("active");
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") document.getElementById("term-popup").classList.remove("active");
});
```

### Deduplication Rule

**Only the FIRST occurrence of each term within a section/recipe should be clickable.**

```javascript
const seen = new Set();
document.querySelectorAll(".clickable-term").forEach(el => {
  const term = el.getAttribute("data-term");
  if (seen.has(term)) {
    el.outerHTML = el.textContent;
  } else {
    seen.add(term);
  }
});
```

### CSS

```css
.term.clickable-term {
  color: var(--accent);
  border-bottom: 2px dotted var(--accent);
  cursor: pointer;
  font-weight: 600;
}

.term-modal {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  align-items: center;
  justify-content: center;
}

.term-modal.active { display: flex; }

.term-modal-content {
  background: var(--surface);
  border: 3px solid var(--accent);
  border-radius: 12px;
  padding: 2rem;
  max-width: 32rem;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}
```

## Audience-Aware Design Constraints

### Cultural/Religious (Muslim Audience)

- **No figurative depictions of Islamic figures** (prophets, companions, angels)
- Acceptable: geometric patterns, arabesque, calligraphy, botanical art, architecture
- Distinguish cultural origins honestly (Ayurvedic vs. Buddhist vs. Islamic)
- Use culturally appropriate colors: green, gold, deep blue, ivory, burgundy

### {HABIT} Accessibility (60+)

- Body text: 18px+ (1.125rem)
- Line height: 1.6+
- High contrast: near-black on warm cream
- Large touch targets (min 44px)
- **Text size controls**: A- / A / A+ buttons adjusting `--text-base`

### Text Size Control Pattern

```javascript
function setTextSize(size) {
  const sizes = { small: "1rem", medium: "1.125rem", large: "1.35rem" };
  document.documentElement.style.setProperty("--text-base", sizes[size] || sizes.medium);
}
```

## Masculine Aesthetic

- **Typography:** Bold, angular display type. Strong geometric lines.
- **Colors:** Deep teal, burgundy, gold — rich and commanding.
- **Language:** Direct, authoritative, instructional. "Do this" not "you might consider."
- **Imagery:** Botanical precision. Scientific diagrams. Maps. Anatomical illustrations.
- **Layout:** Structured, architectural, grounded. Clear hierarchy. No whimsy.

## Pitfalls

- **Do not use `title` tooltips** — use modal popups with full content.
- **Do not duplicate clickable terms** within a section — first occurrence only.
- **Do not leave broken images** — use placeholder containers with prompts.
- **Do not use endless scrolling** — use page-view navigation.
- **Do not use pastel colors** when masculine aesthetic is requested.
- **Do not fabricate religious connections** — distinguish cultural origins honestly.
- **Do not overclaim health evidence** — use conservative language.
- **Do not use hourglass emojis (⏳)** as CSS-generated content — they cut into UI elements.

## Print / PDF Conversion (Print-QA Gate)

Every HTML→PDF job needs a print-QA pass before delivery — the user catches mid-element page breaks immediately ("pdf pages break in between elements").

### Mandatory checks

1. **Render to PDF and check page count against expected sheets** (`pdfinfo file.pdf | grep Pages`). A footer pushed onto a surprise third page is the classic failure — page count is the first signal.
2. **Verify no mid-element breaks**: no heading/footer/table row split across pages, no black bar artifact cutting through content columns.
3. **Add `break-inside: avoid`** to every major block (`.page-footer`, `.stat-hero`, `.comp-table`, `.footnote`, `.sheet-header`, cards).
4. **Suspect malformed CSS when pagination is wrong.** A broken CSS rule — e.g. a regex edit dropped closing braces on 5 rules — silently forces extra pages. Validate the stylesheet renders correctly before blaming layout.
5. **Check the text layer too**: `pdftotext -layout` confirms content ordering and whether blocks landed on the right page.

### Print-ready CSS baseline

- `@page { size: 8.5in 11in; margin: 0; }` with fixed `.page` blocks (`width: 8.5in; height: 11in; overflow: hidden; page-break-after: always;`)
- `-webkit-print-color-adjust: exact; print-color-adjust: exact;` so brand colors survive printing
- Keep every logical sheet inside ONE `.page` container — never let content flow to a natural page break.

## Verification

- File exists at stated path
- All pages navigate correctly
- Clickable terms open modal with full definitions
- Placeholder containers render with prompts
- Text size controls adjust body text
- No console errors
