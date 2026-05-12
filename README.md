# Locus Desktop

A desktop mathematical visualization engine built with CustomTkinter, Matplotlib, SymPy, and NumPy.

## Quick start

```bash
pip install customtkinter matplotlib sympy numpy scipy
python main.py
```

## Current MVP capabilities

- Enter equations like `y=x^2+3x` or `x^2+3x`
- Parse with implicit multiplication and `^` power support
- Plot 2D graphs in an embedded Matplotlib canvas
- Run basic symbolic analysis (derivative, roots, critical points)

## Project structure

- `ui/`: desktop layout and components
- `math_engine/`: parsing, analysis, calculus, and conic helpers
- `graphing/`: rendering and sampling modules
