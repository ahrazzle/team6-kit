#!/usr/bin/env python3
"""
Tests for check-internal-names.py gate.

Uses only stdlib.
"""

import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")


class TestCheckInternalNames(unittest.TestCase):
    """Tests for check-internal-names.py gate."""

    def test_script_exists(self):
        """check-internal-names.py should exist in build directory."""
        path = os.path.join(BUILD, "check-internal-names.py")
        self.assertTrue(os.path.isfile(path), f"check-internal-names.py not found at {path}")

    def test_script_syntax(self):
        """check-internal-names.py should have valid Python syntax."""
        path = os.path.join(BUILD, "check-internal-names.py")
        with open(path, encoding="utf-8") as f:
            source = f.read()
        compile(source, path, "exec")

    def test_internal_name_fails(self):
        """check-internal-names.py should fail on internal agent names in temp dir."""
        path = os.path.join(BUILD, "check-internal-names.py")
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create identifiers.yaml in tmpdir for this test
            yaml_path = os.path.join(tmpdir, "build")
            os.makedirs(yaml_path)
            with open(os.path.join(yaml_path, "identifiers.yaml"), "w") as f:
                f.write("internal_agent_names:\n  - TestAgent\n")
            # Create a test file with internal name
            test_file = os.path.join(tmpdir, "test.md")
            with open(test_file, "w") as f:
                f.write("This file has TestAgent in it\n")
            result = subprocess.run(
                [sys.executable, path, tmpdir],
                capture_output=True,
                text=True,
                timeout=60
            )
            self.assertNotEqual(result.returncode, 0,
                f"Expected internal name to fail, got exit code {result.returncode}")


if __name__ == '__main__':
    unittest.main()
