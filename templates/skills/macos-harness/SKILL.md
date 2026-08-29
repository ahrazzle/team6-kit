<!-- GENERICIZED: 1×{CLIENT}, 3×{RELATIONSHIP} | source: skills/macos-harness/SKILL.md -->
---
name: macos-harness
description: Use when a task needs driving the user's real logged-in Chrome (CDP) or composing multi-step logic in one persistent Python process — the escape hatch when cua-driver hits unverifiable/suspected_noop.
---

# macos-harness / browser-harness

Installed {CLIENT} via `uv tool install --python 3.12` (macos-harness 0.1.x + browser-harness). One-week-old experimental repos — treat upgrades as reviewed changes. **Upgrade protocol (do not skip): re-audit both repos against the new commit → update THIS canonical copy ({RELATIONSHIP}) first → redistribute to all eight profiles with fresh checksums → {RELATIONSHIP} verifies independently.** Audit-before-distribute: a bump is when new code enters eight trust boundaries at once.

## Split-of-duties convention (Team6, {RELATIONSHIP}-approved)
- cua-driver (`computer_use`) owns `see`/`click`/`type`/`key` — default for all desktop interaction.
- macos-harness ONLY for: (a) real-Chrome CDP via browser-harness `browser.*`, (b) persistent-process Python composition when one-action-per-call can't do it, (c) bottom rung of the verify→escalate ladder after cua-driver returns `unverifiable`/`suspected_noop`.

## Hard gates
- **Never call `browser.connect()` without an explicit user go** — it auto-approves AX prompts, may LAUNCH Chrome if closed, and opens chrome://inspect tabs. Controlled tab's title gets a 🐴 prefix.
- Never trigger cloud profile-sync (api.browser-use.com) — copies local cookies to their cloud. Auth-gated only.
- Telemetry is OFF — enforcement layer is the 0600 config files (`~/.config/browser-harness/telemetry.json` and `~/Library/Application Support/macos-harness/telemetry.json`, both `"disabled": true`, verified on a non-interactive shell). The `BH_TELEMETRY=0` / `MACOS_HARNESS_TELEMETRY=0` vars in ~/.zshrc are belt-and-suspenders only: zshrc doesn't load for non-interactive agent/cron shells. browser-harness ignores DO_NOT_TRACK and its cli_event telemetry ships full task scripts (~20KB) bypassing redaction — never re-enable.
- No kill-switch env var exists for AX auto-approve; the gate is procedural only.

## Six primitives
`mac.see(app)`, `mac.key(combo, app=...)`, `mac.type(text, app=...)`, `mac.click(x, y, app=...)`, `mac.ax.at(x, y, app=...)`, `mac.script('AppleScript')`; plus `browser.*` (CDP), `Path`, `subprocess` in the same process. Background capture — never raises apps or moves the real cursor.

```bash
macos-harness <<'PY'
frame = mac.see("Spotify")
mac.key("cmd+k", app="Spotify")
PY
```

## State
Permissions verified: accessibility ✓ screen_recording ✓ post_events ✓. Verified live: `apps` listing + background capture of Finder. Restart discipline: harness process is stateful — restart before trusting stale screen state.
