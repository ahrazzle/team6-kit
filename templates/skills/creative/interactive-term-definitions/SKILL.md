<!-- GENERICIZED: 2×{HABIT}, 1×{RELATIONSHIP} | source: skills/creative/interactive-term-definitions/SKILL.md -->
---
name: interactive-term-definitions
description: Build interactive term definition modals for HTML books.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [interactive, modal, definitions, educational, ux, accessibility, javascript, html]
    related_skills: [claude-design, popular-web-designs]
---

# Interactive Term Definition System

Build clickable terms in HTML that open modal popups with definitions, context, and links. Ideal for books, educational materials, and reference artifacts where readers need deeper understanding of terminology without navigating away.

## When to Use

Use this pattern when:
- The user wants "click on any term to learn more"
- Building a reference book with encyclopedic entries
- Content mixes technical and non-technical terms
- {HABIT} accessibility is needed (large touch targets, keyboard nav)
- Terms repeat across multiple sections but definitions should be consistent

## Core Pattern

### 1. HTML Markup

```html
<!-- Clickable term in content -->
<span class="term clickable-term" data-term="curcumin">curcumin</span>

<!-- Modal structure (place once before </body>) -->
<div id="term-modal" class="term-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="term-modal-content">
    <button class="term-modal-close" aria-label="Close">&times;</button>
    <h3 id="modal-title"></h3>
    <p id="modal-definition"></p>
    <a id="modal-link" href="#" target="_blank" rel="noopener">Learn more →</a>
  </div>
</div>
```

### 2. Data Structure

```javascript
// terms_data_normalized.json — lowercase keys!
{
  "curcumin": {
    "title": "Curcumin",
    "definition": "The bioactive yellow pigment in turmeric...",
    "url": "https://en.wikipedia.org/wiki/Curcumin"
  }
}
```

**Critical**: Keys MUST be lowercase. `data-term="curcumin"` must match `"curcumin"` in the object.

### 3. JavaScript Handler

```javascript
let termsDB = {};

async function initTerms() {
  try {
    const r = await fetch('terms_data_normalized.json');
    termsDB = await r.json();
  } catch (e) { console.warn('Could not load terms DB'); }
  
  document.querySelectorAll('.clickable-term').forEach(el => {
    el.addEventListener('click', function() {
      const key = this.dataset.term.toLowerCase();
      const info = termsDB[key];
      if (info) {
        document.getElementById('modal-title').textContent = info.title;
        document.getElementById('modal-definition').textContent = info.definition;
        const link = document.getElementById('modal-link');
        if (info.url) { link.href = info.url; link.style.display = 'inline'; }
        else { link.style.display = 'none'; }
        document.getElementById('term-modal').classList.add('active');
      }
    });
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); el.click(); }
    });
  });
  
  document.querySelector('.term-modal-close').addEventListener('click', closeModal);
  document.getElementById('term-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });
}

function closeModal() {
  document.getElementById('term-modal').classList.remove('active');
}
```

### 4. CSS Essentials

```css
.term {
  color: var(--accent);
  font-weight: 600;
  cursor: pointer;
  border-bottom: 2px dotted var(--gold);
}
.term:hover { background: rgba(138, 58, 74, 0.08); }

.term-modal {
  display: none;
  position: fixed; inset: 0;
  background: rgba(42, 32, 24, 0.6);
  backdrop-filter: blur(4px);
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 2rem;
}
.term-modal.active { display: flex; }
.term-modal-content {
  background: var(--surface);
  border: 3px solid var(--accent);
  border-radius: 1rem;
  padding: 2rem;
  max-width: 32rem;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
}
```

## Data Sourcing Strategy

For encyclopedic terms, use this priority:

1. **Wikipedia REST API** (`/api/rest_v1/page/summary/{title}`) — returns JSON with title, description, extract, URL. Rate limit gently (0.5s between requests).
2. **Grokipedia** — unstable (502 errors on search, 404 on page-preview). Don't rely as primary source.
3. **Curated definitions** — for domain-specific terms (Ayurvedic concepts, TCM, Islamic scholars), write custom definitions from verified sources.

Build a local JSON file with all terms so the modal works offline and instantly.

## Accessibility Requirements

- **Keyboard**: Terms must be focusable (`tabindex="0"`). Enter/Space opens modal.
- **ARIA**: `role="button"`, `aria-label="Learn more about {term}"`, `aria-modal="true"` on dialog.
- **Focus management**: Modal close returns focus to trigger element.
- **Escape key**: Always closes modal.
- **Touch targets**: Minimum 44px for {HABIT} users.

## Pitfalls

- **Case sensitivity**: `data-term="Agni"` won't match key `"agni"`. Always lowercase.
- **Multiple instances**: One term may appear multiple times. Use `querySelectorAll` to wire all.
- **Fallback**: If local DB fails, offer Wikipedia fetch as backup.
- **External links**: `target="_blank"` with `rel="noopener"` for safety.
- **Rate limiting**: When sourcing from Wikipedia API, add delays between requests.
