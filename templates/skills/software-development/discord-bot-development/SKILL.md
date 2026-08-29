<!-- GENERICIZED: 2×{RELATIONSHIP} | source: skills/software-development/discord-bot-development/SKILL.md -->
---
name: discord-bot-development
description: "Build Discord bots, esp. voice recording/transcription."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [discord, bot, py-cord, voice, transcription, whisper]
    related_skills: [knowledge-drift-monitoring, macos-harness]
---

# Discord Bot Development

> Build Discord bots that work — slash commands, message handling, and the
tricky one: recording/transcribing voice channels. The two non-obvious facts
that save hours: **mainline discord.py has no voice-receive API** (use
py-cord), and **py-cord's API differs from discord.py's** in ways that only
surface at runtime.

## When to Use

- User asks for a Discord bot (meeting recorder, transcriber, notifier, command bot)
- Anything involving voice channels: record a call, capture audio, transcribe
- Slash-command bots with `@bot.slash_command` or interaction handling

**Don't use for:** Teams/Meet/Zoom (that's `teams-meeting-pipeline` territory, and note a Discord bot can only hear audio that is IN Discord); Hermes gateway bot-mode (that's `hermes-agent` / `hermes-bot-mode-troubleshooting`).

## The #1 Gotcha: discord.py vs py-cord

**Mainline `discord.py` has NO voice-receive API.** `VoiceClient.start_recording`,
`discord.sinks`, `AudioSink` — all removed upstream. A bot that "joins the voice
channel and records" is impossible with plain `pip install discord.py`.

**Use py-cord instead** (`pip install "py-cord[voice]"`). It ships the
recording API under the same `discord` import:

- `from discord.sinks import Sink, AudioData` — subclass `Sink`, implement `on_audio_update(self, data: AudioData)` (data.pcm = raw int16 PCM, data.user = speaker)
- `VoiceClient.start_recording(sink, done_callback, *cb_args)`, `stop_recording()`, `is_recording()`
- **Connect with `await channel.connect()` — that's it.** py-cord 2.8's
  `Connectable.connect()` accepts ONLY `timeout`/`reconnect`/`cls`. `self_deaf`
  and `self_receive` are NOT parameters (they were mainline/older-py-cord
  features) — passing either raises `TypeError: Connectable.connect() got an
  unexpected keyword argument 'self_deaf'` at runtime, surfaced as a
  "Could not join: ..." error on `/join`. Recording works by default via the
  VoiceClient in py-cord 2.7+ — no flag needed.
- On the `Bot` class there is NO `self.voice_client` — it's `self.voice_clients`
  (a list). Using the singular raises `AttributeError: 'TranscriberBot' object
  has no attribute 'voice_client'` (in `on_voice_state_update` / done-callback
  cleanup). Guild-scoped access `ctx.guild.voice_client` DOES work.

Always verify the API is present before writing code against it:
`hasattr(VoiceClient, 'start_recording')` — don't trust the package name.

## py-cord API differs from discord.py (verify at runtime)

There is **no `discord.app_commands` and no `Client.tree`** in py-cord. The
slash-command surface is `discord.Bot`:

- `class Bot(discord.Bot)` with `@self.slash_command(name=..., description=...)` inside `setup_hook`
- Command callbacks take `ctx: discord.ApplicationContext` — use `ctx.respond(...)`, `ctx.defer(ephemeral=True)`, `ctx.send_followup(...)` (NOT `interaction.response.*`)
- `ctx.author`, `ctx.guild.voice_client`, `ctx.channel`
- Commands accumulate in `bot.pending_application_commands` until login syncs them; `bot.application_commands` is empty at construction. Test registration with `asyncio.run(bot.setup_hook())` then inspect `pending_application_commands`.
- `@discord.app_commands.command` standalone decorator does NOT register anything — commands silently never appear. Always register on `self.tree`/`self.slash_command`.

## Intents & Login (privileged intent trap)

`message_content` is a **privileged intent**. If the code enables it
(`intents.message_content = True`) but it isn't toggled in the Developer Portal
(Bot → Privileged Gateway Intents), login succeeds then dies immediately with
`discord.errors.PrivilegedIntentsRequired` (Shard ID None, not a token error).
**Slash commands and channel `.send()` do NOT need it** — leave `message_content`
off unless a feature actually reads message content, and if you do turn it on,
the portal toggle must be flipped at the same time or the bot won't start.

Verify the bot's guilds/channels from its own gateway view (`client.guilds` in
`on_ready`) — raw REST `GET /users/@me/guilds` with a bot token often returns
403 (scope nuance), which is NOT a bot failure. A working login + stable
process is the meaningful live check; don't treat a 403 on an ad-hoc REST call
as a blocker.

Delivery-channel fallback: if the configured target channel name doesn't exist
in the server, post the transcript to the text channel where `/join` was typed —
a missing target channel must never block a test. Tell the user either works.

## Python Version Trap

Voice code uses modern unions (`bytes | None`) → **Python 3.10+ required**.
Many machines' system python is 3.9 (this machine's was). Build the venv on
Homebrew python (`/opt/homebrew/bin/python3 -m venv .venv`), never the system
interpreter — the failure is a `TypeError` at class definition, easy to mistake
for a logic bug.

## Transcribing with mlx-whisper (local, free)

- Install `mlx-whisper numpy`; `mlx_whisper.transcribe(path, path_or_hf_repo=...)`
- **Model names MUST be full repo ids**: `mlx-community/whisper-tiny`, `mlx-community/whisper-large-v3-turbo`. The short name `whisper-tiny` 404s.
- Default `mlx-community/whisper-large-v3-turbo` (~1.6GB, downloads on first use); `whisper-tiny` for tests.
- Disk is 48kHz stereo int16 from the sink; average to mono 16-bit before transcribing.
- First HF download may hit transient 401s (rate limit) — retry or warm the cache; a later model that already downloaded is fine.
- **macOS `say` TTS renders ~empty audio files** on some machines — do NOT use it to generate test speech. Download a real speech sample (LibriSpeech/torchaudio tutorial-assets, vosk-api test.wav) instead.

## Testing a Discord bot WITHOUT a token (offline)

A bot with no Discord credentials can still be proven on the pieces that don't
need the network:

1. **Import + API presence** — `hasattr(VoiceClient, 'start_recording')`, `issubclass(Recorder, Sink)`.
2. **Command registration** — `asyncio.run(bot.setup_hook())` then assert `pending_application_commands` names.
3. **Audio pipeline** — feed synthetic PCM (numpy sine) into the sink, assert `get_wav()` returns a valid mono 48k WAV; silence returns None.
4. **Real transcription proof** — transcribe a known speech sample (LibriSpeech clip) and compare to its published transcript.
5. Mark the live Discord gate (join voice → record → deliver) as PENDING-TOKEN, not done.

## Secret Handling (hard rules)

- Bot token lives in a machine-local `.env` (bot auto-loads it) — never in chat, never committed. Add `.env` + `*.log` to `.gitignore` BEFORE the token is written (the exclusion must exist before the secret does).
- **Redact secrets from process output:** a `redact()` that masks any secret-hinted env value (TOKEN/KEY/SECRET/PASSWORD) from every log line and every Discord-bound error string. A traceback carrying the token into a channel is a leak through the same door the transcripts use.
- User asked "where should I put the token?" → the `.env` file in the project workspace, NOT the group chat. Offer to write it from a DM.
- **Validate a token against the API — NEVER classify it by base64 prefix.**
  Prefix pattern-matching ("MTU0… = user token", "MTE4… = bot token") is WRONG
  and burned a session: a valid bot token was rejected as a user token on
  exactly that guess, and the user had to push back. The definitive check is
  live, before writing the token anywhere or telling the user it's the wrong
  type:
  ```bash
  curl -s -H "Authorization: Bot <token>" https://discord.com/api/v10/users/@me
  ```
  HTTP 200 with `"bot": true` in the response = valid bot token (the body
  shows the bot username, e.g. "Audingest"); HTTP 401 = invalid or wrong
  kind. Base64-decode the first segment only if you want the ID — never as a
  type decision.

## Delivery format for transcripts

Discord caps one message at 2000 chars; a real meeting is 3-8k+ words. Deliver
long content as a **file attachment** (`.md`), not inline — one click to
download/copy vs 5+ fragmented messages. State the format choice in the brief.

## Scope reality (state it early)

A Discord bot hears ONLY audio inside Discord. It cannot reach Zoom/Meet/phone
calls. State this before architecting; external-platform capture is a separate
(manual file-drop) path. Also confirm the ACTION surface: does the transcript
just get delivered for a human to read, or must it auto-generate tasks? That
decision drives all the complexity.

## Support Files

- `references/voice-transcription-pipeline.md` — the full worked build (dtt6): Sink subclass + WAV encoding, transcript markdown assembly, env-loading + redaction guard anatomy, offline test suite, and the STATE.md run/token instructions.
