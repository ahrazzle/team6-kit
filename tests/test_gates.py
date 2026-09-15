#!/usr/bin/env python3
"""
Test suite for verify-all.py and surface-scan.py.

Uses only stdlib and matches repository conventions. Runs from a fresh clone.
"""

import os
import subprocess
import sys
import tempfile
import unittest

# Add build directory to path for imports
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")


class TestGenericizePortability(unittest.TestCase):
    """Tests for genericize.py CI portability (missing source handling)."""

    def test_derive_identity_inventory_missing_source(self):
        """derive_identity_inventory should return empty lists when source is absent."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("genericize",
            os.path.join(BUILD, "genericize.py"))
        assert spec is not None
        genericize = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(genericize)

        # Test with non-existent path
        handles, names = genericize.derive_identity_inventory("/nonexistent/path/here")
        self.assertEqual(handles, [])
        self.assertEqual(names, [])

        # Test with path that exists but is not a directory
        with tempfile.NamedTemporaryFile(delete=False) as f:
            tmpfile = f.name
        try:
            handles, names = genericize.derive_identity_inventory(tmpfile)
            self.assertEqual(handles, [])
            self.assertEqual(names, [])
        finally:
            os.unlink(tmpfile)


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


class TestNewContractValidators(unittest.TestCase):
    """Tests for the v1.7.0 contract validators (scored-rollout, reward catalogue)."""

    def _selftest(self, relpath):
        path = os.path.join(ROOT, relpath)
        self.assertTrue(os.path.isfile(path), f"missing {relpath}")
        with open(path, encoding="utf-8") as f:
            compile(f.read(), path, "exec")  # syntax check
        result = subprocess.run(
            [sys.executable, path, "--self-test"],
            capture_output=True, text=True, cwd=ROOT, timeout=120,
        )
        self.assertEqual(result.returncode, 0,
            f"{relpath} --self-test failed:\n{result.stdout}\n{result.stderr}")

    def _example_check(self, relpath):
        path = os.path.join(ROOT, relpath)
        result = subprocess.run(
            [sys.executable, path, "--example-check"],
            capture_output=True, text=True, cwd=ROOT, timeout=120,
        )
        self.assertEqual(result.returncode, 0,
            f"{relpath} --example-check failed:\n{result.stdout}\n{result.stderr}")

    def test_scored_rollout_script_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(BUILD, "check-scored-rollout.py")))

    def test_scored_rollout_selftest(self):
        self._selftest("build/check-scored-rollout.py")

    def test_scored_rollout_example_check(self):
        self._example_check("build/check-scored-rollout.py")

    def test_reward_registry_script_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(BUILD, "check-reward-registry.py")))

    def test_reward_registry_selftest(self):
        self._selftest("build/check-reward-registry.py")

    def test_reward_registry_example_check(self):
        self._example_check("build/check-reward-registry.py")

    def test_aggregate_names_new_gates(self):
        """check-contracts.py (the aggregate gate) must name both new validators."""
        with open(os.path.join(BUILD, "check-contracts.py"), encoding="utf-8") as f:
            source = f.read()
        self.assertIn("check-scored-rollout.py", source)
        self.assertIn("check-reward-registry.py", source)

    def test_release_runner_names_aggregate(self):
        """verify-all.py must run the aggregate contract gate."""
        with open(os.path.join(BUILD, "verify-all.py"), encoding="utf-8") as f:
            source = f.read()
        self.assertIn("check-contracts.py", source)


class TestGitHubWorkflow(unittest.TestCase):
    """Tests for GitHub Actions workflow."""

    def test_workflow_exists(self):
        """verify.yml should exist in .github/workflows."""
        path = os.path.join(ROOT, ".github", "workflows", "verify.yml")
        self.assertTrue(os.path.isfile(path), f"verify.yml not found at {path}")

    def test_workflow_syntax(self):
        """verify.yml should define name/on/jobs.

        PyYAML is not a kit dependency — the kit's validators are stdlib-only
        and CI installs nothing beyond setup-python — so when it is absent the
        test falls back to a structural check instead of failing the whole
        suite on an environment gap. When PyYAML is available the full parse
        is used.
        """
        path = os.path.join(ROOT, ".github", "workflows", "verify.yml")
        with open(path, encoding="utf-8") as f:
            source = f.read()
        try:
            import yaml
        except ImportError:
            yaml = None
        if yaml is not None:
            workflow = yaml.safe_load(source)
            self.assertIn("name", workflow)
            self.assertIn(True, workflow)  # 'on' is parsed as True in Python YAML
            self.assertIn("jobs", workflow)
        else:
            self.assertIn("name:", source)
            self.assertIn("\non:", source)
            self.assertIn("jobs:", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
