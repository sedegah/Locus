from sympy import S, diff, solveset, symbols

from symbolic.integrals import integral
from symbolic.solver import solve_roots

x = symbols("x")


def summarize_expression(expr) -> str:
    derivative = diff(expr, x)
    second_derivative = diff(derivative, x)
    roots = solve_roots(expr)
    critical_points = solve_roots(derivative)
    domain = solveset(S.true, x, domain=S.Reals)

    lines = [
        f"f(x) = {expr}",
        f"f'(x) = {derivative}",
        f"f''(x) = {second_derivative}",
        f"roots: {roots}",
        f"critical points: {critical_points}",
        f"indefinite integral: {integral(expr)}",
        f"domain (assumed real): {domain}",
    ]
    return "\n".join(lines)
