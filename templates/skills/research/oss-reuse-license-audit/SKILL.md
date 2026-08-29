<!-- GENERICIZED: 6×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/oss-reuse-license-audit/SKILL.md -->
---
name: oss-reuse-license-audit
description: "Use when vetting OSS code/assets for reuse in a build."
version: 1.0.0
author: {RELATIONSHIP}
license: internal
metadata:
  hermes:
    tags: [license, oss, reuse, assets, provenance, legal]
    related_skills: [product-discovery, tool-adoption-audit, source-evaluation]
---

# OSS Reuse & License Audit

## When to Use

- The user or a teammate proposes "use this open-source project as a launchpad / fork / asset source."
- Any discovery/reuse report that must carry license terms and the downstream obligation, not just a link.
- Before ANY third-party file (code, {CLIENT}, audio, font) enters a build that will be distributed — especially a public repo or a venture with paid packs.

Core premise: **"publicly available" is not one thing.** MIT/Apache = safe to build on; GPL = forces its license onto what you ship; CC BY-SA = share-alike derivatives; CC BY-NC = kills commercial use. A component that is free to read and illegal to ship is worse than none, because the cost surfaces late. The GitHub API license field and README badges are hints, never evidence — verify from primary sources.

## Methodology

### 1. License from the license FILE, not the API field
- GitHub API `license.spdx_id` can be `NOASSERTION` for custom license files. OpMon's code license lived in `LICENCE.md` (British spelling, a plaintext GPL-3.0 declaration with a note pointing at a separate art license), invisible to the API's `LICENSE` detection.
- Read the actual file: `curl -s https://raw.githubusercontent.com/<org>/<repo>/<branch>/LICENSE` (try LICENSE.md, LICENCE.md, COPYING). A repo can be GPL in code but carry assets under a different license in a sibling repo.

### 2. Code vs assets split (check sub-repos and data repos)
- Engines are often GPL while their asset packs are CC — OpMon (GPL-3.0, Godot) + OpMon-Data (CC-BY-SA-4.0, 82MB data repo registered as a submodule). The engine may be unusable while the assets are reusable (or vice versa). Query the data repo's own license file.
- Standalone engines (Godot/Pygame) are rarely drop-in components for a browser TS plugin — "launchpad" framing usually means a rewrite; the reusable part is typically the asset/design layer, not the code.

### 3. Per-file license mosaics (ATTRIBUTIONS.md pattern)
- Tuxemon: code GPL-3.0+, media = mosaic — 104×CC-BY-SA-4.0, 31×CC0, 23×PD, 15×CC-BY-3.0, 12×CC-BY-NC-SA-3.0 (per-file ledger in ATTRIBUTIONS.md). Lessons: (a) BY-NC assets are commercially dead — identify them by attribution line, not file listing; (b) a single artist can be the whole trap set (12 NC items all by "Oniwanbashu") — exclude by artist name at pull time; (c) per-file ledgers make exclusion enforceable, not aspirational.

### 4. Provenance traces — attribution must be FILLABLE
CC-BY-SA requires attributing the actual author. Trace in order:
1. `Credits.md` / credits files (may list zero music/art credits — a finding in itself).
2. Container metadata: `ffprobe -show_entries format_tags` (Ogg/Vorbis often carry no tags at all).
3. Git history per path: `GET /repos/<org>/<repo>/commits?path=<path>` — if the history is squashed to a restructure commit, the author's identity did not survive.
If the author is unrecoverable, the attribution obligation is **unfillable** → the asset FAILS vetting under any "exclude on doubt" rule, regardless of how good it looks/sounds. This is a structural kill, not a paperwork nit. Also flag remix risk: track names matching known franchises (wildbattle, route14) with unverifiable authors = undetectable IP contamination.

### 5. Asset inventory: count FILES, not directory entries
A directory listing of 171 entries ≠ 171 assets. Exclude engine artifacts (`.import`, `.meta`, `.md`), then count real content files and distinct IDs:
- OpMon-Data `Sprites/opmons`: 171 entries → 85 PNGs → 45 IDs via `N-M.png` pattern — but a naive `(\d+)-(\d+)` regex missed 12 shiny variants (`s10-0`, `ss12-1`) → 51 distinct monsters, 39 with 2-frame poses. Enumerate the full listing; never extrapolate from a sample.
- Animation dirs can hide real motion: `Sprites/opmons/anims/` had 25 PNGs (8 monsters × 2-frame wink cycles + one 8-frame sequence) that a top-level `Animations/` scan missed. Walk ALL subdirectories before declaring "poses, not animation."
- State corrected counts with the exact enumeration method in the report.

### 6. The island pattern (asset-layer separation that survives shipping)
- Reusable CC assets CAN ship beside MIT code if they stay a distinct layer: own directory (`assets/ccbysa/`), own `LICENSE`, per-file attribution ledger (SHA-1 per file, source, author, license), and a machine-generated manifest as the ONLY provenance point the engine reads.
- **Gitignore-FIRST ordering:** a public repo is a permanent distribution surface with eternal history. Excluded files (attribution-unfillable, pending-vet) must be gitignored BEFORE the first push — a file that never enters history can't be resurrected by force-push. `ship: false` flags in the manifest guard the build, but only git exclusion guards the repo.
- Build-side assertion: paid/original content must resolve to ZERO entries from the CC layer — fail the build, not the convention.

### 7. CC0 stopgap hunting (OpenGameArt)
- **Collection pages are NOT evidence; individual item pages carry the license + named author.** Verify each item page: `License(s):` field, `Copyright/Attribution Notice`, author profile.
- Document re-license chains: "CC0 per OGA page, re-licensed from Monster RPG 2 by troutsneeze" is the attribution line; check comments for disputes/sanitization history (a non-original track was already removed from that pack).
- Prefer OGG (matches decode pipelines, no conversion); flag MP3-only items for conversion. BPM is NOT stated on OGA pages — musical tempo must be measured (see script) before a track can drive a beat grid.

### 8. Audio vetting without ears (the "ear pass" substitute)
An agent that cannot listen can still vet audio: (a) provenance per §4, (b) tempo via signal analysis — `scripts/bpm-measure.py` (ffmpeg mono decode + numpy onset-envelope autocorrelation + interval histogram). Compare measured musical tempo against any declared "design BPM": a 43% mismatch (90 vs 129) means the track cannot carry the declared grid. Half-time locking (energy envelope at 60 when the true tempo is 120) is normal — the interval histogram resolves it. Cross-check teammates' BPM claims with an independent method before they lock into a build.

## 9. Network-copyleft & custom licenses (the "QFGPL" trap)

A custom license that *looks* like a standard copyleft can carry a **network-use source-disclosure** clause that the SPDX id or README badge hides. Real case this session:

- **`quran/quran-mcp`** reports as a Quran tool you might "use as a launchpad." Its `LICENSE.md` is **QFGPL-1.0 (Quran Foundation General Public License, v1.0, March 2026)**. TL;DR: "If you modify it and let others use it — including over a network — you must share your source code with those users under [the same license]." That is **AGPL-class network copyleft**, not plain GPL. Reusing its code into any served build triggers a source-disclosure obligation on YOUR deploy.
- The repo's {CLIENT} were also backed by **private** GoodMem + Postgres — no public call surface anyway, so there was nothing to reuse even if licensing allowed it.

Rule: when a license name is unfamiliar (anything not MIT/Apache/BSD/CC/MPL/GPL-with-known-spdx), **read the full text**, specifically hunting for "network", "remote", "over a network", "SaaS", "service". Treat `QFGPL`, `SSPL`, `OSL`, `AGPL` and any "Foundation GPL" as network-copyleft until proven otherwise. Prefer an MIT/Apache alternative even if it means less flashy tooling — our {CLIENT} project's already-trusted `{CLIENT}/{CLIENT}` (MIT) beat the QFGPL MCP server for the exact same job.

## Report shape

- Table per repo/asset class: license (verified file), what's reusable, what's not, verdict (use / use-with-ledger / exclude / reference-only).
- Every verdict carries the downstream obligation (attribution, share-alike, commercial death).
- Distinguish found (primary-source verified) vs inferred vs could-not-verify, with confidence.
- Name the ledger/guardrail requirement (manifest, gitignore, ship:false) before anything is pulled.

## Pitfalls

- Reporting directory entry counts as asset counts (the 171-entry error — .import files inflate listings).
- Trusting the GitHub API license field for custom/nonstandard license files.
- Declaring "no animation exists" from a partial directory walk.
- Treating a re-license declaration as verified provenance without checking the item page and comments.
- For rhythm games: decoupling the note grid from the audio clock (child-pace fix) deletes the audio-determinism machinery — update the product claim ("typing game with rhythm" ≠ "rhythm game") when that coupling is cut, and keep the manifest's note-grid determinism (word + seed → same map) as the replacement.

## References

- `references/{CLIENT}` — full worked case: OpMon/Tuxemon audit, entry-vs-file counting, unfillable-attribution kill, OGA CC0 stopgap finds.
- `scripts/bpm-measure.py` — ffmpeg + numpy BPM detection (onset autocorrelation + interval histogram), no aubio needed.
