import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk
import io
from sympy import S, diff, solveset, symbols, latex

from math_engine.parser import parse_user_equation
from symbolic.integrals import integral
from symbolic.solver import solve_roots

x = symbols("x")


def _create_math_image(math_text: str, fontsize=12) -> Image.Image:
    """Create an image from LaTeX math text using matplotlib's mathtext with dark theme."""
    fig, ax = plt.subplots(figsize=(8, 0.8), dpi=100)
    fig.patch.set_facecolor('#181B26')
    ax.set_facecolor('#181B26')
    ax.text(0.5, 0.5, f'${math_text}$', fontsize=fontsize, color='#FFC72C',
            ha='center', va='center', transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, 
                facecolor='#181B26', edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    
    return Image.open(buf)


def summarize_expression(user_input: str) -> str:
    try:
        expr = parse_user_equation(user_input)
    except Exception as e:
        return f"Error parsing expression: {e}"
    
    derivative = diff(expr, x)
    second_derivative = diff(derivative, x)
    roots = solve_roots(expr)
    critical_points = solve_roots(derivative)
    domain = solveset(S.true, x, domain=S.Reals)

    # Convert to LaTeX strings for mathtext
    expr_latex = latex(expr)
    derivative_latex = latex(derivative)
    second_derivative_latex = latex(second_derivative)
    integral_latex = latex(integral(expr))
    
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


def get_math_analysis_data(user_input: str) -> dict:
    """Return analysis data with LaTeX strings for proper rendering"""
    try:
        expr = parse_user_equation(user_input)
    except Exception as e:
        return {"error": f"Error parsing expression: {e}"}
    
    derivative = diff(expr, x)
    second_derivative = diff(derivative, x)
    roots = solve_roots(expr)
    critical_points = solve_roots(derivative)
    inflection_points = solve_roots(second_derivative)
    domain = solveset(S.true, x, domain=S.Reals)

    # Analyze root types
    real_roots = []
    imaginary_roots = []
    for root in roots:
        if root.is_real:
            real_roots.append(root)
        else:
            imaginary_roots.append(root)
    
    # Analyze concavity at critical points
    concavity_analysis = {}
    concavity_latex_parts = []
    for cp in critical_points:
        if cp.is_real:
            second_deriv_val = second_derivative.subs(x, cp).evalf()
            cp_latex = latex(cp)
            if second_deriv_val > 0:
                concavity_analysis[cp] = "concave up (local minimum)"
                concavity_latex_parts.append(f"{cp_latex}: \\text{{concave up (local minimum)}}")
            elif second_deriv_val < 0:
                concavity_analysis[cp] = "concave down (local maximum)"
                concavity_latex_parts.append(f"{cp_latex}: \\text{{concave down (local maximum)}}")
            else:
                concavity_analysis[cp] = "test inconclusive"
                concavity_latex_parts.append(f"{cp_latex}: \\text{{test inconclusive}}")

    # Format roots as LaTeX sets
    if real_roots:
        real_roots_latex = "\\left\\{" + ", ".join(latex(r) for r in real_roots) + "\\right\\}"
    else:
        real_roots_latex = "\\emptyset"
    
    if imaginary_roots:
        imaginary_roots_latex = "\\left\\{" + ", ".join(latex(r) for r in imaginary_roots) + "\\right\\}"
    else:
        imaginary_roots_latex = "\\emptyset"
    
    # Format concavity as a simpler LaTeX expression
    if concavity_latex_parts:
        concavity_latex = " \\\\ ".join(concavity_latex_parts)
    else:
        concavity_latex = "\\text{No real critical points}"

    # Convert to LaTeX strings
    return {
        "original": latex(expr),
        "derivative": latex(derivative),
        "second_derivative": latex(second_derivative),
        "roots": latex(roots),
        "real_roots": real_roots_latex,
        "imaginary_roots": imaginary_roots_latex,
        "critical_points": latex(critical_points),
        "inflection_points": latex(inflection_points),
        "concavity": concavity_latex,
        "integral": latex(integral(expr)),
        "domain": str(domain)
    }
