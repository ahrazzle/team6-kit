<!-- GENERICIZED: 2×{CLIENT} | source: skills/software-development/licensed-asset-reuse/SKILL.md -->
---
name: licensed-asset-reuse
description: Use when reusing third-party licensed assets in a project.
---

# Licensed Asset Reuse (the asset-island pattern)

Bring third-party assets into a project without licensing leaks. Proven on
OpMon-Data / Tuxemon assets into the {CLIENT} {CLIENT} plugin (see
`references/opmon-tuxemon-audit-2026-08.md`).

## License audit (BEFORE any pull)
- Read the LICENSE file directly. Check Credits.md / ATTRIBUTIONS.md. Check file metadata tags (ffprobe for audio). Check git history for authorship (squashed commits = attribution lost).
- Rule: "inspect at pull, exclude on doubt." CC-BY-SA's attribution obligation is unfillable when the author is unknown → the file CANNOT legally ship, no matter how good it looks.
- GPL code cannot bundle into an MIT project. CC-BY-SA ASSETS can ship beside MIT code IF they stay a distinct asset layer with their own LICENSE + per-file attribution ledger. CC-BY-NC assets are commercially dead. Mixed-license repos (CC0/CC-BY/CC-BY-SA/NC mosaic) need a per-file ledger, and every NC item is a trap.

## The island (structural, not conventional)
- Third-party assets live in their own directory (e.g. `assets/ccbysa/`) with LICENSE + ATTRIBUTION.md: per-file rows of source + author + license + SHA-1.
- The ENGINE never reads paths: it consumes a machine manifest (`poses.json`, `tracks.json`) that is the ONLY provenance point. Original/paid content must reference zero island entries — enforce with a build assertion, not a convention.
- Manifest entries carry `ship: true/false` + vet flags. Excluded files are `ship: false` AND gitignored.
- Generate manifests with a script that walks the layer and writes the ledger — a scripted ledger can't rot or get hand-edited inconsistently.

## gitignore-FIRST ordering (before any public push)
- Excluded files must NEVER enter git history — a file that never exists in history can't be resurrected by force-push or shallow-clone edge. Commit `.gitignore` with excluded paths BEFORE the first push.
- Public repo license layout: root `LICENSE` (MIT for your code), `assets/<layer>/LICENSE` (e.g. CC-BY-SA-4.0), ATTRIBUTION.md visible to any visitor.
- Run a pre-push audit: excluded-file sweep + ledger-vs-disk diff.

## Quality gates on free art
- Sprites: geometry audit (alpha bbox / density / area% / aspect / scaleHint) decides whether pixel art reads at battle scale — sparse sprites become dots. `scripts/geometry-audit.py`.
- Audio: exact duration via ffmpeg PCM sample counts (container can lie ±; sample counts don't); BPM via librosa onset autocorrelation (mind chiptune half-time alias). Music carries the most IP-remix risk — vet provenance hardest.

## CC0 stopgap hunting (when borrowed music fails vetting)
- OpenGameArt: verify on the ITEM page (not collection pages); single-file loopable `.ogg` tracks exist; record attribution line as it appears in the Copyright/Attribution Notice.
- Established packs (Monster RPG 2 OST) are uploader-re-licensed CC0 — record "CC0 per OGA page, re-licensed from <source>" in the ledger.
