<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/software-development/python-venv-repair/SKILL.md -->
---
name: python-venv-repair
description: "Fix venv python 'encodings' crash (base_prefix=/install)."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [python, venv, uv, virtualenv, troubleshooting, interpreter]
---

# Python Virtualenv Interpreter Repair

## When to Use

- A venv interpreter crashes at startup with `ModuleNotFoundError: No module
  named 'encodings'`, `Could not find platform independent libraries <prefix>`,
  or `sys.base_prefix = '/install'`.
- An app/CLI that uses a Python venv fails its update with "exit 1" and a
  cryptic interpreter error, while the underlying git/pull step succeeded.
- `venv/bin/python3` dies but you suspect the venv itself is fine (check the
  interpreter link layout before blaming the code).

Diagnose and fix a Python venv whose `bin/python` fails to start with a
stdlib-location crash — almost always because the interpreter binary was
COPIED into the venv instead of SYMLINKED to its real home.

## Trigger symptoms

`venv/bin/python -c "import sys"` crashes with:

```
Could not find platform independent libraries <prefix>
Could not find platform dependent libraries <exec_prefix>
Python path configuration:
  ...
  stdlib dir = '/install/lib/python3.11'
  sys.base_prefix = '/install'
Fatal Python error: init_fs_encoding: failed to get the Python codec of the filesystem encoding
ModuleNotFoundError: No module named 'encodings'
```

`sys.base_prefix` resolving to `/install` (or any non-existent path) is the
signature: the interpreter cannot locate its stdlib.

## Root cause

Relocatable CPython builds (e.g. uv-managed:
`~/.local/share/uv/python/cpython-3.11.x-*/`) compute their stdlib and
`base_prefix` from the location of the running executable. When `bin/python`
is a real-file COPY of that base interpreter rather than a symlink into the
base directory, the copy falls back to its compile-time prefix (`/install`)
because it can't find `lib/pythonX.Y/encodings` relative to its own path.
Standard venv layout requires the interpreter to be a SYMLINK to the base
binary.

## Diagnose (verify before fixing)

1. Check `bin/python` is a regular file, not a symlink: `ls -la venv/bin/python`.
2. Confirm it's a byte-identical copy of the base:
   `cmp venv/bin/python <base>/bin/python3.11 && echo IDENTICAL`.
3. Find the base from `pyvenv.cfg`: `home = <base>/bin`. Note uv keeps a
   short-name symlink (e.g. `cpython-3.11-...` -> `cpython-3.11.15-...`);
   resolve to the real versioned dir.
4. Prove the interpreter can't self-locate: `venv/bin/python -c "import sys"`
   crashes, while `PYTHONHOME=<base> venv/bin/python -c "import sys"` works.
   PYTHONHOME must be the base PREFIX dir, not the binary path.

## Fix

```
# backup the broken copy
cp venv/bin/python venv/bin/python.bak-broken-copy
# symlink to the real base interpreter
ln -s <base>/bin/python3.11 venv/bin/python
# ensure versioned aliases point at bin/python
ln -sf python venv/bin/python3
ln -sf python venv/bin/python3.11
```

Verify: `venv/bin/python3 -c "import sys; print(sys.prefix, sys.base_prefix)"`
— prefix should be the venv, base_prefix the real base.

## Pitfalls

- Do NOT "fix" by copying another base python into the venv — that recreates
  the bug.
- The fix must work WITHOUT env vars: real launchers (e.g. a `hermes`-style
  shebang wrapper) `unset PYTHONPATH/PYTHONHOME` before exec, so a
  PYTHONHOME-only workaround is NOT a fix.
- Aliases matter: tooling often invokes `python3`/`python3.11` specifically.
  A symlink chain `python3 -> python` is required, or a broken alias
  reproduces the same crash even after `python` is fixed.
- Distinguish from a DIFFERENT family: an anchored/copied interpreter whose
  `LC_RPATH` (`@executable_path/../lib`) resolves into `venv/lib` and is
  missing libpython crashes in dyld. Same root cause family, different
  symptom and fix — check `otool -l` for LC_RPATH when `python` itself dies
  before the encodings error.
- After a hard-reset/force-update (git reset --hard-style), check
  `git status` for working-tree deletions and restore them:
  `git restore <path>`.

## References

- references/hermes-macos-tcc-anchor.md — the specific Hermes macOS case:
  reverted TCC interpreter anchor, `hermes doctor` heal, `.tcc-anchor-source`
  marker, upstream issues, and the residual gap filed as a bug report.
