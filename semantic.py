"""
Phase 4: Semantic Analysis
Checks: undeclared variables, duplicate declarations, type mismatches,
invalid assignments. Uses the Phase 3 symbol table.
"""

from symbol_table import SymbolTable

# Very small type system: int, float, char, bool, string
NUMERIC = {"int", "float"}


class SemanticError(Exception):
    pass


def literal_type(node):
    kind = node["kind"]
    if kind == "IntLit":
        return "int"
    if kind == "FloatLit":
        return "float"
    if kind == "StringLit":
        return "string"
    if kind == "BoolLit":
        return "bool"
    return None


class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []

    def analyze(self, program_ast):
        self.visit_block_body(program_ast["body"])
        if self.errors:
            raise SemanticError("\n".join(self.errors))
        return self.symtab

    def visit_block_body(self, statements):
        for stmt in statements:
            self.visit_stmt(stmt)

    def visit_stmt(self, stmt):
        kind = stmt["kind"]
        if kind == "Decl":
            self.visit_decl(stmt)
        elif kind == "Assign":
            self.visit_assign(stmt)
        elif kind == "If":
            self.expr_type(stmt["cond"])
            self.symtab.enter_scope("if-then")
            self.visit_block_body(stmt["then"]["body"])
            self.symtab.exit_scope()
            if stmt["els"]:
                self.symtab.enter_scope("if-else")
                self.visit_block_body(stmt["els"]["body"])
                self.symtab.exit_scope()
        elif kind == "While":
            self.expr_type(stmt["cond"])
            self.symtab.enter_scope("while-body")
            self.visit_block_body(stmt["body"]["body"])
            self.symtab.exit_scope()
        elif kind == "Print":
            self.expr_type(stmt["value"])
        elif kind == "Block":
            self.symtab.enter_scope()
            self.visit_block_body(stmt["body"])
            self.symtab.exit_scope()
        else:
            self.errors.append(f"Unknown statement kind: {kind}")

    def visit_decl(self, stmt):
        name = stmt["name"]
        var_type = stmt["var_type"]
        init_value = None

        if stmt["init"] is not None:
            init_t = self.expr_type(stmt["init"])
            if init_t is not None and not self._compatible(var_type, init_t):
                self.errors.append(
                    f"Semantic Error (line {stmt['line']}): "
                    f"Cannot assign {init_t} to {var_type} variable '{name}'."
                )
            init_value = self._literal_value(stmt["init"])

        if not self.symtab.declare(name, var_type, init_value):
            self.errors.append(
                f"Semantic Error (line {stmt['line']}): "
                f"Duplicate declaration of variable '{name}'."
            )

    def visit_assign(self, stmt):
        name = stmt["name"]
        entry = self.symtab.lookup(name)
        if entry is None:
            self.errors.append(
                f"Semantic Error (line {stmt['line']}): "
                f"Undeclared variable '{name}'."
            )
            # still analyze RHS for further errors
            self.expr_type(stmt["value"])
            return

        rhs_type = self.expr_type(stmt["value"])
        if rhs_type is not None and not self._compatible(entry["type"], rhs_type):
            self.errors.append(
                f"Semantic Error (line {stmt['line']}): "
                f"Cannot assign {rhs_type} to {entry['type']} variable '{name}'."
            )

    def expr_type(self, expr):
        kind = expr["kind"]
        if kind in ("IntLit", "FloatLit", "StringLit", "BoolLit"):
            return literal_type(expr)
        if kind == "Var":
            entry = self.symtab.lookup(expr["name"])
            if entry is None:
                self.errors.append(
                    f"Semantic Error (line {expr['line']}): "
                    f"Undeclared variable '{expr['name']}'."
                )
                return None
            return entry["type"]
        if kind == "BinOp":
            lt = self.expr_type(expr["left"])
            rt = self.expr_type(expr["right"])
            if expr["op"] in ("&&", "||"):
                return "bool"
            if expr["op"] in ("==", "!=", "<", ">", "<=", ">="):
                return "bool"
            # arithmetic
            if lt in NUMERIC and rt in NUMERIC:
                return "float" if "float" in (lt, rt) else "int"
            if lt is not None and rt is not None and lt != rt:
                self.errors.append(
                    f"Semantic Error: Type mismatch in expression ('{lt}' vs '{rt}')."
                )
            return lt or rt
        if kind == "UnaryOp":
            return self.expr_type(expr["operand"])
        return None

    def _compatible(self, declared_type, value_type):
        if declared_type == value_type:
            return True
        # allow int -> float widening
        if declared_type == "float" and value_type == "int":
            return True
        return False

    def _literal_value(self, expr):
        if expr["kind"] in ("IntLit", "FloatLit", "BoolLit"):
            return expr["value"]
        if expr["kind"] == "StringLit":
            return f'"{expr["value"]}"'
        return None
