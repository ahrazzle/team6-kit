<!-- GENERICIZED: 5×{CLIENT} | source: skills/software-development/web-deployment-safety/references/vercel-cloudflare-staging.md -->
# Vercel + Cloudflare: staging subdomain playbook

Worked example from a real production site ({CLIENT}). The staging loop required:
Vercel CLI (team-scoped), a Cloudflare zone, and four small API calls.

## 1. Create the staging Vercel project

```bash
# CLI (team must be linked): deploys to a NEW project
vercel project add {CLIENT} --yes --token "$TOKEN"   # returns a .vercel.app URL

# Or via API (returns project id)
curl -s -X POST "https://api.vercel.com/v10/projects?teamId=<TEAM_ID>" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"{CLIENT}","framework":null}'
```

## 2. Attach the subdomain + get its verification TXT

```bash
curl -s -X POST "https://api.vercel.com/v9/projects/<PID>/domains?teamId=<TEAM_ID>" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"staging.example.com"}'
# Response carries "verification": [{"domain":"_vercel.example.com","value":"vc-domain-verify=staging.example.com,<hash>"}]
```

Save that TXT value — you need it for Cloudflare.

## 3. Cloudflare DNS (zone-scoped API token)

```bash
# TXT verification record (name without the leading _vercel part — use "_vercel")
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records" \
  -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  -d '{"type":"TXT","name":"_vercel","content":"vc-domain-verify=staging.example.com,<hash>","ttl":300}'

# CNAME sub -> Vercel (unproxied so Vercel edge certs bind)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records" \
  -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  -d '{"type":"CNAME","name":"staging","content":"cname.vercel-dns.com","proxied":false,"ttl":300}'
```

## 4. Wait ~20s, then verify the domain in Vercel

```bash
curl -s -X POST "https://api.vercel.com/v9/projects/<PID>/domains/staging.example.com/verify?teamId=<TEAM_ID>" \
  -H "Authorization: Bearer $TOKEN"
# "verified": true → done. If "added to a different project", delete + re-add on the right project.
```

## 5. Deploy to staging (NOT main)

```bash
# From the project directory
vercel --project {CLIENT} --prod --yes
```

Main production stays untouched — it deploys only via its own `vercel deploy --prod`.

## Token expiry gotcha

Vercel CLI auth tokens expire ~24h (see `expiresAt` in
`~/Library/Application Support/com.vercel.cli/auth.json`). On "Not authorized":
run `vercel whoami` WITHOUT `--token` — the CLI self-refreshes. Deploys that pass
`--token` from a stale file keep failing; drop the flag and let the CLI use its own session.

## Env-var scoping for a separate staging project

`vercel env add` only accepts environments `production`, `preview`, `development` —
there is NO `staging` scope. A staging subdomain that lives on its OWN Vercel
project gets its env vars scoped to that project's **production** environment:

```bash
# from a dir linked to the staging project (vercel link --project {CLIENT})
echo "$API_KEY" | vercel env add OPENROUTER_API_KEY production --yes
```

Without this, a fresh staging baseline answers 503 "Assistant not configured":
the function is deployed, but the key was scoped to the production project only.
Also note: an env-var change requires a REDEPLOY of the staging project before
the function picks it up.

## Root A record vs apex CNAME

- Apex domains on Cloudflare can use a CNAME (flattening) — delete any stale `A` record
  pointing at an old origin before adding the apex CNAME, or the apex serves a dead origin.
- `www` was a second dark surface once: it was 301-redirecting into a dead apex.
  Release `www` from the old binding and point it at the new origin alongside the apex.
