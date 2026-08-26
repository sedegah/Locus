from sympy import Expr, symbols
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

x_sym, y_sym = symbols("x y")

TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def parse_user_equation(equation: str) -> Expr:
    """Parse user input equation string into a SymPy expression.

    Handles:
    - Explicit equations: "y = x^3 - 3x + 1" -> x**3 - 3*x + 1
    - Plain expressions: "x^3 - 3x^2 + 9" -> x**3 - 3*x**2 + 9
    - Implicit equations: "x^2 + y^2 = 25" -> x**2 + y**2 - 25
    """
    normalized = equation.strip()
    if not normalized:
        raise ValueError("Please enter an equation.")

    # Remove leading 'y=' or 'y =' if y is purely on LHS
    if "=" in normalized:
        parts = normalized.split("=", 1)
        lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
        if lhs_str.lower() == "y" and "y" not in rhs_str.lower():
            normalized = rhs_str

    # Handle remaining equation with '=' (e.g. x^2 + y^2 = 25 or 2y = x^2 + 1)
    if "=" in normalized:
        parts = normalized.split("=", 1)
        lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
        lhs_expr = parse_expr(lhs_str, transformations=TRANSFORMS, local_dict={"x": x_sym, "y": y_sym})
        rhs_expr = parse_expr(rhs_str, transformations=TRANSFORMS, local_dict={"x": x_sym, "y": y_sym})
        return lhs_expr - rhs_expr

    return parse_expr(normalized, transformations=TRANSFORMS, local_dict={"x": x_sym, "y": y_sym})

