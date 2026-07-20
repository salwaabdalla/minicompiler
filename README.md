
# Mini Compiler for a Simple Programming Language

A Python implementation of a mini compiler demonstrating the core phases
of the compilation process: lexical analysis, syntax analysis, symbol
table management, semantic analysis, intermediate code generation, and
code optimization.

## 🔧 Features

- **Phase 1 — Lexical Analysis**: tokenizes keywords, identifiers, int/float
  literals, operators, delimiters, comments, and string literals; reports
  invalid tokens
- **Phase 2 — Syntax Analysis**: recursive-descent parser that builds an AST
  and reports syntax errors with line numbers
- **Phase 3 — Symbol Table**: tracks variable name, type, scope, and initial
  value across nested scopes
- **Phase 4 — Semantic Analysis**: catches undeclared variables, duplicate
  declarations, type mismatches, and invalid assignments
- **Phase 5 — Intermediate Code Generation**: emits Three-Address Code (TAC)
- **Phase 6 — Code Optimization**: constant folding and dead code elimination

## 📁 Project Structure


|
 File 
|
 Purpose 
|
|
---
|
---
|
|
`lexer.py`
|
 Phase 1 — tokenizer 
|
|
`parser.py`
|
 Phase 2 — recursive-descent parser, builds AST 
|
|
`symbol_table.py`
|
 Phase 3 — scoped symbol table 
|
|
`semantic.py`
|
 Phase 4 — semantic checks 
|
|
`codegen.py`
|
 Phase 5 — TAC generation 
|
|
`optimizer.py`
|
 Phase 6 — constant folding + dead code elimination 
|
|
`main.py`
|
 Driver — runs all phases and prints output 
|
|
`sample_input.txt`
|
 Example program 
|
|
`sample_output.txt`
|
 Example run output 
|

## 🚀 Getting Started

### Requirements
- Python 3.8+ (standard library only, no dependencies)

### Run the built-in sample program
```bash
python main.py
```

### Run your own source file
```bash
python main.py path/to/program.txt
```

## 📝 Supported Language Features

- **Types:** `int`, `float`, `char`, `bool`
- **Statements:** declaration, assignment, `print(...)`, blocks
- **Control flow:** `if`, `if-else`, `while`
- **Operators:** `+ - * / %`, `< > <= >= == !=`, `&& || !`
- **Literals:** integers, floats, strings, `true`/`false`
- **Comments:** `// line comment`

## 💡 Example

**Input:**
```c
int a = 10;
int b = 20;
int c;
c = a + b;
if (c > 20)
{
    print(c);
}
```

**Output (after optimization):**

a = 10
b = 20
c = 30
t2 = 30 > 20
ifFalse t2 goto L1
print 30
goto L2
L1:
L2:


## ⚠️ Error Handling Examples

| Error type | Example | Message |
|---|---|---|
| Syntax error | `int = x 10;` | `Line 1: expected 'ID' but found '='` |
| Semantic error | `int x; x = "Hello";` | `Cannot assign string to int variable 'x'.` |
| Undeclared variable | `y = 5;` | `Undeclared variable 'y'.` |
| Invalid token | `int x = 10 @;` | `Line 1: Invalid token '@'` |

## 🎓 Course Project

This project was built to satisfy a compiler design course assignment
covering the standard 6-phase compilation pipeline, with optional bonus
target-code generation left as an extension point.

This project was built to satisfy a compiler design course assignment
covering the standard 6-phase compilation pipeline, with optional bonus
target-code generation left as an extension point.
