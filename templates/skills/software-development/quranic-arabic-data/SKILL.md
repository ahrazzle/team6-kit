<!-- GENERICIZED: 9×{CLIENT} | source: skills/software-development/quranic-arabic-data/SKILL.md -->
---
name: quranic-arabic-data
description: Process Quranic Arabic text for study apps.
tags: [quran, arabic, tafsir, corpus, normalization, islam]
---

# Quranic Arabic Data Processing

## Trigger
Use when working with Quranic Arabic text, building Quran study/tafsir apps, or integrating data from Quranic Arabic Corpus, {CLIENT} tafsir API, Quran Foundation API, or QUL JSON dumps.

## Core Principles

1. **Normalize Arabic before matching** — Sources use different character variants (hamza forms, diacritics, ta marbuta, dagger alif, wasla). Always normalize to canonical form before joining.
2. **Total root occurrences, not form counts** — When reporting how many times a root appears in the Quran, count ALL derived forms (verbs, nouns, participles), not just the specific form of the word being studied. The Corpus dictionary page gives the total.
3. **`verse_key` + `word_position` is the stable join key** — This compound key works across Corpus wordbyword data and tafsir APIs.

## Arabic Normalization Pipeline

Order matters. Apply these steps in sequence:

```python
# 1. Strip diacritics (tashkeel) — but convert dagger alif to full alif
# 2. Normalize hamza variants (أ/إ/آ → ا)
# 3. Normalize wasla (ٱ → ا)
# 4. Convert dagger alif (ٰ) to full alif (ا)
# 5. Normalize ta marbuta (ة → ه)
# 6. Strip tatweel/kashida (ـ)
```

### Diacritics to Strip
- Fathatan (ً), Dammatan (ٌ), Kasratan (ٍ)
- Fatha (َ), Damma (ُ), Kasra (ِ)
- Shadda (ّ), Sukun (ْ), Maddah (ٓ)
- Hamza Above (ٔ), Hamza Below (ٕ)
- Tatweel/Kashida (ـ) — visual elongation only

### Special Cases
- **Dagger alif (ٰ)** is a combining vowel marker that represents a full alif. Convert to ا, don't strip.
- **Wasla (ٱ)** is a silent alif. Convert to ا for canonical form.
- **Small noon above (ۤ)** — combining mark, strip.

## Data Sources

### Quranic Arabic Corpus (`corpus.quran.com`)
- **Word-by-word pages**: `wordbyword.jsp?chapter=N&verse=M` — gives Arabic, transliteration, translation, morphology per word
- **Dictionary pages**: `qurandictionary.jsp?q=XYZ` — gives total root occurrence count across ALL derived forms, plus breakdown by form
- **Join key**: `verse_key` (e.g., `1:1`) + `word_position` (e.g., `3`)

### {CLIENT} Tafsir API (`{CLIENT}/tafsir_api` on GitHub)
- **Editions list**: `tafsir/editions.json` — full catalog with slugs, languages, authors
- **Tafsir per surah**: `tafsir/{slug}/{surah_number}.json`
- **Note**: Not all tafsirs have English editions. Ibn Kathir English IS available (`en-tafisr-ibn-kathir`, ID 35). Check editions.json before assuming availability.
- **Self-host recommended** for production (CDN rate limits possible)

### Quran Foundation API
- Requires `x-auth-token` + `x-client-id` headers
- Has tafsir, word-by-word, translations, audio
- Free tier available; register at `api-docs.quran.foundation`

### QUL (Quranic Universal Library by TarteelAI)
- JSON dumps available at `qul.tarteel.ai`
- Full CMS: tafsir, translations, word-by-word, audio, morphology, grammar
- No public API — download JSON or self-host Rails app

### alquran.cloud (navigation / per-ayah metadata)
- **Juz dump**: `api.alquran.cloud/v1/juz/{N}` — every ayah with per-ayah `page`, `juz`, `ruku`, `hizbQuarter`, `manzil`, `sajda`, plus surah metadata. Authoritative for building navigation indexes.
- **Juz 1 verified**: 148 ayahs (1:1-1:7 + 2:1-2:141), pages 1-21.
- **Per-surah**: `api.alquran.cloud/v1/surah/{N}` (add `editions=` for translations).
- Page ranges MUST be derived from this per-ayah data, never hand-typed or copied from an approximate index — see pitfall 7.

## Occurrence Counting (Critical)

**The Corpus dictionary page total is the authoritative count for "how many times does this root appear in the Quran."**

When a user taps a word, they want to know: "How many times does this root appear across the entire Quran?" — not "How many times does this specific derived form appear?"

### Example of the Error
- Root ص-ر-ط (path): Corpus says 45 total
- If you only count the noun `ṣirāṭ` (which is the only form), you get 45 — correct by coincidence
- Root غ-ي-ر (other than): Corpus says 154 total
- If you only count the nominal `ghayr` (147), you miss the verb forms (yughayyiru: 4, yataghayyar: 1) and participles (2) — wrong total

### How to Query
1. Get the root from the wordbyword page
2. Fetch `corpus.quran.com/qurandictionary.jsp?q={root_letters}`
3. Extract the first line: "The triliteral root _X_ occurs N times in the Quran, in Y derived forms"
4. Use that N as the total

## Source Join Strategy

```
┌─────────────────────────────────────────────┐
│  WORD TAP                                   │
│  verse_key: "1:1" + word_position: 3        │
├──────────┬──────────┬──────────┬─────────────┤
│  Verse   │  Word    │  Root    │  Tafsir     │
│  Text    │  + Morph │  → Total │  per Ayah   │
│  (Corpus)│  (Corpus)│  (Corpus)│  ({CLIENT})    │
└──────────┴──────────┴──────────┴─────────────┘
```

Two-tier join:
1. **Verse level**: `verse_key` → tafsir text ({CLIENT}) + all words in verse (Corpus)
2. **Word level**: `verse_key + word_position` → morphology + root (Corpus) → all occurrences of that root (Corpus dictionary)

## Output Schema for Study Pane

Per word tap, produce:
```json
{
  "arabic": "ٱلرَّحْمَـٰنِ",
  "arabic_normalized": "الرحمن",
  "translation": "the Most Gracious,",
  "root": "ر-ح-م",
  "root_meaning": "to be merciful",
  "morphology": {
    "tag": "ADJ",
    "description": "genitive masculine singular adjective",
    "arabic_grammar": "صفة مجرورة"
  },
  "occurrences": {
    "total": 339,
    "breakdown": [
      {"form": "raḥmān (nominal)", "count": 57},
      {"form": "raḥīm (nominal)", "count": 116}
    ]
  },
  "tafsir": [
    {
      "source_id": "{CLIENT}",
      "source_name": "Tafsir al-Jalalayn",
      "text": "..."
    }
  ]
}
```

## Licensing Notes
- Classical Arabic tafsirs (Ibn Kathir, Tabari, Jalalayn): public domain originals
- English translations: often copyrighted — audit per-edition
- Corpus: CC BY-NC
- {CLIENT}: MIT
- fawazahmed0: Unlicense

## Common Pitfalls

1. **Assuming English tafsir exists** — Always check editions.json first. Many tafsirs are Arabic or Urdu only.
2. **Counting forms instead of roots** — See "Occurrence Counting" section above. This destroys trust with scholarly audiences.
3. **Ignoring dagger alif** — Results in `الرحمن` becoming `الرحمان` or `الرحمـن` depending on stripping strategy.
4. **Using CDN-hosted data in production** — Self-host {CLIENT} and QUL data. CDNs have rate limits and availability risk.
5. **Not tagging source_id on every record** — Every tafsir excerpt, translation, and linguistic note must carry its origin for the source framework.
6. **fetch() over file://** — Browsers block `fetch('./data.json')` when opening HTML via `file://` (CORS). For local-only prototypes, embed data directly in a `<script>` tag. For production, serve over HTTP (`python3 -m http.server`).
7. **Trusting approximate navigation page ranges** — A navigation index with hand-built page→ayah ranges can silently disagree with the authoritative per-ayah data (observed: index said page 3 = 2:6-2:20, actual API data = 2:6-2:16). Always derive page ranges from `api.alquran.cloud/v1/juz/{N}` per-ayah `page` fields, and QA-verify a sample before building UI on them.
8. **Stale browser/CDN cache after a data fix** — If users report "all words show the same pattern/value" after you fixed embedded data, the browser is likely serving an old copy. Never tell users to hard-refresh ("the user shouldn't have to deal with it"). Add cache-busting meta tags to every self-contained HTML page so it self-invalidates:
   ```html
   <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
   <meta http-equiv="Pragma" content="no-cache">
   <meta http-equiv="Expires" content="0">
   ```
   GitHub Pages' CDN can also hold a stale copy for minutes after push; a version comment in the file forces a fresh deployment.
9. **Claiming data is wrong without checking the file + git history** — A "data integrity flag" based on a misread or assumed state burns trust as fast as a real bug. Observed: an agent claimed a navigation index's page ranges were wrong (said page 3 = 2:6-2:20, "needed correction") when the file on disk and its git history both had the correct 2:6-2:16 — the claim was fabricated from a faulty comparison. Before asserting a data error: (a) read the actual file, (b) check `git log`/`git show` for the version under discussion, (c) re-derive the value from the authoritative source. Only then flag. "Verify, don't assume" applies to the verifier too.
10. **Wazn/patterning is its own accuracy minefield** — See `references/wazn-annotation.md` for the full pipeline rules: imperatives must use IMPV corpus tags (not perfect), verbal nouns carry NO pattern (pattern depends on root class, hand-verify), auto-derivation must never emit a pattern it cannot source from corpus features, and shape-derived patterns (e.g. فِعَال vs فَعَال) are surface-true but pending — broken plurals (شُهَدَاء → فُعَلَاء, not فَعِيل) are the shape layer's blind spot and must stay manual.

## References
- `references/arabic-normalization.md` — Full normalization rules, test cases, edge cases
- `references/corpus-api.md` — Corpus URL structure, response shapes, query patterns
- `references/tafsir-sources.md` — {CLIENT} slug catalog, Quran Foundation endpoints, QUL data model
- `references/study-pane-patterns.md` — User-approved frontend patterns: bidirectional highlighting, wazn display, 4-level progressive disclosure, single-source switcher, navigation shell
