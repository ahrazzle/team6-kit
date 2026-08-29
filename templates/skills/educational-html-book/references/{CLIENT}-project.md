<!-- GENERICIZED: 9×{CLIENT}, 4×{HABIT}, 5×{RELATIONSHIP} | source: skills/educational-html-book/references/{CLIENT} -->
# {CLIENT} Project Reference

## Project Scope
Traditional medicinal recipe book for a {HABIT} {HABIT} (60+) reader. 10 recipes selected for healthiness, naturalness, uniqueness, and safety. Output: interactive HTML book with deep context woven between steps.

## Finalized Recipe List (Locked)
1. **Kitchari** (Ayurvedic rice-lentil porridge) — India
2. **Golden Milk / Haldi Doodh** (turmeric, black pepper, ginger) — India
3. **Ginger, Goji & Jujube Bone Broth** — China (⚠️ HIGH physical demand, use Instant Pot)
4. **Congee with Shiitake** — China/Japan (Use Rice Cooker)
5. **Saffron & Cardamom Sleep Milk** — Middle East
6. **Low-Sodium Miso Soup with Wakame** — Japan
7. **Hibiscus & Cinnamon Agua de Jamaica** — Latin America
8. **Beetroot, Ginger & Rose Sharbat** — Middle East (⚠️ MODERATE physical demand, use pre-cooked beets)
9. **Black Seed (Habba Sawda) Honey Paste** — Arabic/Prophetic
10. **Sage & Honey Tea** — Mediterranean

## Geographic Distribution
India (2), China (2), Japan (1), Middle East (2), Latin America (1), Arabic (1), Mediterranean (1)

## Safety Decisions
- **Ashwagandha removed** — levothyroxine interaction (thyroid medication common in seniors), documented thyrotoxicosis case reports
- **Chyawanprash removed** — 48-herb complexity, GI discomfort in elderly, BP elevation risk
- **Tulsi Tea removed** — India concentration concern (4 Indian recipes was too many)
- **Astragalus & Ginseng removed from Bone Broth** — warfarin interaction, immunosuppressant concerns, bleeding risk

## Islamic Context Approach
- Authentic connections only: Black Seed (hadith 5688), Honey (Quran 16:69), Saffron (Ibn Sina), Rose water (Ibn al-Qayyim)
- Jujube/Sidr distinction: Quran mentions *sidr* (lote-tree, Ziziphus spina-christi) as cosmic symbol, not as bone broth ingredient
- No fabricated theology on Ayurvedic/Buddhist-rooted recipes
- Honest cultural origins presented

## Physical Demand Audits
- **Bone Broth (HIGH)**: Heavy lifting, hot liquid straining → use Instant Pot, pre-cut bones, smaller batch
- **Beetroot Sharbat (MODERATE)**: Hard peeling, staining → use pre-cooked beets, microplane grater, gloves
- **Congee (LOW-MODERATE)**: Long simmering → use rice cooker with congee setting
- **Kitchari (LOW)**: Occasional stirring → timer reminders, pre-washed lentils

## Evidence Levels
- **High**: Hibiscus (meta-analysis, 7.92 mmHg SBP reduction)
- **Moderate**: Saffron (clinical trials, PMID 24290594), Golden Milk (Planta Medica 1998), Black Seed (preclinical + small human trials), Beetroot (Hypertension 2015)
- **Low-Moderate**: Congee + Mushrooms, Herbal Bone Broth
- **Traditional**: Kitchari

## Design System
- **Palette**: Deep navy primary (#1a1a2e), slate blue secondary (#16213e), cobalt accent (#0f3460), coral highlight (#e94560), cream background (#faf6ee)
- **80s accents**: Memphis geometric patterns as section dividers, not dominant
- **{HABIT} readability**: 18px+ serif body, 1.6+ line height, high contrast
- **Masculine mode**: Stronger weights (700-800), uppercase headings, no pastels

## API Keys (User-Provided)
- **Unsplash**: client_id=U-EmS--yFXUR3-qdQ_vEYdgAeB9vosk1W2iJBdRP8zU (50/day limit)
- **Wikipedia**: Used as fallback for Grokipedia (which had 502/404 errors)

## Grokipedia Issues
- `grokipedia-api` installed but Python 3.9 (system) cannot import it
- Module exists at `/Users/{RELATIONSHIP}/grokipedia-api/grokipedia_api/` but import fails
- Pivoted to Wikipedia API for reliable data

## File Locations
- `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}` — Main book (90.1 KB, 842 lines)
- `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}` — Design system (25 KB)
- `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}` — Project scope and status
- `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}` — {HABIT} physical demands audit
