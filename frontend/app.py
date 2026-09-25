import os
import sys
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import analyze_repo_target
from backend.repo_utils import get_all_repo_functions
from backend.bob_integration import run_bob_blast_analysis

st.set_page_config(page_title="Code Blast Radius Visualizer | IBM Bob", layout="wide", page_icon="⚡")

st.title("⚡ Code Blast Radius Visualizer")
st.caption("AI-Powered AST Dependency Engine integrated with IBM Bob & watsonx")

# Sidebar Controls
st.sidebar.header("🤖 Control Panel")
bob_mode = st.sidebar.toggle("Enable IBM Bob Agent Integration", value=True)

# Select Repository
repo_options = ["sample repo/Simple", "sample repo/Medium", "sample repo/Complex"]
selected_repo = st.sidebar.selectbox("Target Repository", repo_options, index=2)

# Dynamically extract functions from selected repo
available_functions = get_all_repo_functions(selected_repo)

if available_functions:
    target_func = st.sidebar.selectbox("Select Function Modified", available_functions)
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
        direct = set(results["blast_radius"]["direct"])
        indirect = set(results["blast_radius"]["indirect"])

        for node in results["nodes"]:
            if node == target:
                color, label_prefix = "#FF4D4D", "🎯 TARGET: "
            elif node in direct:
                color, label_prefix = "#FFA500", "⚠️ DIRECT: "
            elif node in indirect:
                color, label_prefix = "#FFD700", "⚡ INDIRECT: "
            else:
                color, label_prefix = "#4D94FF", "SAFE: "

            net.add_node(node, label=f"{label_prefix}{node}", color=color, shape="dot")

        for source, callee in results["edges"]:
            net.add_edge(source, callee, color="#666666", arrows="to")

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
            st.markdown(results["ai_report"])