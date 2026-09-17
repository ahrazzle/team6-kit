#!/usr/bin/env python3
"""
Test suite for check-unique-headings.py
Uses only stdlib and matches repository conventions.
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


class TestUniqueHeadings(unittest.TestCase):
    """Tests for check-unique-headings.py."""

    def test_passes_on_clean_file(self):
        """Should exit 0 on a file with no duplicate headings."""
        # Create a temp file with unique headings
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Header 1\n\n")
            f.write("## Section A\n\n")
            f.write("## Section B\n\n")
            f.write("### Subsection A1\n\n")
            f.write("### Subsection A2\n\n")
            tmpfile = f.name
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(BUILD, "check-unique-headings.py"), tmpfile],
                capture_output=True,
                text=True,
                cwd=ROOT
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("unique headings", result.stdout.lower())
        finally:
            os.unlink(tmpfile)

    def test_fails_on_duplicate_headings(self):
        """Should exit 1 on a file with duplicate headings."""
        # Create a temp file with duplicate headings
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Header 1\n\n")
            f.write("## Section A\n\n")
            f.write("## Section A\n\n")  # Duplicate
            f.write("## Section B\n\n")
            tmpfile = f.name
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(BUILD, "check-unique-headings.py"), tmpfile],
                capture_output=True,
                text=True,
                cwd=ROOT
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("duplicate", result.stdout.lower())
        finally:
            os.unlink(tmpfile)

    def test_detects_multiple_duplicates(self):
        """Should report all duplicate headings."""
        # Create a temp file with multiple duplicates
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Header\n\n")
            f.write("## Foo\n\n")
            f.write("## Bar\n\n")
            f.write("## Foo\n\n")  # Duplicate
            f.write("## Bar\n\n")  # Duplicate
            tmpfile = f.name
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(BUILD, "check-unique-headings.py"), tmpfile],
                capture_output=True,
                text=True,
                cwd=ROOT
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Foo", result.stdout)
            self.assertIn("Bar", result.stdout)
        finally:
            os.unlink(tmpfile)

    def test_ignores_heading_depth(self):
        """Should handle headings at different depths."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Main\n\n")
            f.write("## Section\n\n")
            f.write("### Sub\n\n")
            f.write("#### Detail\n\n")
            f.write("## Section\n\n")  # Duplicate at same depth
            tmpfile = f.name
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(BUILD, "check-unique-headings.py"), tmpfile],
                capture_output=True,
                text=True,
                cwd=ROOT
            )
            self.assertEqual(result.returncode, 1)
        finally:
            os.unlink(tmpfile)


if __name__ == "__main__":
    unittest.main()
