#!/usr/bin/env python3
"""
check-path-names.py — Regression gate: rejects tracked paths containing internal codenames.

Policy: any committed file whose path component contains one of the eight
codename substrings (case-insensitive) is a failure. The list is hard-coded
here; the gate shares no substring with the codenames in its own path/name.

Usage:
  python3 build/check-path-names.py [repo_root]

Exit 0 = clean, 1 = codename path found, 2 = usage error.
"""

import os
import sys
import subprocess

# Hard-coded codename vocabulary (lowercased) — must stay in sync with
# leak sweep. Substring match on path components, case-insensitive.
CODENAMES = ["proteus", "hazen", "leo", "frida", "mozi", "shaka", "orda", "aetherean"]

SCRIPT_NAME = "check-path-names.py"


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
            # -z splits on NUL
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
    # Fallback walk
    paths = []
    for root, dirs, files in os.walk(repo):
        # skip .git
        if ".git" in root.split(os.sep):
            continue
        dirs[:] = [d for d in dirs if d != ".git" and not d.startswith(".")]
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, repo)
            paths.append(rel.replace(os.sep, "/"))
    return paths


def is_hit(path):
    """True if any path component contains a codename substring (case-insensitive)."""
    low = path.lower()
    parts = low.split("/")
    for part in parts:
        for cod in CODENAMES:
            if cod in part:
                return True, cod, part
    return False, None, None


def scan_repo(repo):
    hits = []
    for p in tracked_paths(repo):
        hit, cod, part = is_hit(p)
        if hit:
            hits.append((p, cod, part))
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
    # self-test via env? simple
    if args and args[0] == "--self-test":
        # built-in sanity
        assert is_hit("avatars/avatar-01.jpg")[0] is False
        assert is_hit("avatars/proteus.jpg")[0] is True
        assert is_hit("AVATARS/LEO.jpg")[0] is True
        assert is_hit("avatars/hermes-agent.jpg")[0] is False
        assert is_hit("docs/aetherean-notes.md")[0] is True
        print("check-path-names self-test: 5/5 passed")
        return 0

    hits = scan_repo(repo)
    if not hits:
        print(f"No codename-bearing paths found ({len(tracked_paths(repo))} tracked files scanned).")
        return 0
    print("CODENAME PATH HITS (FAIL):")
    for p, cod, part in sorted(hits):
        print(f"  {p}  [component '{part}' contains '{cod}']")
    print(f"\nFiles scanned: {len(tracked_paths(repo))}")
    print(f"Files with hits: {len(hits)}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
