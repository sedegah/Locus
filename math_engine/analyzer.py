from sympy import diff, solve, symbols

x = symbols("x")


def summarize_expression(expr) -> str:
    derivative = diff(expr, x)
    roots = solve(expr, x)
    critical_points = solve(derivative, x)

    lines = [
        f"f(x) = {expr}",
        f"f'(x) = {derivative}",
        f"roots: {roots}",
        f"critical points: {critical_points}",
    ]
    return "\n".join(lines)
