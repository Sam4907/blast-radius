import os
import json
import argparse
import sys
from backend.repo_utils import walk_python_files, parse_git_diff
from backend.analyser.ast_engine import parse_file_ast, map_line_to_function
from backend.analyser.graph_builder import build_dependency_graph_from_calls, get_blast_radius

def analyze_repo_target(repo_path, target_function):
    # 1. Walk repository Python files
    py_files = walk_python_files(repo_path)
    parsed_data = []

    # 2. Parse AST for each file using your ast_engine
    for file_path in py_files:
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            defined, calls = parse_file_ast(file_path, module_name)
            parsed_data.append((defined, calls))
        except SyntaxError:
            continue

    # 3. Build NetworkX Graph
    graph = build_dependency_graph_from_calls(parsed_data)

    # 4. Compute Blast Radius
    impact = get_blast_radius(graph, target_function)

    result = {
        "target": target_function,
        "nodes": list(graph.nodes()),
        "edges": list(graph.edges()),
        "blast_radius": impact
    }
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blast Radius Core CLI")
    parser.add_argument("--repo", default="sample repo/Medium", help="Path to repo directory")
    parser.add_argument("--target", default="billing.charge_card", help="Function modified")
    
    args = parser.parse_args()
    analysis = analyze_repo_target(args.repo, args.target)
    
    print("\n--- BLAST RADIUS JSON OUTPUT ---")
    print(json.dumps(analysis, indent=2))