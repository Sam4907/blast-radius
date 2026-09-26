import argparse
import sys
import os
import json

# Ensure project root is available for imports
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.main import analyze_repo_target
from watsonxservice import generate_risk_report


def build_markdown_banner(target: str, blast_radius: dict) -> str:
    direct = blast_radius.get("direct") or blast_radius.get("direct_impact") or []
    indirect = blast_radius.get("indirect") or blast_radius.get("indirect_impact") or []

    total_impact = len(direct) + len(indirect)
    if total_impact >= 4:
        severity = "CRITICAL 🚨"
    elif total_impact >= 2:
        severity = "HIGH 🔴"
    elif total_impact == 1:
        severity = "MEDIUM 🟠"
    else:
        severity = "LOW 🟢"

    return f"""# 💥 Blast Radius Impact Analysis
**Target Modified Function:** `{target}`  
**Calculated Risk Severity:** {severity}  
**Direct Callers (1-Hop):** `{len(direct)}` | **Indirect Downstream (2+ Hops):** `{len(indirect)}`

---
"""


def main():
    parser = argparse.ArgumentParser(
        description="Blast Radius CLI: Run AST dependency and IBM watsonx Granite risk audits directly from the terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python cli.py \\\n"
            '    --repo "sample repo/Complex" \\\n'
            "    --func stripe_api.process \\\n"
            "    --output pr_comment.md"
        ),
    )
    parser.add_argument(
        "--repo",
        type=str,
        required=True,
        help="Path to the repository or subfolder to analyze (e.g., 'sample repo/Complex')",
    )
    parser.add_argument(
        "--func",
        type=str,
        required=True,
        help="Target function modified (e.g., 'stripe_api.process')",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional file path to write the markdown report (e.g., pr_comment.md)",
    )
    parser.add_argument(
        "--json-dump",
        action="store_true",
        help="Print raw AST payload JSON before the audit report",
    )
    parser.add_argument(
        "--apikey",
        type=str,
        default=None,
        help="Optional IBM Cloud API key override",
    )
    parser.add_argument(
        "--project-id",
        type=str,
        default=None,
        help="Optional IBM watsonx Project ID override",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Optional IBM watsonx URL override",
    )

    args = parser.parse_args()

    # Allow CLI args to populate environment variables if not already present
    if args.apikey:
        os.environ["WATSONX_APIKEY"] = args.apikey
    if args.project_id:
        os.environ["WATSONX_PROJECT_ID"] = args.project_id
    if args.url:
        os.environ["WATSONX_URL"] = args.url

    repo_path = args.repo
    target_func = args.func

    if not os.path.exists(repo_path):
        print(f"❌ Error: Repository directory '{repo_path}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Running AST Dependency Analysis on `{repo_path}` for function `{target_func}`...")

    try:
        results = analyze_repo_target(repo_path, target_func)
    except Exception as e:
        print(f"❌ Error during AST analysis: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json_dump:
        print("\n--- [AST Raw Payload] ---")
        print(json.dumps(results, indent=2))
        print("-------------------------\n")

    # Diagnostic check for credentials
    has_api_key = bool(os.getenv("WATSONX_APIKEY") or os.getenv("IBM_API_KEY"))
    has_proj_id = bool(os.getenv("WATSONX_PROJECT_ID") or os.getenv("IBM_PROJECT_ID"))
    print(f"🔑 Secret Check -> WATSONX_APIKEY present: {has_api_key} | WATSONX_PROJECT_ID present: {has_proj_id}")

    print("🤖 Querying IBM watsonx Granite AI for Risk Assessment...")
    ai_report = generate_risk_report(results)

    banner = build_markdown_banner(target_func, results.get("blast_radius", {}))
    full_markdown = f"{banner}\n{ai_report}\n"

    # Print directly to stdout for terminal review
    print("\n" + "=" * 60)
    print(full_markdown)
    print("=" * 60)

    # Save to file if output path requested
    if args.output:
        out_path = os.path.abspath(args.output)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_markdown)
        print(f"\n✅ Markdown report saved to: {out_path}")


if __name__ == "__main__":
    main()