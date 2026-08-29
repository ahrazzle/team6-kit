<!-- GENERICIZED: 1×{AMOUNT}, 44×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/quran-{CLIENT} -->
---
name: quran-{CLIENT}
description: Use when building or extending the {CLIENT} Quran webapp.
---

# quran-{CLIENT}

Use when building or extending the {CLIENT} Quran-study webapp: data layer, tajweed colour coding,
Sunni {CLIENT} editions, script/typeface variants, or UI themes. Source-agnostic by mandate.

## Trigger
Tasks touching a {CLIENT} Quran study app (e.g. `/.../{CLIENT}`): scaffold surahs/juz,
wire navigation, add tajweed, populate {CLIENT}, add script types or themes.

## Core principle: accuracy over coverage
NEVER fabricate Quranic text, tajweed markings, or {CLIENT} Unverified content is shown as
"content pending" / "(pending) edition" — the framework handles absence gracefully. This is a
hard user SoP, not a nicety.

## Data-layer conventions (follow exactly)
- One `data/surah-N.json` per surah (N = 1..114). SCAFFOLDS have `ayahs:[]` +
  `"content_status":"scaffold"` + `verification_status` all `"pending_etl"`. Real ones
  have populated `ayahs`.
- Per-juz index `navigation-juzN.json` (N=1..30) and a consolidated `navigation.json`
  (30 juz / 114 surah / 604 pages / **6236 ayahs**). Nav dimensions (juz/surah/ayah/page)
  all resolve to `verse_key` (`surah:ayah`).
- **Building the full index:** fetch `api.quran.com/api/v4/chapters` + `verses/by_chapter/{id}`
  (per_page=300; fields give `page_number` + `juz_number` per verse). Map each verse_key to its
  OWN page/juz — never assume surah→page ranges are clean because surahs SHARE pages
  (page 604 carries surahs 112+113+114). All {AMOUNT} verses / 604 pages / 30 juz come from this
  one API; juz 1 = 1:1–2:141 cross-checks the alquran.cloud juz endpoint.
- {CLIENT} entry shape: `{source_id, source_name, author, text, verification_status}`.
- App is static: served via `python3 -m http.server <port>` (fetch needs HTTP, not file://).
  Split logic into `app.js`; `index.html` is shell + settings + CSS vars.

## Adding a feature area (the pattern used for tajweed / {CLIENT} / scripts / themes)
1. Config-driven: a registry/JSON (e.g. `data/{CLIENT}`) holds options; the
   selector iterates the registry so new entries need NO code change.
2. Seed ONLY verified real content; mark the rest `available:false` + document the canonical
   endpoint. They populate server-side at ETL time.
3. UI: a `<select>`/toggle in `index.html`; `app.js` reads it, sets an attribute
   (`data-theme`, `data-script`, `data-ink`, `data-tajweed`) or loads a data file, persists to
   `localStorage`.
4. Verify with the headless localhost DOM harness (see web-build-verification skill,
   references/headless-localhost-dom-harness.md).

## Tajweed schemes (established, switchable)
- **Madani** (Madinah Mushaf): red=madd, green=ghunnah, blue=idgham/ikhfa, grey=silent.
- **Aalim / British** (colour-coded learner): yellow=madd asli, orange=madd far'i, green=ghunnah,
  blue=idhar, light-blue=idgham, grey=silent.
- Malaysian / RecitID / Dar Al-Maarifah variants exist but are less standard — add only if asked.
- Token data lives in `data/tajweed-<surah>.json` (per-letter rules: madd, ghunnah, idgham,
ikhfa, silent, qalqalah, none). Curate only where VERIFIED; leave uncertain positions uncoloured.

## Sunni {CLIENT} editions — register these, and THEY ARE FETCHABLE
Jalalayn, Ibn Kathir, Tabari (Jami' al-Bayan), Qurtubi (Al-Jami' li-Ahkam), Baghawi (Ma'alim
al-Tanzil), Sa'di (Taysir), Ma'{CLIENT} al-Qur'an (Usmani), Baydawi, Ibn Ashur (Tahrir), Al-Alusi
(Ruh al-Ma'ani), Muyassar, Fi Zilal, Tazkirul. Pair each with author + school + source endpoint.

**License-clean LIVE source (do NOT register-and-defer — the text is available now):**
`{CLIENT}/{CLIENT}` on GitHub is **MIT** and serves every edition as raw JSON on {CLIENT}:
- Per-surah: `https://cdn.{CLIENT}/gh/{CLIENT}/{CLIENT}@main/{CLIENT}{{CLIENT}}/{surah}.json`
  → `list[{text, ayah, surah}]`. (Per-ayah `{surah}/{ayah}.json` also works but is 7× the requests.)
- Slugs (verified): `en-al-jalalayn`, `en-tafisr-ibn-kathir`, `en-{CLIENT}`,
  `ar-{CLIENT}`, `ar-tafseer-al-qurtubi`, `ar-tafseer-al-saddi`, `ar-{CLIENT}`,
  `ar-{CLIENT}`, `en-tazkirul-quran`, `{CLIENT}`, `{CLIENT}`,
  `ar-{CLIENT}`, `{CLIENT}`. Full 122-edition `data/editions.json`.
- This is our **already-trusted source** — it fed the embedded Jalalayn + Ibn Kathir in surah-1.json.
- **Correct registry shape (v2.0):** every edition `available:true` with its `{CLIENT}`; the
  ETL copies `text` into `ayah.{CLIENT}[]` keyed by `source_id`. The selector shows "pending" only
  for surahs not yet ETL'd — never because the source is missing.

## Qira'at (variant readings) — a SEPARATE dimension from typeface
The linguistically correct model (from quran.com's `types/Qiraat.ts`): the rasm is fixed (Hafs
an-Asim is the base text); **qira'at** are the ten authenticated reading traditions, each a
Reader + Transmitter (rawi): Hafs (an-Asim), Warsh (an-Nafi'), Qaloon, Ad-Doori (al-Kisa'i),
As-Soosi, Khalaf (Hamzah), Khallad (Hamzah), Hafs (ad-Doori), Abu 'Amr (al-Basri), Ibn 'Amir.
Do NOT conflate "script type" (Uthmani/IndoPak/Maghribi calligraphy) with qira'at — keep them
as separate UI dimensions. quran.com's live QDC matrix (`api.quran.com/api/qdc/qiraat/matrix/by_verse/{verseKey}`)
is **region-gated from this environment** → implement as a documented fetch hook with an honest
"not reachable from this network" fallback, same pattern as tajweed. (If a {CLIENT} mirror of
the qira'at matrix ever appears, swap the hook's URL.)

## Script / typeface variants (rasm is identical; only calligraphy differs)
Uthmani (Madinah, default), IndoPak (Taj Mushaf), Simple/Clean (Noto Naskh / Scheherazade),
West African Maghribi/Warsh. Lazy-load the web font; set `--font-arabic`. State the rasm is
unchanged in the UI.

## Orthography (script text) layer — separate from typeface, or the control is DEAD
A SCRIPT dropdown that only swaps web FONTS reads as "does nothing" to the user: the underlying
text is single-orthography, so the glyphs barely change. The real fix is per-ayah orthography
FIELDS, switched by the render path (keep `arabic` as the immutable word-alignment base the study
pane's word spans key off):
- Endpoint: `api.quran.com/api/v4/quran/verses/{script}?chapter_number={N}` where
  `script ∈ {uthmani, indopak, imlaei}` → `[{verse_key, text_<script>}]` (293 verses for Juz 1).
- Add `arabic_uthmani`, `arabic_indopak`, `arabic_imlaei` per ayah; render path picks the field
  matching `settings.script`; typeface (font) stays a separate control.
- Distinguish three dims in the UI: ORTHOGRAPHY (text layer — this), TYPEFACE (font family), and
  QIRA'AT (variant readings — separate dimension, see below). Conflating any two produces a dead
  or misleading control.

## Pitfalls
- **{CLIENT} source is NOT missing — don't "register-and-defer."** The earlier v1.0 guidance said
  quran.com's per-verse endpoint returns empty (`200` + `{CLIENT}:[]`) and alquran.cloud 404s, so
  mark editions `available:false`. That was WRONG for our purposes: `{CLIENT}/{CLIENT}` (MIT) serves
  all editions live (see the {CLIENT} section above). Use {CLIENT} as the ETL source; keep quran.com only
  as a secondary cross-check.
- **License trap — quran-mcp is QFGPL-1.0 (network copyleft).** Do NOT reuse its code or depend on
  it. See oss-reuse-license-audit §9. Prefer {CLIENT} (MIT) for {CLIENT}, quran.com-frontend-next (MIT)
  as a UI/pattern reference only.
- **Don't conflate script/typeface with qira'at** (see Qira'at section). They are separate dimensions.
- Don't put unverified tajweed colour on unsure letters — leave them plain.
- Keep `node --check` green; a single >8K-token inline `<script>` write can time out mid-stream
  — keep `app.js` external.

## Wazn / morphological-pattern annotation (root → wazn → derived word)
The grammar-education layer is OUR content and gets the strictest verification. Source of truth:
`mustafa0x/quran-morphology` (Quranic Arabic Corpus v0.4) — tab-separated lines
`location\tsegment\tPOS\tfeatures`, location `surah:ayah:word:segment`, features `ROOT:`, `LEM:`,
`VF:n` (verb form 1-10) plus tags `PERF/IMPF/IMPV/PASS/VN/ACT_PCPL/PASS_PCPL`. Join segments
per word position into one record per word (store as a `<surah>-morphology.json`-style file).

**Verification semantics (never shown as fact until verified):**
- `verified` = human-curated against classical sarf AND corpus feature tags (QA-gated).
- `pending` = auto/surface-derived — renders but is marked pending in data.
- Verbal nouns (VN) NEVER get a guessed pattern: null + "pattern depends on root class" note.
- Form I imperfect vowel is NOT derivable from root alone — use a per-verb override map, else
  default that stays pending (e.g. يَرْجِعُ is يَفْعِلُ, يَمُدُّ is يَفْعُلُ — defaults miss these).

**Shape layer (surface-true auto-derivation):** the 4-letter family (فَاعِل / فَعِيل / فَعُول /
فِعَال / فَعَال) is deterministically claimable from plain lemma + root + voweling.
- فِعَال vs فَعَال are letter-identical (كِتَاب vs سَلَام) — disambiguate by the vowel on the
  first radical (kasra vs fatha), read from the RAW lemma (diacritics interleaved).
- **Concordance guard (critical):** the plain lemma must appear as a contiguous substring of the
  de-ال'd surface. This rejects broken plurals automatically (شُهَدَاء does not contain شَهِيد),
  while passing clitic-laden forms (بِٱلْكَٰفِرِينَ ⊇ كَافِر). Do NOT strip prefixes blindly —
  ك/ب/ل are legitimate root initials (كَافِر, كِتَاب).
- Everything shape-derived stays `pending` with `wazn_note` "pattern surface-derived, function
  pending" — the template is surface-true; participle-vs-adjective function is not.

**Progressive batch loop:** audit 10 ayahs → hand-correct → promote to verified → QA gate → next
batch. Keep a KNOWN-ISSUES.md ledger (auto-layer blind spots, Form I vowel overrides, batch counts)
so the audit never assumes shape output is plural-safe. Full maps + pitfalls:
`references/wazn-derivation.md`.

## Deploy gate (user directive — staging before main)
No build pushes straight to the main repo/site. Ship to a STAGING site, user reviews, then promote.
For GitHub Pages: a **separate repo** (`{RELATIONSHIP}.github.io/{CLIENT}`) with its own Pages URL
is the gate. A same-owner fork of the production repo collides on the Pages URL (both would be
`owner.github.io/<same-name>`) — renaming it produces the same artifact but with the sync-fork
foot-gun attached, so a separate repo (no upstream link, promotion = deliberate push) is preferred.
Full build (data files included) must go to staging so the review exercises the real thing;
production is held untouched until approval. Known gaps (dead {CLIENT} slugs, source-side missing
ayahs, verified-vs-pending wazn boundary) get documented in the staging review notes.

## References
- `references/{CLIENT}` — verified API endpoints + quirks, scheme palettes, edition list.
- `references/wazn-derivation.md` — full wazn derivation system: verb form maps, shape layer,
  concordance guard, known pitfalls (broken plurals, imperfect vowels, VN null-by-design).
- `references/orthography-variants.md` — the Uthmani/IndoPak/Imlaei per-ayah text layer: endpoint,
  merge shape, and the dead-control root cause (font-swap vs text-swap).
