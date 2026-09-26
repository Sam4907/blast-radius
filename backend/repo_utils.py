import os
import ast
import subprocess


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

                ast.parse(source, filename=file_path)
                python_files.append(file_path)

            except (UnicodeDecodeError, SyntaxError):
                continue

    return python_files


def get_git_diff():
    """
    Get the diff between origin/main and the current branch.
    """
    result = subprocess.run(
        ["git", "diff", "origin/main...HEAD"],
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout

def get_functions_from_file(file_path, changed_lines):
    """
    Find Python functions that contain changed lines.
    """

    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()

    file_path = os.path.join(repo_root, file_path)

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)

    except (UnicodeDecodeError, SyntaxError):
        return []

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)

            for line in changed_lines:

                if start <= line <= end:
                    functions.append(node.name)
                    break

    return functions

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

        if line.startswith("+++ b/"):
            current_file = line[6:].strip()

            changes.append({
                "file": current_file,
                "added_lines": [],
                "removed_lines": []
            })

            continue

        if line.startswith("--- a/"):
            continue

        if line.startswith("@@"):
            parts = line.split()

            old_range = parts[1][1:]
            old_line = int(old_range.split(",")[0])

            new_range = parts[2][1:]
            new_line = int(new_range.split(",")[0])

            continue

        if current_file is None or old_line is None or new_line is None:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            changes[-1]["added_lines"].append(new_line)
            new_line += 1

        elif line.startswith("-") and not line.startswith("---"):
            changes[-1]["removed_lines"].append(old_line)
            old_line += 1

        else:
            old_line += 1
            new_line += 1

    # Detect modified functions
    for change in changes:

        file_path = change["file"]

        changed_lines = (
            change["added_lines"]
            + change["removed_lines"]
        )

        change["functions"] = get_functions_from_file(
            file_path,
            changed_lines
        )

    return changes



def get_modified_functions(repo_path=None):
    """
    Get modified functions from the Git diff.
    If repo_path is given, only files inside that path are considered.
    """

    diff_text = get_git_diff()

    changes = parse_git_diff(diff_text)

    modified_functions = []

    for change in changes:

        file_path = change["file"]

        if repo_path:
            normalized_repo = repo_path.replace("\\", "/").rstrip("/")
            normalized_file = file_path.replace("\\", "/")

            if not normalized_file.startswith(normalized_repo + "/"):
                continue

        for function in change["functions"]:

            if function not in modified_functions:
                modified_functions.append(function)

    return modified_functions