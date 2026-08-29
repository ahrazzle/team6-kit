<!-- GENERICIZED: 2×{AMOUNT}, 2×{CLIENT}, 5×{RELATIONSHIP} | source: skills/creative/web-design-component-catalog/SKILL.md -->
---
name: web-design-component-catalog
description: "Use when picking a component/icon source for a real surface."
version: 1.0.0
author: {RELATIONSHIP} <{RELATIONSHIP}@{CLIENT}>
license: MIT
metadata:
  hermes:
    tags: [design, components, icons, licensing, catalog]
    related_skills: [popular-web-designs, ui-ux-pro-max, user-design-aesthetic]
---

# Web Design Component Catalog

## When to Use

Use when a real surface needs a **component library, icon set, or design reference** pulled from an external source — to select which of the vetted sources fits, and to confirm the license boundary *before* copying. Do **not** use for full-page templates (reach for `popular-web-designs`) or single-decision rule lookups (`ui-ux-pro-max`).

Curated inventory of component/icon sources vetted {CLIENT} ({RELATIONSHIP}) from link batches in the Control room (batch 1: 19 sources; batch 2: 15 links → 4 overlapped, 11 new). Two buckets:

- **COPY** — code we may ship; license is everything. Verify the LICENSE-file path before copying (provenance check below).
- **REFERENCE** — learn-from only (technique/checklist/inspiration); no copy rights needed, license is not a shipping constraint.

**Companions:** `popular-web-designs` (real-system templates) for full-page work; `ui-ux-pro-max` (single-decision rule lookups) for palette/contrast/pattern rules.

## COPY bucket — component libraries / design systems (8)

| Source | URL | License | LICENSE-file path | Ship boundary |
|---|---|---|---|---|
| threeui | https://github.com/MengTo/threeui | MIT | `github.com/MengTo/threeui/blob/master/LICENSE` | free Community components; Pro/Beta paid |
| Beautiful UI | https://beautifului.dev | MIT | `beautifului.dev/license` (© 2026 Shane Levine) | — |
| beui | https://beui.dev | MIT | `github.com/starc007/ui-components/blob/master/LICENSE` | free tier open; Pro {AMOUNT}/yr paid |
| RareUI | https://rareui.com | MIT | `rareui.com/terms` (registry components "published under the MIT License") | — |
| Transitions | https://transitions.dev | Custom permissive (NOT MIT) | `transitions.dev/terms.html` | use in products, modify freely; **NO redistribution of collection as kit**; tooling is MIT |
| shadcn/ui | https://ui.shadcn.com | MIT | `github.com/shadcn-ui/ui/blob/main/LICENSE.md` | — |
| reui.io | https://reui.io/components | MIT | `github.com/keenthemes/reui/blob/main/LICENSE.md` | free tier open; Pro license paid |
| coss/ui | https://coss.com/ui | MIXED | repo `github.com/cosscom/coss` (AGPL-3.0 at root) — `/ui/` dir is MIT | **ONLY pull from `/ui/` — repo default is AGPLv3** |

## COPY bucket — icon libraries (8)

| Source | URL | License | LICENSE-file path | Ship boundary |
|---|---|---|---|---|
| IconSax | https://iconsax.io | Custom free | `docs.iconsax.io/license-and-terms/license` | 6k free icons, unlimited personal/commercial, no attribution (except digital items); **no loose redistribution**; premium 40k+ paid |
| Morphicons | https://morphicons.com | MIT | `github.com/guillermolg00/morphicons/blob/master/LICENSE` | morphing lib over Lucide (ISC) |
| Isocons | https://isocons.app | CC BY 4.0 (unconfirmed) | **flag — primary page wouldn't extract**; corroborated by 3+ independent refs | **attribution mandatory**; commercial allowed; confirm official page before attribution-sensitive ship |
| Iconly | https://iconly.pro | Custom | `iconly.pro/terms` | all licenses personal+commercial; free tier limited icons, **premium share forbidden** |
| Lucide | https://lucide.dev | ISC | `github.com/lucide-icons/lucide/blob/master/LICENSE` | Feather-derived subset MIT |
| Hugeicons | https://hugeicons.com | MIT (free pack) | `@hugeicons/core-free-icons` (official npm/pub.dev, published by hugeicons.com) | free pack MIT; Pro licensed separately |
| Phosphor | https://phosphoricons.com | MIT | `github.com/phosphor-icons/core/blob/master/LICENSE` | — |
| Nucleo | https://nucleoapp.com | Commercial | `nucleoapp.com/license` | **paid license caps at 250 icons/project** (100 max in templates/themes/OSS, copyright notice required, no resale); free open-source subset no-cost |

## REFERENCE bucket — learn-from only (3)

| Source | URL | What it is |
|---|---|---|
| Design System Checklist | https://designsystemchecklist.com | Open-source a11y/DS audit checklist (MIT, but used as reference) |
| emilkowalski — "You don't need animations" | https://emilkowal.ski/ui/you-dont-need-animations | Prose/opinion on restraint in animation — read, don't copy |
| ui-skills | https://ui-skills.com | **Skill catalog, NOT components** — already contains ui-ux-pro-max (ours, scoped). Do not absorb as a component source (false positive). |

## COPY bucket — batch 2: tokens / motion / backgrounds (4)

| Source | URL | License | LICENSE-file path | Ship boundary |
|---|---|---|---|---|
| Open Props | https://open-props.style | MIT | `github.com/argyleink/open-props` LICENSE | ready-made tokens (colors, shadows, radii, spacing, easing) |
| Motion Primitives | https://motion-primitives.com | MIT | `github.com/ibelick/motion-primitives` LICENSE.md | reusable motion components for React |
| BG Ibelick | https://bg.ibelick.com | MIT | `github.com/ibelick/background-snippets` | copy-paste backgrounds for Tailwind/CSS |
| Animated Buttons | https://animatedbuttons.colorion.co | MIT (README-stated, no file) | README: "LICENSE — MIT" but **no LICENSE file backs it** — accept as author grant, weaker provenance | 99 CSS-only button interactions |

## REFERENCE bucket — learn-from only (batch 2: 6)

| Source | URL | What it is |
|---|---|---|
| VibePrompts | https://vibeprompts.dev | 256 prompts for UI sections (dashboards, pricing, auth, onboarding, hero) — prompt text, no copy rights needed |
| Utopia | https://utopia.fyi | Fluid typography/spacing **generator** — output is ours |
| Icon Creator | https://iconcreator.dev | Browser-based custom icon designer (tool) |
| Interfaces (Rauno) | https://interfaces.rauno.me | Checklist of tiny interaction details that make interfaces feel finished |
| Component Gallery | https://component.gallery | {AMOUNT}+ examples from 95 design systems — **index only**; anything copied from a gallery must be checked against the source design system's own license |
| DesignSystems.one | https://designsystems.one | 88 production design systems w/ tokens, stacks, downloadable design.md — index; gallery-copy rule applies |
| Kinetics | https://kinetics.colorion.co | **UNLICENSED** (pin-pass: `ckissi/kinetics` has no LICENSE file → all rights reserved; batch-2 "MIT family" inference did not survive the actual repo). Learn from its patterns; **do not copy** until the author licenses it |

## How to use (scoped invocation)

Use for **targeted, single-decision selections** on a real surface — never a broad skill-driven refresh of mature, tuned work (that regresses; the ui-ux-pro-max v6 lesson). Flow:

1. Pick the source that fits the *specific* need (a dashboard palette, an icon set, a landing pattern).
2. **Check the license boundary** before copying — coss/ui `/ui/` only, Isocons attribution, Transitions no-redistribution, IconSax/Iconly no loose redistribution, Nucleo free subset.
3. Pull only what the surface needs; verify in **served output** (not a local read).
4. Prefer established design systems already in `popular-web-designs` when the task is full-page; reach here for components/icons.

## Provenance gate

Each LICENSE-file path above is the resolvable dispute point. **{RELATIONSHIP}'s verify pass**: before the catalog counts as live, verify each listed path's license *text* matches the flagged status — a header can drift from a README claim. Catalog is only as trustworthy as the file behind each path.

**Trademark caveat:** brand logos inside icon sets are governed by **trademark**, not the set's license — an MIT icon set does not license the X or Meta glyph for branding. Treat any brand-mark use as a separate clearance, even from a copy-clean set.

**Canonical cross-link:** the license/provenance record's **canonical home is the vet file** — `control/wrk/mct6/OPERATIONS/web-design-sources.md` ({RELATIONSHIP}'s verify-pass table, 7 pinned / 1 open). This catalog is the **operational mirror** carrying a pointer. Isocons' flag (CC BY 4.0, unconfirmed — corroborated by 3+ refs) is resolved in **both**; never diverge one without the other.

## Proof gate (mandatory, per Control room ruling)

The catalog is not "live" until absorbed components are exercised on **one real surface and verified in served output** — the same gate ui-ux-pro-max failed on. A component-level proof, not a palette lookup.
