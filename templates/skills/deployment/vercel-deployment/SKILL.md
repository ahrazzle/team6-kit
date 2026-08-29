<!-- GENERICIZED: 8×{CLIENT}, 2×{RELATIONSHIP} | source: skills/deployment/vercel-deployment/SKILL.md -->
---
name: vercel-deployment
description: "Use when deploying to Vercel or attaching a domain."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [macos, linux, windows]
---

# Vercel Deployment (Static Sites + Custom Domains)

## When to Use

- Deploying a static HTML/JS site to Vercel (e.g. `{CLIENT}`, any `.vercel.app` target)
- Attaching a custom domain or subdomain to a Vercel project
- Verifying why a Vercel URL 302s to SSO instead of serving content
- The {CLIENT} subdomain family ({CLIENT}, acctraining., {CLIENT}, staging.)

## Core Flow

### 1. Link / create the project

```bash
cd <site-dir>
npx vercel link --yes --project <name> --scope <team-id>   # creates project + connects GitHub
npx vercel --prod --yes --scope <team-id>
```

`--scope` targets a team (e.g. `a-4677s-projects`). Omit when the account has one team.

### 2. Static sites need vercel.json — the default expects `public/`

First deploy fails with: `No Output Directory named "public" found`. Fix with a static-site config:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "outputDirectory": ".",
  "buildCommand": "echo 'static site — committed dist/; no build step'",
  "framework": null,
  "cleanUrls": true
}
```

Commit this file — it makes future deploys auto-configure.

### 3. Deployment protection nuance

`curl` on the `*.vercel.app` URL returns **302 → vercel.com/sso-api** when the project has SSO protection. Check the project:

```bash
curl -s "https://api.vercel.com/v1/projects/<projectId>" -H "Authorization: Bearer $TOKEN" | grep ssoProtection
```

`ssoProtection: {"deploymentType": "all_except_custom_domains"}` means: the `.vercel.app` URL is gated, but **the custom domain serves publicly**. Do NOT disable protection — just finish the domain attach.

### 4. Attach a subdomain — CLI refuses, REST API works

`vercel domains add sub.apex.com <project>` fails with `domain_not_owned` (403) when the apex domain is NOT registered in Vercel (it's registered elsewhere, e.g. Cloudflare). The CLI path only works for apex domains you own inside Vercel.

**The REST API attach bypasses this.** Token lives at `~/Library/Application Support/com.vercel.cli/auth.json` (field `token`). Project ID from `<site-dir>/.vercel/project.json`:

```bash
TOKEN=$(python3 -c "import json;print(json.load(open('$HOME/Library/Application Support/com.vercel.cli/auth.json'))['token'])")
curl -s -X POST "https://api.vercel.com/v10/projects/<projectId>/domains" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"sub.apex.com"}'
```

Response shows `"verified": false` plus the exact DNS records needed. This is the same mechanism the dashboard uses — it works for subdomains the CLI rejects.

### 5. DNS records at the external DNS host (usually Cloudflare)

Vercel returns a verification block like:

```json
{"verification":[{"type":"TXT","domain":"_vercel.apex.com",
  "value":"vc-domain-verify=sub.apex.com,<hash>","reason":"pending_domain_verification"}]}
```

Add at the DNS host ({CLIENT} is Cloudflare-managed):

| Type | Name | Content | Proxy |
|---|---|---|---|
| TXT | `_vercel` | `vc-domain-verify=sub.apex.com,<hash>` | — |
| CNAME | `sub` | `cname.vercel-dns.com` | DNS only (grey cloud) |

Once both propagate (~1-2 min), Vercel auto-verifies and the domain serves the deployment.

### 6. Verify

```bash
curl -sI https://sub.apex.com | head -5        # expect 200, not 302-to-sso
curl -s  https://sub.apex.com/demo.html | grep "expected-string"
```

## Pitfalls

- **Don't trust `vercel domains add` errors at face value.** `domain_not_owned` for a subdomain does NOT mean the attach is impossible — it means use the REST API (step 4).
- **Never purchase domains via CLI** — `vercel domains buy` requires interactive terminal and real money; hand to user.
- **Deployment protection is per-project, not per-deployment.** Check `ssoProtection` on the project, not the deployment.
- **SSO 302 ≠ broken deploy.** Check whether the request URL is the `.vercel.app` URL (gated) or the custom domain (public). Only the custom domain matters for launch.
- **GitHub auto-deploy**: `vercel link` connects the repo; a push with vercel.json present redeploys automatically. Commit configs, don't leave them local.
- **No Cloudflare API token on this machine** — DNS records for {CLIENT} must be added by the user at dash.cloudflare.com (or a CF token added to a profile `.env` to enable agent-side DNS).

## References

- `references/{CLIENT}` — the {CLIENT} Vercel/Cloudflare map: which projects serve which subdomains, team/org IDs, deployment history
