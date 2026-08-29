<!-- GENERICIZED: 4×{RELATIONSHIP} | source: skills/sales-enablement/SKILL.md -->
---
name: sales-enablement
description: "Sales enablement: event intelligence and materials."
version: "1.0.0"
author: "{RELATIONSHIP}"
license: "MIT"
tags: [sales, marketing, events, materials, brochures, client-facing]
metadata:
  hermes:
    tags: [sales, marketing, events, materials, brochures, client-facing]
    related_skills: ["grounded-citations", "visual-report-design"]
---

# Sales Enablement

## When to Use

Use this skill when:
- A sales rep is attending an event and needs preparation materials
- Creating client-facing materials (physical or digital)
- Building a full sales enablement package (brochures, info packages, walkthroughs)
- Researching an event, organization, or attendees for networking purposes
- Producing print-ready or mobile-responsive HTML materials

---

## Core Principles

### 1. The Full Stack, Not Just the Flyer

Sales enablement is never just one deliverable. The standard package includes:

| Category | Deliverables |
|----------|--------------|
| **Physical** | Flyers, QR cards, leave-behinds (print-ready) |
| **Digital** | Email-ready brochures, PDF packages, interactive walkthroughs |
| **Prep** | Event intelligence brief, attendee research, networking targets, cheat sheets |
| **Follow-up** | Post-event email templates, lunch-and-learn offers, CRM logging |

If any category is missing, the deliverable is incomplete.

### 2. Formatting QA Gate

Every file flagged "for external distribution" MUST pass through a formatting QA gate before delivery:

- [ ] Brand palette locked (primary, secondary, dark, white)
- [ ] No emojis in business materials
- [ ] Readable font sizes (minimum 10pt for body, 12pt for tables)
- [ ] Mobile-responsive (opens on phone)
- [ ] Print-ready (@page sizing, proper margins)
- [ ] Content accuracy verified against source
- [ ] No raw `.md` or `.txt` files sent to clients — always formatted HTML

### 3. Event Intelligence Protocol

For any event assignment, produce:

1. **Organizational Profile** — Who runs it, history, scope, key personnel
2. **Event Details** — Date, time, location, schedule, capacity, cost
3. **Presenter Intelligence** — Bio, background, strategic read, opening lines
4. **Competitive Landscape** — Who else is there, complementary vs. competitive
5. **Audience Profile** — Who attends, what they care about, pain points
6. **Strategic Positioning** — How our rep fits, key messages, questions to ask
7. **Networking Targets** — Priority list with names, roles, opening lines
8. **Action Checklist** — Before, during, and after the event
9. **Risk Factors** — What could go wrong and mitigations

### 4. The Brief-to-Execution Pipeline

```
Brief lands
  → Research ({RELATIONSHIP})
  → Raw output in workspace
  → AUTO-ROUTE to design ({RELATIONSHIP})
  → Branded HTML formatting
  → QA Gate ({RELATIONSHIP})
  → Delivered
```

No manual handoffs between steps. Any file flagged "for external distribution" auto-routes to design.

### 5. Field-Intel Pivot (Rep Ground Truth Reframes the Package)

When the sales rep sends back ground truth from the field, the package MUST be reframed around it — never keep pitching the audience you guessed:

- **Dormant-account activation:** SKUs already in the buyer's database but unstocked means the problem is EDUCATION, not procurement. No new-vendor approval needed — the pitch becomes enablement: "Your database already has it. Your branches don't stock it. Your reps don't know it."
- **Audience hierarchy:** present to the audience in the room. A DM pitch is NOT a GM pitch — DMs ask "can my reps sell this without friction?", GMs ask "is it profitable?". Match the concern table to the listener (see `references/field-intel-pivot.md`).
- **"They don't talk about it as they are not informed"** is the whole opportunity: product exists in the system, demand exists in the market, the only missing link is a rep knowing it exists and being armed to sell it.
- **Rollout maps come from the rep:** capture their stated sequence (e.g. Texas → Southeast → national) and build the growth-map visual from it.

### 6. Stale-File Hazard Rule

Whenever an HTML deliverable is REBUILT for a changed audience or scope, the old PDF with the same base name is now a landmine:

- Rename/archive the previous version in the SAME change (e.g. `whitecap-gm-prep-GM-VERSION-BACKPOCKET.pdf`).
- A rebuilt document without a matching freshly-generated PDF is an INCOMPLETE deliverable.
- Before declaring a package done, list the workspace: every live HTML must have a same-name `.pdf` generated AFTER the last HTML edit (compare mtimes).

### 7. PDF Generation & Verification (Headless Chrome)

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-sandbox \
  --print-to-pdf="out.pdf" --no-pdf-header-footer "file:///abs/path/in.html"
```

Always verify the output, never trust the exit code alone:
- `head -c5 out.pdf` → `%PDF-` magic bytes
- Page count via `python3 -c "import re;d=open('out.pdf','rb').read();print(len(re.findall(rb'/Type\s*/Page[^s]',d)))"`
- Record and echo the checksum so the room can cross-verify (`md5 out.pdf`).

---

## Print-Ready HTML Patterns

### Page Setup
```css
@page {
  size: 8.5in 11in;
  margin: 0;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
```

### Single-Column Layout (Preferred)
For dense materials, use a single full-width column instead of side-by-side containers.

```css
.content {
  padding: 0.15in 0.25in;
  max-width: 100%;
}
```

### Brand Palette CSS Variables
```css
:root {
  --red: #C22023;
  --red-2: #CB3245;
  --dark: #231F20;
  --white: #FFFFFF;
  --gray: #F5F5F5;
  --gray-2: #E0E0E0;
}
```

---

## Pitfalls

### 1. Raw Files in Workspace
Research produces `.md` files that sit unformatted until someone complains.
**Fix:** Auto-route any file flagged "for external distribution" to design immediately.

### 2. Emojis in Business Materials
Using emojis in client-facing materials looks unprofessional.
**Fix:** Replace with text labels (TEL, EMAIL, KEY TARGETS) or CSS-styled accents.

### 3. Compressed/Illegible Text
Side-by-side containers force small font sizes.
**Fix:** Use single full-width column with readable font sizes (10pt+).

### 4. Incomplete Deliverable Stack
Producing only a flyer when the client needs digital + physical + prep.
**Fix:** Always check the full stack: physical, digital, prep, follow-up.

### 5. No Event Intelligence
Sending a rep to an event without attendee research or networking targets.
**Fix:** Event Intelligence Protocol is mandatory for any field assignment.

### 6. White-on-Transparent Logos Misread as Blank
Vision analysis frequently reports a white-on-transparent logo as "blank/white image". This is a FALSE negative — the asset is fine; the analyser sees white-on-white against its default background. Do NOT declare a brand asset broken or revert to a placeholder on that basis.
**Verify before acting:** (a) check intended placement backgrounds — white logos go on dark/red panels ONLY; (b) never place white-on-white (wrap in a dark chip if a page header is white); (c) trust the user's statement about their own brand assets; they know the file.

### 7. QR Target Must Resolve
A QR code pointing to a path that 404s (e.g. `/resources`) is worse than useless — every scan lands on an error page.
**Fix:** curl/HEAD the exact target URL BEFORE generating the QR; if the nice path doesn't exist, point at the live homepage or the nearest real page.

### 8. Rep's Own Decks Are the Best Source Material
Mine the rep's existing sales presentations (PDF/PPTX) before building anything new — they contain the strongest stats, install steps, and proof points. See `references/sales-deck-extraction.md` for the extraction technique and the exact data points mined (application-specific numbers beat generic claims: a 6" 400 GSM strap carries ~1.7x the load of #4 rebar — stronger sales math than "10x stronger than steel").

---

## References

- `references/event-intelligence-brief.md` — Template and example for event research
- `references/print-ready-html.md` — Technical patterns for print materials
- `references/formatting-qa-gate.md` — QA checklist for external deliverables
- `references/field-intel-pivot.md` — Field-intel reframe case: dormant-account activation, DM→Area→GM audience hierarchy, audience-specific concern tables
- `references/sales-deck-extraction.md` — PPTX/PDF deck extraction technique + mined sales stats and training offers
