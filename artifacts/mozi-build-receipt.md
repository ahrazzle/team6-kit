# Mozi Build Receipt — PR #42

## Commit Summary

Final head SHA: `2891597`
Commit history:
1. `319d455` — Fix proofread defects and add internal-name gate
2. `6331f36` — Restore deleted bullets under Routing and Configuration Principles  
3. `4303127` — Restrict check-internal-names to owned files only
4. `91771c1` — Make internal-name gate honest
5. `2891597` — Fix check-internal-names.py to use consistent relative paths

## Acceptance Criteria Verified

- verify-all.py exit code: 0 (all 12 gates pass)
- git grep -nE "Lugia|Azaraki|KodeKoot|Shayba|Halakukhan" -- choreography/ returns nothing
- python3 build/check-internal-names.py exits 0 with baseline

## Gate Results

All 12 gates passed:
- sweep-gate.py
- review-gate.py
- surface-scan.py
- check-artifact-contract self-test
- preflight/check self-test
- report/check self-test
- check-contracts aggregate
- fresh-clone fork-dryrun
- check-unique-headings
- check-internal-names
- review-repair self-test
- review-repair fixtures

## Changes Made

1. Gate scans whole tree (not just 6 files)
2. Removed /Users/ and /home/ from blocklist (generic placeholders)
3. Shipped identifiers.yaml as default blocklist
4. Created internal-names-baseline.yaml for grandfathered paths
5. Fixed governance.md (replaced internal names with role labels)
6. Updated check-internal-names.py to use consistent relative paths

## Baseline Paths (10 files)

- ./index.html
- ./artifacts/mozi-build-receipt.md
- ./templates/skills/github/github-pr-audit/SKILL.md
- ./templates/skills/creative/external-writing-discipline/SKILL.md
- ./templates/skills/autonomous-ai-agents/zero-context-preservation/SKILL.md
- ./build/freeze-manifest.py
- ./build/surface-scan.py
- ./build/review-gate.py
- ./build/freeze-review.py
- ./build/identifiers.yaml

## Fixture Proof

Adding internal name "TestAgent" to temp fixture file causes gate to exit 1.
Test passes: tests/test_internal_names.py::test_internal_name_fails
