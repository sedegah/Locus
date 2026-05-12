from sympy import Expr, integrate, symbols

x = symbols("x")


def integral(expr: Expr):
    return integrate(expr, x)
