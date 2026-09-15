---
name: sag-tts
description: "Use when a task needs text-to-speech on the command line. Adapter skill for the optional `sag` CLI: detect-or-report the binary, discover voices, stream or save speech, select a provider, dry-run before speaking. Provider-neutral and credential-free at the Team6 layer."
version: 1.0.0
author: Team6-kit
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Text-to-Speech, Voice, Media, CLI-Adapter, ElevenLabs, 60db]
    related_skills: [external-tool-vetting, macos-harness, licensed-asset-reuse]
---

# sag-tts — optional text-to-speech CLI adapter

`sag` is an external, optional CLI that turns text into speech, like the macOS
`say` command but with a modern voice. It streams to speakers by default,
lists voices, and can save audio files. This skill is the Team6 adapter layer:
it does **not** bundle or vendor the `sag` binary (which is Go source in its
own repository). It treats `sag` as an opt-in external tool you install and
configure yourself.

The Team6 layer stays **provider-neutral and credential-free**. The skill
never stores an API key, token, credential path, or provider secret, and never
assumes a specific provider. Provider selection happens only through the
external CLI's own environment, which you set up outside this kit.

## Detect-or-report: never assume the binary exists

Before anything else, check whether `sag` is actually installed. It is an
optional tool — a missing binary is a normal state, not an error to guess
around.

```bash
command -v sag >/dev/null 2>&1 && echo "present" || echo "missing"
sag --help >/dev/null 2>&1 && echo "cli-ok" || echo "cli-unavailable"
```

- If the binary is missing: report a clear **non-success** result, do not
  guess, do not fabricate speech. Suggested next steps (pick the one that fits
  the host; none are run from this kit):
  - macOS via Homebrew: `brew install steipete/tap/sag`
  - Prebuilt binary archive from the upstream releases page
  - Go toolchain: `go install github.com/steipete/sag/cmd/sag@latest`
- If the binary exists but `--help` fails: report the exact failure and the
  raw `--help` exit code.

## Provider selection (external, never stored here)

`sag` supports more than one TTS provider and picks one from the credentials
you have configured in its environment. This kit holds **no** provider secret
and no credential path. Set the provider environment outside the kit (your
profile `.env`, your shell, or a secrets manager — not a committed template):

- The API key for provider A lives in an environment variable such as
  `ELEVENLABS_API_KEY`.
- The API key for provider B lives in an environment variable such as
  `SIXTYDB_API_KEY`.
- Optional voice/defaults may use variables such as `ELEVENLABS_VOICE_ID` or
  `SAG_VOICE_ID`.

Rules you must keep (they are the no-secret contract):

1. Never write a key value, token, or credential path into this skill, a
   script you commit, a command you echo, or a run packet. Reference the
   environment variable name only.
2. If both providers' keys are set, `sag` refuses to auto-select — unset one
   and retry. That is provider hygiene, not a bug.
3. If no key is set, `sag` errors. Report that clear non-success result.

## Voice discovery (explicit, bounded)

List and search voices before speaking. All discovery is read-only.

```bash
# List all available voices (bounded, no speech)
sag voices

# Search by keyword with an explicit limit
sag voices --search english --limit 20
sag voices --search english --limit 5 --try

# Free-text query with a limit
sag voices --query "crazy scientist" --limit 5 --try

# Filter by label and cap the result set
sag voices --label accent=british --label use_case=character --limit 10
```

Always pass a bounded `--limit`. Voice catalogs can be large; an unbounded
listing is an expensive, unbounded action at the Team6 layer.

## Speak (streaming and file output)

The default `sag "text"` form routes to speak automatically (macOS `say`
style). The explicit form is `sag speak`:

```bash
# Stream to speakers with a named voice
sag speak -v Roger "Hello world"

# Speak a named voice with a file output (format inferred from extension)
sag speak -v Roger -o out.mp3 "Save to file"

# Read text from a file or stdin
sag -f text.txt "Read this aloud"
echo "piped input" | sag speak -v Roger

# Rate control (words per minute)
sag -v Roger -r 200 "Faster speech"
```

`--play`/`--no-play` controls speaker playback; `--stream`/`--no-stream`
controls streaming while generating. An explicit output file plus `--no-play`
is the quiet, script-safe form.

## Dry-run first, speak second

Before spending provider quota or producing audio, verify the invocation shape
without committing to speech:

1. Confirm the binary and voice exist (detect-or-report + `sag voices
   --search` with a limit).
2. Confirm the provider environment is set (check the key variable is
   non-empty, **without printing its value**).
3. Confirm flags are valid for the active provider. Note: some flags are
   provider-specific — a flag that is ElevenLabs-only fails fast on the 60db
   provider, and `--stream` may be rejected where the provider buffers output.
4. Then run the bounded speak command.

`--timeout` bounds the generation time (e.g. `sag --timeout 5m ...`); `0`
means no internal timeout. For agent/script runs, give the outer process
timeout headroom and verify generated audio duration with a probe
(`ffprobe`) when truncation would matter. These are the same bounded-action
rules as any external-tool integration.

## Clear non-success results

A result is **success** only when the spoken output (stream, file, or exit 0
with the expected artifact) is actually produced and verified. Otherwise
report a **clear non-success result** — never a silent pass. The non-success
classes:

| Condition | What to report |
|---|---|
| Binary missing | `missing` / `cli-unavailable` with the exact `command -v` result; state install options, do not guess. |
| Provider unconfigured (no key set, or both set) | `provider-error` with the raw `sag` message; do not invent which key to fix. |
| Provider returns an error | `provider-error` with the exact stderr/exit code; no fabricated audio. |
| Interrupted / timed-out stream | `interrupted` with the timeout used and whether a partial file exists; verify duration before claiming a complete file. |
| Provider-invalid flag | `provider-error` naming the flag and the provider, so the caller can adapt. |

Never echo a provider secret in any error, result, or log. Reference the
variable name only.

## Boundaries

- **No vendoring.** The `sag` Go source, its `internal/` packages, and its
  providers are not copied into this kit. This skill is a usage adapter, not
  a fork.
- **No secrets.** No key value, token, credential path, or provider secret is
  stored in this template or generated by it.
- **No unbounded actions.** Voice listings and searches are always capped by
  `--limit`; generation is bounded by `--timeout`.
- **No provider lock-in at the Team6 layer.** The skill describes how to
  select a provider through the external CLI, and treats provider choice as
  the operator's environment concern, not a kit policy.
- **Non-mac hosts.** Playback still works via decoding on some platforms, but
  device-selection flags may be no-ops. Verify on the host before relying on
  them.

## Related skills

- `external-tool-vetting` — adopt, pin, and audit external CLIs before
  distribution; `sag` follows that protocol.
- `licensed-asset-reuse` — voice/audio assets you save inherit their own
  licensing; check before reuse.
