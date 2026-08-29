<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/software-development/hermes-desktop-plugin-storage/SKILL.md -->
---
name: hermes-desktop-plugin-storage
description: "Repair Hermes desktop plugin state in localStorage leveldb."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [desktop, electron, leveldb, localStorage, plugin-storage, data-repair, hermes-bots]
    related_skills: [inspecting-hermes-desktop-dom, systematic-debugging]
---

# Hermes desktop plugin storage (Electron localStorage leveldb)

## What this covers

The Hermes desktop app (Electron) persists **plugin state** — anything a desktop
plugin writes via `ctx.storage.set()` — into Chromium's localStorage, which is a
**LevelDB** on disk. This is where the `hermes-bots` plugin keeps group chats
(`group-chats`), bot metadata (`bot-meta`, `bot-meta-v2`), and the selected
roster row; other desktop plugins keep their data under the same scheme.

When a plugin pane fails to render, or its stored data is corrupt, the fix is a
surgical edit of this LevelDB. This skill is the technique for doing that safely
(read on a copy while the app runs; write only with the app fully quit).

**Distinct from `inspecting-hermes-desktop-dom`** (live DOM over CDP — UI
verification). This is on-disk persistent data — recovery, repair, forensics.

## When to use

- A desktop plugin pane fails to render ("failed to render", a specific throw)
  and the cause is stored state.
- You need to recover or inspect `ctx.storage` data that exists only in the
  desktop app (NOT mirrored to a gateway/profile — check `~/.hermes/profile.yaml`
  `ui_meta` first; group rooms ARE mirrored there under `hermes-bots-groups`,
  but only the recent-messages projection, not full member descriptors).
- You must back up, patch, or clear a specific plugin storage key.

## On-disk layout

| OS | LevelDB directory |
|---|---|
| macOS | `~/Library/Application Support/Hermes/Local Storage/leveldb/` |
| Linux | `~/.config/Hermes/Local Storage/leveldb/` |
| Windows | `%LOCALAPPDATA%\Hermes\Local Storage\leveldb\` |

Key facts that cost real effort to discover:

- **Keys are namespaced.** Plugin storage keys look like
  `_file://\u0000\u0001hermes.plugin.<pluginId>.<storageKey>`. Example:
  `_file://\u0000\u0001hermes.plugin.hermes-bots.group-chats`.
- **Values are UTF-16LE with a leading prefix byte.** The raw bytes are
  `00` (prefix) then the UTF-16LE string; the JSON begins at **byte offset 1**.
  `buf.toString('utf16le', 1)` then `slice(s.indexOf('{'))` parses cleanly.
  Plain `JSON.parse` and `toString('utf8')` both fail confusingly.
- **The running app holds a write-lock** (`LEVEL_LOCKED` on the `LOCK` file).
  You CANNOT open the live store for writing while Hermes is running — and if
  you could, the app's next sync would clobber your change.

## Safe read/write procedure

1. **Check for a mirrored copy first** — `~/.hermes/profile.yaml` `ui_meta`
   (e.g. `hermes-bots-groups`) often holds a recent projection. If it has the
   full data you need, no LevelDB surgery is required. NOTE: the mirror holds
   recent messages + display name only, NOT full member descriptors — so a
   member-level corruption fix still needs the LevelDB.

2. **Install `classic-level`** in a scratch dir (fast, no native build):
   ```bash
   mkdir -p /tmp/ldb_fix && cd /tmp/ldb_fix && npm init -y >/dev/null
   npm install classic-level --no-audit --no-fund
   ```
   (`plyvel` needs C++ leveldb and fails to build; python-snappy absent —
   don't waste time on them.)

3. **While the app runs, read on a COPY** (avoids the lock):
   ```bash
   cp -R "<leveldb dir>" /tmp/ldb_fix/copy
   ```
   Open the copy with `new ClassicLevel(dir, { keyEncoding:'utf8',
   valueEncoding:'buffer' })`. Read values with `valueEncoding:'buffer'` so you
   control the UTF-16LE decode yourself.

4. **Back up the real store before ANY write**:
   ```bash
   cp -R "<leveldb dir>" "<leveldb dir>-BACKUP-$(date +%Y%m%d-%H%M%S)"
   ```

5. **Dry-run and verify on a scratch copy first**, then re-read the written
   copy to confirm round-trip integrity BEFORE touching the live dir.

6. **To write the live store: the app must be FULLY quit** (⌘Q, dock icon gone).
   Confirm no `Hermes.app`/`Hermes Helper`/`hermes serve` processes remain, or
   the lock blocks you / the app clobbers you. Tell the user to quit, wait for
   confirmation, patch, then they reopen.

## Pitfalls

- **Never theorize root cause from config before reading the data.** This
  session's first hypothesis (rooms bound to a remote gateway, per
  `connection.json`) was wrong — the rooms were local, and the real fault was
  corrupt member descriptors in the LevelDB. Read the actual stored value and
  let it drive the diagnosis.
- **Never rewrite a whole storage value by hand.** Load it, patch only the
  broken fields in-memory, re-encode, and verify. Preserve everything else
  (logs, sessions, watermarks, healthy fields).
- **Do not touch numbered/backup copies** — only the active store is
  authoritative.
- **Confirm every change round-trips** (write → re-read → parse) before
  declaring success. A corrupt write is worse than no write.

## Support files

- `references/hermes-bots-group-chat-repair.md` — the "Bot X has no connection
  owner" render error: mechanism, exact broken-descriptor signature, and the
  patch pattern.
- `scripts/dump-plugin-storage.js` — reusable probe to list keys and dump a
  decoded value from a LevelDB copy (use with `node ... <dir> <key>`).
