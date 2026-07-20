"""
Phase 5: Intermediate Code Generation
Generates Three-Address Code (TAC) from the AST.
Each instruction is a plain string, collected into a list, in the order
they should execute.
"""


class TACGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instr):
        self.code.append(instr)

    def generate(self, program_ast):
        for stmt in program_ast["body"]:
            self.gen_stmt(stmt)
        return self.code

    def gen_stmt(self, stmt):
        kind = stmt["kind"]
        if kind == "Decl":
            if stmt["init"] is not None:
                value = self.gen_expr(stmt["init"])
                self.emit(f"{stmt['name']} = {value}")
        elif kind == "Assign":
            value = self.gen_expr(stmt["value"])
            self.emit(f"{stmt['name']} = {value}")
        elif kind == "Print":
            value = self.gen_expr(stmt["value"])
            self.emit(f"print {value}")
        elif kind == "If":
            self.gen_if(stmt)
        elif kind == "While":
            self.gen_while(stmt)
        elif kind == "Block":
            for s in stmt["body"]:
                self.gen_stmt(s)

    def gen_if(self, stmt):
        cond = self.gen_expr(stmt["cond"])
        else_label = self.new_label()
        end_label = self.new_label()

        self.emit(f"ifFalse {cond} goto {else_label}")
        for s in stmt["then"]["body"]:
            self.gen_stmt(s)
        self.emit(f"goto {end_label}")
        self.emit(f"{else_label}:")
        if stmt["els"]:
            for s in stmt["els"]["body"]:
                self.gen_stmt(s)
        self.emit(f"{end_label}:")

    def gen_while(self, stmt):
        start_label = self.new_label()
        end_label = self.new_label()

        self.emit(f"{start_label}:")
        cond = self.gen_expr(stmt["cond"])
        self.emit(f"ifFalse {cond} goto {end_label}")
        for s in stmt["body"]["body"]:
            self.gen_stmt(s)
        self.emit(f"goto {start_label}")
        self.emit(f"{end_label}:")

    def gen_expr(self, expr):
        """Returns a string (temp name, variable name, or literal) representing
        the value of the expression, emitting instructions as needed."""
        kind = expr["kind"]

        if kind == "IntLit":
            return str(expr["value"])
        if kind == "FloatLit":
            return str(expr["value"])
        if kind == "BoolLit":
            return "true" if expr["value"] else "false"
        if kind == "StringLit":
            return f'"{expr["value"]}"'
        if kind == "Var":
            return expr["name"]
        if kind == "UnaryOp":
            operand = self.gen_expr(expr["operand"])
            temp = self.new_temp()
            self.emit(f"{temp} = {expr['op']}{operand}")
            return temp
        if kind == "BinOp":
            left = self.gen_expr(expr["left"])
            right = self.gen_expr(expr["right"])
            temp = self.new_temp()
            self.emit(f"{temp} = {left} {expr['op']} {right}")
            return temp

        raise ValueError(f"Unknown expression kind: {kind}")


def generate_tac(program_ast):
    gen = TACGenerator()
    return gen.generate(program_ast)
