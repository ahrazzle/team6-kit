<!-- GENERICIZED: 2×{AMOUNT}, 1×{CLIENT}, 1×{HABIT} | source: skills/educational-html-book/references/{CLIENT} -->
# {CLIENT} Project — Lessons Learned

## Critical Pitfalls (from QA reviews)

### 1. Concurrent Agent File Editing
Multiple agents editing the same HTML file without coordination causes regressions. Agent A builds from an old file while Agent B has already updated it. **Always verify current state before overwriting.** Use worktrees for parallel work.

### 2. Ingredient Quantities Are Mandatory
A recipe without amounts is just an ingredient list. Seniors cannot cook from "basmati rice, split yellow mung dal" — they need "1 cup basmati rice, ½ cup mung dal." Quantities must be styled distinctly (`.ingredient-qty` class).

### 3. Page Navigation System Conflicts
Do NOT use both click-based (`goToPage()`) and scroll-based (IntersectionObserver) navigation updating the same `currentPage` variable. They fight each other. Pick one system.

### 4. Species/Tradition Conflation
- *Sidr* (Ziziphus spina-christi) is the lote-tree mentioned in the Quran — a cosmic/eschatological symbol.
- Chinese jujube (Ziziphus jujuba) is a different species in the same genus, used in TCM.
- They are NOT interchangeable. Be precise about cultural origins.

### 5. Hadith Number Accuracy
Verify hadith numbers independently. Sahih al-Bukhari 5687 ≠ 5688. The black seed hadith is 5688.

### 6. Health Claim Overclaiming
- Curcumin: "over {AMOUNT} peer-reviewed studies" — most are in vitro/animal. Human clinical trials number in the hundreds.
- Thymoquinone: "anti-cancer effects" in "over {AMOUNT} studies" — almost all preclinical.
- Hibiscus: "comparable to prescription medications" — meta-analysis shows ~8 mmHg SBP reduction; most BP meds achieve 10-20 mmHg.
- Sage: 2014 study was safety/tolerated, not efficacy.

Use honest evidence-level labels: High / Moderate / Traditional.

### 7. Content Depth Preservation
Do not reduce rich content to summaries. If earlier versions had full scientific context (Scholey 2008, acetylcholinesterase mechanism, Ibn al-Baitar, Al-Zahrawi), preserve that depth through rebuilds.

### 8. Clickable Terms System
- Class mismatch: JS looks for `.term` but HTML uses `class="clickable-term"` — zero elements match.
- Solution: Use `class="term clickable-term"` (both classes).
- Modal HTML must be present in the body, not just CSS.
- `title` tooltips are NOT in-depth exploration — they're ~50 character captions.

## User Preferences (from this session)

- **Masculine aesthetic**: Bold weights (700-800), uppercase headings, direct language, no pastels.
- **Real visuals only**: No placeholder boxes. Source from Unsplash/Wikimedia or create SVG.
- **Page-by-page navigation**: Not infinite scroll. Previous/Next buttons + keyboard arrows.
- **Text size controls**: A- / A / A+ buttons for {HABIT} readability.
- **PDF export**: Only if working smoothly — scrap if it adds complexity.
- **Subtitle**: "A Collection of Timeless Kitchen Remedies" (not "Timeless Remedies for Modern Wellness").
