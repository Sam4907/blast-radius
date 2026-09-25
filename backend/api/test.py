import unittest

from backend.repo_utils import walk_python_files, parse_git_diff


class TestRepoUtils(unittest.TestCase):

    def test_walk_python_files(self):
        files = walk_python_files("sample repo")

        self.assertIn("sample repo/billing.py", files)
        self.assertIn("sample repo/checkout.py", files)
        self.assertIn("sample repo/init.py", files)

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