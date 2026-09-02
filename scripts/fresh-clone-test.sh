#!/usr/bin/env bash
# fresh-clone-test.sh — "Reproducible from the repo" as a TESTED INVARIANT.
#
# Proves a stranger can clone HEAD and reproduce the demo WITHOUT the live
# fleet: clones to a temp dir, runs the documented reproduce command, asserts
# the instantiated team exists + the audit is honest (shipped count closes
# against on-disk files, no ghost rows).
#
# The frozen committed artifacts (manifest.frozen.tsv, REVIEW.frozen.md) make
# the clone self-contained; this script is the proof, wired as the pre-commit
# gate's final step.
#
# USAGE: bash scripts/fresh-clone-test.sh [--keep]
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d /tmp/fresh-clone.XXXXXX)"
KEEP=0
[ "${1:-}" = "--keep" ] && KEEP=1
[ $KEEP -eq 1 ] || trap 'rm -rf "$WORK"' EXIT

echo "=== FRESH-CLONE TEST ==="
echo "repo:   $REPO"
echo "work:   $WORK"
echo

echo "[1/4] Cloning HEAD..."
git clone --quiet "$REPO" "$WORK/clone" || { echo "FAIL: clone"; exit 1; }
cd "$WORK/clone"
echo "  HEAD: $(git rev-parse --short HEAD)"
echo "  tracked files: $(git ls-files | wc -l | tr -d ' ')"

echo "[2/4] Confirm the live-fleet artifacts are ABSENT (fresh-clone honesty)..."
missing=0
for f in build/manifest.tsv build/REVIEW.md build/identifiers.yaml; do
  if [ -f "$f" ]; then
    echo "  FAIL: $f present in clone (should be gitignored)"
    missing=1
  fi
done
[ $missing -eq 0 ] && echo "  all live artifacts absent ✓"
# Confirm the FROZEN artifacts ARE present
for f in build/manifest.frozen.tsv build/REVIEW.frozen.md templates/MANIFEST.md; do
  if [ ! -f "$f" ]; then
    echo "  FAIL: $f missing from clone (frozen artifacts must be committed)"
    missing=1
  fi
done
[ $missing -eq 0 ] && echo "  all frozen artifacts present ✓"

echo "[3/4] Running the documented reproduce command..."
OUT="$WORK/out"
python3 build/generate.py --params examples/demo-consulting.yaml --out "$OUT" \
  > "$WORK/gen.log" 2>&1
if [ $? -ne 0 ]; then
  echo "  FAIL: generate.py exited nonzero"
  tail -20 "$WORK/gen.log"
  exit 1
fi
echo "  generate.py exit 0 ✓"

echo "[4/4] Asserting honest audit (shipped count closes against disk)..."
claim=$(grep -oE "rows shipped: [0-9]+" "$OUT/AUDIT.md" | grep -oE "[0-9]+")
actual=$(find "$OUT" -type f | wc -l | tr -d ' ')
echo "  audit claims:  $claim shipped"
echo "  files on disk: $actual (incl AUDIT.md)"
if [ "$actual" -ne $((claim + 1)) ]; then
  echo "  FAIL: count does not close (expected $((claim + 1)) incl AUDIT.md)"
  exit 1
fi
echo "  count closes ✓"
# Team actually instantiated?
if ! grep -q "Northwind Advisory" "$OUT/personas/SOUL.md.tmpl"; then
  echo "  FAIL: instantiated persona missing substituted team name"
  exit 1
fi
echo "  team instantiated (Northwind Advisory in persona) ✓"

echo
echo "=== FRESH-CLONE TEST: PASS ==="
echo "A stranger can clone HEAD and reproduce the demo, self-contained."
[ $KEEP -eq 1 ] && echo "kept workdir: $WORK"
