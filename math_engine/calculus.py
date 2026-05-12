from sympy import diff, integrate, symbols

x = symbols("x")


def derivative(expr):
    return diff(expr, x)


def integral(expr):
    return integrate(expr, x)
