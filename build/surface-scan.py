#!/usr/bin/env python3
"""
surface-scan.py — Multi-surface leak detector (Azaraki's surface matrix).

"Clean" means 0 across N surfaces with N DEDICATED detectors, never one
catch-all grep. Each surface is scanned independently so a content-grep can
never masquerade as a filename check, etc.

SURFACES (each with its own detector):
  S1 content        — file bodies (strong terms only, case-insensitive)
  S2 filenames      — directory/file names in the committed tree
  S3 headers        — GENERICIZED provenance headers (source: field)
  S4 script paths   — absolute/machine-specific paths in .py/.sh
  S5 config defaults— DEFAULT_PARAMS / hardcoded defaults in build/
  S6 gitignore      — generated artifacts are excluded, not committed
  S7 reachability   — live third-party integrations a stranger could reach
                      (Shayba's bar: "can a stranger touch our instance?")
  S8 git history    — checked at commit time (this scanner is pre-commit;
                      the fork's first commit runs the same terms via git log)

USAGE
  python3 build/surface-scan.py
    exit 0 = clean across all surfaces; exit 1 = leaks found (list + surface)

Run by sweep-gate.py before assembly and by the fork gate before first commit.
"""

import os
import re
import sys
import subprocess
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import genericize as G

# ---------------------------------------------------------------------------
# Terms — the gate's actual identifier inventory (derived + config)
# ---------------------------------------------------------------------------
def strong_terms():
    """Strong terms only: handles, codenames, user handles, full phrases.
    Excludes single-word splits of phrases (Free, Foundation, Training) that
    are common English words."""
    inst = G._INST
    strong = set()
    for cat in ('team_handles', 'user_handles', 'codename_terms'):
        for t in inst.get(cat, []):
            strong.add(t.strip().strip('"\''))
    for cat in ('venture_names', 'client_names', 'habit_phrases', 'path_markers'):
        for t in inst.get(cat, []):
            t = t.strip().strip('"\'')
            if len(t.split()) >= 2:
                strong.add(t)
    for n in G._ALL_NAMES:
        if len(n.split()) >= 2:
            strong.add(n)
    return {t for t in strong if t and len(t) > 2}


TERMS = strong_terms()

# Reachability surface (S7): live integrations a stranger could reach.
# INSTANCE_SPECIFIC = integrations tied to OUR instance — zero must survive
#   (a reader reaching these reaches our stack). FAIL if found. Loaded from
#   identifiers.yaml (reachable_integrations) — never hardcoded in source.
# GENERIC_SERVICE = public services documented as generic patterns (any user
#   would use them); not our instance. WARN if found (review), never FAIL.
INSTANCE_REACH_TERMS = [
    t for t in G._INST.get("reachable_integrations", []) if t.strip()]
GENERIC_SERVICE_TERMS = [
    "api.unsplash.com", "vercel.app", ".vercel.app", "quran.com",
    "fawazahmed0", "tarteel", "qul.tarteel.ai",
]

# Self-exclusion: the scanner's own term tables and docstring are its source
# of truth, not leaks. It must not flag itself.
SELF_EXCLUDE = {"build/surface-scan.py"}

# Brand allowlist — terms that are the PRODUCT's own intentional name, not
# instance leaks. Shayba's reachability test resolves these: reaching
# "airefea-kit" is reaching the product (a public artifact), never our
# instance. Keep this minimal — it is the ONLY exemption from S1/S2, and
# adding a term here is a branding decision, not a leak fix.
BRAND_ALLOWLIST = {"Airefea", "airefea-kit", "airefea"}


def committed_files():
    """Yield every file git would commit (respects .gitignore)."""
    out = subprocess.run(['git', 'add', '-A', '-n'], capture_output=True,
                         text=True, cwd=ROOT)
    for line in out.stdout.splitlines():
        f = line.strip()
        if not f.startswith("add "):
            continue
        f = f[4:].strip().strip("'")
        if os.path.isfile(os.path.join(ROOT, f)):
            yield f


def scan_surface(name, findings):
    print(f"S{name}: {len(findings)} hit(s)" if findings else f"S{name}: clean")
    for f, t in sorted(findings)[:12]:
        print(f"    {f}: {t}")
    return len(findings)


def main():
    findings = defaultdict(list)

    # S1 content — strong terms in committed file bodies.
    # Word-boundary matching for ALL terms (single AND multi-word) so common
    # English substrings don't false-positive — a client name must not match
    # "registry", "free" must not match "free-tier". Compound code identifiers
    # (hideProjectStats) are NOT this surface's job — genericize's own rules
    # handle those, and S7-reachability covers instance integrations.
    content_re = []
    for t in TERMS:
        content_re.append((t, re.compile(r'\b' + re.escape(t) + r'\b', re.I)))
    for f in committed_files():
        if f in SELF_EXCLUDE:
            continue
        if not f.endswith(('.py', '.sh', '.yaml', '.md', '.txt', '.json',
                           '.html', '.css', '.js', '.tmpl')):
            continue
        low = open(os.path.join(ROOT, f), encoding='utf-8',
                   errors='replace').read()
        for t, rx in content_re:
            if rx.search(low) and t not in BRAND_ALLOWLIST:
                findings['1-content'].append((f, t))

    # S2 filenames — instance tokens in committed path names.
    # Word-boundary matching: "egis" must not match "registry" in a filename.
    fname_re = []
    for t in TERMS:
        fname_re.append((t, re.compile(r'\b' + re.escape(t) + r'\b', re.I)))
    for f in committed_files():
        if f in SELF_EXCLUDE:
            continue
        base = f.rsplit('/', 1)[-1]
        for t, rx in fname_re:
            if rx.search(base) and t not in BRAND_ALLOWLIST:
                findings['2-filenames'].append((f, t))

    # S3 headers — GENERICIZED source: fields.
    # Word-boundary matching (same rationale as S1/S2 — a client name must
    # not match "registry" in a source path).
    header_re = []
    for t in TERMS:
        header_re.append((t, re.compile(r'\b' + re.escape(t) + r'\b', re.I)))
    for f in committed_files():
        if f in SELF_EXCLUDE:
            continue
        if not f.endswith('.md'):
            continue
        low = open(os.path.join(ROOT, f), encoding='utf-8',
                   errors='replace').read()
        for line in low.splitlines():
            if 'source:' in line and any(
                    rx.search(line) for _, rx in header_re):
                findings['3-headers'].append((f, line.strip()[:80]))
                break

    # S4 script paths — absolute machine paths in build/
    for f in committed_files():
        if f in SELF_EXCLUDE:
            continue
        if not f.endswith(('.py', '.sh')):
            continue
        low = open(os.path.join(ROOT, f), encoding='utf-8',
                   errors='replace').read()
        if re.search(r'/Users/[A-Za-z0-9_]+/', low) or 'Documents/ai work' in low:
            findings['4-script-paths'].append((f, 'absolute path'))

    # S5 config defaults — instance names in DEFAULT_* / defaults
    for f in committed_files():
        if f in SELF_EXCLUDE:
            continue
        if not f.endswith('.py'):
            continue
        low = open(os.path.join(ROOT, f), encoding='utf-8',
                   errors='replace').read()
        if 'Airefea Team' in low or 'TEAM_NAME' in low and any(
                t.lower() in low.split('DEFAULT_PARAMS')[-1].lower()[:200]
                for t in TERMS):
            findings['5-config-defaults'].append((f, 'default param'))

    # S6 gitignore — generated artifacts must be excluded
    gi = open(os.path.join(ROOT, '.gitignore')).read()
    for art in ('manifest.tsv', 'manifest.md', 'REVIEW.md', 'dist/',
                'kits/', 'identifiers.yaml'):
        if art not in gi:
            findings['6-gitignore'].append(('.gitignore', f'missing {art}'))

    # S7 reachability — instance-specific integrations (FAIL) vs generic
    # services (WARN, review-only)
    for f in committed_files():
        if f in SELF_EXCLUDE:
            continue
        if not f.endswith(('.md', '.py', '.sh', '.txt', '.html')):
            continue
        low = open(os.path.join(ROOT, f), encoding='utf-8',
                   errors='replace').read().lower()
        for t in INSTANCE_REACH_TERMS:
            if t in low:
                findings['7-reachability'].append((f, t))
        for t in GENERIC_SERVICE_TERMS:
            if t in low:
                findings['7-generic-service'].append((f, t))

    # ---- report ----
    total = 0
    warns = 0
    print("=" * 60)
    print("SURFACE MATRIX — leak scan (N surfaces, N detectors)")
    print("=" * 60)
    for name in sorted(findings.keys()):
        if name == '7-generic-service':
            warns += scan_surface(name + " (WARN)", findings[name])
        else:
            total += scan_surface(name, findings[name])
    # report clean surfaces too
    scanned = {'1-content', '2-filenames', '3-headers', '4-script-paths',
               '5-config-defaults', '6-gitignore', '7-reachability'}
    for s in sorted(scanned - set(findings.keys())):
        print(f"S{s}: clean")
    print("-" * 60)
    if warns:
        print(f"WARN — {warns} generic-service mention(s) (review, not blocking).")
    if total:
        print(f"FAIL — {total} leak(s) across "
              f"{len(set(findings) - {'7-generic-service'})} surface(s).")
        return 1
    print("PASS — 0 instance leaks across all 7 surfaces.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
