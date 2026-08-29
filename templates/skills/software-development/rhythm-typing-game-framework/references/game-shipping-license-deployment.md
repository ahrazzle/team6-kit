<!-- GENERICIZED: 3×{CLIENT} | source: skills/software-development/rhythm-typing-game-framework/references/game-shipping-license-deployment.md -->
# Shipping a rhythm game publicly — license boundaries & deployment guardrails

How to take a {CLIENT} plugin from dev workspace to a public repo + GitHub
Pages demo without leaking unlicensable assets or shipping stale bytes. Verified
on the {CLIENT} project ({CLIENT}).

## A public repo is a SECOND distribution surface with different leak rules

Two surfaces, two different guard mechanisms:

- **The git repo (history) is the permanent leak risk.** Git history is
  effectively eternal — a file that once enters it can be resurrected by a
  force-push or a shallow-clone edge. A manifest flag (`ship: false`) does NOT
  guard git; git doesn't read manifests.
- **GH Pages (served bundle) only ships what the build emits.** The
  manifest's `ship: false` already guards the build path; the load-bearing gate
  there is verifying the LIVE-SERVED bytes match the canonical bundle (see
  related skill `deploy-artifact-verification`).

**Rule: `.gitignore`-FIRST.** Before the very first push, gitignore any
excluded/`ship:false`/dev-test assets (`*.ogg` under `test-audio/`, etc.) so they
NEVER enter history. A file that never enters history can't be resurrected. This
must be a committed `.gitignore` entry, NOT a manual pre-push sweep — a manual
audit is one forgetful push from being skipped. Run a pre-push excluded-file
sweep + ledger-vs-disk diff as the gate too.

## License boundary visible to any visitor (not just build scripts)

GitHub shows license badges per-repo from root. Make the island's license
architecture self-evident on a public surface:

```
LICENSE                      # MIT at root — covers engine/plugin code
assets/ccbysa/LICENSE        # CC-BY-SA-4.0 alongside the ledger
assets/ccbysa/ATTRIBUTION.md # per-file manifest: source repo + author + license + SHA-1
assets/ccbysa/audio/         # CC0 rows with named authors per track
```

The manifest/ledger is the only provenance point the ENGINE reads AND the
ship-time proof that a visitor can check. It also makes off-by-N count disputes
verifiable (the manifest is what catches a missed file, not eyeballing a listing).

## CC0 sourcing from OpenGameArt — verify on the ITEM page

When hunting CC0 audio/art as a dev/test or shipping lane:
- **The license field on the individual item page is evidence; collection pages
  are not.** A "42 tracks, CC0" pack page proves nothing — open each item.
- Prefer OGG-native files (matches the track-manifest pipeline directly; `.mp3`
  needs conversion to OGG).
- Record the re-license chain in the attribution line, e.g.
  `troutsneeze / Nooskewl Games — OGG CC0 (re-licensed from Monster RPG 2)` or
  `Ted Kerr (Wolfgang_) — CC0, OGA item #43483`.
- OGA/asset pages rarely state musical tempo — measure it after pull (see audio
  determinism in the umbrella) before assigning a design BPM.

## The focused-demo rule (user acceptance gate)

A public demo the user will test should be a FOCUSED playable slice — one
monster, one enemy, one vetted track — that exercises the real feel targets
end-to-end, not a full asset/taxonomy sheet. The acceptance gate the user cares
about is "does this feel good to type" (the cadence), not completeness. A
gesture-gated "Start Battle" screen both fixes browser autoplay policy AND is the
first feel moment, so give it the game's real visual language.
