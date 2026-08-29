<!-- GENERICIZED: 12×{CLIENT} | source: skills/research/product-discovery/references/{CLIENT} -->
# {CLIENT} Domain Research Case Study

## Summary
Research for a {CLIENT} (Quranic exegesis) study platform — differentiating from "reader" apps by building a "study" environment.

## Domain
**{CLIENT}** (تفسير) = Quranic exegesis/commentary. Scholarly discipline explaining Quran's text, context, language, rulings. Methods: tradition-based (*bi-al-ma'thūr*), reason-based (*bi-al-ra'y*), linguistic.

## Existing Solutions
| App | Strength | Limitation |
|-----|----------|------------|
| Quran.com | Free, 50+ translations, word-by-word | Reader, not study tool |
| RecitID | Recitation ID, AI explain, 40+ translations | AI behind paywall |
| Ayat (KSU) | Classical {CLIENT}, Tajweed Mushaf | Academic UX |
| Al Quran {CLIENT} & by Word | Morphology, I'rab, 8 Arabic {CLIENT} | Buggy |
| Tarteel AI | AI recitation feedback | Narrow scope |
| Muslim Pro | Lifestyle + reader | Shallow tools |
| Quranic Arabic Corpus | Morphological/syntactic/semantic annotation | No {CLIENT} integration |

## Gaps Identified
1. No true "study" platform — readers, not deep study environments
2. Linguistic analysis siloed (root, morphology, syntax not woven into {CLIENT})
3. No open collaborative layer (no GitHub-equivalent for {CLIENT})
4. UX debt in content-rich apps
5. No "modern questions" bridge (classical↔contemporary)

## Data Sources Evaluated
| Source | Verdict | License |
|--------|---------|---------|
| Quran Foundation API | Build on | Free tier, requires auth |
| {CLIENT}/{CLIENT} | Build on | CDN-hosted, self-host recommended |
| fawazahmed0/quran-api | Build on | Unlicense, 90+ languages |
| QUL (TarteelAI) | Build on | Rich data, JSON dumps |
| Quranic Arabic Corpus | Build on | Academic, morphology gold standard |
| Tadabur dataset | Build on | Open-source |

## Join Feasibility
Confirmed: deterministic join on `verse_key` + `word_position` across sources. Arabic normalization layer required (hamza variants, diacritics, ta marbuta).

## Key Insights
- Study layer > reader: word is the unit of study (not verse)
- Licensing must be in data model from day one (copyrighted English translations vs public-domain Arabic)
- Modern Questions = AI-curated thematic index, not community feature (MVP scope)
- Precompute cross-references as batch job, not real-time
- MVP = one surah (Al-Fatihah), one {CLIENT} (Jalalayn), word-tap study pane, offline JSON, no auth

## Architecture Pattern
```
Client → API Gateway → Services → Cache (Redis) → Store (PostgreSQL)
                                        ↕
                                   ETL Pipeline (external sources)
```

v1: single endpoint serving pre-joined JSON. v3: microservices split.
