<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/creative/client-brand-collateral/SKILL.md -->
---
name: client-brand-collateral
description: Use when building client-facing sales collateral.
version: 1.0.0
author: {RELATIONSHIP}
license: internal
metadata:
  hermes:
    tags: [collateral, branding, print, pdf, sales, marketing]
    related_skills: [analytical-report-design, claude-design]
---

# Client Brand Collateral

## When to Use

Use for any client-facing sales/marketing material that must be on-brand and print-ready: flyers, brochures, business cards, QR cards, information packages, event prep, sales-rep prep. Also use when raw `.md` research briefs need to become presentable branded documents.

Produce client-facing materials (flyers, brochures, cards, information packages, sales-rep/event prep) as print-ready HTML + PDF, strictly on the client's real brand.

## Core Rules (user-enforced, non-negotiable)

1. **Extract the brand palette from the client's actual site — never invent colors.** Visit their domain, pull the real hex values, and lock them project-wide. Rhino example: invented orange/gold was rejected; the real palette is `#C22023` (red), `#CB3245` (secondary red), `#231F20` (dark), white.
2. **No emojis on business materials — ever.** Replace with SVG iconography, red/dark left-border accents, or geometric chips. Emojis are unprofessional; this was an explicit user correction.
3. **Verify logo contrast at every placement.** A white logo on a white field is invisible. White/light logos go on dark or red backgrounds ONLY. If a light background is unavoidable, put a dark chip behind the logo (e.g. `background:#231F20; border-radius:4px; padding:4px 10px`). Check every page header/footer, not just the cover.
4. **Logo assets that include the wordmark replace text logos.** Do NOT keep "RHINO Carbon Fiber" text beside a logo that already contains it — redundant. Remove the placeholder (e.g. red "R" square) entirely and give the logo generous space; never squeeze it into a small square.
5. **Verify QR-code landing URLs before finalizing.** A QR pointing at a 404 is a wasted print run. Fetch the URL first; if the specific path is dead, point at the homepage (or a live, context-relevant page).
6. **Layout: tight and legible.** "Too much blank space" is a rejection. Use the full page: single wide column for tables/specs rather than narrow side-by-side containers that compress text. Print tables ≥10pt, body ≥9pt, hero headlines large. Content should fill the page — dead space reads as unfinished.

## Workflow

1. **Brief lands → design → build → QA → deliver.** No waiting for explicit "go" between steps. The sales/event brief itself is the trigger.
2. **Formatting gate:** any `.md` research brief destined for external distribution must be converted to branded HTML before the deliverable closes. Raw markdown for a human (sales rep, client) to read is a failure.
3. **Deliver both HTML and PDF.** HTML for phone/laptop viewing, PDF for print and email attachments. The user's browser-based HTML→PDF export gave poor results — use the headless Chrome script (below).
4. **No human timeline tracking.** Deliver at best pace, quality first. Emergency packages ship as fast as they can be built correctly.
5. **On-demand packaging:** when a sales rep needs materials for a meeting/event, produce the full kit — print pieces, digital brochures, info packages, technical walkthroughs, and event/company intelligence — not just a flyer.

## Print-Ready CSS Pattern

```css
@page { size: 8.5in 11in; margin: 0; }        /* card: 3.5in 2in */
body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 8.5in; height: 11in; page-break-after: always; overflow: hidden; }
```
Use `@media print` overrides for screen-first docs. For multi-page prep packages, keep page headers consistent (logo + page number + red rule).

## PDF Export

Use `scripts/html-to-pdf.sh` (headless Chrome). It respects `@page` sizing and print CSS exactly. Verify the result: page count via Python one-liner counting `/Type /Page` objects minus `/Type /Pages` in the raw PDF bytes. Chrome prints a `CVDisplayLink` error to stderr on macOS — harmless, ignore.

## Verification Checklist

- [ ] Palette = client's real brand colors (extracted from their site)
- [ ] Zero emojis in HTML body
- [ ] Every logo placement has sufficient contrast (no white-on-white)
- [ ] No redundant wordmark text beside a logo that includes it
- [ ] QR/links verified live (no 404 targets)
- [ ] Layout fills the page; tables readable (no compressed narrow columns)
- [ ] All `.md` sources converted to branded HTML
- [ ] HTML + PDF both generated; PDF page count sane
- [ ] Filenames consistent and in the project workspace

## References

- `references/rhino-carbon-fiber-brand.md` — Rhino Carbon Fiber brand lock, logo assets, rep contact, event/White Cap context
