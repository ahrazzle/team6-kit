<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/creative/print-material-design/SKILL.md -->
---
name: print-material-design
description: Design print-ready materials and sales enablement packages.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [design, print, flyer, brochure, business-card, qr, sales, enablement, brand, physical]
    related_skills: [claude-design, html-report-design]
---

# Print Material Design

Design print-ready physical materials and comprehensive sales enablement packages. Covers the full lifecycle: brief understanding, layout and brand asset handling, print-specific QA, and delivering a complete package of physical and digital materials.

## When to Use

Use this skill when the user asks for:
- Print flyers or one-pagers
- Business cards, contact cards, QR cards
- Brochures or multi-page print documents
- Information packages for clients/prospects
- Event materials (handouts, leave-behinds)
- Any physical material that will be printed from HTML

Also use when the user asks for a "package" for a sales rep attending an event — this triggers the full Sales Enablement scope (see below).

## The Full Scope: Sales Enablement is Broader Than a Flyer

When a user asks for materials for a sales rep, **think comprehensively.** A flyer alone is almost never enough. The full package typically includes:

1. **Physical materials** — flyer, QR card, leave-behinds for the event
2. **Digital brochures** — multi-page HTML brochures that can be emailed as PDFs
3. **Information packages** — condensed technical overviews for quick email attachment
4. **Interactive technical walkthroughs** — step-by-step guides prospects can click through
5. **Event prep research** — who's attending, networking targets, competitive landscape, talking points
6. **Rep profile / contact materials** — business cards, contact reference cards

**Propose the full package proactively.** Do not wait for the user to ask for each piece individually. If you only produce what was explicitly requested, you have under-delivered.

## Print Layout Rules

### Blank Space is a Failure

If the user says "too much blank space," the layout is wrong. Compress margins, reduce padding, fill the page. If content doesn't fill a double-sided layout, **go single-sided** rather than leaving an empty back page. Empty space on a print document signals incomplete work.

### Single Wide Column Beats Two Narrow Columns

Two narrow side-by-side columns compress text into illegibility. Tables and specs need width. Use a single wide column with content stacked (e.g., comparison table above, specs below) so text can be 10-11pt and readable from distance. Narrow columns force small text that cannot be read from a normal viewing distance.

### Minimum Print Sizes

- **Body text:** minimum 10pt for print materials
- **Table text:** minimum 10pt
- **Labels/captions:** minimum 8pt
- **Headlines:** 24-42pt depending on hierarchy
- **Stat values:** 20-26pt for scannability

### No Emojis on Business Materials

Never use emojis (phone icons, building icons, flags, etc.) in print flyers, brochures, or business cards. Replace with text labels or structured typography. Emojis signal unprofessionalism in physical business materials.

### Phone Numbers Must Not Break Across Lines

In business cards and contact info, stack phone and email **vertically** rather than side-by-side in a flex row. Side-by-side layouts force the phone number to wrap across two lines, which looks broken.

## Brand Asset Handling

### Logo Visibility Requires Contrast

White logos need dark or colored backgrounds to be visible. Never place a white logo on a white field. If the only logo available is white, ensure every placement sits on a dark or brand-color background. **Verify this explicitly before delivery** — check every instance of the logo in every file.

### Logo Replacement: Remove ALL Redundant Elements

When replacing a placeholder (e.g., red "R" div + text) with an official logo asset:
1. Remove the placeholder div
2. Remove the text beside it
3. The official logo replaces BOTH
4. Do not leave redundant text next to the new logo

### Give Logos Adequate Space

When replacing a small placeholder (e.g., 36px red square) with a wider logo asset, give the logo its own adequate width. Do not force it into the old square's dimensions. Make a large space that covers the area where both the old square and text were.

### Grayscale Logos for Red Backgrounds

If the user provides a grayscale logo "designed for red backgrounds," use it on red brand panels. The white version goes on dark/black backgrounds. Using the wrong variant on the wrong background makes it invisible.

## Event-Specific Materials

### Event Hook in Headlines

For event-specific materials, the headline should reference the event's theme/topic to create immediate relevance. Research the event and align the messaging. Example: for a "Ground Improvement" event, lead with "Ground Improvement Solves the Soil. Rhino Repairs the Structure."

### Event Intelligence Brief

For any event deployment, produce:
- Organization background & key personnel
- Expected attendees / who's crucial to meet
- Competitor/sponsor presence
- Strategic angles for the rep
- Networking targets with talking points
- Day-of checklist (arrive early, target quality conversations, collect contacts, follow up within 48 hours)

## Print-Specific QA Checklist

Before declaring a deliverable done, verify ALL of the following:

1. **No blank space** — content fills the page; if not, go single-sided
2. **Readable text** — all body text 10pt+, tables 10pt+, readable from distance
3. **No emojis** — scan every file for emoji characters
4. **Logo visibility** — every logo instance sits on a contrasting background
5. **No redundant elements** — placeholder divs/text removed when logos are swapped
6. **Phone numbers** — stacked vertically, not breaking across lines
7. **Print CSS** — `@page` sizing, `print-color-adjust: exact`, proper page breaks
8. **Brand palette** — colors match the official brand, not invented accents
9. **All files consistent** — same logo treatment, same palette, same typography across all deliverables

## Verification

For print materials, verification is limited in a headless environment. Be honest about what you can and cannot verify:

- **Can verify:** file exists, HTML is saved, grep for emojis, grep for old placeholder classes, check CSS values
- **Cannot verify:** actual visual rendering, print output quality, logo visibility on specific backgrounds (unless browser tools are available)

If browser tools are available, open each file and screenshot it. If not, state clearly: "Verified file structure and content, but visual rendering not confirmed — please preview before printing."

## File Delivery

- Self-contained HTML files with embedded CSS
- `@page` rules for print sizing
- `print-color-adjust: exact` for color fidelity
- Exact on-disk paths in final response
- Group deliverables by type (print vs. digital vs. research)

## Pitfalls

- **Do not claim browser verification unless it actually happened.** If you couldn't open the file visually, say so.
- **Do not ship redundant elements.** When swapping a logo, remove everything it replaced.
- **Do not use emojis on business materials.** Ever.
- **Do not compress text into narrow columns.** Use full width, stack content vertically.
- **Do not leave blank space on print documents.** Fill the page or go single-sided.
- **Do not propose only a flyer when the user needs a full package.** Think comprehensively about sales enablement.
- **Do not wait for the user to ask for event research.** It should be automatic for any event deployment.
