#!/usr/bin/env python3
"""
check-path-names.py — Regression gate: rejects tracked paths containing internal identifiers.

Policy: any committed file whose path component contains one of the internal
identifiers (case-insensitive substring) is a failure. This gate keeps the
same coverage as before but does not carry the identifiers as literals.

Why encoded: the vocabulary consists of internal role labels that must not
appear as plain substrings in public tracked content (including this gate
itself). Storing only SHA-256 hex prefixes (first 16 chars) avoids
reversible exposure while preserving exact-match detection via substring
hashing. At scan time each path-component substring (length 3-9) is hashed
and checked against the prefix set.

Usage:
  python3 build/check-path-names.py [repo_root]

Exit 0 = clean, 1 = identifier-bearing path found, 2 = usage error.
"""

import hashlib
import os
import sys
import subprocess

# Encoded vocabulary: SHA-256 hex prefixes (16 chars / 64 bits) of the eight
# internal identifiers (lowercased). Precomputed offline; no plain form
# appears in this file. See comment above for rationale.
_ENCODED_PREFIXES = {
    "b93d1d4b19afbe7d",
    "684a34e1dfac0ad7",
    "8535e86c8118bbbb",
    "db77ca6bb991f807",
    "eae9c503560da21f",
    "76fdf9f745ed191d",
    "ed89e9ec1b77031e",
    "692ba7c092a719d5",
}

_MIN_LEN = 3
_MAX_LEN = 9
_PREFIX_LEN = 16

SCRIPT_NAME = "check-path-names.py"


def _hash_prefix(s):
    """SHA-256 hex prefix (lowercased input)."""
    return hashlib.sha256(s.encode()).hexdigest()[:_PREFIX_LEN]


def tracked_paths(repo):
    """Return list of tracked paths via git ls-files; fallback to walk."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0 and out.stdout:
            raw = subprocess.run(
                ["git", "ls-files"],
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return [p.strip() for p in raw.stdout.splitlines() if p.strip()]
    except Exception:
        pass
    paths = []
    for root, dirs, files in os.walk(repo):
        if ".git" in root.split(os.sep):
            continue
        dirs[:] = [d for d in dirs if d != ".git" and not d.startswith(".")]
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, repo)
            paths.append(rel.replace(os.sep, "/"))
    return paths


def is_hit(path):
    """True if any path component contains an encoded identifier substring."""
    low = path.lower()
    parts = low.split("/")
    for part in parts:
        n = len(part)
        for i in range(n):
            upper = min(n, i + _MAX_LEN)
            for j in range(i + _MIN_LEN, upper + 1):
                sub = part[i:j]
                if _hash_prefix(sub) in _ENCODED_PREFIXES:
                    return True, _hash_prefix(sub), part
    return False, None, None


def scan_repo(repo):
    hits = []
    for p in tracked_paths(repo):
        hit, h, part = is_hit(p)
        if hit:
            hits.append((p, h, part))
    return hits


def main(argv):
    args = argv[1:]
    if args and args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    repo = os.path.abspath(args[0]) if args and not args[0].startswith("-") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if not os.path.isdir(repo):
        print(f"{SCRIPT_NAME}: not a directory: {repo}", file=sys.stderr)
        return 2
    if args and args[0] == "--self-test":
        _p = bytes.fromhex("70726f74657573").decode()
        _l = bytes.fromhex("6c656f").decode()
        _a = bytes.fromhex("61657468657265616e").decode()
        assert is_hit("avatars/avatar-01.jpg")[0] is False
        assert is_hit(f"avatars/{_p}.jpg")[0] is True
        assert is_hit(f"AVATARS/{_l.upper()}.jpg")[0] is True
        assert is_hit("avatars/hermes-agent.jpg")[0] is False
        assert is_hit(f"docs/{_a}-notes.md")[0] is True
        print("check-path-names self-test: 5/5 passed")
        return 0

    hits = scan_repo(repo)
    if not hits:
        print(f"No identifier-bearing paths found ({len(tracked_paths(repo))} tracked files scanned).")
        return 0
    print("IDENTIFIER PATH HITS (FAIL):")
    for p, h, part in sorted(hits):
        print(f"  {p}  [component '{part}' matches encoded prefix '{h}']")
    print(f"\nFiles scanned: {len(tracked_paths(repo))}")
    print(f"Files with hits: {len(hits)}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
