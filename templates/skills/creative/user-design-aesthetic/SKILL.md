<!-- GENERICIZED: 2×{CLIENT}, 1×{HABIT}, 1×{RELATIONSHIP} | source: skills/creative/user-design-aesthetic/SKILL.md -->
---
name: user-design-aesthetic
description: User design preferences for HTML deliverables.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, preferences, accessibility, ui, ux]
    related_skills: [claude-design]
---

# User Design Aesthetic Preferences

Load this skill alongside `claude-design` for this user's HTML deliverables.

## Palette & Tone
- Masculine saturated palette — NOT pastel fintech-dashboard energy
- Gold #d4a853 cyan #5ab9d4 rose #d4788a emerald #5eb894 violet #9580c9
- DM Serif Display headlines never Instrument Serif
- Deep ink #1a140e on warm cream #f5f0e6 high contrast

## Typography {HABIT}-Readable
- Body 18px 1.7 line height generous spacing
- DM Serif Display 800 Playfair Display 700/800 Lora body

## Navigation
- Page-by-page Previous/Next + keyboard arrows NOT scrolling
- Text size controls A-/A/A+ top-right
- 44px min hit targets skip-link page counter

## Interactive
- Deduplicate markers per page first instance only
- Terms open modal not tooltip
- Evidence badges High/Moderate/Traditional required

## Flair ("blow them away")
- Recurring ask: the deliverable must *demonstrate* capability, not just state it. Prefer an interactive proof moment (a parameter-driven responder the user types into) over decorative motion — "we can do the impossible" is answered with something that responds to *their* input.
- Honesty is non-negotiable even under "make it impressive": never fabricate stats/credentials on a client-facing site. Real numbers the client supplies, or honest capability language — never invented counters. See `marketing-site-delivery` → "Flair = interactive proof, not decoration; honesty is non-negotiable" for the full rule.

## Sleek / Futuristic tone ("sleek", "futuristic", "technological")
- **"Sleek" is a WEIGHT/REGISTER signal, not a family-shopping exercise.** This user rejected a 4-attempt loop (Geist Mono → Manrope 700 → Space Grotesk 500) where each was "a thinner font in a different family." The fix that landed was **dropping to weight 500**, not a new family. Sleek/futuristic = **weight 500–600 geometric sans with light tracking** — NOT bold, NOT mono, NOT heavy.
- **Space Grotesk 500** is the canonical futuristic-tech face (DeFi/crypto/Google-AI register) and reads "technological/futuristic while easily legible." **Manrope at 700 was explicitly rejected as "thick."** Don't reach for a heavy weight when asked for sleek.
- For a tech/digital division vs an industrial one, keep a **tone split**: sleek geometric/mono for digital, blocky/condensed (Rostex) for the physical/industrial side. The wordmark + CTA buttons carry the same sleek face for consistency.
- Verify small-instance legibility: at weight 500 on a nav-scale button over dark, a targeted 600 on just that instance keeps it sleek while readable.

## Responsive & Containers (hard preferences)
- **Mobile is a HARD gate, not optional** — "looks horrible on mobile is unacceptable in the modern day." Every surface ships a real mobile tier (≤900/≤720/≤560 breakpoints, stacked layouts, 44px+ touch targets, `overflow-x:clip` guard, fluid hero padding/type via clamp). Mobile Lighthouse ≥80 is a binding check; a desktop-only page review is not sufficient to close.
- **Containers span the full page width and breathe** — fixed-pixel width cages (six caps like 1120/840/680px) read as "clunky." Use `width:min(100% - 48px, 1200px)` sections; never a fixed-px container width.
- **No flat/empty backgrounds and no stark flat rectangles.** Every surface needs depth (layered gradients, grid texture at visible opacity, a balancing composition element) and every container must read as a container (rounded, bordered, shadowed — see `references/corporate-site-design.md` "Deploy & QA-gate discipline" for the computed-style + contrast-floor rules that keep this from shipping flat).

## Placeholders
- Styled containers with generation prompts not empty boxes

## Recipe Conventions
- Follow IDEA.md finalized list
- No Ashwagandha no Chyawanprash
- Bukhari 5688 not 5687
- Honest health claims no overclaiming
- Sidr lote-tree not Chinese jujube

## Workflow
- No execute_code for large files write_file or heredoc
- Verify browser rendering
- Fix foundation before features
- Iterative refinement expected
- **Design review must include a competitor/industry benchmark checkpoint before any MVP is declared complete.** This user explicitly demanded the process after catching a clear oversight (two {CLIENT} sources rendered stacked at once — "almost every Quran app already does single-source + switcher"). Before calling a design done, compare the surface against how major industry players solve the same problem (Quran.com, Ayat, RecitID, etc.) and catch the obvious standard patterns yourself rather than shipping them for the user to flag.
- **Scoped deltas over broad refreshes on tuned work.** A user rejection was traced to exactly this: applying an external design-rules skill (`ui-ux-pro-max`) as a broad refresh across a heavily-tuned surface regressed prior work ("no visible improvements, many past improvements undone") and got reverted. On mature/approved surfaces, make *targeted single-decision* changes (one palette pick, one contrast/pattern lookup) — never re-run a whole rules layer over finished polish. External design skills are decision lookups, not rebuild drivers. When a new design-skill rule is proposed, prove it on one real task and record what it changed before trusting it.

## Theme / Ink dark-mode handling
- Distinguish an **adaptive ink** that follows the active theme's foreground (`var(--ink)`, i.e. "Black / White" — dark ink on light themes, white on dark) from **fixed inks** (a literal hex like sepia-brown/green/navy/maroon).
- On **dark themes** (midnight/royal), every fixed ink must be **remapped to a light parchment tone** (match the sepia theme's background) so Arabic text stays readable against the dark surface. Only the adaptive ink stays exempt (it already inverts via `var(--ink)`).
- Implement in `applyTheme()`: `if (DARK_THEMES.includes(theme) && ink !== adaptive) ink = PARCHMENT`. Keep the dark-theme set and parchment constant as named config so the rule reads once, and keep non-dark themes unaffected (fixed inks show their real color on light backgrounds).
- Label the adaptive ink honestly in the UI — "Black / White" not "Classic black", because it turns white on dark themes.

## Honest data-coverage / "built vs pending" states
- When an app is progressively populated (only some juz/surahs/pages built), the user wants **free navigation everywhere + an honest empty state** — never trap them, never fake coverage with empty files. Show real metadata (name, revelation type, page range, ayah count) plus one clear line "not built yet" and a **progress strip** ("1 of 30 juz built · 3%") so the limitation reads as a roadmap, not a bug.
- **Derive "built" from the actual loaded data files, not from navigation metadata.** A surah's `pages` array often lists its full extent even when only part is populated (surah 2 → pages 2–49 in nav, but only 2–21 in the file). Count a unit (juz/page) as built only if every page it spans is present in a genuinely-loaded content file (`BUILT_PAGES` populated from `ayah.page` as files load). The naive "does the surah have content" or "does nav say pages present" check silently overcounts and claims coverage that isn't there — the exact honesty failure this user rejects.

## Approved interaction patterns (positive reinforcement — replicate)
User explicitly praised these and asked they be committed as "what success looks like". They are the strongest evidence of the user's taste:
- **Progressive disclosure over everything-at-once.** Expandable/collapsible sections are the "best of both worlds" between simplicity/focus and depth. Default collapsed; user expands for more. Never dump all layers simultaneously.
- **Single content source at a time, with a user-selectable switcher.** Showing two {CLIENT} sources stacked at once was flagged as a clear design oversight. One source rendered, a dropdown/sidebar to switch. (Most Quran apps already do this.)
- **Bidirectional linked highlighting.** Hovering/touching a word in one language highlights its counterpart in the paired translation — a subtle "follow along" affordance, not a separate tool.
- **Clever visualizations that make abstract concepts tangible.** The winning example: slotting root letters into a morphological template "like algebra" (everyone has learned algebra). Turning a rule into a visible, rearrangeable structure reads as "so clever and intuitive."
- **Tidy explanation systems bundled with the feature.** A one-line explanation of what a form means, right where the user meets it, beats a separate reference.
- **Accuracy over coverage.** "Better to teach a little of a right thing than a lot of the wrong." Depth/features defer to correctness of the small piece actually shown.

## Info-density: boundary signposts + color-coding legends
- **Don't repeat constant context on every item — surface it only when it changes.** The user rejected per-ayah "p.1 · j.1" on every verse as noise. Replace with a **boundary signpost** that renders only at the point a value actually changes mid-scroll ("Page 21", "Juz 2 · Page 22") — a rare, meaningful marker instead of per-item repetition. The first item still shows the starting context; after that, only real deltas. This reads as intentional signposting, not clutter. (Verified logic: show if `!prev || prev.page !== cur.page || prev.juz !== cur.juz`.)
- **Any color-coding of text needs a toggleable legend.** When enabling visual markers (tajweed rules, syntax coloring), provide a small legend mapping each color → meaning, with **live swatches resolved from the current theme** (getComputedStyle on a probe element). Gate it with the same toggle that enables the coloring, so it's opt-in and never permanent chrome.

## Pitfall — prototype data loading (`file://`)
A standalone HTML prototype that loads a local JSON via `fetch()` fails over the `file://` protocol (CORS) even when the file sits in the same directory — the browser blocks local reads. Two fixes: embed the data as a JS `const` in the `<script>` (right for data under ~100KB), or serve via `python3 -m http.server` (right for larger datasets that must be fetched). When the user reports "text shows but data didn't load," this is the first suspect. For data that grows large, keep the fetch-over-HTTP approach and ship on a host (GitHub Pages) that serves it, not as a local double-click file.

## Scope
Two deliverable classes for this user: (a) document-style HTML (see sections below) and (b) corporate/marketing websites — see `references/corporate-site-design.md` for the approved register there (threeui glass/bento/gradient borders, division-gateway pattern, dynamic layered backgrounds, logo asset discipline).

## Pitfalls
- No generic SaaS
- No unverified browser claims
- No execute_code over 8KB
- No sidr/jujube conflation
- No overclaimed evidence
