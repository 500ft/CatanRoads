"""Negative controls for the README presentation checker; entirely offline."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check_presentation.py")

class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "docs/media").mkdir(parents=True)
        for name in ("docs/START_HERE.md", "docs/REPOSITORY_IDENTITY.md", "CONTRIBUTING.md"):
            (self.root / name).write_text("# Guide\n")
        (self.root / "docs/media/project-overview.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><title>Concept</title>'
            '<desc>Not measured</desc></svg>')
        self.readme = (
            "# Test Project\n\n"
            "![CI](https://github.com/500ft/test-project/actions/workflows/ci.yml/badge.svg?branch=main)\n\n"
            "## Evidence\n\n[Evidence](#evidence)\n[Guide](docs/START_HERE.md#guide)\n"
        )
        (self.root / "README.md").write_text(self.readme)

    def check(self):
        return subprocess.run(
            [sys.executable, str(CHECKER), str(self.root), "Test Project", "test-project"],
            text=True, capture_output=True)

    def test_valid_and_code_example_not_treated_as_link(self):
        (self.root / "README.md").write_text(self.readme + "\n\x60\x60\x60\n[not-a-link](absent.md)\n\x60\x60\x60\n")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_document_fails(self):
        (self.root / "README.md").write_text(self.readme + "\n[Missing](absent.md)\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing absent.md", result.stdout)

    def test_wrong_anchor_fails(self):
        (self.root / "README.md").write_text(self.readme.replace("#evidence)", "#absent)"))
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing anchor #absent", result.stdout)

    def test_inaccessible_svg_and_wrong_identity_fail(self):
        (self.root / "README.md").write_text(self.readme.replace("# Test Project", "# Wrong"))
        (self.root / "docs/media/project-overview.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("heading does not match", result.stdout)
        self.assertIn("missing title/description", result.stdout)

if __name__ == "__main__":
    unittest.main()
