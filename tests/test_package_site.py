"""Protect the boundary between repository files and the public deployment."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "package_site.py"
REVISION = "a" * 40


class PackageSiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        self.output = Path(self.temp.name) / "output"
        (self.root / "assets").mkdir()
        (self.root / "assets/logo.png").write_bytes(b"image")
        (self.root / "index.html").write_text('<html><head><title>Example</title></head><body><img src="assets/logo.png"></body></html>')
        (self.root / ".htaccess").write_text("Options -Indexes\n")
        (self.root / "favicon.ico").write_bytes(b"icon")
        (self.root / "VERSION").write_text("1.1.0\n")

    def run_package(self):
        return subprocess.run([sys.executable, str(SCRIPT), "--source", str(self.root), "--output", str(self.output), "--revision", REVISION], capture_output=True, text=True)

    def test_only_public_files_are_published_with_release_identity(self):
        (self.root / ".env").write_text("PRIVATE=secret")
        (self.root / "README.md").write_text("Private operational notes")
        (self.root / "cards").mkdir()
        (self.root / "cards/private.pdf").write_bytes(b"private")
        result = self.run_package()
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = {str(p.relative_to(self.output)) for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(actual, {"index.html", ".htaccess", "favicon.ico", "assets/logo.png", "version.json"})
        self.assertEqual(json.loads((self.output / "version.json").read_text()), {"version": "1.1.0", "commit": REVISION})

    def test_missing_referenced_asset_stops_publication(self):
        (self.root / "assets/logo.png").unlink()
        result = self.run_package()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing local asset", result.stderr)
        self.assertFalse(self.output.exists())

    def test_symlink_cannot_publish_files_outside_the_repository(self):
        outside = Path(self.temp.name) / "credentials.png"
        outside.write_text("secret")
        (self.root / "assets/escape.png").symlink_to(outside)
        result = self.run_package()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Symlinks are not publishable", result.stderr)
        self.assertFalse(self.output.exists())

    def test_private_files_inside_assets_stop_publication(self):
        (self.root / "assets/.env").write_text("secret")
        result = self.run_package()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported public asset", result.stderr)
        self.assertFalse(self.output.exists())

    def test_invalid_version_stops_publication(self):
        (self.root / "VERSION").write_text("not-a-version")
        result = self.run_package()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("VERSION must", result.stderr)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
