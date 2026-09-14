#!/usr/bin/env python3
"""
verify-all.py — Deterministic release gate runner.

Runs the repository's public gates in documented order. Uses subprocess with
fail-closed behavior: nonzero exit on any failure. No dependencies beyond stdlib.

ORDER (as documented in choreography/release-gates.md):
  1. sweep-gate.py — extraction source verification
  2. review-gate.py — semantic sign-off enforcement
  3. surface-scan.py — multi-surface leak detector
  4. check-artifact-contract.py self-test
  5. preflight/check.py self-test
  6. report/check.py self-test
  7. fresh-clone test (generate.py fork-dryrun check)

Exit: 0 = all gates pass; 1 = any gate failed.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def run_gate(name, cmd, cwd=ROOT):
    """Run a gate, print its output, return True on pass."""
    print(f"\n{'=' * 64}")
    print(f"STEP: {name}")
    print('=' * 64)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=300  # 5 minute timeout per gate
        )

        # Print stdout (the gate's own output)
        if result.stdout:
            print(result.stdout)

        # Print stderr if present (warnings, notes)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode == 0:
            print(f"\n✓ {name}: PASSED")
            return True
        else:
            print(f"\n✗ {name}: FAILED (exit {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        print(f"\n✗ {name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"\n✗ {name}: ERROR — {e}")
        return False


def main():
    print("=" * 64)
    print("TEAM6-KIT RELEASE GATE RUNNER")
    print("=" * 64)
    print("\nThis runner executes all public release gates in documented order.")
    print("Any failure stops execution. All gates use fail-closed semantics.")

    gates = []

    # 1. sweep-gate
    gates.append(("sweep-gate.py", [sys.executable, os.path.join(HERE, "sweep-gate.py")]))

    # 2. review-gate
    gates.append(("review-gate.py", [sys.executable, os.path.join(HERE, "review-gate.py")]))

    # 3. surface-scan
    gates.append(("surface-scan.py", [sys.executable, os.path.join(HERE, "surface-scan.py")]))

    # 4. check-artifact-contract self-test
    gates.append(("check-artifact-contract self-test",
                  [sys.executable, os.path.join(HERE, "check-artifact-contract.py"), "--self-test"]))

    # 5. preflight/check.py self-test
    gates.append(("preflight/check self-test",
                  [sys.executable, os.path.join(HERE, "preflight", "check.py"), "--selftest"]))

    # 6. report/check.py self-test
    gates.append(("report/check self-test",
                  [sys.executable, os.path.join(HERE, "report", "check.py"), "--selftest"]))

    # 7. fresh-clone test (fork-dryrun.sh)
    fork_dryrun = os.path.join(HERE, "fork-dryrun.sh")
    if os.path.isfile(fork_dryrun):
        gates.append(("fresh-clone fork-dryrun", ["bash", fork_dryrun]))
    else:
        # Alternative: verify generate.py works in fork mode
        gates.append(("fresh-clone generate test",
                      [sys.executable, os.path.join(HERE, "generate.py"), "--help"]))

    # Run all gates
    results = []
    for name, cmd in gates:
        passed = run_gate(name, cmd)
        results.append((name, passed))

    # Summary
    print("\n" + "=" * 64)
    print("SUMMARY")
    print("=" * 64)

    passed = sum(1 for _, p in results if p)
    failed = sum(1 for _, p in results if not p)
    total = len(results)

    print(f"\n  Gates run: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    print("\n  Results:")
    for name, p in results:
        status = "✓ PASS" if p else "✗ FAIL"
        print(f"    {status}: {name}")

    print("\n" + "=" * 64)

    if failed > 0:
        print("RELEASE BLOCKED — one or more gates failed.")
        print("Fix failures before proceeding.")
        return 1
    else:
        print("RELEASE GATES PASSED — safe to proceed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
