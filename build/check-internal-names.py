#!/usr/bin/env python3
"""
check-internal-names.py — Gate for internal agent names in public surfaces.

Scans the whole public tree for internal agent names.
Loads blocklist from build/identifiers.yaml.
Reads baseline from build/internal-names-baseline.yaml.
Fails on any hit outside the baseline or with more hits than baseline.

Usage: python3 build/check-internal-names.py [path/to/repo]
Default: current directory
Exit: 0 = clean; 1 = leaks found
"""

import os
import re
import sys

SCRIPT_NAME = 'check-internal-names.py'
BASELINE_PATH = 'build/internal-names-baseline.yaml'
IDENTIFIERS_PATH = 'build/identifiers.yaml'


def load_blocklist(repo):
    yaml_path = os.path.join(repo, IDENTIFIERS_PATH)
    if not os.path.exists(yaml_path):
        return []
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = f.read()
        # Parse internal_agent_names list manually
        values = []
        in_list = False
        for line in data.splitlines():
            stripped = line.strip()
            if stripped.startswith('#') or not stripped:
                continue
            if stripped.startswith('internal_agent_names:'):
                in_list = True
                continue
            if in_list:
                if stripped.startswith('- '):
                    values.append(stripped[2:].strip())
                elif not stripped.startswith('#'):
                    in_list = False
                    continue
        return values
    except Exception:
        return []


def load_baseline(repo):
    baseline_path = os.path.join(repo, BASELINE_PATH)
    if not os.path.exists(baseline_path):
        return {}
    try:
        with open(baseline_path, 'r', encoding='utf-8') as f:
            data = f.read()
        # Parse key: value pairs manually
        result = {}
        for line in data.splitlines():
            stripped = line.strip()
            if stripped.startswith('#') or not stripped:
                continue
            if ': ' in stripped:
                path, count = stripped.rsplit(': ', 1)
                result[path] = int(count)
        return result
    except Exception:
        return {}


def scan_file(path, patterns):
    if os.path.basename(path) == SCRIPT_NAME:
        return 0, []
    matches = []
    count = 0
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                for pat_name, pattern in patterns:
                    if pattern.search(line):
                        matches.append((i, line.rstrip(), pat_name))
                        count += 1
    except (IOError, OSError):
        pass
    return count, matches


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    repo = os.path.abspath(repo)
    
    blocklist = load_blocklist(repo)
    if not blocklist:
        print('No blocklist found (build/identifiers.yaml missing). Gate cannot run.')
        return 1
    
    baseline = load_baseline(repo)
    
    patterns = []
    for name in blocklist:
        if name.strip():
            patterns.append((name, re.compile(re.escape(name), re.IGNORECASE)))
    
    if not patterns:
        print('No valid blocklist terms found. Gate cannot run.')
        return 1
    
    all_leaks = []
    files_scanned = 0
    files_with_hits = []
    
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for fname in files:
            fpath = os.path.join(root, fname)
            if not os.path.isfile(fpath):
                continue
            
            if fname.endswith(('.pyc', '.so', '.png', '.jpg', '.gif', '.pdf', '.zip', '.tar.gz')):
                continue
            
            files_scanned += 1
            count, matches = scan_file(fpath, patterns)
            
            if count > 0:
                # Always use relative path from repo root, prefixed with ./
                rel_path = './' + os.path.relpath(fpath, repo)
                files_with_hits.append((rel_path, count))
                for line_num, line, pat_name in matches:
                    all_leaks.append((rel_path, line_num, line, pat_name))
    
    baseline_files = set(baseline.keys())
    hits_outside_baseline = [f for f, _ in files_with_hits if f not in baseline_files]
    
    count_violations = []
    for fpath, count in files_with_hits:
        if fpath in baseline:
            if count > baseline[fpath]:
                count_violations.append((fpath, count, baseline[fpath]))
    
    if all_leaks:
        print('INTERNAL NAME LEAKS FOUND:')
        for fpath, line_num, line, reason in all_leaks:
            print('  ' + fpath + ':' + str(line_num) + ' INTERNAL NAME: ' + reason)
            suffix = '...' if len(line) > 100 else ''
            print('    ' + line[:100] + suffix)
        print()
        print('Files scanned: ' + str(files_scanned))
        print('Files with hits: ' + str(len(files_with_hits)))
        
        if hits_outside_baseline:
            print('Leaks outside baseline (FAIL): ' + str(len(hits_outside_baseline)) + ' files')
            for f in hits_outside_baseline:
                print('  ' + f)
        
        if count_violations:
            print('Baseline hit count violations (FAIL): ' + str(len(count_violations)) + ' files')
            for f, got, expected in count_violations:
                print('  ' + f + ': got ' + str(got) + ', expected ' + str(expected))
        
        if hits_outside_baseline or count_violations:
            print()
            print('Total leaks: ' + str(len(all_leaks)))
            return 1
        else:
            print('All hits are within baseline and match recorded counts.')
            return 0
    else:
        print('No internal name leaks found in ' + str(files_scanned) + ' files.')
        return 0


if __name__ == '__main__':
    sys.exit(main())