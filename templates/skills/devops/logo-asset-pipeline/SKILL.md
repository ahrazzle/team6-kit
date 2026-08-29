<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/devops/logo-asset-pipeline/SKILL.md -->
---
name: logo-asset-pipeline
description: Use when preparing client logos for web builds. Transparency extraction, variants, provenance.
version: 1.0.0
author: {RELATIONSHIP}
---

# Logo Asset Pipeline

## When to Use

- A client supplies logo files (.png/.jpeg/.svg) for a website or app build.
- Logos render with checkerboard boxes, opaque rectangles, or lost detail on dark backgrounds.
- Multiple same-named logo files exist in different directories and agents disagree about which is real.

How to turn client-supplied logo files into clean, deployable web assets without destroying artwork. Born from a real build where every supplied file had baked-in checkerboard and two same-named files existed in different directories.

## Source triage (do this first)

1. **Inventory every candidate copy** of the logo across the workspace (`logos/`, `assets/`, `mats/`, uploads). Hash each (`shasum -a 256`) and record mode+size via PIL. Same-named files in different dirs are common; hash comparison settles which is real in one command.
2. **Check alpha truth, not filenames**: `Image.open(f)` → `.mode` and corner pixel alpha. `RGBA` with alpha=0 corners = true transparency. `RGB`, or RGBA with alpha=255 everywhere, means baked background.
3. **Declare one source-of-truth directory** (typically `assets/`) and quarantine the rest as reference-only. Derivatives go to the authority dir; originals are never mutated in place.

## Checkerboard removal (when no clean-alpha source exists)

Baked checkerboards come in light (white + ~gray-220 squares) and dark variants — inspect corner pixels to learn the palette before choosing thresholds.

**Flood-fill from borders beats global color-keying.** Global "make light pixels transparent" punches holes through light-gray artwork (metal, glass, machinery). Instead:

1. Classify background pixels: high lightness, low saturation (`max(r,g,b) > T` and `max-min < S`). Start strict (light checker only), flood-fill from all border pixels, then progressively lower T until enclosed checker regions (inside arrow outlines, frame gaps) get reached by the fill.
2. Soften edges: pixels within distance ~2 of the filled region get partial alpha (e.g. `255 - near*22`).
3. Crop to content bbox, save, **verify visually at zoom** (vision model: "any holes in artwork? any checker remnants?") after each threshold step.
4. Iterate thresholds downward stepwise (~190 → 150 → 120 → 100 → 80 → 60) — each pass reaches deeper enclosed regions; re-verify artwork integrity after every pass.

If anti-aliased fringing survives at production scale, the correct fix is asking the user for a clean export from their design tool — a reconstructed logo shipped to production is a liability.

## Favicon / small-size derivatives

Fine detail (nodes, traces, gears) dies below ~48px. Derive a simplified silhouette: key shapes only, on a rounded-rect tile in the brand's dark tone.

## Vectorization (PNG → SVG)

Once a clean transparent PNG exists and the mark is shown large (hero marks, brand headers), vectorize with `vtracer` (color-aware tracing, spline mode). Real SVG is resolution-independent and usually smaller than the PNG source.

- Verify the output is a TRUE vector, not a wrapper: grep the file for `<path` (expect hundreds/thousands) and confirm ZERO raster embeds (`'<image'` absent). A PNG embedded inside an SVG is not a conversion.
- Add a `viewBox`; transparency is preserved (no background rect).
- Swap `<img>` refs PNG → SVG with a `?v=N` bump.
- **Pitfall:** when the new mark is square but the old PNG was not, DELETE stale `width`/`height` attributes left over from the old PNG (e.g. `width="1109" height="1131"`) — they distort the vector.
- **Pitfall:** a `<source type="image/webp">` must point at an actual `.webp` URL — pointing it at a `.png` is a decode mismatch that breaks browsers.
- Keep PNG/WebP fallbacks in the bundle for older clients; SVG renders in all modern browsers.

## Canonical artwork replacement (the swap)

When the client says "wrong logo," first compare ARTWORK, not dimensions — a larger file may be a genuinely different design (e.g. a new single-faceted grey/orange mark replacing a blue double-AA monogram), not a size upgrade. The old mark still shipping in the build is an outdated brand asset.

1. Swap: copy new canonical marks (`logos/` → `assets/` in BOTH the versioned build and the repo root that deploys).
2. Archive superseded marks into `vers/archive-brand-<v>/` — never delete superseded brand assets mid-project.
3. Retire derived contrast variants that were surgery on the OLD artwork (`assets/derived/*-light`, `assets/opt/*`) — they must not ship anywhere. Grep ALL pages for stale refs (`grep -rn "assets/opt\|assets/derived"`), fix every one including `<picture>` source blocks and `og:image` — a retired derivative can remain load-bearing in one page (e.g. the gateway) after the rest are clean.
4. Retune CSS palette to the new mark's true colors — the mark's accent (e.g. safety orange `#F97316`) is the palette anchor; old-theme colors baked into gradients/chips/buttons get replaced.
5. Add `?v=N` cache-bust to every image ref so browsers stop serving the old artwork from cache — unversioned asset names are why users saw stale logos for multiple rounds after clean files deployed.
6. **Regenerate the favicon from the CURRENT mark** — the browser-tab favicon is a first-class brand surface and users notice when it still shows the retired mark ("favicon is using old outdated logo"). Derive a new simplified silhouette (key shapes only, on a rounded-rect tile in the brand's dark tone) from the new canonical artwork, replacing the old `favicon.svg`. Also re-point `og:image` where it referenced a retired derivative.
7. Regenerate MANIFEST.sha256, push, and verify the SERVED bytes match the new hashes (curl the live asset, not just the local file).

## Verification before sign-off

- Corner alphas = 0, mode RGBA.
- Visual check: mark intact (no holes punched through light areas), zero checker remnants anywhere including enclosed cutouts.
- Manifest (`MANIFEST.sha256`) regenerated after any asset change; report hashes + dimensions back.
- An unchanged hash after a rebuild from identical input is reproducibility, not staleness — check mtime before flagging.

## Pitfalls

- JPEG cannot store alpha; a .jpeg logo always has its transparency indicator baked in. PNG may still be RGB — verify per-file.
- macOS Preview exports can composite the transparency checkerboard INTO the pixels when users copy/share files — a user-supplied "screenshot" of a logo may be opaque even though the original was transparent.
- Two agents reporting different facts about "the logo" usually means two files with similar names — hash first, argue never.
- Deep-navy strokes vanish on dark hero/card backgrounds — derive a brightness-lifted variant into `assets/derived/` with its own manifest entry rather than hacking CSS halos.
- Cache-bust image refs (`?v=N`) on any brand swap — browsers cache unversioned asset URLs and keep showing the rejected artwork even after clean files deploy.
- A "larger logo" from the client can be a different design — compare artwork (motifs, colors), not just mode/size/hash.
- MANIFEST.sha256 entries must be root-relative to the build directory (so `shasum -c` passes when run from inside the build), not relative to the workspace parent — a manifest that only resolves from the wrong directory is a fragile artifact.
- Retired derived assets (e.g. `*-light.png`) must be DELETED from the shipped bundle, not merely unlinked in HTML — dead files still deploy and confuse later audits (confirm removal with a 404 on the live URL).
- After any logo swap, grep the SERVED HTML (curl), not just local files, for stale refs to retired derivatives — one load-bearing page (e.g. the gateway) can still point at the old mark after every other page is clean.
