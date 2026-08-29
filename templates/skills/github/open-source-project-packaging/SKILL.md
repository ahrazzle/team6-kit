<!-- GENERICIZED: 2×{CLIENT}, 3×{RELATIONSHIP} | source: skills/github/open-source-project-packaging/SKILL.md -->
---
name: open-source-project-packaging
description: "Make a repository fork-ready for open source."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP})
license: MIT
platforms: [linux, macos, windows]
---

# Open-Source Project Packaging

## When to Use

- User asks to "make a repo ready for open source", "everything a good open source project needs", "make it forkable"
- Shipping a handoff package so external teams can build on / contribute to a framework or library
- Final revision pass to a repo before announcing it public

## The Fork-Ready Kit

A repo is genuinely forkable when a stranger can (a) understand it from the README in 5 minutes, (b) build on it, and (c) contribute without guessing. That requires:

1. **LICENSE** — the single biggest gap. READMEs often claim a license with no LICENSE file. A missing license file is a real legal gap: downstream can't legally redistribute. Add the full MIT text (not just a one-liner) and mirror the claim in `package.json` (`"license": "MIT"`).
2. **README.md** — a working quickstart FIRST (clone → build → 5-line bootstrap → react-to-events → cleanup), then an architecture diagram, key concepts, a docs index, and a **Community & Governance** section (issues/features, security, code of conduct, changelog links). Add badges (License, PRs-welcome) near the top. Point the live-demo link at the production URL, not a stale dev URL.
3. **CONTRIBUTING.md** — dev setup, test commands, conventions, PR process. Keep ONE canonical copy (root is the GitHub-surface default); delete `docs/CONTRIBUTING.md` duplicates — root and docs copies diverge.
4. **SECURITY.md** — private reporting path (GitHub Security tab), trust model, response SLA. For a client-side framework, state the trust model explicitly ("plugins are trusted code", "no telemetry / nothing leaves the browser").
5. **CODE_OF_CONDUCT.md** — Contributor Covenant 2.1.
6. **CHANGELOG.md** — Keep-a-Changelog format; an `[Unreleased]` section plus the current release.
7. **Docs-consistency check** — if the repo has one (`npm run docs`), run it after touching docs; it verifies the API reference matches source. Keep it green.

## Pitfalls (paid in blood)

- **README claims a license, no LICENSE file exists.** Always verify the file on disk matches the README/package.json claim; the claim alone isn't a license.
- **Stale internal doc links after a file moves.** When `PLUGIN_DEVELOPMENT.md` became `docs/PLUGIN_GUIDE.md`, links in `API_REFERENCE.md` and `CONTRIBUTING.md` broke. After renaming/moving docs, grep the whole repo for the OLD filename and fix every reference — including ones inside code comments.
- **Duplicate docs that diverge.** root `CONTRIBUTING.md` and `docs/CONTRIBUTING.md` drifted apart. Pick one canonical location (root for CONTRIBUTING) and delete the other.
- **Live URL rot.** The README's "live demo" pointed at the old `{RELATIONSHIP}.github.io` path after a custom domain went live. Grep for the old URL when a deploy target changes.
- **Don't stop at README.** A good README with no LICENSE/SECURITY/CHANGELOG is not fork-ready — the governance files are what let a community form.

## Verification Discipline

Gate the release on a served read-back, not local files:

```bash
# Each new file must be served (HTTP 200) at the raw URL
for f in LICENSE SECURITY.md CHANGELOG.md CODE_OF_CONDUCT.md; do
  echo -n "$f: "; curl -s -o /dev/null -w "%{http_code}" \
    "https://raw.githubusercontent.com/OWNER/REPO/main/$f"; echo
done
# Confirm the README's live link is the production URL
curl -s https://raw.githubusercontent.com/OWNER/REPO/main/README.md | grep -i "<live-url>"
```

## References

- `references/{CLIENT}` — the {CLIENT} repo final revision: exact files added, stale-link fixes, doc-consistency check, commit summary
