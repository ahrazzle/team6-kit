#!/usr/bin/env python3
"""
check-contracts.py — aggregator for contract-validator self-tests.

Runs each validator's self-test in sequence, capturing output and reporting
one [ok] or [FAIL] per step. Exits 0 iff all pass. No network, credentials,
or writes. This is the aggregate contract gate: step 7 in the release runner
(build/verify-all.py) and step 5 in the fresh-clone gate, verifying the
working tree's validators are operational.

Covered contracts: artifact-contract, preflight, report, grouped
scored-rollout (self-test + both fixtures), and the declarative reward
catalogue (self-test + both fixtures). The two new fixtures are asserted to
their expected verdicts: the valid fixture must exit 0 and the invalid
fixture must exit non-zero (so the step names an expected return code).
"""
import os
import subprocess
import sys


def main():
    # Resolve paths from this file's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    os.chdir(repo_root)

    steps = [
        ("build/check-artifact-contract.py --self-test", "artifact-contract validator", 0),
        ("build/check-artifact-contract.py --example-check", "artifact-contract examples", 0),
        ("build/preflight/check.py --selftest", "preflight validator", 0),
        ("build/report/check.py --selftest", "report validator", 0),
        ("build/check-scored-rollout.py --self-test", "scored-rollout contract validator", 0),
        ("build/check-scored-rollout.py --example-check", "scored-rollout contract examples", 0),
        ("build/check-scored-rollout.py examples/scored-rollout-group.valid.jsonl",
         "scored-rollout valid fixture", 0),
        ("build/check-scored-rollout.py examples/scored-rollout-group.invalid.jsonl",
         "scored-rollout invalid fixture (must fail)", 1),
        ("build/check-reward-registry.py --self-test", "reward-registry contract validator", 0),
        ("build/check-reward-registry.py --example-check", "reward-registry contract examples", 0),
        ("build/check-reward-registry.py examples/reward-functions.valid.yaml",
         "reward-registry valid fixture", 0),
        ("build/check-reward-registry.py examples/reward-functions.invalid.yaml",
         "reward-registry invalid fixture (must fail)", 1),
    ]

    all_passed = True
    for cmd, desc, expect in steps:
        print(f"\n=== {desc} ===")
        try:
            result = subprocess.run(
                [sys.executable] + cmd.split(),
                capture_output=True,
                text=True,
                timeout=120,
            )
            output = result.stdout + result.stderr

            # Print the last 15 lines if there's output
            lines = output.splitlines()
            if lines:
                for line in lines[-15:]:
                    print(f"  {line}")

            if result.returncode == expect:
                print(f"[ok] {desc}")
            else:
                print(f"[FAIL] {desc} (exit {result.returncode}, expected {expect})")
                all_passed = False
        except subprocess.TimeoutExpired:
            print(f"[FAIL] {desc} (timeout)")
            all_passed = False
        except Exception as e:
            print(f"[FAIL] {desc} ({e})")
            all_passed = False

    print("\n=== CONTRACT VALIDATOR GATE ===")
    if all_passed:
        print("All self-tests passed.")
        return 0
    else:
        print("One or more self-tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
