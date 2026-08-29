<!-- GENERICIZED: 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/git-remote-troubleshooting/SKILL.md -->
---
name: git-remote-troubleshooting
description: "Use when git fetch/clone/push hangs or stalls."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, github, networking, fetch, clone, http2, troubleshooting, update]
---

# Git Remote Operation Troubleshooting

## When to Use

- `git fetch`, `git clone`, or `git push` hangs for minutes or appears to loop forever.
- An update tool (e.g. `hermes update`, desktop "Looking for updates") stalls on the
  fetch/check phase while general web browsing works fine.
- git remote ops are slow or flaky, but `curl`/browser reach the same host instantly.

Diagnose and fix a stalled/slow git remote operation where the failure is NOT
DNS, offline, or missing credentials — it is a protocol or host-path problem
(HTTP/2 mishandled by a middlebox/firewall/VPN path, or egress-IP throttling).

## Core insight

`curl`/browser reaching a host in 0.3s does NOT mean git will. **git negotiates
HTTP/2 by default** (via its bundled libcurl); plain `curl` defaults to HTTP/1.1.
When a network path mishandles HTTP/2, git stalls (0 bytes after TLS) while curl
succeeds instantly. That asymmetry is the strongest single clue.

## Diagnosis ladder (cheap first)

1. **Inspect the stuck process tree** (if one is hung right now):
   `ps aux | grep "git fetch"` → chain is `git fetch` → `git-remote-https` →
   `git-remote-http`. Check connection state with `lsof -nP -iTCP -p <pid>`.
   `ESTABLISHED` but idle for minutes = wedged socket (protocol/path). `SYN_SENT` = no route.
   `sample <pid> 1` shows the blocking syscall: `__select` in `http_request` =
   waiting on a socket that never became ready. Note: an orphaned chain (PPID 1)
   means a previous fetch got abandoned — clean it up, then re-test fresh.

2. **Rule out offline / DNS** with curl:
   `curl -sS -o /dev/null -w "HTTP %{http_code} in %{time_total}s" --max-time 5 https://github.com`
   Fast 2xx/3xx/429 = network path alive; git's problem is elsewhere.

3. **Protocol isolation — the decisive test.** Time a shallow clone under HTTP/2
   vs HTTP/1.1. If HTTP/2 stalls and HTTP/1.1 completes, it is a protocol-path issue:
   ```
   git clone --depth 1 --filter=blob:none https://github.com/owner/repo.git /tmp/t2   # default (http2)
   git -c http.version=HTTP/1.1 clone --depth 1 --filter=blob:none https://github.com/owner/repo.git /tmp/t1
   ```

4. **Check rate-limiting.** GitHub returns HTTP 429 on many requests when an
   egress IP is throttled. Confirm the token is not the cause:
   `gh auth token` then `curl -H "Authorization: token <tok>" https://api.github.com/rate_limit`
   and read `resources.core.remaining/limit`. If the token is healthy but
   anonymous/authenticated requests still 429, it is egress-IP throttling, not auth.

5. **Rule out MTU black hole** (small transfers fast, large ones stall):
   `ping -c 4 -s 1472 github.com` — large ICMP packets should pass at 0% loss.

6. **Rule out a misrouted VPN.** `ifconfig` for `utun*` interfaces; `route -n get default`
   for the active egress interface; `ps aux | grep -i vpn` for daemons. A VPN daemon
   may be running but *disconnected* (not routing) — traffic then egresses the physical
   interface, so the degradation is on the ISP/corporate path, not the machine.

## Fix

Stage 1 — force HTTP/1.1 (kills the HTTP/2 dead-stall):

```
git config --global http.version HTTP/1.1
```

Durable and global. Verify with a timed fetch afterwards.

Stage 2 — if the path is flaky/slow on BOTH protocols, add a low-speed abort so a
stalled connection fails FAST instead of hanging forever:

```
git config --global http.lowSpeedLimit 1000   # bytes/sec
git config --global http.lowSpeedTime 15      # abort after 15s under 1KB/s
git config --global fetch.timeout 30          # git >= 2.34
```

This is the fix that actually clears a hung update UI. After it, a stalled fetch
returns `fatal: unable to access '...': Operation too slow. Less than 1000
bytes/sec transferred the last 15 seconds` in ~15s (verified) — never hangs. The
op then succeeds on retry when the connection isn't blackholed.

CAUTION: the values above are a fast-fail dial, and too aggressive a setting
becomes a false-failure CAUSE on slow-but-alive links (see Stage 3). Start with
the patience-window values there if the path is merely slow rather than dead.

Stage 3 — patience window for slow-but-alive links (the 15s/30s values are a footgun):

A degraded path can be alive and still dribble <1KB/s for 10-120s before
completing (github.com over HTTP/1.1 on this machine: ls-remote ~14s, full fetch
~2min, both verified {CLIENT}). With `lowSpeedTime=15` / `fetch.timeout=30`,
git aborts BEFORE completion and the caller surfaces a connectivity error even
though the link works. Symptom: "Couldn't check for updates / Check your
connection and try again" in a desktop app while the user's own connectivity
checks pass — the message is a lie; git's patience ran out.

Prove config causality (never guess network-vs-config):
```
# same command the failing tool runs, with the abort lifted:
git -c http.lowspeedlimit=0 -c http.lowspeedtime=0 ls-remote --exit-code --heads https://github.com/owner/repo.git main
```
Succeeds in seconds while the plain command aborts with "Operation too slow" =
the config is the culprit, not the network.

Fix (back up the config first — `cp ~/.gitconfig ~/.gitconfig.pre-<fix>`):
```
git config --global http.lowSpeedTime 90
git config --global fetch.timeout 120
```
Keep `lowSpeedLimit=1000` — it still kills true dead-stalls, just with a 90s
patience window. Trade-off to state honestly: a genuinely dead link now takes up
to ~2min to fail instead of 15s. Verify with the real fetch afterward.

Important nuance: a degraded path does NOT stay on one protocol — it can flip
between "HTTP/2 stalls, HTTP/1.1 works" and "HTTP/1.1 stalls, HTTP/2 works" across
minutes and different GitHub edge IPs. So no single protocol choice is reliable;
the low-speed abort is the robust answer regardless of which protocol is up.

## Pitfalls

- Do NOT assume HTTP/1.1 alone fixes a flaky path. It kills the HTTP/2 dead-stall,
  but a degraded path can also stall HTTP/1.1 (15-90s per request, intermittent
  blackholes, 429s). Add the low-speed abort (Stage 2) so a stalled connection
  fails fast and the op can succeed on retry — this is what makes an update tool
  resolve instead of looping.
- Desktop Electron update check: `apps/desktop/electron/main.ts` `runGit` has NO
  subprocess timeout — it resolves only on git's `exit`. So a hung git fetch pins
  the "Looking for updates…" UI forever (`checking` never clears). The git-level
  low-speed abort fixes this without any app rebuild: the next spawned fetch fails
  fast with a non-zero exit, and the UI resolves to a retry-able error. The CLI
  `hermes update` path is separately bounded (banner `_check_via_local_git`,
  5-10s timeouts, 6h cache) and is NOT the hang.
- Update-check UIs map ANY git failure to a generic connectivity error. On Hermes
  desktop, "Couldn't check for updates" + "Check your connection and try again"
  = `status.error` from IPC `hermes:updates:check` → `checkUpdates()` in
  electron/main.ts → `runGit(['fetch','--quiet','origin',branch])` exited
  non-zero (usually "Operation too slow" from Stage 2/3 values). The renderer
  bridge (`preload.ts` `ipcRenderer.invoke`) has NO timeout, so git config is the
  ONLY gate — diagnose by running the exact git command the app spawns, never by
  trusting the app's error copy. See references/hermes-desktop-update-check.md
  for the full trace (file paths, reproduction, verification).
- Do NOT assume a full-rate-limit token means auth is fine and stop there. A healthy
  token + still-hanging fetch points to protocol/path, not credentials.
- `GIT_CURL_VERBOSE=1 git fetch` is the fast way to see the actual HTTP exchange —
  whether an `Authorization` header is sent and what status comes back. On a hang,
  run it in the background and poll the trace (a foreground run with a short timeout
  eats the partial stderr on the timeout).
- If you forced HTTP/1.1 and a later `git fetch` STILL hangs, check for a fresh
  orphaned fetch chain and rate-limit status before re-diagnosing from scratch.
- `hermes update` / desktop "Looking for updates" hanging is a symptom surface of
  this class. The fix is git-level, not a Hermes code change.
