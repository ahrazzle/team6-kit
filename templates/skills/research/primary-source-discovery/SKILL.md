<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/research/primary-source-discovery/SKILL.md -->
---
name: primary-source-discovery
description: Use when locating the oldest accessible copy of a text.
version: 1
author: {RELATIONSHIP}
license: MIT
metadata:
  hermes:
    tags: [research, provenance, manuscripts, primary-sources, history]
    related_skills: [source-evaluation]
---

# Primary Source Discovery

Find the oldest or most authoritative *accessible* copy of a historical text,
and prove it is actually reachable — not merely that it exists.

## When to use
- "Find the oldest version of the book"
- "Earliest edition / first printed edition / oldest manuscript"
- "Publicly accessible copy of [historical text]"
- Provenance / stemma research for a text you intend to edit, translate, or study

## Core principle
**"Oldest surviving" ≠ "oldest accessible."** Always report both. The physically
oldest manuscript may sit in a locked vault; the oldest *reachable* version is
often a 19th-century printed edition typeset from that manuscript strand.

## Steps
1. **Map the landscape first.** Several independent `web_search` queries, including
   the vernacular / transliterated title. Cover manuscripts, first prints, critical
   editions, and digitized copies.
2. **Distinguish manuscript from print.** A MS predates any print. Build the stemma:
   which MSS are autograph/authorial, copied in the author's lifetime, or underlay
   first printed editions. A translator's textual-history introduction is gold — it
   often lists the full MS census with sigla.
3. **Verify ACTUAL accessibility — do not trust snippets.** Search engines return
   mirror/aggregate pages that mislabel items. For an Archive.org candidate:
   - `web_extract` the `https://archive.org/download/<identifier>/` directory page;
     confirm a `.pdf` (or `_djvu.txt`, `jp2.zip`) actually exists there.
   - A bare identifier match can be a *false positive* (different book, same number).
     Open the item page to confirm title, language, date before citing.
   - **Acquisition mechanics (verified this session):**
     * Use `https://archive.org/download/<id>/<id>_djvu.txt` for the OCR text layer —
       this works and returns real text. The `stream/<id>/<id>_djvu.txt` pattern
       returns an HTML error page, NOT the text. Use `download/`, never `stream/`.
     * Don't guess part-number PDFs like `p2<id>.pdf` / `p3<id>.pdf` — they 404.
       Pull the item's *metadata* JSON (`https://archive.org/metadata/<id>`) and read
       the `files[]` list to find the real PDF/DjVu names. Often one combined volume
       PDF exists (`<id>.pdf`) and the "part" split is an illusion.
     * **Arabic vs French djVu OCR:** de Slane's 1863 French OCR is clean and usable;
       Quatremère's 1858 *Arabic* djVu OCR is unusable noise (Arabic OCR garbles
       heavily). Keep the Arabic PDF as a spot-check edition, not a text source.
   - **Wikisource (ar.wikisource.org) for the Arabic base text:**
     * Top "book" page is a TOC; real text lives on nested sub-pages (e.g.
       `مقدمة ابن خلدون/الكتاب الأول في طبيعة العمران البشري`).
     * Fetch raw with `?action=raw`, but Wikimedia **403s the default Python UA** —
       send a `User-Agent` header (any browser string) or the request is forbidden.
     * Wikitext carries a `{{ترويسة}}` template header and `[[link|label]]` markup;
       strip before translation use.
4. **Establish the provenance chain.** State which MS strand a printed edition
   descends from (e.g. "MS A formed the basis of Quatremère's edition"). This is
   what makes an old print a faithful proxy for the oldest copy.
5. **Report a ranked hierarchy** with confidence levels: oldest surviving → oldest
   accessible → gaps (MSS not digitized, prints not freely downloadable). Cite URLs
   verified, not inferred.

## Pitfalls
- **Search-snippet false positives.** An Archive.org identifier that "looks right"
  can be an unrelated item (a Brooklyn city directory). Open the item page first.
- **Guessed filenames 404.** Verify via directory listing, then cite the real path.
- **"First edition" ≠ "best edition".** First print may follow a single MS; a later
  critical edition collates many. Report both; let the user pick fidelity vs rigor.
- **"Not located" ≠ "does not exist."** A MS or print may exist in a gated library
  scan you could not reach. State that explicitly; never assert absence.

## Verification gate
Before calling a source "accessible", you must have either (a) retrieved the real
file-listing page and seen the downloadable artifact, or (b) extracted content from
the item. A search-result title alone is NOT verification.

## References
- `references/muqaddimah-provenance.md` — worked example: manuscript stemma and
  verified-accessible editions of Ibn Khaldun's *Al-Muqaddimah* (project: prolego).
  Reuse the *pattern*, not just the data.
