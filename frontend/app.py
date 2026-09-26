import os
import sys
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import analyze_repo_target
from backend.repo_utils import get_all_repo_functions
from backend.bob_integration import run_bob_blast_analysis
from watsonxservice import generate_risk_report

st.set_page_config(page_title="Code Blast Radius Visualizer | IBM Bob", layout="wide", page_icon="⚡")

st.title("⚡ Code Blast Radius Visualizer")
st.caption("AI-Powered AST Dependency Engine integrated with IBM Bob & watsonx")

# Sidebar Controls
st.sidebar.header("🤖 Control Panel")
bob_mode = st.sidebar.toggle("Enable IBM Bob Agent Integration", value=True)
if bob_mode:
    st.sidebar.caption("🤖 Bob mode — automated guardrail analysis")
else:
    st.sidebar.caption("🧠 watsonx mode — AI risk assessment")

# Select Repository
repo_options = ["sample repo/Simple", "sample repo/Medium", "sample repo/Complex"]
selected_repo = st.sidebar.selectbox("Target Repository", repo_options, index=2)
repo_descriptions = {
    "sample repo/Simple": "🟢 Direct dependency — demonstrates a basic impact.",
    "sample repo/Medium": "🟠 Multiple dependencies — demonstrates wider impact.",
    "sample repo/Complex": "🔴 Multi-hop payment flow — demonstrates full blast radius."
}

st.sidebar.caption(repo_descriptions[selected_repo])

# Dynamically extract functions from selected repo
available_functions = get_all_repo_functions(selected_repo)

if available_functions:
    default_index = 0

    if selected_repo == "sample repo/Complex" and "stripe_api.process" in available_functions:
        default_index = available_functions.index("stripe_api.process")

    target_func = st.sidebar.selectbox(
        "Select Function Modified",
        available_functions,
        index=default_index
    )
else:
    target_func = st.sidebar.text_input("Modified Function", value="stripe_api.process")

run_btn = st.sidebar.button("Run Blast Analysis", type="primary")

if run_btn or "results" in st.session_state:
    if run_btn:
        with st.spinner("Analyzing AST & Computing Blast Radius..."):
            st.session_state.results = analyze_repo_target(selected_repo, target_func)

    results = st.session_state.results
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("🌐 Dependency Network Graph")
        net = Network(height="480px", width="100%", directed=True, bgcolor="#111111", font_color="white")
        
        target = results["target"]
        
        # Support both 'direct'/'indirect' and 'direct_impact'/'indirect_impact' keys
        blast_data = results.get("blast_radius", {})
        direct_list = blast_data.get("direct") or blast_data.get("direct_impact") or []
        indirect_list = blast_data.get("indirect") or blast_data.get("indirect_impact") or []

        direct = set(direct_list)
        indirect = set(indirect_list)

        st.markdown("### 📊 Impact Summary")

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric("Direct Impact", len(direct))
        metric2.metric("Indirect Impact", len(indirect))
        metric3.metric("Total Affected", len(direct | indirect))

        for node in results["nodes"]:
            # Handle node formatted as dict or string
            node_id = node["id"] if isinstance(node, dict) else node
            node_label = node.get("label", node_id) if isinstance(node, dict) else node_id

            if node_id == target:
                color, label_prefix = "#FF4D4D", "🎯 TARGET: "
            elif node_id in direct:
                color, label_prefix = "#FFA500", "⚠️ DIRECT: "
            elif node_id in indirect:
                color, label_prefix = "#FFD700", "⚡ INDIRECT: "
            else:
                color, label_prefix = "#4D94FF", "SAFE: "

            net.add_node(node_id, label=f"{label_prefix}{node_label}", color=color, shape="dot")

        for edge in results["edges"]:
            # Handle edge formatted as dict or tuple/list
            if isinstance(edge, dict):
                src, callee = edge["source"], edge["target"]
            else:
                src, callee = edge[0], edge[1]
            net.add_edge(src, callee, color="#666666", arrows="to")

        net.toggle_physics(True)
        net.save_graph("graph.html")

        with open("graph.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=500)

    with col2:
        if bob_mode:
            st.subheader("🤖 IBM Bob Agent Directive")
            bob_output = run_bob_blast_analysis(selected_repo, target_func)
            st.info("Formatted as an automated guardrail directive for IBM Bob Agent workflows:")
            st.markdown(bob_output)
        else:
            st.subheader("📋 Risk Report")
            # If backend didn't supply ai_report, invoke live watsonx Granite directly
            report = results.get("ai_report")
            if not report:
                with st.spinner("Generating live watsonx Granite risk report..."):
                    report = generate_risk_report(results)
                    results["ai_report"] = report
            if "```markdown" in report:
                report = report.replace("```markdown", "").replace("```", "").strip()

            st.markdown(report)