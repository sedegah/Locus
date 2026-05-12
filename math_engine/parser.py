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


def _is_circle_equation(expr_str: str) -> bool:
    """Check if equation represents a circle"""
    # Look for patterns like (x-h)^2 + (y-k)^2 = r^2
    # Check if it contains both x^2 and y^2 terms
    has_x2 = 'x**2' in expr_str or 'x^2' in expr_str
    has_y2 = 'y**2' in expr_str or 'y^2' in expr_str
    
    # Also check for LaTeX fraction format
    has_frac = 'frac{' in expr_str or '}' in expr_str
    has_both_vars = ('x' in expr_str and 'y' in expr_str)
    
    print(f"DEBUG Circle Check: expr_str={expr_str}, has_x2={has_x2}, has_y2={has_y2}, has_frac={has_frac}, has_both_vars={has_both_vars}")
    
    # Consider it a circle if it has both variables and either squared terms or fractions
    is_circle = has_both_vars and (has_x2 or has_y2 or has_frac)
    
    return is_circle


def parse_user_equation(equation: str) -> Expr:
    normalized = equation.strip()
    
    # Handle circle equations - they contain both x and y
    if 'y' in normalized and 'x' in normalized and ('**2' in normalized or '^2' in normalized):
        # This is likely a circle equation, return as-is for special handling
        return normalized
    
    # Handle implicit equations like "19y=2x^2-92x+20"
    if '=' in equation_str and not equation_str.startswith('y='):
        # This is likely an implicit equation that needs rearranging
        try:
            # Try to solve for y in terms of x
            from sympy import solve, Eq
            x, y = symbols('x y')
            
            # Parse the equation
            eq = Eq(eval(equation_str.replace('=', '==')))
            
            # Try to solve for y
            solution = solve(eq, y)
            
            if solution:
                # Return the solved expression for y
                return solution[0]
            else:
                # If solving fails, try to parse as-is
                return sympify(equation_str.replace('=', '=='))
        except Exception as e:
            print(f"DEBUG: Implicit equation solving failed: {e}")
            # If solving fails, try to parse as-is
            return sympify(equation_str.replace('=', '=='))
    
    if normalized.startswith("y="):
        normalized = normalized[2:]

    if not normalized:
        raise ValueError("Please enter an equation.")

    # Replace ^ with ** for exponentiation
    normalized = normalized.replace('^', '**')

    return parse_expr(normalized, transformations=TRANSFORMS, local_dict={"x": x})
