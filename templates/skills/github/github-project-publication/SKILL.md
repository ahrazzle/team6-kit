<!-- GENERICIZED: 2×{CLIENT}, 1×{RELATIONSHIP} | source: skills/github/github-project-publication/SKILL.md -->
---
name: github-project-publication
description: "Publish a project workspace to GitHub as a repo + Pages."
version: 1.0.0
author: {RELATIONSHIP} (curator-managed)
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Repositories, Git, Pages, gh-cli, Publication, Project]
    related_skills: [github-auth, github-repo-management]
---

# GitHub Project Publication

Publish an existing project workspace to GitHub as a repository (and, for
static sites, a live Pages URL). Complements the bundled `github-auth`
(authentication) and `github-repo-management` (repo CRUD) skills — this one
owns the WORKFLOW for taking the user's project folder and turning it into a
verified GitHub presence, with the user's conventions baked in.

## When to use

- "put up project X", "upload X to GitHub", "make a repo for X", "publish the site"

## Workflow

1. **Auth check** — `gh auth status`. If not authenticated, use the device
   flow per `github-auth`; if its hosts.yml write goes wrong, recover per
   `references/auth-hosts-yml-recovery.md` (do NOT re-run the flow).

2. **Locate the active workspace and read the project's rules first.**
   Check for `AGENTS.md` / `IDEA.md` in the workspace root — they often
   declare which paths are active work and which are user backups. This is a
   real trap: {CLIENT}'s AGENTS.md said "Do NOT touch ../vers/ (user version
   backups)" — the repo must be built from the ACTIVE workspace only.

3. **Exclude user backup folders.** `vers/`, `*.bak`, `~1~`, numbered
   snapshots are user-made backups — never commit them. Committing them
   pushes stale duplicates and violates the project's own conventions.

4. **Confirm visibility + scope before pushing** (use the clarify form).
   If the user doesn't answer: client-facing material → default **private**;
   personal deliverables → **public** is fine. State the default you picked
   and how to flip it. Note: free GitHub Pages requires a PUBLIC repo.

5. **Init, commit, create, push in one shot** (per-commit identity avoids
   depending on global git config being set):

```bash
cd <active-workspace>
git init -b main
printf '.DS_Store\n__pycache__/\n*.pyc\n' > .gitignore
git add -A
git -c user.name="$GH_USER" -c user.email="<email>" commit -m "<describe the project>"
gh repo create <repo-name> --private|--public --source=. --push
```

6. **Verify — do not trust the push output alone:**

```bash
git status -sb                                   # should show tracking origin/main
gh repo view OWNER/REPO --json name,visibility,url
git ls-files | wc -l                             # confirms what actually got committed
```

7. **Static sites → enable Pages** (public repos only) and verify with a real
   HTTP check, not just the API status:

```bash
gh api -X POST repos/OWNER/REPO/pages -f "source[branch]=main" -f "source[path]=/"
# status goes "building" -> poll until "built" (~40s)
gh api repos/OWNER/REPO/pages --jq '.status'
curl -s -o /dev/null -w "%{http_code}" https://OWNER.github.io/REPO/   # expect 200
```

## Pitfalls

- **Backup folders are off-limits.** Read AGENTS.md/IDEA.md before deciding
  what to commit; the project's own rules are the source of truth.
- **Pages requires public.** Private repo + Pages is a contradiction; offer
  the tradeoff instead of silently failing.
- **Push success ≠ repo correct.** Always re-verify with `gh repo view` and
  the tracked-file count.
- **Pages "building" is not done.** Poll to "built", then curl the live URL.
- **Non-static repos: don't force Pages — serve a landing page instead.** Source monorepos whose interactive pages need a build step or cross-origin-isolation headers (Vite + `SharedArrayBuffer`, WASM, COI/COEP) cannot run on GitHub Pages — a redirect to the app renders blank/broken. Publish a clean static `index.html` at repo root (project summary + link to source + local run instructions) and let the repo itself be the deliverable (Vibetrade).
- **GH Pages subpath breaks absolute URLs** — project Pages serve under
  `https://<user>.github.io/<repo>/`, so an absolute fetch like
  `/demo/words.json` resolves to `<user>.github.io/demo/words.json` → 404.
  All internal URLs must be RELATIVE to the page (`fetch("words.json")` with
  the file next to `index.html`), which resolves correctly at server root
  AND under the repo subpath. This bug passes local preview and only appears
  on the live subpath — probe the served URL's fetches, not just the local
  page ({CLIENT} hit this class twice).
- **License-excluded assets must be gitignored BEFORE the first push** (see
  `licensed-asset-reuse`): files whose attribution is unfillable (e.g.
  CC-BY-SA with no surviving composer credit) must NEVER enter git history —
  a file that never exists in history can't be resurrected by force-push.
  Ship the license boundary visibly: root `LICENSE` (your code), per-layer
  `LICENSE` + ATTRIBUTION.md (third-party assets), and run a pre-push audit
  (excluded-file sweep + ledger-vs-disk diff) before `gh repo create`.

## References

- `references/auth-hosts-yml-recovery.md` — recover when the gh device flow
  writes a malformed `~/.config/gh/hosts.yml` (token stays recoverable from
  the file; no re-auth needed).
- `references/licensed-asset-reuse.md` — the asset-layer island pattern:
  CC-BY-SA layer beside MIT code, manifest-as-only-provenance-point,
  unfillable-attribution exclusion, `.gitignore`-first ordering, public-repo
  license boundary.
