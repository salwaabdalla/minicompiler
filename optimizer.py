"""
Phase 6: Code Optimization
Implements two optimization techniques on the TAC:
  1. Constant Folding      - t1 = 5 * 4        -> t1 = 20
  2. Dead Code Elimination - remove temps that are computed but never used
"""

import re

ASSIGN_RE = re.compile(r"^(\w+)\s*=\s*(.+)$")
BINOP_RE = re.compile(r"^(-?\d+(?:\.\d+)?)\s*([+\-*/%])\s*(-?\d+(?:\.\d+)?)$")
UNARY_RE = re.compile(r"^-(-?\d+(?:\.\d+)?)$")


def is_number(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def fold_constant(expr_str):
    """Try to evaluate a constant arithmetic expression string. Returns the
    folded value as a string, or the original string if it can't be folded."""
    m = BINOP_RE.match(expr_str)
    if m:
        left, op, right = m.groups()
        lv = float(left) if "." in left else int(left)
        rv = float(right) if "." in right else int(right)
        try:
            if op == "+":
                result = lv + rv
            elif op == "-":
                result = lv - rv
            elif op == "*":
                result = lv * rv
            elif op == "/":
                result = lv / rv if isinstance(lv, float) or isinstance(rv, float) else lv // rv
            elif op == "%":
                result = lv % rv
            else:
                return expr_str
            return str(result)
        except ZeroDivisionError:
            return expr_str

    m = UNARY_RE.match(expr_str)
    if m:
        val = m.group(1)
        num = float(val) if "." in val else int(val)
        return str(-num)

    return expr_str


def constant_folding(tac_code):
    """Pass 1: fold constant sub-expressions, and propagate folded constants
    into subsequent uses within straight-line code."""
    folded = []
    known_constants = {}

    for line in tac_code:
        m = ASSIGN_RE.match(line)
        if not m:
            folded.append(line)  # labels, goto, ifFalse, print (handled separately below)
            continue

        target, expr = m.groups()

        # substitute any known constant temps/vars into the expression
        tokens = expr.split()
        new_tokens = [known_constants.get(tok, tok) for tok in tokens]
        new_expr = " ".join(new_tokens)

        folded_expr = fold_constant(new_expr)
        folded.append(f"{target} = {folded_expr}")

        if is_number(folded_expr):
            known_constants[target] = folded_expr
        else:
            known_constants.pop(target, None)

    # also propagate constants into print/ifFalse statements
    final = []
    for line in folded:
        if line.startswith("print "):
            var = line[len("print "):].strip()
            final.append(f"print {known_constants.get(var, var)}")
        elif line.startswith("ifFalse "):
            # format: ifFalse <cond> goto <label>
            rest = line[len("ifFalse "):]
            cond, _, label = rest.partition(" goto ")
            cond = known_constants.get(cond, cond)
            final.append(f"ifFalse {cond} goto {label}")
        else:
            final.append(line)
    return final


def dead_code_elimination(tac_code):
    """Pass 2: remove temp assignments whose result is never used again."""
    # collect all uses (right-hand sides + conditions)
    used = set()
    for line in tac_code:
        m = ASSIGN_RE.match(line)
        if m:
            _, expr = m.groups()
            for tok in re.split(r"\s+", expr):
                if tok.startswith("t") and tok[1:].isdigit():
                    used.add(tok)
        elif line.startswith("print "):
            var = line[len("print "):].strip()
            if var.startswith("t") and var[1:].isdigit():
                used.add(var)
        elif line.startswith("ifFalse "):
            rest = line[len("ifFalse "):]
            cond = rest.partition(" goto ")[0]
            if cond.startswith("t") and cond[1:].isdigit():
                used.add(cond)

    result = []
    for line in tac_code:
        m = ASSIGN_RE.match(line)
        if m:
            target, _ = m.groups()
            # only eliminate unused *temporaries*; never remove real variables
            if target.startswith("t") and target[1:].isdigit() and target not in used:
                continue  # dead code, drop it
        result.append(line)
    return result


def optimize(tac_code):
    step1 = constant_folding(tac_code)
    step2 = dead_code_elimination(step1)
    return step2
