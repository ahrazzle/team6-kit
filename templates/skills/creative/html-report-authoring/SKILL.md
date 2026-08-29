<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/creative/html-report-authoring/SKILL.md -->
---
name: html-report-authoring
description: "Use when building large HTML report deliverables."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [HTML, Reports, Deliverables, File-Writing, Validation]
    category: creative
---

# HTML Report Authoring

Build large, self-contained HTML report deliverables (the user's preferred format for analytical work — they prefer HTML over markdown) without stream timeouts, structural corruption, or silent content loss.

## When to Use
- Any analytical deliverable the user wants as a visual HTML report
- Building a single large HTML file (>30KB) incrementally
- Reports with large data tables (100+ rows) that must be machine-injected

## Core Rules
1. **Keep every tool-call payload under ~8K tokens.** Large `write_file`/`patch` calls stall the stream and the action is NOT executed ("stream stalled mid tool-call"). Split content into sequential small writes (one section per call).
2. **Anchor every patch uniquely.** Never patch on a bare closing tag (`</section>`, `</div>`) — it matches multiple times (patch fails with "Found N matches") or replaces the WRONG closer. Anchor on the full last line of the preceding block.
3. **Verify each write landed** (file size, marker string) before the next.
4. **Injection must fail loudly.** When injecting generated content via placeholder replace, `assert anchor in text` first. A silent no-op (`str.replace` with a nonexistent marker) exits 0 and leaves the document incomplete.

## Build Protocol
1. Shell first, in parts: head+CSS, masthead, exec summary, TOC — each its own write.
2. Append body sections one per write, anchored on the previous section's unique closing line.
3. Generate data rows programmatically (python → `rows.html`), then inject via a script that asserts the anchor exists.
4. On structural mishap: **rebuild deterministically** — extract each section by its unique opening marker (`<section id="X">` up to the next `<section id=`), reassemble in canonical order, rewrite the file from components. Never hand-surgery duplicated blocks inside a corrupted file.
5. Validate before delivery:
   - Tag balance: HTMLParser stack check (unclosed tags, orphan closes)
   - Section order: regex all `<section id="...">` and confirm canonical order
   - Content audit: row counts (`<tr>`), empty-cell scan (`<td></td>`), placeholder leftovers (`__ROWS__`)
   - File ends with `</html>` exactly once
6. Open in the preview pane and read back a sample before delivering.

## Pitfalls
- **Ambiguous anchors**: bare `</section>` / `</div>` anchors either fail ("Found 2 matches") or silently replace the wrong closer, scrambling document order. Always include preceding unique text in `old_string`.
- **Silent injection no-op**: replacing a marker that never existed returns the string unchanged and exits 0. `assert anchor in text` before `replace`.
- **Duplicate-block cascade**: rebuilding a document from its own corrupted output compounds errors. Regenerate affected sections from scratch (verbatim payloads are recoverable from conversation history) rather than re-extracting the damaged file.
- **Stream timeout**: the message "Stream stalled mid tool-call; the action was not executed" means the file is NOT written. Split and retry; do not retry the same oversized payload.
- **Orphan closes after concatenation**: run a stack-based scan that reports `</section>` with no matching open; remove them before finalizing.
- **CSS token corruption mid-write**: hand-written CSS blocks can carry stray tokens right after generation (observed: `color:#c9b globalization;` — a word where a hex color belongs, in the masthead rule). Tag-balance and section-order validation will NOT catch this; only the rule silently degrades. After every chunk that contains CSS, scan the new block's `color:` / `background:` / `border:` declarations for invalid values (eyeball pass, or a regex like `#[0-9a-fA-F]{3,8}[^;]*[a-z]`), fix immediately, and re-run full validation at the end.

## Feeding Data Into the Report
For large per-item tables (114 rows, etc.):
- Extract source data with parallel subagents — chunked by range, verbatim-only rule, entry boundaries mapped from page titles when the source is paginated.
- Workers write JSON to a shared dir; a build script validates count/uniqueness (dups, missing numbers) before generating rows.
- If a worker dies (connection error), re-dispatch that chunk with a leaner brief; other chunks' outputs are unaffected.
- When a late async batch notification arrives after integration, verify integration state (counts, spot-check rows) instead of re-processing.

## References
- `references/large-report-assembly-case.md` — the surah-names report session: full failure sequence (scrambled order, silent injection, duplicate blocks) and the fixes that worked.
