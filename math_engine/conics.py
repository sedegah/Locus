from sympy import Poly, symbols

x, y = symbols("x y")


def classify_quadratic(expr):
    poly = Poly(expr, x, y)
    A = poly.coeff_monomial(x**2)
    B = poly.coeff_monomial(x * y)
    C = poly.coeff_monomial(y**2)
    disc = B**2 - 4 * A * C
    if disc < 0:
        return "ellipse"
    if disc == 0:
        return "parabola"
    return "hyperbola"
