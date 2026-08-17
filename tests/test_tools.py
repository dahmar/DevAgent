import os
import unittest
from pathlib import Path

from tools import create_app_project, create_file, get_errors, grep_search


class ToolsTests(unittest.TestCase):
    def setUp(self):
        self.workspace_dir = Path("workspace")
        self.workspace_dir.mkdir(exist_ok=True)

    def tearDown(self):
        for path in [
            self.workspace_dir / "test_search.py",
            self.workspace_dir / "test_errors.py",
            self.workspace_dir / "sample_site",
        ]:
            if path.exists():
                if path.is_dir():
                    for child in sorted(path.rglob("*"), reverse=True):
                        if child.is_file():
                            child.unlink()
                        elif child.is_dir():
                            child.rmdir()
                    path.rmdir()
                else:
                    path.unlink()

    def test_grep_search_finds_text_in_file(self):
        create_file("test_search.py", "print('hello from agent')\nprint('world')\n")

        result = grep_search("hello", "test_search.py")

        self.assertIn("hello from agent", result)
        self.assertIn("test_search.py", result)

    def test_get_errors_reports_syntax_error(self):
        create_file("test_errors.py", "def broken(:\n    pass\n")

        result = get_errors("test_errors.py")

        self.assertIn("Syntax error", result)

    def test_create_app_project_creates_site_files(self):
        result = create_app_project("sample_site", project_type="website")

        self.assertIn("Created project", result)
        self.assertTrue((self.workspace_dir / "sample_site" / "index.html").exists())
        self.assertTrue((self.workspace_dir / "sample_site" / "style.css").exists())
        self.assertTrue((self.workspace_dir / "sample_site" / "script.js").exists())


if __name__ == "__main__":
    unittest.main()
