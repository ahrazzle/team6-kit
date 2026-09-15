#!/usr/bin/env python3
"""
check-golden.py — dependency-free golden-artifact regression gate.

Inspired by AntV Infographic's SSR golden examples: small, committed inputs
and outputs that prove the renderer behaves correctly without network calls
or external dependencies. This gate uses only Python stdlib.

USAGE
  python3 build/check-golden.py <input.json> <expected.txt>   # validate files
  python3 build/check-golden.py --self-test        # built-in pass/fail

EXIT    0 = valid (or all self-tests behaved)   1 = invalid

The gate:
1. Reads a JSON input fixture
2. Generates deterministic output from it (no model, network, or renderer)
3. Compares generated output to the expected file
4. Prints a useful diff summary on mismatch
5. Exits nonzero on mismatch or when expected is missing
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def generate_output_from_fixture(input_path):
    """
    Generate deterministic output from the input fixture.
    This is a simple, stdlib-only transformation that produces a stable,
    reproducible output suitable for golden testing.
    """
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)
    
    # Deterministic output format: one line per field
    lines = []
    lines.append(f"Agent: {data.get('name', 'unknown')}")
    lines.append(f"Version: {data.get('version', 'unknown')}")
    lines.append(f"Agent count: {data.get('agent_count', 'unknown')}")
    lines.append("Status: verified")
    
    return "\n".join(lines) + "\n"


def compute_diff(expected, actual):
    """
    Compute a simple line-by-line diff for display.
    Returns a list of diff lines.
    """
    expected_lines = expected.rstrip().splitlines()
    actual_lines = actual.rstrip().splitlines()
    
    diff = []
    max_lines = max(len(expected_lines), len(actual_lines))
    
    for i in range(max_lines):
        exp_line = expected_lines[i] if i < len(expected_lines) else ""
        act_line = actual_lines[i] if i < len(actual_lines) else ""
        
        if exp_line != act_line:
            diff.append(f"  Line {i+1}:")
            if exp_line:
                diff.append(f"    EXPECTED: {exp_line}")
            else:
                diff.append(f"    EXPECTED: <none>")
            if act_line:
                diff.append(f"    ACTUAL:   {act_line}")
            else:
                diff.append(f"    ACTUAL:   <none>")
    
    return diff


def validate_golden(input_path, expected_path):
    """
    Run the golden validation.
    Returns (passed, messages) where messages is a list of output lines.
    """
    messages = []
    
    # Check that expected file exists
    if not os.path.isfile(expected_path):
        messages.append(f"ERROR: expected file not found: {expected_path}")
        messages.append("The golden regression gate requires a committed expected file.")
        return False, messages
    
    # Read expected output
    try:
        with open(expected_path, encoding="utf-8") as f:
            expected = f.read()
    except OSError as e:
        messages.append(f"ERROR: cannot read expected file: {e}")
        return False, messages
    
    # Generate actual output from input
    try:
        actual = generate_output_from_fixture(input_path)
    except (OSError, json.JSONDecodeError) as e:
        messages.append(f"ERROR: cannot process input file: {e}")
        return False, messages
    
    # Compare
    if actual == expected:
        messages.append("Golden check PASSED")
        return True, messages
    
    # Mismatch - show diff
    messages.append("Golden check FAILED - output mismatch:")
    diff_lines = compute_diff(expected, actual)
    messages.extend(diff_lines)
    messages.append("")
    messages.append("To fix:")
    messages.append("  1. If the expected file is stale, regenerate and update it")
    messages.append("  2. If the implementation changed, update the golden file")
    
    return False, messages


def self_test():
    """Built-in pass/fail guarantee (no external fixtures required)."""
    print("check-golden — self-test")
    
    cases = []
    
    # Case 1: valid input matches expected
    valid_input = '{"name": "test", "version": "1.0", "agent_count": 2}'
    expected_output = "Agent: test\nVersion: 1.0\nAgent count: 2\nStatus: verified\n"
    cases.append(("valid input matches expected", valid_input, expected_output, True))
    
    # Case 2: input mismatch
    cases.append(("input mismatch fails", valid_input, "different output\n", False))
    
    # Case 3: empty expected fails
    cases.append(("empty expected fails", valid_input, "", False))
    
    passed = failed = 0
    for name, inp, exp, want_ok in cases:
        # Create temp files for this test
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "input.json")
            expected_file = os.path.join(tmpdir, "expected.txt")
            
            with open(input_file, "w") as f:
                f.write(inp)
            with open(expected_file, "w") as f:
                f.write(exp)
            
            passed_test, msgs = validate_golden(input_file, expected_file)
            ok = passed_test == want_ok
            
            mark = "PASS" if ok else "FAIL"
            passed += ok
            failed += not ok
            print(f"  [{mark}] {name}")
            
            if not ok:
                for m in msgs[:3]:
                    print(f"         {m}")
    
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def main():
    args = sys.argv[1:]
    
    if "--self-test" in args:
        return self_test()
    
    if not args or args[0].startswith("-"):
        print(__doc__.strip())
        return 2
    
    if len(args) < 2:
        print("Usage: python3 check-golden.py <input.json> <expected.txt>")
        print("       python3 check-golden.py --self-test")
        return 2
    
    input_path = args[0]
    expected_path = args[1]
    
    passed, messages = validate_golden(input_path, expected_path)
    
    for msg in messages:
        print(msg)
    
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
