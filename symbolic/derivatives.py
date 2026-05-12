from sympy import Expr, diff, symbols

x = symbols("x")


def derivative(expr: Expr):
    return diff(expr, x)
