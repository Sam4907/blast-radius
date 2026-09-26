import os
import json
import argparse
import sys

from backend.repo_utils import (
    walk_python_files,
    get_modified_functions
)

from backend.comment_generator import generate_markdown_comment

from backend.analyser.ast_engine import (
    parse_file_ast
)

from backend.analyser.graph_builder import (
    build_dependency_graph_from_calls,
    get_blast_radius
)


def analyze_repo_target(repo_path, target_function):

    # 1. Walk repository Python files
    py_files = walk_python_files(repo_path)
    parsed_data = []

    # 2. Parse AST for each file
    for file_path in py_files:

        module_name = os.path.splitext(
            os.path.basename(file_path)
        )[0]

        try:
            defined, calls = parse_file_ast(
                file_path,
                module_name
            )

            parsed_data.append(
                (defined, calls)
            )

        except SyntaxError:
            continue

    # 3. Build dependency graph
    graph = build_dependency_graph_from_calls(
        parsed_data
    )

    # 4. Find the full function name
    target_node = target_function

    for node in graph.nodes():

        if node.endswith("." + target_function):
            target_node = node
            break

    # 5. Compute blast radius
    impact = get_blast_radius(
        graph,
        target_node
    )

    result = {
        "target": target_node,
        "nodes": list(graph.nodes()),
        "edges": list(graph.edges()),
        "blast_radius": impact
    }

    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Blast Radius Core CLI"
    )

    parser.add_argument(
        "--repo",
        default="sample repo/Medium",
        help="Path to repo directory"
    )

    args = parser.parse_args()

    # Automatically detect modified functions
    # from the Git diff
    modified_functions = get_modified_functions(
        args.repo
    )

    if not modified_functions:

        print("No modified functions detected.")

        sys.exit(0)

    print("\n--- MODIFIED FUNCTIONS ---")

    for function in modified_functions:
        print(function)

    print("\n--- BLAST RADIUS JSON OUTPUT ---")

    for function in modified_functions:

        analysis = analyze_repo_target(
            args.repo,
            function
        )

        print(
            json.dumps(
                analysis,
                indent=2
            )
        )

        # Build dependency tree
        dependency_tree = analysis["target"]

        for caller in analysis["blast_radius"]["direct"]:
            dependency_tree += f"\n└── {caller}"

        for caller in analysis["blast_radius"]["indirect"]:
            dependency_tree += f"\n    └── {caller}"

        # Recommended test commands
        test_commands = [
            "pytest tests/",
            f"pytest tests/test_{function}.py"
        ]

        # Generate Markdown PR comment
        markdown_comment = generate_markdown_comment(
            function,
            analysis["blast_radius"],
            dependency_tree,
            test_commands
        )

        print("\n--- MARKDOWN PR COMMENT ---")

        print(markdown_comment)