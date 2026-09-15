#!/usr/bin/env python3
"""
check-internal-names.py — Gate for internal agent names in public surfaces.

POLICY (hash blocklist)
  build/identifiers.yaml carries `internal_agent_name_hashes`: SHA-256 digests of
  the internal agent names. The gate never stores, and never prints, a plaintext
  internal name. It hashes the candidate tokens it finds in each file and compares
  those digests to the blocklist:

      digest = sha256(token lowercased, UTF-8).hexdigest()

  Direction of the check:
    - a file that carries a blocklisted name in plaintext IS a hit
    - a file that merely carries a digest string is NOT a hit

  A text scan for literal hash strings had this inverted: it fired only when a
  file already carried a hash, so a planted plaintext name passed and the same
  file with the digest string failed. Hashing candidate content restores the
  intended direction.

  build/internal-names-baseline.yaml records the paths allowed to carry names and
  their recorded hit counts. The gate fails on a hit outside the baseline, or on
  more hits than recorded for a baselined path.

USAGE
  python3 build/check-internal-names.py [path/to/repo]    # default: .
  python3 build/check-internal-names.py --hash <candidate>
  python3 build/check-internal-names.py --self-test

EXIT  0 = clean (or every self-test case behaved)   1 = leaks found, or the
      blocklist is missing/unusable   2 = usage error
"""

import hashlib
import os
import re
import sys
import tempfile

SCRIPT_NAME = 'check-internal-names.py'
BASELINE_PATH = 'build/internal-names-baseline.yaml'
IDENTIFIERS_PATH = 'build/identifiers.yaml'
BLOCKLIST_KEY = 'internal_agent_name_hashes'

# Candidate token: starts alphanumeric, may continue with alphanumerics, dot,
# underscore, or hyphen. "Name's" yields the token "Name" and the token "s".
TOKEN_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.\-]*')
HEX64_RE = re.compile(r'^[0-9a-f]{64}$')

SKIP_SUFFIXES = ('.pyc', '.so', '.dylib', '.png', '.jpg', '.jpeg', '.gif', '.ico',
                 '.pdf', '.zip', '.tar.gz', '.woff', '.woff2', '.mp4', '.lock')


def digest(candidate):
    """SHA-256 of the lowercased candidate, UTF-8. The single digest convention."""
    return hashlib.sha256(candidate.lower().encode('utf-8')).hexdigest()


def load_blocklist_hashes(repo):
    """Load the SHA-256 digests from build/identifiers.yaml (manual parse, no deps)."""
    yaml_path = os.path.join(repo, IDENTIFIERS_PATH)
    if not os.path.exists(yaml_path):
        return []
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = f.read()
    except OSError:
        return []

    values = []
    in_list = False
    for line in data.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if stripped.startswith(BLOCKLIST_KEY + ':'):
            in_list = True
            continue
        if in_list:
            if stripped.startswith('- '):
                value = stripped[2:].strip().lower()
                if HEX64_RE.match(value):
                    values.append(value)
            else:
                in_list = False
    return values


def load_baseline(repo):
    """Load the baseline of legitimate internal-name occurrences."""
    baseline_path = os.path.join(repo, BASELINE_PATH)
    if not os.path.exists(baseline_path):
        return {}
    try:
        with open(baseline_path, 'r', encoding='utf-8') as f:
            data = f.read()
    except OSError:
        return {}

    result = {}
    for line in data.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if ': ' in stripped:
            path, count = stripped.rsplit(': ', 1)
            try:
                result[path] = int(count)
            except ValueError:
                continue
    return result


def scan_file(path, blocklist):
    """Hash every candidate token in the file. Return (count, [(line_no, digest)]).

    The plaintext token is never returned, printed, or recorded: only its line
    number and the matching digest.
    """
    count = 0
    hits = []
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, 1):
                line_digests = {digest(tok) for tok in TOKEN_RE.findall(line)}
                if not line_digests:
                    continue
                for value in blocklist:
                    if value in line_digests:
                        count += 1
                        hits.append((lineno, value))
    except (IOError, OSError):
        pass
    return count, hits


def scan_repo(repo):
    """Scan a tree. Return (exit_code, output_lines, files_scanned, hit_count)."""
    out = []
    blocklist = load_blocklist_hashes(repo)
    if not blocklist:
        out.append('No hash blocklist found (' + IDENTIFIERS_PATH + ' missing, or no '
                   + BLOCKLIST_KEY + ' digest present). Gate cannot run.')
        return 1, out, 0, 0

    baseline = load_baseline(repo)

    all_hits = []
    files_scanned = 0
    files_with_hits = []

    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']

        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            if not os.path.isfile(fpath):
                continue
            if fname.endswith(SKIP_SUFFIXES):
                continue

            files_scanned += 1
            count, hits = scan_file(fpath, blocklist)

            if count > 0:
                rel_path = './' + os.path.relpath(fpath, repo).replace(os.sep, '/')
                files_with_hits.append((rel_path, count))
                for lineno, value in hits:
                    all_hits.append((rel_path, lineno, value))

    baseline_files = set(baseline.keys())
    hits_outside_baseline = [f for f, _ in files_with_hits if f not in baseline_files]

    count_violations = []
    for fpath, count in files_with_hits:
        if fpath in baseline and count > baseline[fpath]:
            count_violations.append((fpath, count, baseline[fpath]))

    if not all_hits:
        out.append('No internal name hash matches found in ' + str(files_scanned) + ' files.')
        return 0, out, files_scanned, 0

    out.append('INTERNAL NAME HASH MATCHES (plaintext name whose digest is blocklisted):')
    for fpath, lineno, value in all_hits:
        out.append('  ' + fpath + ':' + str(lineno) + ' BLOCKLISTED DIGEST ' + value[:12] + '...')
    out.append('')
    out.append('Files scanned: ' + str(files_scanned))
    out.append('Files with matches: ' + str(len(files_with_hits)))

    if hits_outside_baseline:
        out.append('Matches outside baseline (FAIL): ' + str(len(hits_outside_baseline)) + ' files')
        for f in hits_outside_baseline:
            out.append('  ' + f)

    if count_violations:
        out.append('Baseline count violations (FAIL): ' + str(len(count_violations)) + ' files')
        for f, got, expected in count_violations:
            out.append('  ' + f + ': got ' + str(got) + ', baseline ' + str(expected))

    out.append('')
    out.append('Total matches: ' + str(len(all_hits)))

    if hits_outside_baseline or count_violations:
        return 1, out, files_scanned, len(all_hits)

    out.append('All matches sit inside the baseline at or below their recorded counts.')
    return 0, out, files_scanned, len(all_hits)


def _fixture_repo(tmpdir, blocklist_hashes, files, baseline_lines=None):
    """Build a throwaway tree: one blocklist and a set of relative-path files."""
    os.makedirs(os.path.join(tmpdir, 'build'), exist_ok=True)
    with open(os.path.join(tmpdir, IDENTIFIERS_PATH), 'w', encoding='utf-8') as f:
        f.write('# synthetic fixture — digests only\n\n' + BLOCKLIST_KEY + ':\n')
        for value in blocklist_hashes:
            f.write('  - ' + value + '\n')
    if baseline_lines is not None:
        with open(os.path.join(tmpdir, BASELINE_PATH), 'w', encoding='utf-8') as f:
            f.write('# synthetic fixture baseline\n')
            for line in baseline_lines:
                f.write(line + '\n')
    for rel, body in files.items():
        target = os.path.join(tmpdir, rel)
        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(body)


def self_test():
    """Built-in pass/fail guarantee: proves the direction of the check."""
    print('check-internal-names — self-test')

    planted = 'SyntheticAgent'
    planted_digest = digest(planted)
    cases = []

    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp, [planted_digest], {'notes.md': 'This file names ' + planted + ' plainly.\n'})
        code, _, _, hits = scan_repo(tmp)
        cases.append(('plaintext blocklisted name is caught', code == 1 and hits == 1))

    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp, [planted_digest], {'notes.md': 'Digest text ' + planted_digest + '\n'})
        code, _, _, hits = scan_repo(tmp)
        cases.append(('literal digest text is not a hit', code == 0 and hits == 0))

    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp, [planted_digest], {'notes.md': planted + 'Variant\n'})
        code, _, _, hits = scan_repo(tmp)
        cases.append(('different token is not a hit', code == 0 and hits == 0))

    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp, [planted_digest], {'notes.md': planted + ' here\n'},
                      baseline_lines=['./notes.md: 1'])
        code, _, _, hits = scan_repo(tmp)
        cases.append(('baselined match stays green', code == 0 and hits == 1))

    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp, [planted_digest],
                      {'notes.md': planted + ' first\n' + planted + ' second\n'},
                      baseline_lines=['./notes.md: 1'])
        code, _, _, hits = scan_repo(tmp)
        cases.append(('more hits than the baseline fails', code == 1 and hits == 2))

    with tempfile.TemporaryDirectory() as tmp:
        code, _, _, hits = scan_repo(tmp)
        cases.append(('missing blocklist refuses to run', code == 1 and hits == 0))

    passed = failed = 0
    for name, ok in cases:
        mark = 'PASS' if ok else 'FAIL'
        passed += ok
        failed += not ok
        print('  [' + mark + '] ' + name)

    print('')
    print(str(passed) + ' passed, ' + str(failed) + ' failed')
    return 0 if failed == 0 else 1


def main(argv):
    args = argv[1:]

    if args and args[0] == '--hash':
        if len(args) < 2:
            print('Usage: python3 ' + SCRIPT_NAME + ' --hash <candidate>')
            return 2
        print(digest(args[1]))
        return 0

    if args and args[0] == '--self-test':
        return self_test()

    if args and args[0].startswith('-'):
        print(__doc__.strip())
        return 2

    repo = os.path.abspath(args[0]) if args else os.path.abspath('.')
    code, out, _, _ = scan_repo(repo)
    for line in out:
        print(line)
    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv))
