from sympy import Expr, factor, expand


def factor_expr(expr: Expr):
    return factor(expr)


def expand_expr(expr: Expr):
    return expand(expr)
