"""
IBM Bob Integration Layer for Code Blast Radius Visualizer.
Acts as a tool / agent payload provider for IBM Bob workflows.
"""

import json
from backend.main import analyze_repo_target


def run_bob_blast_analysis(repo_path: str, target_function: str) -> str:
    """
    Called by IBM Bob agent workflows before executing code modifications.
    Returns a structured markdown payload formatted for IBM Bob context injection.
    """
    analysis = analyze_repo_target(repo_path, target_function)
    
    direct_count = len(analysis["blast_radius"]["direct"])
    indirect_count = len(analysis["blast_radius"]["indirect"])
    total_impact = direct_count + indirect_count
    
    # Formatted specifically as an IBM Bob Context Prompt / Report
    bob_formatted_prompt = f"""🤖 **IBM Bob Agent Guardrail Report**
--------------------------------------------------
**Target Refactor Scope:** `{analysis['target']}`
**Blast Radius Severity:** {"CRITICAL 🔴" if total_impact > 3 else "HIGH 🟠" if total_impact > 0 else "SAFE 🟢"}

**Call Graph Intelligence:**
- **Direct Callers (1-hop):** {direct_count} functions `{analysis['blast_radius']['direct']}`
- **Indirect Callers (2+ hops):** {indirect_count} functions `{analysis['blast_radius']['indirect']}`

---
### 🛡️ Recommended Actions for IBM Bob:
1. **Safety Check:** Ensure changes to `{analysis['target']}` preserve backwards compatibility for `{analysis['blast_radius']['direct']}`.
2. **Automated Testing:** Run test suites on callers: `{', '.join(analysis['blast_radius']['direct']) if analysis['blast_radius']['direct'] else 'None'}`.
"""
    return bob_formatted_prompt


if __name__ == "__main__":
    # Test execution for IBM Bob Agent integration
    result = run_bob_blast_analysis("sample repo/Complex", "stripe_api.process")
    print(result)