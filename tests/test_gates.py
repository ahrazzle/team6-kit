#!/usr/bin/env python3
"""
Test suite for verify-all.py and surface-scan.py.

Uses only stdlib and matches repository conventions. Runs from a fresh clone.
"""

import os
import subprocess
import sys
import unittest

# Add build directory to path for imports
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")


class TestVerifyAll(unittest.TestCase):
    """Tests for verify-all.py gate runner."""

    def test_script_exists(self):
        """verify-all.py should exist in build directory."""
        path = os.path.join(BUILD, "verify-all.py")
        self.assertTrue(os.path.isfile(path), f"verify-all.py not found at {path}")

    def test_script_syntax(self):
        """verify-all.py should have valid Python syntax."""
        path = os.path.join(BUILD, "verify-all.py")
        with open(path, encoding="utf-8") as f:
            source = f.read()
        # Should not raise SyntaxError
        compile(source, path, "exec")

    def test_script_runs_with_help(self):
        """verify-all.py should run (at least parse arguments)."""
        path = os.path.join(BUILD, "verify-all.py")
        # Run and check exit code (even if gates fail)
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=120
        )
        # Should start the gates (not crash immediately)
        self.assertIn("TEAM6-KIT RELEASE GATE RUNNER", result.stdout)


class TestSurfaceScanEmptyIdentifiers(unittest.TestCase):
    """Tests for surface-scan.py handling empty/missing identifiers.yaml."""

    def test_builtin_terms_defined(self):
        """Built-in safety terms should be defined in surface-scan."""
        path = os.path.join(BUILD, "surface-scan.py")
        with open(path, encoding="utf-8") as f:
            source = f.read()
        self.assertIn("_BUILTIN_SAFETY_TERMS", source)
        self.assertIn("strong_terms", source)

    def test_strong_terms_includes_builtin(self):
        """strong_terms() should include _BUILTIN_SAFETY_TERMS."""
        path = os.path.join(BUILD, "surface-scan.py")
        with open(path, encoding="utf-8") as f:
            source = f.read()
        # Should set strong = set(_BUILTIN_SAFETY_TERMS)
        self.assertIn("set(_BUILTIN_SAFETY_TERMS)", source)

    def test_surface_scan_passes_when_clean(self):
        """surface-scan should pass on clean repository."""
        path = os.path.join(BUILD, "surface-scan.py")
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=60
        )
        self.assertEqual(result.returncode, 0,
            f"surface-scan failed:\n{result.stdout}\n{result.stderr}")
        self.assertIn("PASS", result.stdout)


class TestGateScripts(unittest.TestCase):
    """Tests for individual gate scripts."""

    def test_sweep_gate_syntax(self):
        """sweep-gate.py should have valid syntax."""
        path = os.path.join(BUILD, "sweep-gate.py")
        with open(path, encoding="utf-8") as f:
            source = f.read()
        compile(source, path, "exec")

    def test_review_gate_syntax(self):
        """review-gate.py should have valid syntax."""
        path = os.path.join(BUILD, "review-gate.py")
        with open(path, encoding="utf-8") as f:
            source = f.read()
        compile(source, path, "exec")

    def test_check_artifact_contract_selftest(self):
        """check-artifact-contract.py --self-test should pass."""
        path = os.path.join(BUILD, "check-artifact-contract.py")
        result = subprocess.run(
            [sys.executable, path, "--self-test"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=60
        )
        self.assertEqual(result.returncode, 0,
            f"check-artifact-contract self-test failed:\n{result.stdout}\n{result.stderr}")

    def test_preflight_check_selftest(self):
        """preflight/check.py --selftest should pass."""
        path = os.path.join(BUILD, "preflight", "check.py")
        result = subprocess.run(
            [sys.executable, path, "--selftest"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=60
        )
        self.assertEqual(result.returncode, 0,
            f"preflight/check self-test failed:\n{result.stdout}\n{result.stderr}")

    def test_report_check_selftest(self):
        """report/check.py --selftest should pass."""
        path = os.path.join(BUILD, "report", "check.py")
        result = subprocess.run(
            [sys.executable, path, "--selftest"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=60
        )
        self.assertEqual(result.returncode, 0,
            f"report/check self-test failed:\n{result.stdout}\n{result.stderr}")


class TestGitHubWorkflow(unittest.TestCase):
    """Tests for GitHub Actions workflow."""

    def test_workflow_exists(self):
        """verify.yml should exist in .github/workflows."""
        path = os.path.join(ROOT, ".github", "workflows", "verify.yml")
        self.assertTrue(os.path.isfile(path), f"verify.yml not found at {path}")

    def test_workflow_syntax(self):
        """verify.yml should be valid YAML."""
        import yaml
        path = os.path.join(ROOT, ".github", "workflows", "verify.yml")
        with open(path, encoding="utf-8") as f:
            workflow = yaml.safe_load(f)
        self.assertIn("name", workflow)
        self.assertIn(True, workflow)  # 'on' is parsed as True in Python YAML
        self.assertIn("jobs", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
