"""
Mini Compiler - Main Driver
Runs source code through all phases:
  1. Lexical Analysis
  2. Syntax Analysis (Parser)
  3. Symbol Table construction
  4. Semantic Analysis
  5. Intermediate Code Generation (TAC)
  6. Code Optimization (constant folding + dead code elimination)

Usage:
    python main.py <source_file>
    python main.py            (runs built-in sample program)
"""

import sys

from lexer import tokenize, LexError
from parser import parse, ParseError
from semantic import SemanticAnalyzer, SemanticError
from codegen import generate_tac
from optimizer import optimize

SAMPLE_PROGRAM = """int a = 10;
int b = 20;
int c;
c = a + b;
if (c > 20)
{
    print(c);
}
"""


def compile_source(source, show_tokens=True):
    print("=" * 60)
    print("PHASE 1: LEXICAL ANALYSIS")
    print("=" * 60)
    try:
        tokens = tokenize(source)
        if show_tokens:
            for t in tokens:
                if t.kind != "EOF":
                    print(f"  {t.kind:<10} {t.value}")
    except LexError as e:
        print("Lexical Error(s):")
        print(e)
        return
    print("Lexical analysis completed successfully.\n")

    print("=" * 60)
    print("PHASE 2: SYNTAX ANALYSIS")
    print("=" * 60)
    try:
        ast = parse(source)
    except ParseError as e:
        print("Syntax Error:")
        print(e)
        return
    print("Syntax analysis completed successfully. AST built.\n")

    print("=" * 60)
    print("PHASE 3 & 4: SYMBOL TABLE + SEMANTIC ANALYSIS")
    print("=" * 60)
    analyzer = SemanticAnalyzer()
    try:
        symtab = analyzer.analyze(ast)
    except SemanticError as e:
        print("Semantic Error(s):")
        print(e)
        return
    symtab.print_table()
    print("Semantic analysis completed successfully.\n")

    print("=" * 60)
    print("PHASE 5: INTERMEDIATE CODE GENERATION (TAC)")
    print("=" * 60)
    tac = generate_tac(ast)
    for line in tac:
        print(f"  {line}")
    print()

    print("=" * 60)
    print("PHASE 6: CODE OPTIMIZATION")
    print("=" * 60)
    optimized = optimize(tac)
    print("Before optimization:")
    for line in tac:
        print(f"  {line}")
    print("\nAfter optimization:")
    for line in optimized:
        print(f"  {line}")
    print()
    print("Optimizations applied: Constant Folding, Dead Code Elimination")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            src = f.read()
    else:
        src = SAMPLE_PROGRAM
    compile_source(src)
