"""
Phase 1: Lexical Analysis (Scanner)
Recognizes keywords, identifiers, int/float literals, operators, delimiters,
comments, string literals, and reports invalid tokens.
"""

import re

KEYWORDS = {"int", "float", "char", "bool", "if", "else", "while", "for",
            "print", "true", "false"}

# Token specification, order matters (longest / most specific first)
TOKEN_SPEC = [
    ("COMMENT",     r"//[^\n]*"),
    ("FLOAT",       r"\d+\.\d+"),
    ("INT",         r"\d+"),
    ("STRING",      r'"[^"\n]*"'),
    ("ID",          r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",          r"==|!=|<=|>=|&&|\|\||[+\-*/%<>=!]"),
    ("DELIM",       r"[(){};,]"),
    ("NEWLINE",     r"\n"),
    ("SKIP",        r"[ \t]+"),
    ("MISMATCH",    r"."),
]

MASTER_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))


class Token:
    def __init__(self, kind, value, line):
        self.kind = kind
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, line={self.line})"


class LexError(Exception):
    pass


def tokenize(source):
    """Returns a list of Token objects. Raises LexError on invalid tokens."""
    tokens = []
    line_num = 1
    errors = []

    for m in MASTER_RE.finditer(source):
        kind = m.lastgroup
        value = m.group()

        if kind == "NEWLINE":
            line_num += 1
            continue
        elif kind == "SKIP" or kind == "COMMENT":
            continue
        elif kind == "ID" and value in KEYWORDS:
            tokens.append(Token("KEYWORD", value, line_num))
        elif kind == "MISMATCH":
            errors.append(f"Line {line_num}: Invalid token '{value}'")
            continue
        else:
            tokens.append(Token(kind, value, line_num))

    if errors:
        raise LexError("\n".join(errors))

    tokens.append(Token("EOF", None, line_num))
    return tokens


if __name__ == "__main__":
    sample = 'int x = 10;\nfloat y = x + 5.5;'
    for t in tokenize(sample):
        print(t)
