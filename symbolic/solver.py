from sympy import Eq, Expr, solve, symbols

x = symbols("x")


def solve_roots(expr: Expr):
    return solve(Eq(expr, 0), x)
