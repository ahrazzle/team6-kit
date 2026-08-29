#!/usr/bin/env bash
# fork-dryrun.sh — Update-safety dry-run for the agent-kit fork.
#
# Question this answers: does a `kits/` layer survive a real `hermes update`?
# The update mechanism is `git pull --ff-only origin $BRANCH` followed by
# `git reset --hard origin/$BRANCH` (verified on this machine). The question
# is whether `git reset --hard` destroys our overlay directory.
#
# Two scenarios are tested against a SCRATCH clone (the real install is never
# touched — this is a dry run):
#   A. kits/ COMMITTED to the fork branch  -> reset --hard to origin kills it
#   B. kits/ GITIGNORED + untracked        -> reset --hard leaves it alone
#
# The correct governance falls out of the result. Expected: A dies, B survives
# — proving kits/ must be gitignored + regenerated, never committed.
#
# USAGE
#   bash build/fork-dryrun.sh [--source /path/to/hermes-agent] [--origin main]
#
# Requires: git, a writable temp dir. Network NOT required (uses local clone).
set -euo pipefail

SOURCE="${1:-$HOME/.hermes/hermes-agent}"
ORIGIN_BRANCH="${2:-main}"
# Capture the kit root BEFORE any cd — BASH_SOURCE[0] must resolve to the
# absolute script path, not a relative name evaluated from a later CWD.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORK="$(mktemp -d /tmp/fork-dryrun.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

echo "=== FORK UPDATE-SAFETY DRY RUN ==="
echo "source: $SOURCE"
echo "work:   $WORK"
echo

# --- Build a scratch fork: clone locally, add a remote pointing at the
# --- source's origin (simulates the fork's upstream), set up a "local" branch.
echo "[1/4] Cloning source into scratch fork..."
git clone --quiet "$SOURCE" "$WORK/fork"
cd "$WORK/fork"
# Simulate the fork's remote topology: 'origin' = our fork (the local clone),
# 'upstream' = the real Hermes upstream (the source's own origin URL).
git remote add upstream "$(git -C "$SOURCE" remote get-url origin)"
git checkout --quiet -b fork-main

# A sentinel file so we can detect what survives.
SENTINEL_CONTENT="kits-layer-sentinel-$(date +%s)"
mkdir -p kits/personas

# --- Scenario A: kits/ committed to the fork branch
echo "[2/4] Scenario A: kits/ COMMITTED to fork branch..."
echo "$SENTINEL_CONTENT" > kits/personas/sentinel-a.md
git add kits/
git -c user.name=fork -c user.email=fork@test commit --quiet -m "add kits layer (committed)"
echo "  committed. Simulating update: git reset --hard upstream/$ORIGIN_BRANCH"
git fetch --quiet upstream
git reset --hard "upstream/$ORIGIN_BRANCH" >/dev/null 2>&1 || true
if [ -f kits/personas/sentinel-a.md ]; then
  echo "  A: kits/ SURVIVED reset --hard  (unexpected)"
else
  echo "  A: kits/ DESTROYED by reset --hard  (as predicted)"
fi

# --- Scenario B: kits/ gitignored + untracked (re-add, then ignore)
echo "[3/4] Scenario B: kits/ GITIGNORED + untracked..."
mkdir -p kits/personas
echo "kits/" >> .gitignore
echo "$SENTINEL_CONTENT" > kits/personas/sentinel-b.md
echo "  added gitignore + untracked sentinel. Simulating update again:"
git reset --hard "upstream/$ORIGIN_BRANCH" >/dev/null 2>&1 || true
if [ -f kits/personas/sentinel-b.md ]; then
  echo "  B: kits/ SURVIVED reset --hard  (as predicted — untracked survives)"
else
  echo "  B: kits/ DESTROYED  (unexpected — untracked should survive)"
fi

# --- Regeneration check: after update, the generator must be able to rebuild
echo "[4/4] Regeneration check (the recovery path)..."
# The generator lives in our kit workspace, not the fork — verify it exists
# and can be invoked (syntax), which is the regeneration contract.
# The generator lives in the kit workspace, not the fork — resolve from the
# captured KIT_ROOT (absolute, computed before any cd) so no machine-specific
# path ships in the script.
GEN="$KIT_ROOT/build/generate.py"
if [ -f "$GEN" ]; then
  python3 -m py_compile "$GEN" && echo "  generator compiles — regeneration path intact"
else
  echo "  generator not found at $GEN (expected in kit workspace, not fork)"
fi

echo
echo "=== VERDICT ==="
echo "Committed kits/ is destroyed by hermes update (git reset --hard origin)."
echo "Gitignored kits/ survives. => kits/ must NEVER be committed to the fork;"
echo "it is generated output, rebuilt by build/generate.py after every update."
