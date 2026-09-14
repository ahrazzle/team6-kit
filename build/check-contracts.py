#!/usr/bin/env python3
"""
check-contracts.py — aggregator for contract-validator self-tests.

Runs each validator's self-test in sequence, capturing output and reporting
one [ok] or [FAIL] per step. Exits 0 iff all pass. No network, credentials,
or writes. This is used as step 5 in the fresh-clone gate to verify the
working tree's validators are operational.
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
        ("build/check-artifact-contract.py --self-test", "artifact-contract validator"),
        ("build/check-artifact-contract.py --example-check", "artifact-contract examples"),
        ("build/preflight/check.py --selftest", "preflight validator"),
        ("build/report/check.py --selftest", "report validator"),
    ]

    all_passed = True
    for cmd, desc in steps:
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

            if result.returncode == 0:
                print(f"[ok] {desc}")
            else:
                print(f"[FAIL] {desc} (exit {result.returncode})")
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
