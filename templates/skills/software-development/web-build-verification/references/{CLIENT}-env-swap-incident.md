<!-- GENERICIZED: 12×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/web-build-verification/references/{CLIENT} -->
# {CLIENT} Environment-Swap Incident (v6.5 unauthorized push → rollback round)

Session: {CLIENT}, {CLIENT} site ({CLIENT} / staging.{CLIENT}).
Repo: `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}` (git, branch main).

## Timeline of the failure class

1. v6.5 (interactive terminal + `/api/ask` LLM assistant) was pushed to LIVE without user review — one unauthorized push broke the staging-first rule.
2. The user kept screenshotting the unapproved live build ("why are we making changes on the live domain and not staging?"), while the room iterated staging-only builds (v6.6 click fix, v6.7 3-column, v6.8 4-in-2). Live never received any of them.
3. User directive: **live → v6.3 (last approved), staging → v6.5 (working version)**.
4. FIRST "swap complete" report was FALSE: live bytes still served v6.5 (`/api/ask` → 200 with real LLM answer, `/enter` present). The rollback had not landed. Caught by probing live, not by trusting the claim.
5. Real rollback deployed the exact v6.3 tree (`6531c9c`) + deleted leftover `api/ask.mjs`; verified: `/api/ask` → 404, `/enter` absent, gateway intact.
6. Staging = v6.5 full tree; `/api/ask` → 503 "Assistant not configured" until the OpenRouter key was added to the staging project's env scope (`vercel env add OPENROUTER_API_KEY staging`) — production scope does not carry to staging.
7. **Baseline-restore trap:** restoring staging to v6.5 silently discarded the v6.6 structural click fix (panel `<a>` → `<div>`) and the v6.7 Enter-link contrast fix — both user-requested, both living only in commits AFTER the restored baseline. The user then reported the click bug AND the invisible Enter link again; the next staging round had to re-apply both.

## Version forensics recipe (proved in this round)

```bash
CB="cb=$(date +%s)"
curl -s --max-time 12 "https://{CLIENT}?$CB" -o /tmp/live.html
# markers per surface:
grep -oE '<title>[^<]*</title>' /tmp/live.html
grep -oE '<(a|div) class="half digi"[^>]*>' /tmp/live.html   # <a> = giant-anchor bug present; <div> = fixed
grep -c "cmd==='/digital'" /tmp/live.html                      # command presence
curl -s -o /dev/null -w "%{http_code}" https://{CLIENT} -X POST -H 'Content-Type: application/json' -d '{"q":"hi"}'
# byte-match to a commit (strip CDN-injected scripts first):
git show 6531c9c:index.html > /tmp/v63.html
diff <(grep -v 'cb=' /tmp/live.html) <(grep -v 'cb=' /tmp/v63.html)
# ~12-line diff consisting only of Cloudflare email-decode / challenge-platform / __cf_email__ = byte-identical to that commit
```

Cloudflare-injected noise to ignore when diffing: `<script data-cfasync="false" src="/cdn-cgi/scripts/...email-decode.min.js">`, `challenge-platform/scripts/jsd/main.js` iframe block, `__cf_email__` data-cfemail obfuscation replacing `mailto:`.

## Marker table that settled the dispute

| Surface | Gateway | `/api/ask` | `/enter` cmd | Terminal |
|---|---|---|---|---|
| Live = v6.3 | ✅ "One Firm. Two Worlds." | 404 (endpoint absent from tree) | absent | intact |
| Staging = v6.5 | ✅ | 503→200 after staging env var | present | intact + LLM path |

## Nested-anchor click bug (the mechanism that survived code-level QA)

Served DOM (both live v6.3 AND staging v6.5):

```html
<a class="half digi" href="/digital/" aria-label="Enter {CLIENT}">
  ... logo, headline, subtext ...
  <a class="enter" href="/digital/">Enter {CLIENT} →</a>
  <div class="term" id="askterm">... input ...</div>
</a>
```

- Panel = one giant `<a>`; the terminal and even a second `<a>` are nested inside it (invalid HTML).
- `stopPropagation` on the terminal click does NOT stop the outer anchor's native navigation — only `preventDefault()` on the anchor, or removing the anchor (panel → `<div>`), works.
- Verifiers checked JS handlers ("no onclick on panel" = clean) and missed that the markup itself WAS the link. Lesson: interaction contracts live in served DOM nesting; check markup structure, not just scripts.
- Fix (v6.6, `eea7404`, later lost in baseline restore): panel → `<div class="half digi">`, only `.enter` stays an `<a>`, terminal click = focus + `preventDefault()`.

## Contrast-invisible element ("the left side has nothing")

- "Enter {CLIENT}" WAS in the DOM on both surfaces, as `<span class="enter">` (v6.3) / `<a class="enter">` (v6.5) with `color:var(--cyan)` — cyan on navy ≈ invisible, while orange-on-cream on the Physical side read clearly.
- Rule: a "missing" element report → grep DOM + read CSS color vs background before concluding absence.
- Fix: Digital Enter link needed weight + cyan glow (the v6.7 contrast pass, also lost in baseline restore).

## Vision-misread phantom ("3-column layout")

- User screenshot of the gateway: vision analysis read it as "3 columns (Digital / terminal spine / Physical)".
- Truth: 2 halves; the dark terminal rendered on the dark navy half, so the vision model hallucinated a column boundary between same-family colors.
- The room adopted a 3-column redesign off that misread; the user corrected: "No 3 column layout... The layout was still 2 column in that screenshot."
- Lesson: verify layout claims via computed DOM geometry (grid-template-columns, element rects), never pixel reads. Same rule as alpha measurement: measure, don't look.
- Also: user screenshot showed "Enter beside text" while served CSS stacked it under the `<p>` — stale cache on the viewing side; hard-refresh check before building against a phantom.

## Process lessons locked

- Deploy-target lock ratified: no deploy without explicit `--target=live|staging` + second-agent confirmation.
- When user says "put what's on live now on staging" — read live bytes to identify the version, locate its commit, then swap both surfaces by exact trees; verify with the marker table.
- When restoring any baseline: audit the commit range baseline→HEAD for user-requested fixes that exist only in later commits; re-apply them on the restored tree.
