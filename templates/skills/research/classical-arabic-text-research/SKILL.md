<!-- GENERICIZED: 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/classical-arabic-text-research/SKILL.md -->
---
name: classical-arabic-text-research
description: "Use when researching a classical Arabic/Islamic text."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Arabic, Translation, Manuscripts, Textual Criticism, Islamic Scholarship]
    category: research
    related_skills: [grounded-citations, source-evaluation, html-report-authoring]
---

# Classical Arabic Text Research

Research a classical Arabic / Islamic work deeply enough to ground a new translation, an edition decision, or a study — then hand the analysis stage a decision matrix, not a data dump. Built for the Prolego project (Al-Muqaddimah translation) and reusable for any classical-text work ({CLIENT}, hadith, philosophy, historiography).

## When to Use
- A translation project needs its base-text decision (which Arabic edition / manuscript state to translate from)
- The user asks about "the original" of a classical work — its language, register, manuscript tradition
- Verifying what prior translations exist, from what bases, under what doctrine
- Building a terminology glossary for a classical text's technical vocabulary

## Core Workflow
① **Identify the work and authorial context.** Full title, composition dates and places, author's scholarly identity (jurist / philosopher / historian — the discipline shapes the vocabulary: a Mālikī jurist's terms carry legal weight).
② **Language & register profile.** What kind of Arabic (classical, post-classical, Maghribī/Eastern); the author's relationship to the norms (a translator's introduction often says outright that the author deviated from grammarian's Arabic); style fingerprints (long sentences, parallelism, pronoun chains, inversions); embedded vernacular material (dialect poems, quoted street verse) = register switches a translation must have a policy for.
③ **Manuscript map.** Lifetime copies and sigla; holograph/autograph status (and whether an authentic autograph *note* survives even when the holograph is lost); which witnesses carry the early vs. late state of the text.
④ **Authorial states vs. "recensions".** Classical works often exist in two authorial states (early draft vs. later revision). Say what the evidence shows; use "recension" only if the scholarship does. Authorial additions/corrections are the norm, not scribal corruption.
⑤ **Edition lineage.** Editio princeps → reprints → modern critical edition. Check each link for: free editorial emendation (`lectio facilior` traps), silent omission or censorship (occult chapters, dialect poems, religious remarks), misprint accumulation across reprints. A modern critical edition (if one exists) is the recommended base — but inspect its apparatus; "critical" is a claim, not a guarantee.
⑥ **Translation landscape.** Every prior translation, its base text, and its doctrine (literal / modernizing / recast). This sets the positioning for a new translation and exposes what a new one can genuinely improve (often: the poetry and end-matter, the terminology consistency, the variant apparatus).
⑦ **Terminology crux glossary.** The technical terms — often the author's own coinages for his "new science" — with prior renderings and the anachronism risks (e.g., "state" for `dawla`, "nationalism" for `ʿaṣabiyya`). Consistency policy is a translation decision, not an afterthought; prior translators admitted their own inconsistency (a target to beat).
⑧ **Deliverable.** Visual HTML dossier (user preference; see html-report-authoring): exec summary → methodology → language → text history → editions → translations → decision matrix → access table → gaps → sources. Every load-bearing claim carries a confidence chip (high/moderate/low/unknown). Human-readable numbered Sources list in the HTML must keep 1:1 id parity with the citation ledger (grounded-citations), even though the block is hand-styled for readability.

⑨ **File-level validation when a candidate file is supplied.** If the user hands over a PDF/.doc and asks "is this a valid original text we can use?", run the forensic edition check in `references/source-file-validation.md` BEFORE any translation work: metadata (`file`/`pdfinfo`/`textutil` + author/edit-time red flags) → text-layer cleanliness (`pdftotext`/`textutil`, spot-read for OCR gibberish) → diacritic ratio (unvocalized ≈ 0.003 = not a base; vocalized ≈ 0.08+ = edited) → edition markers (`grep` colophon for 1886/بولاق/باريس/etc.) → fetch the real critical edition as the recommended base. A file can contain the genuine text yet still fail as a base (garbled OCR, unsourced paste, unvocalized). Report a File × Usable-as-base table with confidence chips; never call such a file a valid base.

## Sources to Hunt First
- **Translator's introductions** to major translations — often the one place where manuscripts, editions, and translation history are treated together (e.g., Rosenthal's Muqaddimah introduction).
- **Full text of an existing translation** on Internet Archive — download the plain text and grep it for verbatim evidence of the passages you need; do not quote from memory.
- **Archival records**: national library catalogues (BnF/Gallica), IIIF manifests (Biblissima), Ottoman palace inventories, manuscript-platform records.
- **Free Arabic text platforms** (Shamela, Arabic Wikisource, noor-book) for the Arabic text — ALWAYS verify which printed edition they reproduce (Bulaq-lineage is common and editorially contaminated).
- **Wikimedia Commons** for autograph / manuscript photographs when provenance is discussed in scholarship.

## Pitfalls
- **Censored / expurgated editions**: some printed editions silently omit occult chapters, dialect poems, and remarks on religion or sexuality. Check what an edition dropped before using it as a base.
- **Snippet-level citations for load-bearing claims**: extract the page before citing (grounded-citations rule).
- **"Original copy" ambiguity**: confirm whether the user means the author's autograph, a specific printed edition, or the original-language text generally. The edition-lineage map resolves the question once a physical copy is identified.
- **Poetry / vernacular end-matter** is the weakest zone of early printed editions — a new translation can genuinely improve here.
- **Author's own date discrepancies** (e.g., five months in the work vs. six in the autobiography): note, don't silently resolve.
- **Unverifiable leads**: a claim that survives in one secondary source (e.g., a manuscript reportedly containing vernacular poems) stays flagged unverified until the primary witness is checked.
- **Supplied-file trap**: a file that contains the genuine text is NOT automatically a usable base. A garbled-OCR scan (diacritic ratio ~0.002, extract reads as `ملواوعييةالرم…`), an unsourced paste (Word doc with author "The Baker Street Irregular", 5-min edit time, unvocalized), or an unverified edition label ("1886" asserted only in IA metadata, absent from the book's own colophon) all fail as bases. Run `references/source-file-validation.md` before trusting any dropped file.
- **Filename ≠ edition**: "1886 Edition" in a filename is a claim, not the book's date. PDF `CreationDate` dates the *file* (IA derivatives read 2025); the underlying edition must be proven from the book's own imprint, not its title string.
- **Translation doctrine — meaning-first wins over formal equivalence.** For the
  Prolego project the user explicitly set the goal: a smooth English that *captures
  essence*, NOT a word-for-word render that sacrifices readability for "integrity."
  This is **dynamic equivalence** (sense-for-sense, modern idiom, sentence restructured)
  — the opposite of Rosenthal's formal-equivalence style, which the user found obtuse.
  Encode this as the default posture for any new translation work here. It also solves
  the license problem: Rosenthal (© Princeton) is excluded anyway, so the base is the
  **public-domain Arabic** (Wikisource / Quatremère 1858) translated fresh, with
  **de Slane's 1863 French** (public domain, rated the best meaning-capture) as the
  free meaning-anchor. Lock the crux-term glossary (ʿaṣabiyya, ʿumrān, etc.) ONCE in a
  translator's note before chapter work, so the voice stays consistent across the whole.

## Verification
- Verbatim evidence pulled from full translation texts on disk, not from memory.
- Manuscript/edition claims cross-corroborated across ≥2 independent sources (translator's intro + modern manuscript studies + archival records).
- Explicit gap list: what could NOT be inspected (print-only critical editions, paywalled papers) with confidence chips, so the analysis stage knows where judgment must substitute for evidence.

## References
- `references/muqaddimah-research-bank.md` — the Al-Muqaddimah research bank: composition timeline, manuscript map (A–E + Fez), edition lineage, translation history, terminology glossary, key URLs, open questions. Reuse for Prolego; do not re-research from scratch.
- `references/source-file-validation.md` — when the user supplies a PDF/.doc and asks "is this a valid original text we can use?": a reproducible forensic recipe (metadata → text-layer cleanliness → diacritic ratio → edition-marker grep → fetch real critical edition) to separate genuine-but-unusable files (garbled OCR, unsourced paste, unvocalized) from a valid base.
