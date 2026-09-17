# AntV Infographic Learnings

**[VERIFIED — public conceptual source]**

## Source

- **Project**: AntV Infographic (github.com/antvis/Infographic)
- **License**: MIT
- **Commit studied**: main branch (no specific commit pinned)

## Pattern Adopted

Infographic uses **SSR (Server-Side Rendering) golden examples** as regression guards:

1. **Small, committed fixtures**: Tiny input files that exercise specific rendering paths
2. **Committed expected output**: Golden output files that serve as the truth
3. **Deterministic checks**: A validator compares current output to the golden file
4. **No external dependencies**: The check runs with minimal tooling

Team6 adopts this pattern as a **golden-artifact regression gate**:

- `build/check-golden.py` — A Python stdlib-only validator
- `demo/golden-artifact/` — A minimal fixture pair (input.json, expected.txt)
- Wired into `build/verify-all.py` and `build/check-contracts.py`

## What Team6 Does NOT Copy

- No AntV dependencies (npm, @antv/infographic, etc.)
- No AntV renderer or SSR pipeline
- No AntV fixtures or test data
- No AntV build configuration

Team6 implements a clean, independent Python-only version of the principle.

## Acceptance Evidence

- Gate self-test: 100% pass on committed test cases
- Gate fixture: PASS (expected output matches generated output)
- Surface scan: PASS (no internal paths or identifiers leaked)
- Wired into release runner: Step 1 in `build/verify-all.py`
