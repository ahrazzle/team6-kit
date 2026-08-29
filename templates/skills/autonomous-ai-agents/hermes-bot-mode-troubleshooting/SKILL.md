<!-- GENERICIZED: 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/autonomous-ai-agents/hermes-bot-mode-troubleshooting/SKILL.md -->
---
name: hermes-bot-mode-troubleshooting
description: "Use when Hermes Desktop group chats fail to open or crash."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [hermes, bots, group-chat, troubleshooting, desktop, multi-agent]
    related_skills: [hermes-agent]
---

# Hermes Bot-Mode Troubleshooting

Use when a Hermes Desktop **group chat** or **Bot roster** fails to open, throws
an error-boundary crash, or shows a "Bot X has no connection owner" style
error. Applies to the `hermes-bots` desktop plugin (the Bots tab), which is
bundled and on by default. Also useful when a Bot's DM won't open or a room
member is "missing".

## Key mental model

A Bot is just a Hermes profile (`~/.hermes/profiles/<name>/`). When a group
room crashes, **do not assume a profile is missing or dead** — check
`hermes profile list` first. The overwhelmingly common cause of a group-chat
render crash is **corrupt persisted room metadata in the desktop plugin**, not
a broken bot.

The single most common crash signature is:

> `"plugin-workspace:hermes-bots:group:<name>" failed to render`
> `Bot <name> has no connection owner`

This fires from `apps/desktop/src/plugins/hermes-bots/plugin.js` (search the
source for `has no connection owner`). It throws only when a room member is
flagged `sourceScoped`/`remoteSource` **but has an empty `connectionId`** in its
route. I.e. the room record says "this bot lives on another connection" but
doesn't say which one, so the plugin can't resolve a gateway owner and the
whole room fails to render. When all bots are actually local, that descriptor
is stale/corrupt persisted state, not reality.

## Diagnose (in order)

1. **Confirm profiles exist.** `hermes profile list` — every bot named in the
   failing room should be present. If a profile truly is gone, that's a
   different (restore) problem.
2. **Confirm the gateway is healthy.** `hermes status` — the `default` gateway
   should be running. Bot Mode is just a UI over profiles routed through it.
3. **Read the renderer error.** `tail -50 ~/.hermes/logs/desktop.log` and grep
   for `error-boundary:contrib:plugin-workspace:hermes-bots:group`. This names
   the exact room(s) and the exact bot that fails. One bad member breaks every
   room that contains it (a single corrupt bot can take down both `command` and
   `{CLIENT}`).
4. **Find the throwing code.** In the local source
   (`~/.hermes/hermes-agent/apps/desktop/src/plugins/hermes-bots/plugin.js`)
   grep for the error string to confirm *why* it throws and which flag is
   involved.

## Fix — primary path (no data loss)

Re-adding the bad member rewrites its descriptor with a valid local route:

1. Bots tab → **right-click the offending bot** → **Manage groups**.
2. **Uncheck** the affected rooms → **Apply**. (Purges the corrupt descriptor
   from each room.)
3. **Right-click the bot again** → **Manage groups** → **check** the rooms back →
   **Apply**.

Why this works: Manage groups on the *bot* row does not render the broken room,
so it doesn't crash — and re-adding writes both the desktop's cached room
record and the backend profile metadata with a correct route.

## Fix — fallback (only if the dialog can't open)

If Manage groups itself is blocked, the room data lives in the Electron
localStorage of the desktop app:

- Path: `~/Library/Application Support/Hermes/Local Storage/leveldb/`
- Key: `group-chats` (rooms + member descriptors), also `bot-meta-v2` (per-bot
  display meta)
- Safe sequence: quit Hermes Desktop → clear the `group-chats` key → relaunch →
  re-add members. More invasive (all memberships re-add), so prefer the UI path.
- See `references/leveldb-storage.md` for how to read Chrome/Electron
  localStorage values when you need to inspect the actual persisted JSON.

## Pitfalls

- **The `.log` file inside `Local Storage/leveldb/` can contain your own agent
  session transcript**, not just DB data. If you grep it and see your own tool
  reasoning or chat text, that's a red herring — look at the `.ldb` SST files
  instead.
- **A bot's model pin is in its profile config, not the room.** A typo like
  `stealth/ox-alpha` (stray slash) vs `stealth-ox-alpha` in a bot's model pin is
  a separate issue from a group-chat crash — fix it via Edit Profile → Model,
  but don't confuse the two.
- **One corrupt member breaks every room it's in.** Fix the member once and all
  affected rooms come back; don't repair room-by-room.
- **Changes to profile metadata/rooms sync to backend profile metadata**, so a
  bad descriptor can reappear if another connected desktop re-seeds it. If the
  crash returns after the fix, check Settings → Connections for a stale second
  gateway/desktop.

## Related

- `hermes-agent` (bundled) is the authoritative reference for Hermes
  configuration. This skill covers bot-mode/plugin troubleshooting that the
  bundled docs' troubleshooting reference may not spell out.
