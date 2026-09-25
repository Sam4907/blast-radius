import networkx as nx

def build_dependency_graph_from_calls(parsed_files_data):
    """
    Takes parsed AST data [(defined_funcs, calls), ...] and builds a DiGraph.
    """
    G = nx.DiGraph()
    all_defined = set()
    all_calls = []

    for defined_funcs, calls in parsed_files_data:
        all_defined.update(defined_funcs)
        all_calls.extend(calls)

    for caller, callee_raw in all_calls:
        for full_func in all_defined:
            if full_func == callee_raw or full_func.endswith(f".{callee_raw}"):
                G.add_edge(caller, full_func)

    return G

def get_blast_radius(graph, modified_function):
    """
    Calculates direct and indirect affected callers.
    """
    if modified_function not in graph:
        return {"direct": [], "indirect": []}

    direct_callers = set(graph.predecessors(modified_function))
    all_affected = nx.ancestors(graph, modified_function)
    indirect_callers = all_affected - direct_callers

    return {
        "direct": list(direct_callers),
        "indirect": list(indirect_callers)
    }