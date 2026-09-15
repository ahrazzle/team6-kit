#!/usr/bin/env python3
"""
check-unique-headings.py — Detect duplicate section headings in markdown files.

Usage:
    python3 build/check-unique-headings.py [file1.md file2.md ...]

If no files are given, scans choreography/ and README.md by default.

Exit codes:
    0 — No duplicate headings found
    1 — One or more duplicate headings found (prints each duplicate with file, heading text, and line numbers)
"""

import os
import re
import sys

# Default files to scan if none provided
DEFAULT_FILES = [
    "README.md",
    "choreography/open-source-contribution.md",
    "choreography/orchestration.md",
    "choreography/self-improving-flywheel.md",
]


def find_headings(filepath):
    """
    Find all markdown headings in a file.
    Returns a list of (line_number, heading_text) tuples.
    """
    headings = []
    pattern = re.compile(r'^(#{1,6}) (.+)$')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                match = pattern.match(line.strip())
                if match:
                    heading_text = match.group(2).strip()
                    headings.append((line_num, heading_text))
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return None

    return headings


def check_file(filepath):
    """
    Check a single file for duplicate headings.
    Returns list of (heading_text, [line_numbers]) for duplicates.
    """
    headings = find_headings(filepath)
    if headings is None:
        return []

    # Group by heading text
    heading_to_lines = {}
    for line_num, heading_text in headings:
        if heading_text not in heading_to_lines:
            heading_to_lines[heading_text] = []
        heading_to_lines[heading_text].append(line_num)

    # Find duplicates
    duplicates = []
    for heading_text, line_nums in heading_to_lines.items():
        if len(line_nums) > 1:
            duplicates.append((heading_text, line_nums))

    return duplicates


def main():
    files = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_FILES

    all_duplicates = {}
    has_errors = False

    for filepath in files:
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} does not exist, skipping", file=sys.stderr)
            continue

        duplicates = check_file(filepath)
        if duplicates:
            all_duplicates[filepath] = duplicates

    if all_duplicates:
        for filepath, duplicates in all_duplicates.items():
            print(f"\n{filepath}:")
            for heading_text, line_nums in duplicates:
                line_str = ", ".join(str(n) for n in line_nums)
                print(f"  Line {line_str}: {heading_text}")

        print("\n" + "=" * 64)
        print(f"Duplicate headings found in {len(all_duplicates)} file(s)")
        print("=" * 64)
        return 1

    print("All checked files have unique headings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
