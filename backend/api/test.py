import os
import unittest

# Import repo_utils regardless of whether test is run from root or backend/api/
try:
    from backend.repo_utils import walk_python_files, parse_git_diff
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from backend.repo_utils import walk_python_files, parse_git_diff


class TestRepoUtils(unittest.TestCase):

    def test_walk_python_files(self):
        # Locate sample repo relative to project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        sample_repo_dir = os.path.join(project_root, "sample repo")

        files = walk_python_files(sample_repo_dir)

        # Normalize paths for cross-platform OS compatibility (Windows vs Mac/Linux)
        normalized_files = [os.path.normpath(f) for f in files]

        self.assertTrue(any("billing.py" in f for f in normalized_files))
        self.assertTrue(any("checkout.py" in f for f in normalized_files))
        self.assertTrue(any("__init__.py" in f for f in normalized_files))
    def test_parse_git_diff_added_line(self):
        diff = """--- a/billing.py
+++ b/billing.py
@@ -1,3 +1,4 @@
 def charge_card(user, amount):
+    log_transaction(user)
     print("Charging card")
     return True
"""

        result = parse_git_diff(diff)

        self.assertEqual(
            result,
            [{
                "file": "billing.py",
                "added_lines": [2],
                "removed_lines": []
            }]
        )

    def test_parse_git_diff_removed_line(self):
        diff = """--- a/billing.py
+++ b/billing.py
@@ -1,4 +1,3 @@
 def charge_card(user, amount):
-    old_log(user)
     print("Charging card")
     return True
"""

        result = parse_git_diff(diff)

        self.assertEqual(
            result,
            [{
                "file": "billing.py",
                "added_lines": [],
                "removed_lines": [2]
            }]
        )


if __name__ == "__main__":
    unittest.main()