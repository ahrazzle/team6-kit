<!-- GENERICIZED: 1×{AMOUNT}, 6×{CLIENT} | source: skills/autonomous-ai-agents/agent-pager/SKILL.md -->
---
name: agent-pager
description: Page user when a Hermes agent session pauses or completes.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [agent, pager, notification, session-monitoring, pause-detection, phone-alert]
prerequisites:
  commands: []
  env_vars: []
---

# Agent Pager

Use when the user asks to be notified/paged/alerted on their phone or another channel when a long-running Hermes agent session completes, pauses, hits a review gate, or produces a deliverable.

This skill covers the FULL pattern: which channel to use, how to find the right session, how to detect a pause, what to put in the alert, and how to poll without wasting tokens. It is NOT about sending a single message — for that, use the relevant channel skill directly (e.g. `imessage` for iMessage/SMS).

## Channel Selection

Always check which channels are actually available before picking one. The user's `.env` (at `~/.hermes/profiles/<profile>/.env`) holds the configured keys — most are commented out by default.

**Priority order (highest to lowest):**

1. **Discord DM** — if a Discord bot token is configured and the user's Discord user ID is known. Discord mobile push is reliable and requires no OS permissions. Use the `discord` toolset.

2. **WhatsApp** — if `WHATSAPP_ENABLED=true` and `WHATSAPP_ALLOWED_USERS` includes the phone number in `.env`. Run `hermes whatsapp` to pair the account first. WhatsApp mobile push is reliable.

3. **Email (Gmail SMTP)** — if `EMAIL_ADDRESS` and `EMAIL_PASSWORD` (a Gmail App Password, not the account password) are set in `.env`. Use any SMTP-capable tool or the `email` / `himalaya` skill.

4. **iMessage/SMS via imsg** — if `imsg` is installed AND Full Disk Access is granted to the terminal (or parent launcher). For SMS fallback: `imsg send --to "<phone>" --text "<msg>" --service sms`. Specifying `--service sms` forces the green-bubble path and avoids iMessage delivery failures.

5. **Push webhook service** — if the user has a self-hosted or SaaS push service (Gotify, Boxcar, Pushover, ntfy.sh, etc.). Preferred when OS-level messaging bridges are blocked or unavailable. **Research existing push services the user already uses before building a custom one.**

6. **Telegram** — if `TELEGRAM_BOT_TOKEN` is configured. Reliable mobile push.

**Do NOT default to iMessage.** The user explicitly prefers other channels when available. Always check `.env` for configured keys and ask the user which channel they want before sending.

## Finding the Session to Watch

Sessions live in `~/.hermes/profiles/<profile>/state.db` (SQLite). To find the session doing work on a specific project:

```sql
SELECT id, source, started_at, ended_at, end_reason,
       message_count, cwd, git_branch, git_repo_root
FROM sessions
WHERE cwd LIKE '%<project_path_fragment>%'
ORDER BY started_at DESC;
```

The session with `ended_at IS NULL` (or the most recent `started_at` without an `ended_at`) is the active one. Note its `id` — you need it for polling.

Also read `~/.hermes/profiles/<profile>/logs/agent.log` for recent activity on that session ID. The log line format is:

```
{CLIENT} 15:39:{AMOUNT} INFO [SESSION_ID] agent.conversation_loop: API call #N: ...
```

## Pause / Completion Detection

A Hermes agent session can stop or pause in several ways. Poll for these signals:

| Signal | Where to check | What it means |
|---|---|---|
| `ended_at` becomes non-NULL | `state.db` → `sessions` table | Agent session ended (completed, stopped, or crashed). Read `end_reason` for why. |
| `message_count` stops increasing | `state.db` → `sessions` table, poll interval 60–120s | Agent is idle, waiting for user input (review gate, sign-off pause, clarification). |
| `agent.log` shows a conversation_loop stall or guardrail trigger | `logs/agent.log`, grep for the session ID | Agent hit a tool_loop_guardrails limit, ran out of turns, or is waiting on a long-running tool. |
| The agent wrote a review package / deliverable file | Watch the project directory for new `.md`, `.pdf`, `.html`, build outputs | A pause point where the user needs to review something. |
| `agent.log` shows `run_agent: Agent loop finished` or similar | `logs/agent.log` | Session fully complete. |

**Polling intervals:**

- **Active work** (message_count increasing, API calls happening): poll every 60–120 seconds.
- **Idle / waiting for input** (message_count flat for 2+ consecutive polls): poll every 2–5 minutes — the agent is waiting for the user, not doing work.
- **After a pause is detected**: send the alert immediately; do not wait for another poll cycle.

**Do NOT poll faster than 30 seconds.** Fast polling wastes tokens and can race with the agent's own turn.

## Alert Message Content

An alert message should tell the user what happened, where to go, and what to do next. Include:

1. **Session ID** — so the user can look it up in the session list or state.db.
2. **One-line summary** of what was produced or what paused (e.g. "Design review package written", "P1 pause reached", "Session ended — exited with reason X").
3. **Where to find the deliverable** — absolute path to the file or directory.
4. **What the user needs to do** — e.g. "come check on it", "review and sign off", "continue the process".
5. **How to resume** — if the session is paused waiting for input, tell the user how to continue (e.g. reply in the Hermes desktop app, or resume the session).

Keep it short. The user is on their phone.

## Existing Agent Notification Infrastructure

Before building a custom polling + alert pipeline, check whether the user already has push notification infrastructure they can reuse:

- **ntfy.sh** — free, self-hostable push notification service. Simple HTTP PUT to publish, mobile/web subscribers. Good fit for agent alerts.
- **Gotify** — self-hosted push notification server. REST API to send, mobile apps to receive.
- **Pushover** — SaaS, paid, reliable iOS/Android push.
- **Boxcar** — iOS push, both self-hosted and hosted options.
- **Slack / Discord / Telegram webhooks** — if the user already uses one of these, a simple HTTP POST can deliver the alert without any Hermes channel configuration.

**Research what the user already has before recommending a new service.**

## Pitfalls

- **Do not assume any channel is available.** The `.env` has everything commented out by default. Check before using.
- **Do not poll the database faster than 30s.** It wastes tokens and can race with the agent.
- **Do not send an alert for every idle poll.** Only alert when there is an actual pause, completion, or deliverable — not when the agent is just thinking.
- **Do not hardcode the phone number or channel.** Ask the user which channel they want, and read the number from their instructions (not from somewhere in the filesystem unless they told you to).
- **If imsg is blocked by Full Disk Access, do not recommend granting it as the only path.** Offer Discord/WhatsApp/email/push webhook as alternatives. The user may not want to grant Full Disk Access to terminal.
- **A session can appear "active" in state.db while actually stalled** (e.g. waiting on a long-running tool with no progress). Check `agent.log` for stall patterns, not just `ended_at`.
- **Session IDs in state.db do not always map to a readable display name.** Use the session ID directly when referencing it to the user.

## Example: Full Pager Setup

**User:** "Ping me on my phone when the {CLIENT} project work is paused and ready for me to check on it."

**Steps:**

1. **Identify the session:**
   ```sql
   SELECT id, started_at, ended_at, message_count, cwd
   FROM sessions
   WHERE cwd LIKE '%{CLIENT}%'
   ORDER BY started_at DESC;
   ```
   Pick the active one (no `ended_at`, or most recent).

2. **Confirm the channel with the user.** Read `.env` to see what is configured. Ask: "Discord, WhatsApp, email, iMessage, or push webhook? Here's what I found configured..."

3. **Choose polling targets:**
   - `state.db` → `sessions` table: `ended_at` and `message_count` for the session ID.
   - Project directory: watch for new deliverable files (the user can tell you what "done" looks like — a file, a build, a review package).

4. **Set up the poller.** A cron job (via `cronjob` tool) running every 60–120s is the durable option — it outlives the current session. A background terminal process works for short-lived alerts but dies if the parent exits.

5. **Send the alert** via the chosen channel with session ID, summary, deliverable path, and what to do next.

## What This Session Learned

From the user's actual setup (August 2026):

- **Phone number:** +1 (416) 807-1609 (Toronto area code — Canadian SMS/iMessage).
- **Preferred channels (in order):** Discord, WhatsApp, email. iMessage is a fallback only.
- **imsg was not initially installed** — installed via `brew install steipete/tap/imsg`. The brew download returned HTTP 503 transiently; retrying succeeded.
- **imsg failed with `authorization denied (code: 23)`** — Full Disk Access is required for the terminal (or parent launcher) to read the Messages database at `~/Library/Messages/chat.db`. This is the most common imsg failure on macOS.
- **osascript AppleScript for Messages.app also failed** — `Invalid key form (-10002)` when trying to send via AppleScript. The Messages bridge requires the account identifier in a specific format; `buddy "<phone>" of account "appleid"` did not work with a raw phone number.
- **No Discord bot token, WhatsApp config, or email credentials were set in `.env`** — all commented out. The user will need to configure at least one channel before alerts can be sent.
- **Two Hermes gateway processes were running** (one for the desktop app, one CLI). Both had `state.db` with session data.
- **The active {CLIENT} session** was `20260812_152443_7b6d75` (cwd: `~/{CLIENT}{CLIENT} Saudi/workspace`, 18 messages, no `ended_at`). Its `agent.log` showed it was in the middle of writing a design review package.

## References

- Channel-specific skills: `imessage` (iMessage/SMS), `himalaya` (email via CLI), `discord` toolset (Discord DM).
- Hermes session store: `~/.hermes/profiles/<profile>/state.db` and `logs/agent.log`.
- Hermes cron: use the `cronjob` tool for durable polling that outlives the current session.
- Session and channel discovery for this profile: `references/channel-discovery.md`.
