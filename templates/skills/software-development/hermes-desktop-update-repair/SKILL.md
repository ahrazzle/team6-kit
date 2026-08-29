<!-- GENERICIZED: 2×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/hermes-desktop-update-repair/SKILL.md -->
---
name: hermes-desktop-update-repair
description: "Use when Hermes desktop update/boot fails (90000ms/check)."
version: 1.0.0
author: {RELATIONSHIP}
license: internal
metadata:
  hermes:
    tags: [hermes, desktop, update, boot, troubleshooting]
    related_skills: [inspecting-hermes-desktop-dom, hermes-desktop-plugin-storage]
---

# Hermes Desktop Update & Boot Repair

## When to Use

Trigger on any of: "Couldn't check for updates" / "Check your connection and try again"; "Timed out connecting to Hermes backend (90000ms)"; the desktop app failing to start or looping after a `hermes update`; a kill-restart boot loop in `~/.hermes/logs/desktop.log`. Also use when a `hermes update` succeeded (exit 0) but the app will not boot afterwards.

Diagnose and fix Hermes desktop app update/boot failures on this machine. Triggered by: "Couldn't check for updates", "Timed out connecting to Hermes backend (90000ms)", app failing to start after `hermes update`, or a kill-restart boot loop.

## Where the truth lives

- `~/.hermes/logs/desktop-update-handoff.log` — the update handoff run (spawn posix.sh, `hermes update` output, exit code, fleet restart). Read the LAST hand-off block for the most recent update.
- `~/.hermes/logs/desktop.log` — desktop main-process boot transcript. The success sequence is authoritative: `HERMES_BACKEND_READY port=N` → "Waiting for Hermes backend to become ready" → "Hermes backend is ready."
- `~/.hermes/desktop-build-stamp.json` — `contentHash` + `builtAt` of the desktop binary. Compare `builtAt` against the handoff log completion timestamp; a mismatch means a separate rebuild happened.
- `~/.hermes/logs/update_receipts/` — update receipts.
- The shipped main-process code: `apps/desktop/release/mac-arm64/Hermes.app/Contents/Resources/app.asar.unpacked/dist/electron-main.mjs`. Grep it to confirm what code actually shipped vs. what the source says (source and binary can disagree after rebuilds).

## The READY sentinel contract (critical)

The desktop spawns the backend (`venv/bin/python -m hermes_cli.main serve --host 127.0.0.1 --port 0`) and waits for this sentinel on the child's **STDOUT only** (electron/backend-ready.ts `waitForDashboardPort` attaches to `child.stdout`):

    HERMES_BACKEND_READY port=N

If the sentinel lands anywhere else, boot waits 90s then kills the backend: "Timed out waiting for Hermes backend port announcement (90000ms)", and the renderer loops `refreshProfiles failed after 3 attempt(s)` every ~30s.

Diagnostic rule: if desktop.log shows the backend announced READY but boot still timed out, the sentinel went to the wrong stream — reproduce the spawn yourself and check where the line lands. The 90000ms is NOT the backend being slow; a healthy boot announces in ~2s.

## Known regression: tui_gateway.server import redirects the sentinel

`hermes_cli/web_server.py` `start_server()` imports `from tui_gateway.server import install_exit_flush_signal_handlers` (added in a 2026-08 update). Importing that module executes a module-level `sys.stdout = sys.stderr` (tui_gateway/server.py:401) — correct for the gateway (stdout = JSON-RPC), catastrophic for `serve`: every later print, including the READY sentinel, goes to stderr.

Fix (applied + verified): save/restore `sys.stdout` around that import. OS-level fd 1 is never redirected, only Python's `sys.stdout` object — that is why restoring the object works without touching fds.

Patch: `~/.hermes/patches/desktop-ready-stdout-fix.patch`. **Re-apply after every `hermes update`** (updates hard-reset the repo):

    cd ~/.hermes/hermes-agent && git apply ~/.hermes/patches/desktop-ready-stdout-fix.patch

Verify with scripts/check-ready-sentinel.sh. Full root-cause chain and proof in references/{CLIENT}-stdout-regression.md.

## Known issue: git low-speed abort on this machine's degraded GitHub path

- Symptom: "Couldn't check for updates" + "Check your connection and try again" while the machine clearly has internet.
- Mechanism: the app runs `git ls-remote` / `git fetch` against github.com; this machine's path to GitHub is slow-dribble (HTTP/2 stalls, HTTP/1.1 under 1KB/s for 10-20s).
- Cause: `http.lowSpeedTime=15` / `fetch.timeout=30` in `~/.gitconfig` abort too early.
- Fix (applied): `http.lowSpeedTime=90`, `fetch.timeout=120`. Backup at `~/.gitconfig.pre-lowspeed-fix`.
- Diagnostic: run the EXACT command the app runs (`git ls-remote --exit-code --heads https://github.com/NousResearch/hermes-agent.git main` in the checkout) with `GIT_TRACE=1`. "Operation too slow" → raise the patience window; don't blame connectivity. Note github.com also throws intermittent HTTP 429s; anonymous ls-remote can work while authenticated is throttled.

## Diagnostic workflow (use in order)

1. Read the log tail to determine the failing stage: update handoff, boot, or renderer loop.
2. If boot: did the backend announce READY? Yes-but-timeout → stream contract broken (sentinel on wrong stream). No → backend crashed or never bound; run it by hand.
3. Reproduce the spawn exactly as the desktop does, stdout/stderr SEPARATED:
   `venv/bin/python -m hermes_cli.main serve --host 127.0.0.1 --port 0 > /tmp/out 2> /tmp/err`
   Then check which file holds the READY line, and `lsof -p <pid>` to see what fd1/fd2 point to — this distinguishes an OS-level dup2 from a Python-level `sys.stdout` rebind.
4. If a regression is suspected, diff code between the last-known-good commit and HEAD for the suspect files, and grep for module-level side effects: `sys.stdout =` / `os.dup2(2,1)`.
5. Confirm what actually shipped: grep `app.asar.unpacked/dist/electron-main.mjs` for the same patterns.
6. Apply the fix, verify with the same reproduction BEFORE touching the live app, then relaunch desktop and watch desktop.log for "Hermes backend is ready."
7. Save any new patch to `~/.hermes/patches/` and record the re-apply step in memory.

## Pitfalls

- A `hermes update` exit code 0 does NOT mean the desktop will boot. Separate stages, separate failures.
- Don't trust the app's message ("Check your connection") — verify with the actual command it runs.
- Multiple update failures can stack and be unrelated (the git lowSpeed issue and the post-update boot loop happened in the same session).
- `hermes update` deletes `apps/desktop/src/plugins/accent/plugin.js` and `kanban/plugin.js` from the working tree — `git restore` them after updating (cosmetic, source tree only).
- If the renderer loops "refreshProfiles failed after 3 attempt(s)" every 30s, the backend is dead from the main process's perspective — fix the main-process side, not the renderer.
- Don't chase a "concurrent startHermes race" theory when logs show READY announced then a clean 90s timeout — the discriminator is: race = "Ignoring stale Hermes backend exit / superseded by a newer connection attempt" during an active boot; sentinel regression = READY then clean SIGTERM at exactly 90s with no competing spawn.

## Support files

- scripts/check-ready-sentinel.sh — spawns `hermes serve` the way the desktop does; reports which stream carries HERMES_BACKEND_READY and whether the patch is applied.
- references/{CLIENT}-stdout-regression.md — full root-cause chain, patch diff, proof steps, and recommended upstream fix.
