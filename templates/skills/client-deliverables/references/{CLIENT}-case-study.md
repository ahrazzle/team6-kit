<!-- GENERICIZED: 1×{AMOUNT}, 1×{CLIENT}, 9×{HABIT} | source: skills/client-deliverables/references/{CLIENT} -->
# {CLIENT} Case Study: Traditional Recipe Book for {HABIT} Audience

## Project Overview
- **Title:** "{HABIT} {HABIT}: Timeless Remedies for Modern Wellness"
- **Audience:** {HABIT} (60+, {HABIT}) and his wife
- **Scope:** 10 traditional healing recipes with deep cultural/Islamic context woven between steps
- **Output:** Single-page HTML book with real images, interactive elements, {HABIT}-friendly design

## Key Decisions & Lessons

### Recipe Selection
- Started with 10 recipes ranked by healthiness, naturalness, uniqueness
- Swapped Ashwagandha Moon Milk → Saffron & Cardamom Sleep Milk (drug interaction risk)
- Swapped Chyawanprash → Sage & Honey Tea (complexity/allergy risk)
- Swapped Tulsi Tea → Hibiscus Agua de Jamaica (geographic diversity)
- Removed astragalus/ginseng from bone broth (warfarin interaction)
- Final list: India (2), China (2), Japan (1), Middle East (2), Latin America (1), Arabic (1), Mediterranean (1)

### Islamic Content Approach
- User directive: "Don't force theology but find and explore real connections"
- Verified all hadith numbers (Black Seed: Bukhari 5688, not 5687)
- Quranic references verified (An-Nahl 16:69 for honey, Al-Waqi'ah 56:28 for sidr)
- Distinguished Chinese jujube (Ziziphus jujuba) from Quranic sidr (Ziziphus spina-christi)
- Presented Ayurvedic/Buddhist origins honestly while noting Islamic scholarly connections to ingredients

### Health Claims QA
- Added evidence-level badges: High / Moderate / Traditional
- Removed "over {AMOUNT} peer-reviewed studies" for curcumin (most are in vitro/animal)
- Removed "comparable to prescription medications" for hibiscus (8 mmHg vs 10-20 mmHg for drugs)
- Softened sage Alzheimer's claim to "well-tolerated and showed promise"
- Removed "anti-cancer effects" overclaiming for thymoquinone (mostly preclinical)

### Design Execution
- Title page: Memphis-style geometric frame, bold retro display type
- Color palette: warm cream base, coral/teal/gold accents
- Typography: 18px+ Lora serif body, DM Serif Display headings
- Masculine aesthetic: bold headings, strong letter-spacing, confident tone
- One recipe per spread with "Back to Contents" navigation
- Fixed top nav, skip links, smooth scroll anchors

### Visual Sourcing
- All 10 recipes have real Unsplash images
- Images verified via API before inclusion
- Botanical/contextual photos, not just ingredient shots
- Photographer attribution included

### Interactive Features
- Clickable terms with hover tooltips (phytic acid, Ibn al-Qayyim, spleen qi, thymoquinone, etc.)
- Pantry-availability icons (🟢🟡🔴)
- Evidence badges on every "Why This Heals" callout
- Safety warnings for hot liquids and {HABIT} physical demands
- "Where to Find Ingredients" shopping guide at the back

### {HABIT} Accessibility
- Physical demands audit completed for all 10 recipes
- Bone broth flagged HIGH (heavy lifting, hot straining) → Instant Pot solution
- Beetroot flagged MODERATE (hard peeling, staining) → pre-cooked beets solution
- Congee flagged LOW-MODERATE (long simmering) → rice cooker solution
- Prep/cook time, difficulty, servings on every recipe

## User Preferences Observed
- Comprehensive by default — if user asks for recipe book, produce digital + physical + research
- Honest evidence over marketing hype — don't overclaim health benefits
- Cultural authenticity matters — verify religious references, don't fabricate connections
- {HABIT} readability is non-negotiable — large type, clear hierarchy, safety warnings
- Masculine aesthetic when requested — bold, confident, structured
- Interactive elements appreciated — clickable terms, tooltips, navigation

## Technical Notes
- Grokipedia API installed for on-demand term definitions
- Unsplash API configured (50/day limit, access key provided)
- No faces of Islamic figures per Islamic rules
- Species distinctions matter (jujube vs. sidr) — state explicitly when relevant
