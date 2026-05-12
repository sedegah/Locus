from sympy import Expr, pi, simplify, symbols

x = symbols("x")


def trig_summary(expr: Expr) -> str:
    simplified = simplify(expr)
    return f"simplified trig form: {simplified}; reference constant pi={pi}"
