# OpenShorts route

## 1. Scope

This route handles **finished short-video production requests only** — where you explicitly ask for a rendered short. Transcript-only, video-summary, and media-research requests are not routed here; they stay on the existing media skills.

## 2. Routing triggers

Route here only when all are true:
- (a) User asked for a finished rendered short
- (b) Source material or approved brief exists
- (c) User confirmed they want an external render step

Otherwise, stay on existing media skills.

## 3. Prerequisites

Before any external step:
- OpenShorts installed separately by the user
- Upstream available at the pinned commit
- User accepts external-tool terms
- Source rights confirmed for any third-party text/audio/clips

## 4. Sequence

1. **Install** — user installs OpenShorts separately and checks its current license and dependency terms before use
2. **Doctor** — verify the install and check the upstream commit pin
3. **Estimate** — get a preview of what will be produced and confirm it matches the brief
4. **Run** — produce the rendered short
5. **Export** — save a local file the user reviews

Each step requires the prior step to complete successfully before moving on. Link to upstream docs for command details; commit pin: `60317c252af9f4576a1cb3cabf7ee8f86760c268`.

## 5. No-auto-posting

Team6-kit never posts, publishes, or schedules on your behalf. The route ends at a local export you review. Any posting is a separate manual user action outside this route.

## 6. Quality and provenance gates

Before delivery:
- Watch or review the export
- Confirm no unresolved or unlicensed assets are included
- Record source of script, voice, music, and clips in the job notes

Upstream contains unresolved sample assets and incomplete audio provenance, so every user must review current asset provenance before delivery.

## 7. Fallback behavior when OpenShorts is unavailable

If OpenShorts is missing, broken, license-unclear, or the request is not a finished-short request: fall back to existing media skills (transcript, summary, research) and tell the user what was produced instead and what would be needed to render later. Never stall, never silently substitute a lower-quality render and call it finished.

## 8. Boundary statement

OpenShorts (jnMetaCode/openshorts, commit 60317c2) is an external local-first short-video pipeline. Team6-kit does not render video by itself. Users must check the current upstream license and dependency terms before installing or using OpenShorts.

This is an evaluated external reference, not a Team6 component; it is not adopted, installed, or approved by Team6-kit.
