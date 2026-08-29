<!-- GENERICIZED: 13×{CLIENT}, 3×{RELATIONSHIP} | source: skills/static-site-production/SKILL.md -->
---
name: static-site-production
description: Use when deploying static sites. Deploy, cache, assets.
---

# Static Site Production

Class-level discipline for shipping static marketing sites (HTML/CSS/JS on Vercel, GitHub Pages, Netlify) to production without the recurring bug classes: stale layouts, asset-provenance traps, unversioned cache, and functional-but-unpresented UI.

## Deploy mechanism — verify, don't assume

- A pushed commit is NOT proof of deployment. Determine how the project actually deploys: Vercel CLI (`vercel --prod`), git integration (auto-deploy on push), or Pages. Check `.vercel/project.json`, `.vercel/README.txt`, run `vercel ls <project>`.
- If the deploy is CLI-driven, `git push` alone leaves production stale. Run the CLI deploy, confirm `vercel ls` shows Ready, then HTTP-probe the live domain.
- The CLI may live outside PATH (e.g. `~/.npm-global/bin/vercel`) — locate it before assuming it is absent.

## Asset provenance — one source of truth

- Declare one build-source directory (e.g. `assets/`). Every other directory (`mats/`, `logos/`, `vers/`, `opt/`) is reference-only / quarantined by definition. QA verifies builds reference zero files outside the source dir.
- Watch for traps: `.png` files that are actually JPEG-encoded (RGB, zero alpha, baked checkerboard), and "masters" with baked dark/light checkerboard layers. Verify with `file`, hash comparison, and alpha-channel inspection (RGBA, corners alpha=0).
- Maintain `MANIFEST.sha256` written at build time; QA diffs against it instead of hunting provenance after the fact.
- When a source master is corrupt, the cleanest source may be the user's original upload — never surgery on a corrupt master.

## Cache-busting — version ALL asset refs, not just images

- CDNs serve `cache-control: max-age` TTLs; unversioned CSS/JS served against new HTML produces stale-layout bugs (run-on text, missing rules, broken spacing) for up to the TTL. This class of bug ships as "user sees something broken that is not broken in source."
- Every layout-carrying asset reference in production HTML gets a version param: `/system.css?v=<deploy-sha>`. Images too. Bump per deploy.
- Verify through a cache-buster (`?cb=<deploy-sha>` on your own curls/fetches) so "stale bytes vs live bytes" disputes never happen. But production refs must carry the version themselves — users' browsers never run cache-busters.

## Staging-first review gate + environment separation

User directive ({CLIENT}, 2026-08): **every new version deploys to a staging subdomain and waits for user review before anything touches the main site.** The main site only receives what the user explicitly approved. No direct-to-main, ever — a single unauthorized `vercel --prod` to live (an intentional-looking but unreviewed push) caused an entire incident round. Deploy-target lock: no deploy runs without an explicit target and (where possible) a second agent's confirmation.

- The staging domain is often a **separate Vercel project**, not the same project's preview channel. `vercel --prod` from a repo linked to the production project deploys to PRODUCTION, not staging. Deploy staging with an explicit project: `vercel --prod --project <staging-project>`. Verify which project serves which domain (`vercel project ls`, `.vercel/project.json`) before running any deploy.
- Env vars are scoped per project and per environment. A key added to `production` does NOT exist in the staging project — staging serverless functions return 503 "Assistant not configured" until `vercel env add <KEY> staging` runs.
- Record what each environment's baseline *contains*, not just which commit it is at: swapping environments reverted two already-approved fixes (click-split, Enter contrast) and shipped a click bug a third time. The swap must re-verify approved fixes are still present in the new baseline.

## Served bytes are the truth; screenshots are user reality

Recurring across this project: a fix verified in local source repeatedly shipped as broken on the served surface, and every "verified fixed" claim that was contradicted by the user's screenshot turned out to be a stale read, a wrong-project deploy, or a cache artifact — the served bytes and user screenshots were right every time the local-source read was wrong.

- Any claim about a served value is only valid from a **cache-busted fetch of the current versioned ref** (`?cb=` on your curl) — not from local files, not from a plain fetch that a CDN may have cached.
- When the user reports a regression, reproduce it against the LIVE served URL before rebuilding — two earlier "terminal missing" fixes were dispatched against stale screenshots when the current build already matched the user's words.
- `git checkout <sha> -- .` restores tracked files but does NOT remove files that exist at HEAD but not in the target tree (e.g. an `api/` dir added after the target commit). For a clean rollback: `git rm -r --cached <dir>` + `rm -rf` it, then deploy — otherwise the old surface keeps serving (the "rollback landed" claim was false until the orphaned file was actually deleted).

## Flagship visibility: visible by default, JS only enhances

A `no-js` flash-guard class that hides the terminal until JS removes it is an inverted dependency: if the class-removal loses the race (script deferred, init racing the component load), the flagship stays invisible forever — "container missing" on a page where the markup is present. Fix: serve the HTML without the hiding class and without the `.no-js .term{opacity:0}` rule. The terminal renders visible on first paint; JS only adds behavior (auto-type, commands, LLM). Never gate critical UI on a JS runtime step the user's browser can lose.

## Single-file bundle deploys (esbuild → static host) — served-vs-source drift

When a page imports one bundled JS file (`dist/bundle.js`) and you deploy by pushing to a static host (GitHub Pages, Netlify), a distinct bug class appears: the page the user loads is NOT the code you tested. Recurring failure sequence (observed repeatedly in the {CLIENT} demo):

1. `dist/` in `.gitignore` → the bundle is never pushed → the page imports a 404 or an old cached file → "nothing works, buttons do nothing."
2. Source edited + committed, but the bundle NOT rebuilt → served bundle lacks methods the new page calls → `TypeError: getAccuracy is not a function` on game end → hard freeze.
3. `demo.html` and `bundle.js` committed non-atomically → page references a new API, bundle is old → same class of crash.
4. Browser cache serves the old bundle despite repeated "hard refresh" instructions → user stuck on a broken screen while the team says "hard refresh" for the fourth time.
5. Temp fixes (e.g. a "ghost note" injected to make the first ring visible) persist after the real fix lands and pollute user-visible content.

Discipline:

- Keep `dist/` OUT of `.gitignore` when the page imports the bundle from it, or point the page at a committed build artifact. Verify with `git ls-files dist/`.
- Rebuild the bundle in the SAME step as committing the page: `esbuild src/index.ts --bundle --outfile=dist/bundle.js` then `git add -A && git commit && git push`.
- Version the bundle import (`bundle.js?v=N`, bump per deploy) and add `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">`. Without a cache-buster, "hard refresh" eventually fails as a remedy.
- Before ever telling the user "fixed — hard refresh," VERIFY THE SERVED ARTIFACT:
  `curl -sL <live-url>/dist/bundle.js | grep -c "methodName"` and `curl -sL <live-url>/demo.html | grep -c "expectedMarker"`. If the live bundle lacks the method, the fix is NOT deployed — do not claim it is.
- The host CDN lags 1–3 minutes after push; `?v=N` on your own curl defeats your own cache, not the CDN's.
- When a temp workaround exists, track it and delete it the moment the real fix lands (the ghost-note spacebar polluted user content for multiple rounds).

See `references/bundle-deploy-case-study.md` for the full {CLIENT} sequence and the concrete curl verification recipe.

## GitHub Pages repo-subpath — the absolute-path 404 class

A page served from a Pages **project repo** loads at a subpath: `https://<user>.github.io/<repo>/demo/`, not the site root. Any **absolute** asset/fetch path in the page — `fetch("/demo/words.json")`, `img.src = "/" + path` — resolves against the site root and 404s on the live subpath:

- `fetch("/demo/words.json")` → `<user>.github.io/demo/words.json` → 404 → no word pool, no battle content, page half-dead.
- It works fine in local preview (`http://127.0.0.1:PORT/demo/`) — which is exactly how it ships. The 404 only appears on the live subpath.

Rule:
- Use **relative** paths (`fetch("words.json")` with the file next to the page) or a base-path-aware helper, not absolute. Mirror whatever the existing vendor script tag uses.
- The verification gate must probe the **live-served subpath URL's** fetch, not the local page: `curl -sL https://<user>.github.io/<repo>/demo/ | grep` for the marker, and hit the fetched resource at its repo-subpath URL. A local 200 proves nothing.
- Sweep the whole page for a single absolute path among otherwise-relative ones — the odd one out is the leak (grep `src="`/`fetch("` for leading `/`).

## Presentation pass — functional is not presentable

- An interactive component that works but skipped its presentation pass ships as "weird text": raw scaffold copy, cryptic tokens, unstyled hints, em-dash CLI flags (`—help` instead of `--help`).
- Before shipping any flagship UI: device chrome (frame, header bar, glow edge), styled affordances (muted hint lines, command chips), full labels over abbreviations, and an honesty guard for demos ("we map this to your actual situation") so demonstrations never fake a diagnosis.
- QA gate item: "no raw/unstyled scaffold copy visible in served DOM."

## Flair that earns trust (not decoration)

- Interactive proof-of-capability beats decorative motion: a parameter-driven responder (user types `/build supply chain`, terminal maps to an engagement path from a client-side lookup table) reads as capability; a canned script reads as decoration.
- Constraints: pure client-side (zero network), `prefers-reduced-motion` aware, gated off mobile (`innerWidth<=820` early-return + `defer`), no fabricated precision — real numbers only from the user, else capability language.
- Perf: gating JS to desktop is not just CSS-hiding. A script that parses/runs on mobile costs Lighthouse points even when invisible — early-return before it runs.

### Terminal-as-chatbot (LLM in the flagship)

- **Interaction split:** the click surface and the typing surface are different contracts. A whole panel wrapped in one `<a>` makes terminal clicks navigate — stopPropagation + focus() on the terminal, and only a styled "Enter" anchor navigates. Verify the click in a live browser (pathname stays, input focused), not just in the markup.
- **Slash vs raw dispatch:** input starting with `/` stays client-side (nav/mailto/tel commands, zero network); anything else POSTs to the serverless function. Slash path keeps working if the LLM endpoint dies.
- **Command map as data:** one array of `{cmds:[...], action, target}` drives BOTH dispatch and `/help` output — no drift between what works and what's documented. Aliases group to one branch.
- **Key hygiene:** the LLM API key lives in a serverless env var (production AND staging scopes, separately), never in repo or client JS. A key posted in chat is treated as exposed — rotation recommended before real traffic, even for free tiers.
- **System prompt pitfalls:** an unconditional trailing instruction ("end every answer with X") makes the model repeat X on EVERY reply — the "scheduled: intro call" spam. Make such lines conditional on expressed intent. Contact details (email/phone) belong in the prompt verbatim so the assistant can answer them; keep the honesty guard (showcase assistant, not the firm; no advice/quotes/fabricated credentials).
- **The command set grows; so must the affordance copy.** When nav commands, easter eggs, and aliases are added, `/help` and the hint line must render from the same data — a command that works but isn't discoverable is a drift bug.

## Custom domain / subdomain binding (GitHub Pages)

To serve a Pages site at a branded subdomain (e.g. `{CLIENT}` beside `acctraining.{CLIENT}`), two halves must both land — GitHub binds the domain, DNS must resolve it to the Pages IPs. They are separate systems; only the GitHub half is scriptable from the agent.

**GitHub half (agent-doable via `gh`):**
1. Commit a `CNAME` file at repo root containing the bare domain (`{CLIENT}\n`).
2. Set the Pages custom domain via API:
   `gh api -X PUT repos/OWNER/REPO/pages -f cname="{CLIENT}"`
3. Read back to confirm: `gh api repos/OWNER/REPO/pages` → expect `"cname":"{CLIENT}"`, `"status":"building"`.

**DNS half (external gate — Cloudflare dashboard or a CF API token the agent may not have):**
- CNAME `{CLIENT}` → `{RELATIONSHIP}.github.io`, proxy on (orange cloud, same as the existing `acctraining` record). The site will NOT serve until DNS resolves; GitHub shows `pending_domain_unverified_at` until then.
- Verify propagation: `dig +short {CLIENT}` then `curl -sI https://{CLIENT}`.

**GOTCHA:** the agent often has full GitHub access (`gh` authed) but zero Cloudflare credentials — the GitHub half "succeeds" (cname set, build running) while the domain still 404s. Report the GH side as done, hand the DNS record to the user as a one-line dashboard action, and don't claim the URL is live until curl 200s. Check for stored CF tokens (env, wrangler config, .env.local) BEFORE starting; don't assume you can do both halves.

**Local DNS negative-cache trap:** a brand-new subdomain that was previously NXDOMAIN can be held in the OS resolver's negative cache — `dig +short` resolves to the Cloudflare edge (172.64.x) and `curl --resolve sub.domain:443:<ip>` returns 200, but the browser/urllib on that machine gets HTTP 000 and "still broken". This is NOT a deployment bug; do not chase it as one. Flush `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder` (needs sudo — never ask the user to paste a password into chat) or wait for TTL expiry. Verify the live edge with `dig` + `curl --resolve`, not the local resolver.

**One owner per subdomain — settle before the user touches DNS.** If two deploy paths get stood up in parallel for the same subdomain (a Vercel project AND GitHub Pages, as happened with {CLIENT}), you will hand the user two conflicting CNAME records (`cname.vercel-dns.com` vs `{RELATIONSHIP}.github.io`) — whichever they add, the deploy looks broken, and the goodwill loss is the real cost. Resolve ownership FIRST: public/fork-target repos → GitHub Pages (CNAME → `{RELATIONSHIP}.github.io`, no TXT); private repos → Vercel (`cname.vercel-dns.com` + a `_vercel` TXT). Delete the losing project / detach its domain BEFORE the user adds any record, then hand them exactly one CNAME line.

## Headless sim ≠ real browser (interactive UI gate)

An automated/simulated-DOM test passing is NOT evidence that interactive UI works for a real user. Recurring, verified across multiple sessions of {CLIENT}: an "autofight" sim drove the game to "VICTORY" headless, yet real browser input dead-broke at the user's first test ("game no longer registers key presses at all").

Why sims lie for interactive UI:
- A fixed-cadence sim types on an interval, not to the beat — it exercises the `stale` path, never the `late correct key` path, and trips timing-early-guard swallows that a human never hits. The bug only lives on the path the sim never takes.
- Session lifecycle (destroy → recreate per round) and event-listener wiring behave differently with a real DOM, real focus, and real autoplay/user-gesture policy than in a stubbed DOM. A sim can't see focus loss, doubled listeners, or a dead judge.
- "Verified headless, full VICTORY" is the announce-and-hope trap wearing a lab coat.

Rule: for any interactive web game/tool, the acceptance gate is the **served page a real child/user interacts with**. Verify real key presses through a full round in the actual deployed surface before reporting. Profile one realistic user path the sim can't reach (e.g. rest mid-word, slow late keystroke) and trace it by hand. Do not claim "works" from a sim; the sim is a smoke test, not a sign-off.

## QA gate (binding)

- One primary CTA per surface; verify hrefs actually differ (duplicate-mailto CTA is a QA slip).
- Mobile Lighthouse ≥80 against the live deploy, not local files.
- Real mobile emulation pass (390px screenshots per surface).
- Desktop-width visual regression (axis agreement: layout direction must match background-gradient direction, or text lands on the wrong contrast half).
- Like-for-like screenshot comparison vs reference sites at fixed viewports (1440px + 390px).
- Container symmetry is measured on the CONTENT axis, not the frame: "same size" between two sibling pages means matching rendered width/height and structure (extra wrapping on one page changes computed size even with the same class). Unify the section structure, not just the class.

## Design-tone contract: "sleek" is weight/register, not family-shopping

When a user says a font/button "isn't sleek / looks thick / doesn't fit the tone", the signal is almost always **weight and register**, not a missing font family. Four-attempt loop that cost a full round: Geist Mono → Manrope 700 (user: "you chose a thick font") → Space Grotesk 500 (landed). The fix was dropping to weight 500, not a new family. Standing rule for this user's Digital division: sleek = weight 500–600 geometric sans with light tracking; not bold, not mono, not heavy. Before swapping families, re-read the complaint as a weight/register request.

## Shared components beat copy-paste mounts

A component mounted in two places must be ONE implementation with config (theme, command set, intro), not two copies. Copies drift: one gets fixed, the other ships the old bug (terminal wiring, click-split, no-js class all recurred after duplication). Data-driven config also makes "command works but help doesn't list it" structurally impossible.

## References

- `references/vtracer-svg-pipeline.md` — PNG→SVG vectorization recipe (verified working).
- `references/bundle-deploy-case-study.md` — esbuild bundle deploy case study + curl verification recipe.
