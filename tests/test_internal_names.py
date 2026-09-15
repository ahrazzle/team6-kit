#!/usr/bin/env python3
"""
Tests for check-internal-names.py gate (hash blocklist policy).

The gate hashes candidate tokens and compares the digests to the blocklist, so a
blocklisted name in plaintext fails while a file that only carries the digest
string stays clean. A synthetic candidate stands in for a real internal name, and
every fixture is built in a temporary directory outside this repository, so no
plaintext internal name is ever added to the tree.

Uses only stdlib.
"""

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")
GATE = os.path.join(BUILD, "check-internal-names.py")

BLOCKLIST_KEY = "internal_agent_name_hashes"
SYNTHETIC = "SyntheticGuardName"


def digest(candidate):
    """The gate's digest convention: SHA-256 of the lowercased candidate, UTF-8."""
    return hashlib.sha256(candidate.lower().encode("utf-8")).hexdigest()


class TestCheckInternalNames(unittest.TestCase):
    """Tests for check-internal-names.py gate."""

    def _run(self, target):
        return subprocess.run(
            [sys.executable, GATE, target],
            capture_output=True,
            text=True,
            timeout=120
        )

    def _fixture_repo(self, tmpdir, blocklist, files, baseline=None):
        """Build a throwaway tree: a digest blocklist plus a few files."""
        os.makedirs(os.path.join(tmpdir, "build"), exist_ok=True)
        with open(os.path.join(tmpdir, "build", "identifiers.yaml"), "w", encoding="utf-8") as f:
            f.write("%s:\n" % BLOCKLIST_KEY)
            for value in blocklist:
                f.write("  - %s\n" % value)
        if baseline is not None:
            with open(os.path.join(tmpdir, "build", "internal-names-baseline.yaml"), "w",
                      encoding="utf-8") as f:
                f.write(baseline)
        for rel, body in files.items():
            target = os.path.join(tmpdir, rel)
            parent = os.path.dirname(target)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(body)

    def test_script_exists(self):
        """check-internal-names.py should exist in build directory."""
        self.assertTrue(os.path.isfile(GATE), f"check-internal-names.py not found at {GATE}")

    def test_script_syntax(self):
        """check-internal-names.py should have valid Python syntax."""
        with open(GATE, encoding="utf-8") as f:
            source = f.read()
        compile(source, GATE, "exec")

    def test_hash_mode_matches_the_documented_convention(self):
        """--hash prints sha256 of the lowercased candidate."""
        result = subprocess.run(
            [sys.executable, GATE, "--hash", SYNTHETIC],
            capture_output=True,
            text=True,
            timeout=60
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), digest(SYNTHETIC))

    def test_plaintext_blocklisted_name_fails(self):
        """A blocklisted name in plaintext must be caught."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._fixture_repo(
                tmpdir,
                [digest(SYNTHETIC)],
                {"notes.md": "This file names %s plainly.\n" % SYNTHETIC}
            )
            result = self._run(tmpdir)
            self.assertNotEqual(result.returncode, 0,
                "Expected a plaintext blocklisted name to fail the gate:\n" + result.stdout)
            self.assertIn("./notes.md:1", result.stdout)

    def test_literal_digest_text_passes(self):
        """A file that only carries the digest string must stay clean."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._fixture_repo(
                tmpdir,
                [digest(SYNTHETIC)],
                {"notes.md": "Digest text %s\n" % digest(SYNTHETIC)}
            )
            result = self._run(tmpdir)
            self.assertEqual(result.returncode, 0,
                "Expected a literal digest string to pass:\n" + result.stdout)

    def test_other_token_passes(self):
        """A different token must not match the digest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._fixture_repo(
                tmpdir,
                [digest(SYNTHETIC)],
                {"notes.md": "%sVariant\n" % SYNTHETIC}
            )
            result = self._run(tmpdir)
            self.assertEqual(result.returncode, 0,
                "Expected an unrelated token to pass:\n" + result.stdout)

    def test_baselined_path_stays_green(self):
        """A recorded path at or below its baseline count must stay green."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._fixture_repo(
                tmpdir,
                [digest(SYNTHETIC)],
                {"notes.md": "%s here\n" % SYNTHETIC},
                baseline="./notes.md: 1\n"
            )
            result = self._run(tmpdir)
            self.assertEqual(result.returncode, 0,
                "Expected a baselined match to pass:\n" + result.stdout)

    def test_missing_blocklist_fails(self):
        """A tree without a digest blocklist must fail closed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self._run(tmpdir)
            self.assertNotEqual(result.returncode, 0,
                "Expected a missing blocklist to fail the gate")

    def test_self_test_passes(self):
        """The gate's built-in self-test must report every case as behaving."""
        result = subprocess.run(
            [sys.executable, GATE, "--self-test"],
            capture_output=True,
            text=True,
            timeout=120
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("6 passed, 0 failed", result.stdout)

    def test_repository_tree_is_clean(self):
        """The committed tree must satisfy the gate at its own head."""
        result = self._run(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
