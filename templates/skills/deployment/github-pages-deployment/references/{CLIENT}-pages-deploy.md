<!-- GENERICIZED: 15×{CLIENT}, 4×{RELATIONSHIP} | source: skills/deployment/github-pages-deployment/references/{CLIENT} -->
# {CLIENT} GitHub Pages deployment ({CLIENT})

Target: `{CLIENT}` served from repo `{RELATIONSHIP}/{CLIENT}` (public, meant for forking).

## What converged

The team first went Vercel (project created, domain attached via REST API), then pivoted to **GitHub Pages** because the repo is public-by-design for external forking, the Pages build was already `built`, and it matched the `acctraining.{CLIENT}` precedent. Vercel was removed to avoid a CNAME conflict — one owner per hostname.

## Vercel path (abandoned) — for reference only

- `npx vercel link --yes --project {CLIENT} --scope a-4677s-projects` created the project.
- First deploy failed: `No Output Directory named "public"` — fixed with `vercel.json` `outputDirectory: "."` (later deleted when converging on Pages).
- Domain attach: `vercel domains add sub.apex <project>` fails `domain_not_owned` for a subdomain whose apex isn't in Vercel's registry; REST works:
  `curl -X POST https://api.vercel.com/v10/projects/<projectId>/domains -d '{"name":"sub.apex.com"}'` (token at `~/Library/Application Support/com.vercel.cli/auth.json`).
- Project `ssoProtection: all_except_custom_domains` → `.vercel.app` is gated, custom domain serves publicly.

## GitHub Pages path (final)

1. Committed `CNAME` = `{CLIENT}` (`git add -f CNAME` — a prior `vercel link` had added `.vercel`/`.env*` to `.gitignore`, but CNAME itself wasn't ignored).
2. `gh api -X PUT repos/{RELATIONSHIP}/{CLIENT} -f cname={CLIENT} -f source[branch]=main -f source[path]=/`
3. Read-back: `gh api repos/{RELATIONSHIP}/{CLIENT}` → `cname: {CLIENT}`, `status: building→built`, `html_url: http://{CLIENT}`.
4. Cloudflare CNAME record added by user: `{CLIENT}` → `{RELATIONSHIP}.github.io`, proxied (orange cloud).
5. Verified live: `curl --resolve {CLIENT}:443:172.64.80.1 https://{CLIENT}` → HTTP 200, 8 marker matches.

## Key verification detail

`curl https://api.github.com/repos/o/r/pages` (no auth) → 404. The Pages endpoint needs an authenticated `gh api`. One teammate misread this as "domain not set" when it had been set via `gh` — always use `gh api` and trust the `gh` read-back.

## Local stale-cache quirk

After the domain went from NXDOMAIN → live, the local macOS resolver held a stale negative-cache entry: `dig` and other networks resolved, local browser/urllib failed. `curl --resolve` bypasses it for verification. Flush with `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder`.
