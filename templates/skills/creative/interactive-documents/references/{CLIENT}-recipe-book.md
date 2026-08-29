<!-- GENERICIZED: 1×{AMOUNT}, 1×{CLIENT}, 9×{HABIT}, 2×{RELATIONSHIP} | source: skills/creative/interactive-documents/references/{CLIENT} -->
# {CLIENT} Recipe Book — Session Notes

## Project Overview
Traditional recipes and formulas for healthy consumables. Digital mini recipe book, 10 recipes with deep context woven between steps. Target: {HABIT}, 60+ {HABIT}, {HABIT}. His wife, also 60+.

## Title
"{HABIT} {HABIT}: Timeless Remedies for Modern Wellness"
- Compiled for {HABIT}
- by Ahraz {RELATIONSHIP} and Team6

## Final 10 Recipes
1. Kitchari (Ayurvedic rice-lentil porridge)
2. Ginger, Goji & Jujube Bone Broth (TCM)
3. Golden Milk / Haldi Doodh (turmeric, black pepper, ginger)
4. Congee with Shiitake (China/Japan)
5. **Saffron & Cardamom Sleep Milk** (Middle East) — REPLACES Ashwagandha Moon Milk
6. Miso Soup with Wakame (Japan)
7. Hibiscus & Cinnamon Agua de Jamaica (Latin America)
8. Beetroot, Ginger & Rose Sharbat (Middle East)
9. Black Seed (Habba Sawda) Honey Paste (Arabic)
10. **Sage & Honey Tea** (Mediterranean) — REPLACES Chyawanprash

**Reason for swaps:** Ashwagandha flagged for {HABIT} safety (blood pressure interaction, thyroid concerns). Chyawanprash flagged for {HABIT} safety (48-ingredient complexity, sugar content, difficulty sourcing). Both replaced with {HABIT}-accessible alternatives with Islamic/Middle Eastern roots.

## APIs Used

### Grokipedia API
- Package: `grokipedia_api` (installed at `/Users/{RELATIONSHIP}/Library/Python/3.9/lib/python/site-packages/`)
- Import: `from grokipedia_api import GrokipediaClient`
- Usage: `client = GrokipediaClient(); result = client.search('term')`
- Result structure: `result['results'][0]['title'], result['results'][0]['snippet']`
- Rate limit: Add `time.sleep(0.5)` between calls
- Note: Some terms (Avicenna, Al-Zahrawi) hit 502 errors — have custom fallback content ready

### Unsplash API
- Endpoint: `https://api.unsplash.com/search/photos`
- Auth: `client_id` query param with access key
- Limit: 50 requests/day
- Recipe queries that worked well:
  - `rice lentil porridge bowl` → kitchari
  - `turmeric golden milk` → golden milk
  - `bone broth soup` → bone_broth
  - `congee rice porridge mushroom` → congee
  - `saffron milk drink` → saffron_milk
  - `miso soup japanese` → miso_soup
  - `hibiscus tea drink` → hibiscus
  - `beetroot juice drink` → beetroot_sharbat
  - `sage tea honey` → sage_tea
  - `black seed honey` → returned NO results — need user-generated visual

## Custom SVG Visuals Generated
1. **silk_road_map.svg** — Trade route map showing ingredient movement
2. **nitric_oxide_pathway.svg** — Beetroot → nitric oxide → vasodilation process
3. **curcumin_absorption.svg** — How piperine blocks curcumin breakdown in liver
4. **spice_route_map.svg** — Global spread of spices (India, China, Iran → world)
5. **timeline.svg** — {AMOUNT} years of kitchen medicine history
6. **body_diagram.svg** — Anatomical diagram showing where golden milk works

## Clickable Terms (30+)
Scientific compounds (piperine, curcumin, thymoquinone, beta-glucans, anthocyanins, zeaxanthin, nitric oxide, ACE inhibitors)
Cultural/historical figures (Imam Ibn al-Qayyim, Ibn Sina/Avicenna, Al-Zahrawi/Abulcasis, Scholey)
TCM/Ayurvedic concepts (agni, spleen qi, tridoshic, Panchakarma, immunosenescence)
Religious references (Prophetic Medicine, Al-Tibb al-Nabawi, Habba Sawda)

## Design System
- **Body text:** 18px+, 1.6+ line height, Lora/DM Serif Text
- **Background:** Warm cream (#faf6ee) with subtle paper texture
- **Headings:** Deep teal/burgundy, bold retro display type
- **80s accents:** Coral, teal, gold — Memphis frame on title page
- **Pantry icons:** 🟢 Pantry staple | 🟡 Easy to find | 🔴 Specialty store

## CRITICAL LESSON: Destructive Script Overwrites
A Python script that does `with open('index.html', 'w')` will **destroy** the existing file. If the script only has partial data, you lose everything. ALWAYS:
1. Run `cp index.html index.html.bak` before any script that writes to the same file
2. Prefer targeted `patch` operations over full-file rewrites
3. Write to a NEW file first, verify, then rename

## Hadith Reference Correction
Black seed hadith is **Sahih al-Bukhari 5688** (not 5687). Always verify hadith numbers.

## Islamic Context Approach
- Present cultural origins honestly
- Don't force theology on Ayurvedic/Buddhist-rooted recipes
- Highlight authentic Islamic connections (Black Seed, Honey, Saffron, Rose, Ginger)
- No faces of Islamic figures (per Islamic rules)
