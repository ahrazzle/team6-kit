<!-- GENERICIZED: 5×{CLIENT}, 3×{RELATIONSHIP} | source: skills/deployment/github-pages-deployment/SKILL.md -->
---
name: github-pages-deployment
description: "Deploy a GitHub Pages site with a custom domain."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [linux, macos, windows]
---

# GitHub Pages Deployment (Custom Domain)

## When to Use

- Serving a public repo's static site at a custom subdomain (e.g. `{CLIENT}`)
- Setting or verifying a GitHub Pages custom domain
- Deciding between GitHub Pages vs Vercel/Netlify for a static repo
- Diagnosing "live site won't load" when the deploy itself is healthy

Complements `vercel-deployment` — that skill covers the Vercel path; this covers Pages. Pick ONE owner per hostname (see Single-Owner Rule).

## Core Flow

### 1. Ensure the build artifact is committed

Pages serves from the repo (default: root or `/docs` of the default branch). `dist/` MUST be tracked (not in `.gitignore`) or the bundle 404s silently:

```bash
cat .gitignore            # ensure dist/ is NOT listed
npx esbuild src/index.ts --bundle --outfile=dist/game.js --format=esm
```

### 2. Commit a CNAME file

`CNAME` (repo root) containing exactly `sub.apex.com` (one line, no trailing spaces). Commit and push. If a prior Vercel `vercel link` added `.vercel` / `.env*` to `.gitignore`, add the CNAME with `git add -f CNAME`.

### 3. Register the custom domain via the API

Use the **authenticated** `gh` CLI (not an unauthenticated curl — that returns 404):

```bash
gh api -X PUT repos/OWNER/REPO/pages \
  -f cname=sub.apex.com -f source[branch]=main -f source[path]=/
```

Then verify the registration:

```bash
gh api repos/OWNER/REPO/pages | jq '{cname, status, html_url, https_enforced}'
# expect: cname: sub.apex.com, status: built, html_url: http://sub.apex.com/
```

### 4. DNS record at the external host (usually Cloudflare)

GitHub Pages needs ONE CNAME (no TXT verification record, unlike Vercel):

| Type | Name | Content | Proxy |
|---|---|---|---|
| CNAME | `sub` | `{RELATIONSHIP}.github.io` | Proxied (orange cloud) |

This is the same pattern as `acctraining.{CLIENT}`. DNS for {CLIENT} lives at Cloudflare; there is **no Cloudflare API token on this machine** (keychain/.env/config all empty), so the record is a user action at dash.cloudflare.com unless a Zone→DNS→Edit token is provided. Scope any provided token to that zone + `DNS Edit` only.

### 5. Verify the live site

```bash
dig +short sub.apex.com                    # expect a Cloudflare edge IP (e.g. 172.64.x.x)
curl -sI https://sub.apex.com | head -5    # expect 200, real content
curl -s https://sub.apex.com/demo.html | grep -c "expected-marker"
```

## Pitfalls

- **Single-Owner Rule — never run two deploy paths to one hostname.** Vercel + GitHub Pages both attaching the same `sub.apex.com` creates a CNAME conflict; Cloudflare serves whichever it likes and the deploy looks broken. Choose one owner and remove the other's domain/project BEFORE handing the user DNS instructions. Never present two conflicting CNAME targets in consecutive messages.
- **`gh api` for Pages, not curl.** The Pages endpoint requires an authenticated token; plain `curl https://api.github.com/repos/o/r/pages` returns 404. Use `gh api`. (This bit the team once — a 404 was misread as "domain unset" when it had actually been set via `gh`.)
- **Stale local negative DNS cache.** After a domain was NXDOMAIN, the OS resolver may hold a stale negative-cache entry for minutes — `dig` and other networks resolve fine, but the local browser fails. Verify the edge regardless of the local resolver:
  ```bash
  curl -s --resolve sub.apex.com:443:172.64.80.1 https://sub.apex.com -o /tmp/live -w "HTTP %{http_code}\n"
  ```
  Tell the user it's transient, or flush with `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder`.
- **Pages CDN lags ~45-60s after push** (raw GitHub reflects the commit immediately). See `web-app-debugging` for the raw-vs-Pages divergence and served-bundle verification protocol — verify fixes at the SERVED URL, not local source.
- **`dist/` in `.gitignore` breaks Pages silently** — the bundle import 404s and the page appears to "do nothing". Remove `dist/` from `.gitignore` and commit the bundle.

## Verification Discipline

Every deploy claim is gated on a served read-back: `gh api .../pages` for the domain registration, `curl` (optionally `--resolve`) for live content, `dig` for DNS. Never report "live" from local source or a successful push alone.

## References

- `references/{CLIENT}` — the {CLIENT} deployment: page registration, Cloudflare CNAME, Vercel-conflict cleanup, stale-cache quirk
