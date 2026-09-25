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
    old_line = None
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

        # Read hunk header: @@ -old_start,old_count +new_start,new_count @@
        if line.startswith("@@"):
            parts = line.split()
            
            # Parse old file starting line (-1,4 -> 1)
            old_range = parts[1][1:]
            old_line = int(old_range.split(",")[0]) if "," in old_range else int(old_range)

            # Parse new file starting line (+1,3 -> 1)
            new_range = parts[2][1:]
            new_line = int(new_range.split(",")[0]) if "," in new_range else int(new_range)
            continue

        if current_file is None or old_line is None or new_line is None:
            continue

        # Added line (+)
        if line.startswith("+") and not line.startswith("+++"):
            changes[-1]["added_lines"].append(new_line)
            new_line += 1

        # Removed line (-)
        elif line.startswith("-") and not line.startswith("---"):
            changes[-1]["removed_lines"].append(old_line)
            old_line += 1

        # Unchanged context line
        else:
            old_line += 1
            new_line += 1

    return changes