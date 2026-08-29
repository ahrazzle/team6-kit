<!-- GENERICIZED: 4×{CLIENT}, 2×{RELATIONSHIP} | source: skills/autonomous-ai-agents/hermes-desktop-app-internals/SKILL.md -->
---
name: hermes-desktop-app-internals
description: "Patch packaged Hermes desktop app for hardcoded behavior."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Team6
license: MIT
platforms: [macos, linux, windows]
---

# Hermes Desktop App Internals

Locate, inspect, and patch the **packaged** Hermes desktop app (Electron) when a
behavior is hardcoded with no settings surface. The classic case: Bot Mode
group-chat caps (rounds / messages / continuations) are constants in the bundled
`hermes-bots` plugin and cannot be raised from the UI — only by patching the
bundle. Re-signing on macOS keeps the app launchable; patching the repo source
keeps the change through rebuilds.

## When to Use

- User asks to change desktop app behavior that has no settings toggle (Bot Mode group-chat caps, sync budgets, member limits, any bundled-plugin constant)
- "Where does the desktop app store X / why isn't my change taking effect"
- You need to re-apply a bundle patch after a desktop app update wiped it

Don't use for: profile config (`config.yaml` — use `hermes config set`), skins, DOM inspection (see `inspecting-hermes-desktop-dom`).

## Bundle Layout (the thing that trips everyone)

The app runs from a packaged asar, NOT the repo source:

- `~/Library/Application Support/…` is user data; the APP binary is at
  `<repo>/apps/desktop/release/mac-arm64/Hermes.app` (confirm with `ps aux | grep Hermes` → `--app-path=…/Resources/app.asar`).
- `Contents/Resources/app.asar` holds the JS/HTML. **Large assets are NOT in the asar**: they live in `Contents/Resources/app.asar.unpacked/` and the asar entry is a stub marked `unpacked: true` (no content, `integrity.hash` only).
- Consequence: `asar extract` gives you stubs for unpacked files. Patch the **real file in `app.asar.unpacked/`**; do NOT repack the whole asar inline — the naive repack inflates 8.4MB → ~50MB and breaks native-module unpacking (`node-pty`, prebuilds).

## Procedure

1. **Find the app and its bundle.** `ps aux | grep -i hermes` shows the `--app-path`. Resources: `Contents/Resources/app.asar` + sibling `app.asar.unpacked/`.
2. **Locate the constant in source first.** `search_files(pattern='<CONST>', path='<repo>/apps/desktop/src/plugins/…')` — the bundled plugins live in `apps/desktop/src/plugins/hermes-bots/plugin.js`. If the source has a named constant (`GROUP_CHAT_MAX_ROUNDS`), the minified bundle still inlines it as a literal.
3. **Find the real file.** `node_modules/.bin/asar list <app.asar> | grep <bundle>.js`, then check `app.asar.unpacked/dist/assets/<bundle>.js` exists. Confirm the asar entry is a stub: `asar list --is-pack <app.asar> | grep <file>` prints `unpack : <path>`.
4. **Back up** both the asar and the real file (`cp … /tmp/name-$(date +%Y%m%d-%H%M%S)`).
5. **Patch the real file in place.** Prefer `scripts/patch-groupchat-caps.py` (re-runnable: context-anchored regexes per cap site, idempotent, `node --check` after, exit code 3 = "shape changed, unverified"). Or a python replace asserting exactly one occurrence. **The minifier (rolldown) now INLINES the caps as literals at context-anchored sites — the `var <a>=3,<b>=10,<c>=2,<d>=6;` declaration no longer exists** (see Pitfalls). Match each cap by its surrounding structural code, never by variable name, filename, or a value-sequence declaration.
6. **Never repack the whole asar.** The unpacked dir holds the real content.
7. **Re-sign on macOS** (app is adhoc-signed): `codesign --force --deep --sign - <Hermes.app>`, then `codesign --verify --deep --strict <Hermes.app>`.
8. **Restart the app.** The running renderer holds the old bundle in memory — the patch is live only after relaunch.
9. **Also patch the repo source** (`apps/desktop/src/plugins/…`) with a dated comment. NOTE: this is a seed only — see "Why source edits don't survive" below. The only self-healing mechanism on this machine is the launchd watchdog.

## Why source edits don't survive updates (verified in update_cmd.py)

Do NOT tell yourself a committed source change will ride through updates. The updater is designed to keep the source pristine:

- Desktop flow runs `hermes update --yes --gateway --keep-stash` → uncommitted edits are stashed and NEVER re-applied (they stay parked in git stash).
- On `main` with diverged history → `reset --hard origin/<branch>` (kills local commits).
- On a custom branch → auto-switch to the target branch (commits kept on the branch, but that branch is not what gets built).
- No update-related hook event exists in the hooks system (`hermes hooks list`).

=> The durable fix is a **launchd watchdog** that detects the clobber and re-patches automatically:

- `~/.hermes/scripts/team6-caps-watchdog.sh` — thin launcher that calls `~/.hermes/scripts/patch-groupchat-caps.py` and classifies EVERY run by its exit code: `0` = override present (patched or already applied) → clear alert, re-sign only if a patch actually landed; `3` = no cap pattern matched → build shape changed, caps unverified → write `~/.hermes/logs/team6-caps-watchdog.ALERT`, log an ALERT line, fire a macOS notification, exit 1; any other rc = real error → alert. Target values are now 9999/9999/9999 (effectively-unlimited), members stays 6.
- `~/Library/LaunchAgents/com.team6.caps-watchdog.plist` — RunAtLoad + hourly StartInterval; it calls the same script path, so a script fix goes live on the next run without reload.
- Log: `~/.hermes/logs/team6-caps-watchdog.log`. Proven {CLIENT}: simulated clobber → watchdog re-patched + re-signed in ~1s; three-state harness verified (upstream → patch, patched → no-op, unrelated pattern → ALERT + exit 1).

**Never let a watchdog treat "no match" as success.** A quiet watchdog on a shape change is a silently-reverted cap that pages nobody — the exact failure the watchdog was built to prevent. State 3 (unknown shape) must ALERT, not no-op.

Match by VALUE pattern + STRUCTURAL anchor, never by variable name or filename — variables and bundle filenames change per build (observed `Zve` → `Fve`; `index-vTWQdFhH.js` → `index-g1BOm50G.js` → `index-Dh-pjnId.js`), and a build can drop the declaration form entirely (see the inlining pitfall).

## Pitfalls

- **Minified variable names are build artifacts.** `Zve=3,gb=10,_b=2,vb=6` means rounds/messages/continuations/members in ONE build only. Find constants by regexing the declaration pattern near known string literals (e.g. the `capped` status string), never by hardcoding names across versions.
- **The bundler can INLINE the constants, killing the declaration regex.** {CLIENT} the rolldown minifier stopped emitting a single `var A=3,B=10,C=2,D=6;` and instead inlined each cap as a literal at its use site — the old watchdog's `=3,=10,=2,=6` regex matched nothing and it ALERTed every hour for a day while the app actually ran with restrictive caps. Fix: match each cap site by its surrounding STRUCTURAL code (e.g. `s=\`settled\`;try{for(let <v>=0;<v><3;<v>++){for(let` for the rounds loop, `!i()||<v>>=10){i()?s=\`capped\`` for the message cap, `if(<v>+=1,r.length&&<v><=2){` for continuations). The surrounding code is stable across minifier renames; the literal is not. Keep a shape-changed canary (rc=3) so a future build that re-inlines differently pages you instead of silently reverting.
- **Value changed to 9999 in {CLIENT}.** Earlier builds patched 999/999/999; the inlined-shape patch raises to 9999/9999/9999 for genuinely-removed caps. Both are "effectively unlimited" — rooms still settle on a full silent round.
- **The fourth constant (6) is the members cap — do NOT raise it.** The `=6` value gates max bots per room: the new-group picker ("Pick 2–6 bots", `members.slice(0,N)`, `selected.length >= N` validation). It is NOT a round/message cap. Raising 3/10/2 to 999 while leaving the fourth at 6 is correct and intentional; "members stays 6" is by design, not an oversight. Verify what an unknown constant gates before touching it (grep its usages in the bundle) — the first audit of the v0.17.0 build flagged the fourth constant as a possible hidden cap until usage review showed it was the member picker.
- **Repacking the whole asar breaks native modules.** Patch in place; the asar needs no rebuild when the file lives in `app.asar.unpacked/`.
- **Restart required.** A patched bundle that isn't relaunched shows zero effect; the user's running session keeps the old behavior.
- **Giant-file greps can trip the command hardline.** Use `python3 -c` regex over the file content instead of `grep -o` with huge context windows on multi-MB minified JS.
- **App updates wipe bundle patches — and the source commit dies too.** Updater uses `--keep-stash` (desktop) or `reset --hard` (main divergence) or branch auto-switch; none preserve your edit. The launchd watchdog (see "Why source edits don't survive") is the reliable re-apply path. After any `hermes update`, let the watchdog fire (or run the script once) and re-verify with the value-pattern grep below — do NOT trust that an old filename or old variable name still matches.
- **A watchdog that no-ops on "no pattern found" is a silent failure.** Any self-healing patcher must classify three states — upstream found / already patched / unknown shape — and ALERT on the third (canary file + notification + non-zero exit). Value-pattern drift (minifier reorder, added constant, changed default) is exactly when you need paging, not quiet.

## Verification

Match by value pattern, not names (both minified variable names and bundle filenames change per build):

```bash
# The override is live iff the patcher reports rc=0 (patched or already applied).
# rc=3 = no cap pattern matched => build shape changed, caps UNVERIFIED.
python3 ~/.hermes/scripts/patch-groupchat-caps.py; echo "rc=$?"   # expect rc=0
node --check "<real-bundle>" && echo SYNTAX OK     # bundle still parses
bash ~/.hermes/scripts/team6-caps-watchdog.sh && tail -3 ~/.hermes/logs/team6-caps-watchdog.log
codesign --verify --deep --strict "<Hermes.app>" && echo SIGNATURE OK
# spot-check the 9999 values landed in the group driver (structural anchor):
grep -oE '!i\(\)\|\|[a-z]>=[0-9]+\)\{i\(\)\?s=\x60capped\x60' "<real-bundle>"  # shows the capped guard
```

Then relaunch the app and confirm behavior in a live room (e.g. a 4+ message exchange that previously stopped at the cap).

## References

- `references/bot-mode-group-chat-caps.md` — the full cap-patch recipe: exact constants, minified-name evolution across builds, and the {CLIENT} build-3 INLINED-shape update (why the declaration regex died + the 6 structural-anchor sites).
- `scripts/patch-groupchat-caps.py` — the current context-anchored patcher (6 inlined cap sites, idempotent, rc=0 live / rc=3 shape-changed canary / rc=1 error). Port to `~/.hermes/scripts/` and run directly or via the watchdog.
- `scripts/team6-caps-watchdog.sh` — the self-healing watchdog (launcher that calls the patcher; classifies by exit code: 0=override live, 3=shape changed → ALERT + exit 1, else error → alert). Port to `~/.hermes/scripts/` + `~/Library/LaunchAgents/com.team6.caps-watchdog.plist` (RunAtLoad + hourly) on any machine that needs the caps override.
