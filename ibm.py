import os
import ast
import networkx as nx

class CodeCallVisitor(ast.NodeVisitor):
    """
    This visitor walks through a single Python file's AST.
    Whenever it enters a function definition, it notes down:
    1. The name of the function currently being defined.
    2. Any function calls made INSIDE that function.
    """
    def __init__(self, current_module):
        self.current_module = current_module
        self.current_function = None
        self.calls = []  # list of tuples: (caller, callee)

    def visit_FunctionDef(self, node):
        # We just stepped inside a function definition!
        previous_func = self.current_function
        self.current_function = f"{self.current_module}.{node.name}"
        
        # Continue visiting all child lines inside this function
        self.generic_visit(node)
        
        # Reset when leaving the function
        self.current_function = previous_func

    def visit_Call(self, node):
        # We found a function call! (e.g., charge_card(100))
        if self.current_function:
            callee_name = None
            if isinstance(node.func, ast.Name):
                callee_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                callee_name = node.func.attr
            
            if callee_name:
                self.calls.append((self.current_function, callee_name))
        
        # Continue checking if there are nested calls (e.g., f(g(x)))
        self.generic_visit(node)


def build_dependency_graph(repo_path):
    """
    Walks all .py files in a repo, parses them with AST, 
    and returns a directed networkx graph.
    """
    G = nx.DiGraph()
    all_defined_functions = set()
    raw_calls = []

    # 1. Walk through every .py file in the folder
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=file_path)
                    except SyntaxError:
                        continue  # Skip unparseable files
                
                visitor = CodeCallVisitor(module_name)
                visitor.visit(tree)
                
                # Keep track of all defined functions and all calls found
                for caller, callee in visitor.calls:
                    raw_calls.append((caller, callee))
                    all_defined_functions.add(caller)

    # 2. Add edges to our NetworkX graph
    # If function A calls function B, draw an arrow: A -> B
    for caller, callee_short_name in raw_calls:
        # Match callee_short_name to any defined function ending with that name
        for full_func in all_defined_functions:
            if full_func.endswith(f".{callee_short_name}"):
                G.add_edge(caller, full_func)

    return G


def get_blast_radius(graph, modified_function):
    """
    Given a modified function, find who calls it:
    - Direct (1 hop)
    - Indirect (2+ hops)
    """
    # Since an edge is Caller -> Callee, the functions affected by modifying
    # the Callee are its PREDECESSORS in the graph!
    if modified_function not in graph:
        return {"direct": [], "indirect": []}

    # Direct callers (1 step backwards)
    direct_callers = set(graph.predecessors(modified_function))
    
    # All callers upstream (ancestors)
    all_affected = nx.ancestors(graph, modified_function)
    
    # Indirect = all affected minus the direct ones
    indirect_callers = all_affected - direct_callers

    return {
        "direct": list(direct_callers),
        "indirect": list(indirect_callers)
    }


if __name__ == "__main__":
    # Test our engine on sample_repo
    repo_directory = "./sample_repo"
    graph = build_dependency_graph(repo_directory)

    print("--- 1. ALL GRAPH EDGES (CALL RELATIONSHIPS) ---")
    for caller, callee in graph.edges():
        print(f"[{caller}] calls ---> [{callee}]")

    print("\n--- 2. BLAST RADIUS TEST ---")
    target = "billing.charge_card"
    print(f"Modifying target: '{target}'")
    
    impact = get_blast_radius(graph, target)
    print(f"Direct Impact (1-hop):   {impact['direct']}")
    print(f"Indirect Impact (2+ hop): {impact['indirect']}")