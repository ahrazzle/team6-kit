<!-- GENERICIZED: 27×{CLIENT}, 2×{RELATIONSHIP} | source: skills/deployment/vercel-deployment/references/{CLIENT} -->
# {CLIENT} — Vercel / Cloudflare Subdomain Map

## DNS Host

- `{CLIENT}` is **Cloudflare-managed** (NS: marjory.ns.cloudflare.com, konnor.ns.cloudflare.com).
- No Cloudflare API token exists on this machine (checked keychain, `~/.wrangler`, `~/.cloudflare`, profile `.env` files, config.yaml). DNS record changes at dash.cloudflare.com must be done by the user, or a CF token added to a profile `.env`.

## Vercel

- Account: `{RELATIONSHIP}`; team: `a-4677s-projects` (orgId `team_FaoexnZzdTcrVOAXDutsVakN`)
- CLI auth token: `~/Library/Application Support/com.vercel.cli/auth.json` (field `token`)
- Projects serving subdomains (attach via REST API when CLI says domain_not_owned):

| Subdomain | Vercel Project | Project ID | Notes |
|---|---|---|---|
| {CLIENT} / www | {CLIENT} | prj_g27G8Lvqan5gATvQMXx8JpHG2b6L | gateway landing (Digital/Physical split) |
| {CLIENT} | {CLIENT} | — | CNAME → cname.vercel-dns.com, verified |
| acctraining.{CLIENT} | acctraining | — | hosts '{CLIENT}' (never '{CLIENT}' publicly) |
| {CLIENT} | {CLIENT} | prj_fmD4sEVZCfICP2xDTJHRwYmVrFQp | attached {CLIENT}, pending DNS verify |
| staging.{CLIENT} | {CLIENT} | prj_zcZuSzilfYCOh2cRLzEuZNOg16SD | deploy-gate staging for {CLIENT} |

## {CLIENT} deploy (worked example, {CLIENT})

1. `npx vercel link --yes --project {CLIENT} --scope a-4677s-projects` → created project, connected GitHub repo `{RELATIONSHIP}/{CLIENT}`
2. First `--prod` deploy failed: no `public/` dir → added `vercel.json` with `outputDirectory: "."` → deploy Ready at `{CLIENT}`
3. `.vercel.app` URL 302→SSO (project `ssoProtection: all_except_custom_domains`) → custom domain will serve publicly once attached
4. `vercel domains add {CLIENT} {CLIENT}` → `domain_not_owned` (403): apex not in Vercel registry
5. REST API attach succeeded: `POST https://api.vercel.com/v10/projects/prj_fmD4sEVZCfICP2xDTJHRwYmVrFQp/domains` `{"name":"{CLIENT}"}` → `verified:false`
6. Pending DNS (user action at Cloudflare):
   - TXT `_vercel` → `vc-domain-verify={CLIENT},44787fc7b95b3bb5016d`
   - CNAME `{CLIENT}` → `cname.vercel-dns.com` (DNS only, grey cloud)

## Verification pattern

- `dig +short sub.{CLIENT}` → CNAME `cname.vercel-dns.com` + Vercel IPs = attached
- `curl -sI https://sub.{CLIENT}` → 200 = live; 302 to vercel.com/sso-api = protection gating the non-custom URL
