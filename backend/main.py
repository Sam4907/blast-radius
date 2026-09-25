import os
import json
import argparse
import sys

# Ensure root directory is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.repo_utils import walk_python_files
from backend.analyser.ast_engine import parse_file_ast
from backend.analyser.graph_builder import build_dependency_graph_from_calls, get_blast_radius
from watsonxservice import generate_risk_report


def analyze_repo_target(repo_path: str, target_function: str) -> dict:
    """
    Full pipeline: Parses repo AST -> Builds NetworkX Graph -> 
    Calculates Blast Radius -> Generates watsonx AI Report.
    """
    py_files = walk_python_files(repo_path)
    parsed_data = []

    for file_path in py_files:
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            defined, calls = parse_file_ast(file_path, module_name)
            parsed_data.append((defined, calls))
        except SyntaxError:
            continue

    # Build graph & compute blast radius
    graph = build_dependency_graph_from_calls(parsed_data)
    impact = get_blast_radius(graph, target_function)

    # Format pipeline output
    analysis_payload = {
        "target": target_function,
        "nodes": list(graph.nodes()),
        "edges": list(graph.edges()),
        "blast_radius": impact
    }

    # Generate IBM watsonx AI report
    ai_report = generate_risk_report(analysis_payload)
    analysis_payload["ai_report"] = ai_report

    return analysis_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Code Blast Radius Engine")
    parser.add_argument("--repo", default="sample repo/Medium", help="Path to target repository")
    parser.add_argument("--target", default="billing.charge_card", help="Modified function to analyze")

    args = parser.parse_args()
    results = analyze_repo_target(args.repo, args.target)

    print("\n================ BLAST RADIUS REPORT ================")
    print(f"Target Function: {results['target']}")
    print(f"Direct Impact:   {results['blast_radius']['direct']}")
    print(f"Indirect Impact: {results['blast_radius']['indirect']}")
    print("====================================================\n")
    print(results["ai_report"])