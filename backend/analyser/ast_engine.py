import ast
from typing import Dict, List, Set, Tuple


class EnhancedCodeVisitor(ast.NodeVisitor):
    """
    AST Visitor that traverses a single Python file to extract:
    1. Defined functions and class methods.
    2. Imports and import aliases (to resolve dynamic function calls).
    3. Function calls made inside each function definition.
    """

    def __init__(self, current_module: str):
        self.current_module = current_module
        self.current_scope: List[str] = []  # Tracks nested classes/functions
        self.imports: Dict[str, str] = {}    # Local name -> Full qualified name
        self.calls: List[Tuple[str, str]] = [] # List of (caller, callee_raw_name)

    def visit_Import(self, node: ast.Import):
        """Track 'import module' and 'import module as alias'."""
        for alias in node.names:
            local_name = alias.asname if alias.asname else alias.name
            self.imports[local_name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track 'from module import func' and 'from module import func as alias'."""
        module = node.module if node.module else ""
        for alias in node.names:
            local_name = alias.asname if alias.asname else alias.name
            full_name = f"{module}.{alias.name}" if module else alias.name
            self.imports[local_name] = full_name
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """Push class name to scope stack for class method resolution."""
        self.current_scope.append(node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Push function/method name to scope stack and analyze child nodes."""
        self.current_scope.append(node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Handle async functions identically to standard functions."""
        self.current_scope.append(node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_Call(self, node: ast.Call):
        """Extract function call names within active function scopes."""
        if self.current_scope:
            caller_full = f"{self.current_module}." + ".".join(self.current_scope)
            callee_raw = self._resolve_callee_name(node.func)
            
            if callee_raw:
                # Resolve alias if present in imports map
                resolved_callee = self.imports.get(callee_raw, callee_raw)
                self.calls.append((caller_full, resolved_callee))

        self.generic_visit(node)

    def _resolve_callee_name(self, node: ast.AST) -> str:
        """Helper to extract string names from Name, Attribute, or Call nodes."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # Handles module.func or self.method
            prefix = self._resolve_callee_name(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""


def parse_file_ast(file_path: str, module_name: str) -> Tuple[Set[str], List[Tuple[str, str]]]:
    """
    Parses a single .py file and returns:
    1. A set of fully qualified defined functions (e.g. 'checkout.complete_order')
    2. A list of raw call tuples (caller, callee)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    visitor = EnhancedCodeVisitor(module_name)
    visitor.visit(tree)

    # Collect defined function signatures
    defined_functions = set()
    for caller, _ in visitor.calls:
        defined_functions.add(caller)

    return defined_functions, visitor.calls