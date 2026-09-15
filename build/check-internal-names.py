#!/usr/bin/env python3
"""
check-internal-names.py — Gate for internal agent names and paths in public surfaces.

Scans public surfaces for internal agent names and home-path patterns (/Users/, /home/).
Fails on any hit.

Usage: python3 build/check-internal-names.py [path/to/repo]
Default: current directory
Exit: 0 = clean; 1 = leaks found
"""

import os
import re
import sys

# Internal agent names to block (role labels are OK)
INTERNAL_NAMES = [
    'lugia',
    'azaraki',
    'kodekoot',
    'shayba',
    'halakukhan',
]

# Home-path patterns to block
HOME_PATHS = [
    '/Users/',
    '/home/',
]

# Public surfaces to scan
PUBLIC_SURFACES = [
    'README.md',
    'CHANGELOG.md',
    'choreography/',
    'templates/',
    'build/',
    'tests/',
]


def scan_file(path, pattern):
    """Scan a file for pattern matches. Return list of (line_num, line) tuples."""
    matches = []
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                if pattern.search(line):
                    matches.append((i, line.rstrip()))
    except (IOError, OSError):
        pass
    return matches


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    leaks = []
    
    for surface in PUBLIC_SURFACES:
        surface_path = os.path.join(repo, surface)
        if not os.path.exists(surface_path):
            continue
        
        if os.path.isdir(surface_path):
            # Scan all .md and .py files in the directory
            for root, dirs, files in os.walk(surface_path):
                for fname in files:
                    if fname.endswith('.md') or fname.endswith('.py'):
                        fpath = os.path.join(root, fname)
                        for name in INTERNAL_NAMES:
                            pattern = re.compile(re.escape(name), re.IGNORECASE)
                            for line_num, line in scan_file(fpath, pattern):
                                leaks.append((fpath, line_num, line, f'INTERNAL NAME: {name}'))
                        for path_pat in HOME_PATHS:
                            pattern = re.compile(re.escape(path_pat))
                            for line_num, line in scan_file(fpath, pattern):
                                leaks.append((fpath, line_num, line, f'HOMEPATH: {path_pat}'))
        else:
            # Scan the file directly
            for name in INTERNAL_NAMES:
                pattern = re.compile(re.escape(name), re.IGNORECASE)
                for line_num, line in scan_file(surface_path, pattern):
                    leaks.append((surface_path, line_num, line, f'INTERNAL NAME: {name}'))
            for path_pat in HOME_PATHS:
                pattern = re.compile(re.escape(path_pat))
                for line_num, line in scan_file(surface_path, pattern):
                    leaks.append((surface_path, line_num, line, f'HOMEPATH: {path_pat}'))
    
    if leaks:
        print("INTERNAL NAME LEAKS FOUND:")
        for fpath, line_num, line, reason in leaks:
            print(f"  {fpath}:{line_num} {reason}")
            print(f"    {line[:100]}{'...' if len(line) > 100 else ''}")
        print(f"\nTotal leaks: {len(leaks)}")
        return 1
    else:
        print("No internal name leaks found.")
        return 0


if __name__ == '__main__':
    sys.exit(main())
