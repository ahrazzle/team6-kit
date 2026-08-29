<!-- GENERICIZED: 5×{CLIENT}, 3×{HABIT}, 1×{RELATIONSHIP} | source: skills/creative/interactive-documents/SKILL.md -->
---
name: interactive-documents
description: "Build interactive HTML books with API content, SVG visuals."
version: 1.0.0
author: {RELATIONSHIP} (Team6)
license: MIT
platforms: [macos, linux, windows]
---

# Interactive Documents

> Build standalone HTML documents with API-sourced content, programmatic visuals, and interactive elements.

## Trigger

Use when the user asks for:
- A digital book, recipe book, or interactive document
- HTML pages that integrate external APIs for content/images
- Documents with clickable/tappable elements for deeper exploration
- Custom visual generation (maps, diagrams, timelines) via SVG
- {HABIT}-accessible design with large type and clear hierarchy

## Workflow

### Phase {CLIENT}: Foundation Lock

**CRITICAL: Lock the IDEA.md and project structure before any build work.**

1. Create the project workspace with standard folders:
   - `PROJECTS/`, `OUTPUTS/`, `TEMPLATES/`, `LOG/`, `RESEARCH/`, `ASSETS/`
2. Write IDEA.md with: title, audience, scope, design direction, content requirements, safety notes
3. Get user sign-off on IDEA.md BEFORE dispatching build work
4. Any scope changes require IDEA.md update first

**Pitfall:** Building before locking the foundation causes rework. The team will build from whatever is in the file — if it's wrong, the output is wrong.

### Phase {CLIENT}: Research & Asset Collection

#### API Integration

**Grokipedia API** (term definitions and general knowledge):
```python
from grokipedia_api import GrokipediaClient
client = GrokipediaClient()
result = client.search('term')
# Returns: results[].title, results[].snippet, results[].slug
```

**Unsplash API** (hero images and photography):
```python
import requests
access_key = 'YOUR_ACCESS_KEY'
url = 'https://api.unsplash.com/search/photos'
params = {'query': 'search term', 'per_page': 5, 'client_id': access_key}
r = requests.get(url, params=params)
# Returns: results[].urls.regular, results[].urls.small, results[].user.name
```

**Rate limits:** Unsplash 50/day. Grokipedia: add `time.sleep(0.5)` between calls.

#### Programmatic SVG Visuals

Generate custom visuals as SVG files for:
- **Trade route maps** — Show ingredient/culture movement across regions
- **Process diagrams** — Chemical pathways, biological mechanisms
- **Historical timelines** — Key events and figures
- **Anatomical diagrams** — Where remedies act on the body
- **Comparison diagrams** — Before/after, with/without scenarios

SVG generation approach:
```python
def generate_visual():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
  <!-- Content here -->
</svg>'''
    with open('ASSETS/visual.svg', 'w') as f:
        f.write(svg)
```

**Design principles for SVGs:**
- Match the document's CSS custom properties (colors, fonts)
- Keep viewBox dimensions consistent (800x400 for landscapes, 400x500 for portraits)
- Use semantic class names for styling hooks
- Include text labels directly (SVG renders text crisply)
- Test at multiple widths (SVGs scale responsively)

### Phase {CLIENT}: HTML Build

#### Clickable Terms Pattern

Wrap unfamiliar terms in clickable spans:
```html
<span class="clickable-term" data-term="piperine" 
      title="The active compound in black pepper...">piperine</span>
```

CSS:
```css
.clickable-term {
  border-bottom: 1px dotted var(--teal);
  cursor: pointer;
  color: var(--teal-deep);
  font-weight: 600;
}
.clickable-term:hover {
  background: rgba(74, 159, 168, 0.1);
}
```

**Terms to make clickable:** Scientific compounds, cultural/historical figures, unfamiliar concepts, ingredients with specific significance, religious/theological references.

#### Content Weaving Pattern

For instructional content, weave contextual information between steps:
1. **Health/Science** — Explain the biological mechanism
2. **History** — Origin and transmission of the knowledge
3. **Cultural** — Traditions and ceremonies
4. **Religious** — Theological connections (where authentic)
5. **Fun Fact** — Interesting tidbits to maintain engagement

Place context blocks after steps that involve waiting or repetitive tasks.

### Phase {CLIENT}: Design System

#### {HABIT} Accessibility (Non-Negotiable)

- **Body text:** Minimum 18px, 1.6+ line height
- **Contrast:** Dark charcoal on warm cream (not pure black on white)
- **Spacing:** Generous margins, never crowded
- **Hierarchy:** Clear visual distinction between headings, body, captions

#### Masculine Aesthetic

- **Language:** Direct, authoritative, instructional. Active voice. Strong verbs.
- **Typography:** Bold, angular display type. No delicate elements.
- **Colors:** Deep teal, burgundy, gold. Coral as accent only.
- **Layout:** Structured, architectural, grounded. No whimsy.

#### 80s Retro Accent (Optional)

- Memphis-style geometric frames on title page
- Bold dot patterns and squiggle dividers
- Tamed pastel-neon accents (coral, teal, gold)

**Key balance:** 80s as *accent and flavor*, never as foundation. {HABIT} readability always takes priority.

## Pitfalls

### CRITICAL: Destructive Script Overwrites

A Python script that does `with open('index.html', 'w')` will **destroy** the existing file. If the script only has partial data, you lose everything.

**Prevention:**
1. Always run `cp index.html index.html.bak` before any script that writes to the same file
2. Prefer targeted `patch` operations over full-file rewrites
3. If generating, write to a NEW file first, verify, then rename
4. Use `git` if available — commit before destructive operations

### API Rate Limits

- Unsplash: 50 requests/day. Batch queries efficiently. Cache results locally.
- Grokipedia: Add delays between calls. Cache results as JSON.

### Image Fallbacks

If an API returns no results:
1. Try broader/synonym queries
2. Leave the container blank with a descriptive prompt for the user
3. Never break the layout with missing images

### Islamic Content Authenticity

- Present cultural origins honestly — don't force theology where none exists
- Highlight authentic connections (Black Seed, Honey, Saffron, Rose, Ginger)
- Distinguish between Islamic, Ayurvedic, and Buddhist traditions
- No faces of Islamic figures (per Islamic rules)

## References

- `references/{CLIENT}` — Session details: APIs, SVG patterns, asset pipeline
