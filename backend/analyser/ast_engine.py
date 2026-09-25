import ast
import os
from typing import Dict, List, Set, Tuple


class EnhancedCodeVisitor(ast.NodeVisitor):
    def __init__(self, current_module: str):
        self.current_module = current_module
        self.current_scope: List[str] = []
        self.imports: Dict[str, str] = {}
        self.calls: List[Tuple[str, str]] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            local_name = alias.asname if alias.asname else alias.name
            self.imports[local_name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module if node.module else ""
        for alias in node.names:
            local_name = alias.asname if alias.asname else alias.name
            full_name = f"{module}.{alias.name}" if module else alias.name
            self.imports[local_name] = full_name
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.current_scope.append(node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.current_scope.append(node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.current_scope.append(node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_Call(self, node: ast.Call):
        if self.current_scope:
            caller_full = f"{self.current_module}." + ".".join(self.current_scope)
            callee_raw = self._resolve_callee_name(node.func)
            
            if callee_raw:
                resolved_callee = self.imports.get(callee_raw, callee_raw)
                self.calls.append((caller_full, resolved_callee))

        self.generic_visit(node)

    def _resolve_callee_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            prefix = self._resolve_callee_name(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""


def parse_file_ast(file_path: str, module_name: str) -> Tuple[Set[str], List[Tuple[str, str]]]:
    """Parses a single .py file and returns defined functions & call tuples."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    visitor = EnhancedCodeVisitor(module_name)
    visitor.visit(tree)

    defined_functions = set()
    for caller, _ in visitor.calls:
        defined_functions.add(caller)

    return defined_functions, visitor.calls


def map_line_to_function(file_path: str, line_number: int) -> str:
    """Maps a changed line number to a function name."""
    if not os.path.exists(file_path):
        return ""

    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    matched_function = ""

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start_line = getattr(node, "lineno", None)
            end_line = getattr(node, "end_lineno", None)

            if start_line is not None:
                if end_line is not None:
                    if start_line <= line_number <= end_line:
                        matched_function = f"{module_name}.{node.name}"
                else:
                    if start_line <= line_number:
                        matched_function = f"{module_name}.{node.name}"

    return matched_function