import os
import ast


def walk_python_files(repo_path):
    """
    Walk through a repository and return all valid Python files.

    Files with non-UTF-8 content or invalid Python syntax are skipped.
    """
    python_files = []

    for root, _, files in os.walk(repo_path):
        for file in files:

            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source = f.read()

                # Check whether the Python file has valid syntax
                ast.parse(source, filename=file_path)

                python_files.append(file_path)

            except (UnicodeDecodeError, SyntaxError):
                continue

    return python_files

def parse_git_diff(diff_text):
    """
    Parse a unified Git diff and return changed files
    with their added and removed line numbers.
    """
    changes = []

    current_file = None
    new_line = None

    for line in diff_text.splitlines():

        # Detect the new file path
        if line.startswith("+++ b/"):
            current_file = line[6:]
            changes.append({
                "file": current_file,
                "added_lines": [],
                "removed_lines": []
            })
            continue

        # Ignore the old-file marker
        if line.startswith("--- a/"):
            continue

        # Read a hunk header such as:
        # @@ -1,4 +1,5 @@
        if line.startswith("@@"):
            parts = line.split()

            new_range = parts[2]      # +1,5
            new_range = new_range[1:] # remove +

            if "," in new_range:
                new_line = int(new_range.split(",")[0])
            else:
                new_line = int(new_range)

            continue

        if current_file is None or new_line is None:
            continue

        # Added line
        if line.startswith("+") and not line.startswith("+++"):
            changes[-1]["added_lines"].append(new_line)
            new_line += 1

        # Removed line
        elif line.startswith("-") and not line.startswith("---"):
            changes[-1]["removed_lines"].append(new_line)

        # Normal unchanged line
        else:
            new_line += 1

    return changes