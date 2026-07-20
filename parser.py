"""
Phase 2: Syntax Analysis (Parser)
Recursive-descent parser. Builds an AST and reports syntax errors with
line numbers.

Grammar (simplified EBNF):
    program    -> statement*
    statement  -> decl_stmt | assign_stmt | if_stmt | while_stmt
                | print_stmt | block
    decl_stmt  -> TYPE ID ('=' expr)? ';'
    assign_stmt-> ID '=' expr ';'
    if_stmt    -> 'if' '(' expr ')' block ('else' block)?
    while_stmt -> 'while' '(' expr ')' block
    print_stmt -> 'print' '(' expr ')' ';'
    block      -> '{' statement* '}'
    expr       -> logic_or
    logic_or   -> logic_and ('||' logic_and)*
    logic_and  -> equality ('&&' equality)*
    equality   -> relational (('=='|'!=') relational)*
    relational -> additive (('<'|'>'|'<='|'>=') additive)*
    additive   -> term (('+'|'-') term)*
    term       -> factor (('*'|'/'|'%') factor)*
    factor     -> INT | FLOAT | STRING | ID | '(' expr ')' | '-' factor | '!' factor
"""

from lexer import tokenize, LexError

TYPES = {"int", "float", "char", "bool"}


class ParseError(Exception):
    pass


# ---------- AST Node types (simple dict-based nodes for readability) ----------
def node(kind, **fields):
    d = {"kind": kind}
    d.update(fields)
    return d


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def check(self, kind, value=None):
        tok = self.peek()
        if tok.kind != kind:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    def expect(self, kind, value=None):
        if not self.check(kind, value):
            tok = self.peek()
            expected = value if value else kind
            raise ParseError(
                f"Line {tok.line}: expected '{expected}' but found '{tok.value}'"
            )
        return self.advance()

    # ---- top level ----
    def parse_program(self):
        statements = []
        while not self.check("EOF"):
            statements.append(self.parse_statement())
        return node("Program", body=statements)

    def parse_statement(self):
        tok = self.peek()

        if tok.kind == "KEYWORD" and tok.value in TYPES:
            return self.parse_decl()
        if tok.kind == "KEYWORD" and tok.value == "if":
            return self.parse_if()
        if tok.kind == "KEYWORD" and tok.value == "while":
            return self.parse_while()
        if tok.kind == "KEYWORD" and tok.value == "print":
            return self.parse_print()
        if tok.kind == "DELIM" and tok.value == "{":
            return self.parse_block()
        if tok.kind == "ID":
            return self.parse_assign()

        raise ParseError(f"Line {tok.line}: unexpected token '{tok.value}'")

    def parse_decl(self):
        type_tok = self.advance()  # type keyword
        name_tok = self.expect("ID")
        init = None
        if self.check("OP", "="):
            self.advance()
            init = self.parse_expr()
        self.expect("DELIM", ";")
        return node("Decl", var_type=type_tok.value, name=name_tok.value,
                     init=init, line=name_tok.line)

    def parse_assign(self):
        name_tok = self.expect("ID")
        self.expect("OP", "=")
        value = self.parse_expr()
        self.expect("DELIM", ";")
        return node("Assign", name=name_tok.value, value=value, line=name_tok.line)

    def parse_if(self):
        line = self.advance().line  # 'if'
        self.expect("DELIM", "(")
        cond = self.parse_expr()
        self.expect("DELIM", ")")
        then_branch = self.parse_block()
        else_branch = None
        if self.check("KEYWORD", "else"):
            self.advance()
            else_branch = self.parse_block()
        return node("If", cond=cond, then=then_branch, els=else_branch, line=line)

    def parse_while(self):
        line = self.advance().line  # 'while'
        self.expect("DELIM", "(")
        cond = self.parse_expr()
        self.expect("DELIM", ")")
        body = self.parse_block()
        return node("While", cond=cond, body=body, line=line)

    def parse_print(self):
        line = self.advance().line  # 'print'
        self.expect("DELIM", "(")
        value = self.parse_expr()
        self.expect("DELIM", ")")
        self.expect("DELIM", ";")
        return node("Print", value=value, line=line)

    def parse_block(self):
        self.expect("DELIM", "{")
        statements = []
        while not self.check("DELIM", "}"):
            statements.append(self.parse_statement())
        self.expect("DELIM", "}")
        return node("Block", body=statements)

    # ---- expressions (precedence climbing) ----
    def parse_expr(self):
        return self.parse_logic_or()

    def parse_logic_or(self):
        left = self.parse_logic_and()
        while self.check("OP", "||"):
            op = self.advance().value
            right = self.parse_logic_and()
            left = node("BinOp", op=op, left=left, right=right)
        return left

    def parse_logic_and(self):
        left = self.parse_equality()
        while self.check("OP", "&&"):
            op = self.advance().value
            right = self.parse_equality()
            left = node("BinOp", op=op, left=left, right=right)
        return left

    def parse_equality(self):
        left = self.parse_relational()
        while self.check("OP", "==") or self.check("OP", "!="):
            op = self.advance().value
            right = self.parse_relational()
            left = node("BinOp", op=op, left=left, right=right)
        return left

    def parse_relational(self):
        left = self.parse_additive()
        while self.peek().kind == "OP" and self.peek().value in ("<", ">", "<=", ">="):
            op = self.advance().value
            right = self.parse_additive()
            left = node("BinOp", op=op, left=left, right=right)
        return left

    def parse_additive(self):
        left = self.parse_term()
        while self.peek().kind == "OP" and self.peek().value in ("+", "-"):
            op = self.advance().value
            right = self.parse_term()
            left = node("BinOp", op=op, left=left, right=right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.peek().kind == "OP" and self.peek().value in ("*", "/", "%"):
            op = self.advance().value
            right = self.parse_factor()
            left = node("BinOp", op=op, left=left, right=right)
        return left

    def parse_factor(self):
        tok = self.peek()

        if tok.kind == "OP" and tok.value == "-":
            self.advance()
            operand = self.parse_factor()
            return node("UnaryOp", op="-", operand=operand)
        if tok.kind == "OP" and tok.value == "!":
            self.advance()
            operand = self.parse_factor()
            return node("UnaryOp", op="!", operand=operand)
        if tok.kind == "INT":
            self.advance()
            return node("IntLit", value=int(tok.value))
        if tok.kind == "FLOAT":
            self.advance()
            return node("FloatLit", value=float(tok.value))
        if tok.kind == "STRING":
            self.advance()
            return node("StringLit", value=tok.value.strip('"'))
        if tok.kind == "KEYWORD" and tok.value in ("true", "false"):
            self.advance()
            return node("BoolLit", value=(tok.value == "true"))
        if tok.kind == "ID":
            self.advance()
            return node("Var", name=tok.value, line=tok.line)
        if tok.kind == "DELIM" and tok.value == "(":
            self.advance()
            expr = self.parse_expr()
            self.expect("DELIM", ")")
            return expr

        raise ParseError(f"Line {tok.line}: unexpected token '{tok.value}' in expression")


def parse(source):
    tokens = tokenize(source)  # may raise LexError
    p = Parser(tokens)
    return p.parse_program()  # may raise ParseError


if __name__ == "__main__":
    sample = "int x = 10;\nint y = 20;\nif (x < y) { print(y); }"
    ast = parse(sample)
    import pprint
    pprint.pprint(ast)
