from sympy import Expr, symbols
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

x = symbols("x")


TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def parse_user_equation(equation: str) -> Expr:
    normalized = equation.strip()
    if normalized.startswith("y="):
        normalized = normalized[2:]

    if not normalized:
        raise ValueError("Please enter an equation.")

    return parse_expr(normalized, transformations=TRANSFORMS, local_dict={"x": x})
