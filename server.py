#!/usr/bin/env python3
"""
Locus Web Server
Lightweight, multi-threaded HTTP server providing REST API for SymPy / NumPy math operations
and serving the modern native web application frontend.
"""

import json
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import numpy as np
from sympy import Expr, diff, lambdify, latex, symbols, sympify

from math_engine.analyzer import get_math_analysis_data
from math_engine.parser import parse_user_equation
from symbolic.derivatives import derivative
from symbolic.integrals import integral

x_sym, y_sym, t_sym, theta_sym = symbols("x y t theta")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")


def _eval_1d_safe(expr: Expr, x_vals: np.ndarray) -> np.ndarray:
    try:
        fn = lambdify(x_sym, expr, modules=["numpy", {"abs": np.abs}])
        res = fn(x_vals)
        if np.isscalar(res):
            res = np.full_like(x_vals, float(res))
        res = np.where(np.isnan(res) | np.isinf(res) | (np.abs(res) > 1e6), np.nan, res)
        return res
    except Exception:
        res = []
        for v in x_vals:
            try:
                val = float(expr.evalf(subs={x_sym: v}))
                res.append(val if abs(val) < 1e6 else np.nan)
            except Exception:
                res.append(np.nan)
        return np.array(res)


def _eval_2d_safe(expr: Expr, x_vals: np.ndarray, y_vals: np.ndarray) -> np.ndarray:
    try:
        fn = lambdify((x_sym, y_sym), expr, modules=["numpy", {"abs": np.abs}])
        res = fn(x_vals, y_vals)
        if np.isscalar(res):
            res = np.full_like(x_vals, float(res))
        elif isinstance(res, np.ndarray) and res.shape != x_vals.shape:
            res = np.broadcast_to(res, x_vals.shape)
        res = np.where(np.isnan(res) | np.isinf(res) | (np.abs(res) > 1e6), np.nan, res)
        return res
    except Exception:
        Z = np.zeros_like(x_vals, dtype=float)
        for i in range(x_vals.shape[0]):
            for j in range(x_vals.shape[1]):
                try:
                    val = float(expr.evalf(subs={x_sym: x_vals[i, j], y_sym: y_vals[i, j]}))
                    Z[i, j] = val if abs(val) < 1e6 else np.nan
                except Exception:
                    Z[i, j] = np.nan
        return Z


class LocusRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        return json.loads(raw)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        try:
            body = self._read_json_body()

            if path == "/api/analyze":
                eq = body.get("equation", "y = x^3 - 3x + 1")
                data = get_math_analysis_data(eq)
                self._send_json({"success": True, "data": data})

            elif path == "/api/eval_2d":
                eq = body.get("equation", "y = x^3 - 3x + 1")
                x_min = float(body.get("x_min", -10))
                x_max = float(body.get("x_max", 10))
                points = int(body.get("points", 600))

                expr = parse_user_equation(eq)
                x_vals = np.linspace(x_min, x_max, points)
                y_vals = _eval_1d_safe(expr, x_vals)

                # Clean NaNs for JSON
                y_list = [None if np.isnan(v) else float(v) for v in y_vals]
                d_expr = derivative(expr)
                int_expr = integral(expr)

                self._send_json({
                    "success": True,
                    "x": x_vals.tolist(),
                    "y": y_list,
                    "equation_latex": latex(expr),
                    "derivative_latex": latex(d_expr),
                    "integral_latex": latex(int_expr),
                })

            elif path == "/api/eval_derivative":
                eq = body.get("equation", "y = x^3 - 3x + 1")
                x_min = float(body.get("x_min", -10))
                x_max = float(body.get("x_max", 10))
                points = int(body.get("points", 600))

                expr = parse_user_equation(eq)
                d_expr = derivative(expr)
                x_vals = np.linspace(x_min, x_max, points)
                y_vals = _eval_1d_safe(expr, x_vals)
                dy_vals = _eval_1d_safe(d_expr, x_vals)

                self._send_json({
                    "success": True,
                    "x": x_vals.tolist(),
                    "y": [None if np.isnan(v) else float(v) for v in y_vals],
                    "dy": [None if np.isnan(v) else float(v) for v in dy_vals],
                    "equation_latex": latex(expr),
                    "derivative_latex": latex(d_expr),
                })

            elif path == "/api/eval_integral":
                eq = body.get("equation", "y = x^3 - 3x + 1")
                a = float(body.get("a", -2.0))
                b = float(body.get("b", 2.0))
                x_min = float(body.get("x_min", -10))
                x_max = float(body.get("x_max", 10))

                expr = parse_user_equation(eq)
                x_vals = np.linspace(x_min, x_max, 600)
                y_vals = _eval_1d_safe(expr, x_vals)

                x_fill = np.linspace(a, b, 200)
                y_fill = _eval_1d_safe(expr, x_fill)

                # Compute exact integral value
                exact_val = None
                try:
                    int_expr = integral(expr)
                    val = float(int_expr.evalf(subs={x_sym: b}) - int_expr.evalf(subs={x_sym: a}))
                    exact_val = round(val, 6)
                except Exception:
                    pass

                self._send_json({
                    "success": True,
                    "x": x_vals.tolist(),
                    "y": [None if np.isnan(v) else float(v) for v in y_vals],
                    "x_fill": x_fill.tolist(),
                    "y_fill": [None if np.isnan(v) else float(v) for v in y_fill],
                    "a": a,
                    "b": b,
                    "exact_value": exact_val,
                    "equation_latex": latex(expr),
                })

            elif path == "/api/eval_riemann":
                eq = body.get("equation", "y = x^3 - 3x + 1")
                a = float(body.get("a", -3.0))
                b = float(body.get("b", 3.0))
                n = max(1, min(int(body.get("n", 12)), 200))
                method = body.get("method", "midpoint")

                expr = parse_user_equation(eq)
                dx = (b - a) / n
                if method == "left":
                    x_evals = np.linspace(a, b - dx, n)
                elif method == "right":
                    x_evals = np.linspace(a + dx, b, n)
                else:  # midpoint
                    x_evals = np.linspace(a + dx / 2, b - dx / 2, n)

                y_evals = _eval_1d_safe(expr, x_evals)
                total_area = float(np.nansum(y_evals * dx))

                x_lefts = np.linspace(a, b - dx, n)
                rectangles = []
                for xl, y_h in zip(x_lefts, y_evals):
                    if np.isfinite(y_h):
                        rectangles.append({
                            "x0": float(xl),
                            "x1": float(xl + dx),
                            "y0": 0.0,
                            "y1": float(y_h),
                        })

                # Base curve
                x_vals = np.linspace(min(a - 2, -10), max(b + 2, 10), 600)
                y_vals = _eval_1d_safe(expr, x_vals)

                self._send_json({
                    "success": True,
                    "x": x_vals.tolist(),
                    "y": [None if np.isnan(v) else float(v) for v in y_vals],
                    "rectangles": rectangles,
                    "total_area": round(total_area, 6),
                    "n": n,
                    "method": method,
                    "equation_latex": latex(expr),
                })

            elif path == "/api/eval_parametric":
                expr_x_str = body.get("expr_x", "cos(3*t)")
                expr_y_str = body.get("expr_y", "sin(4*t)")
                t_min = float(body.get("t_min", 0))
                t_max = float(body.get("t_max", 2 * np.pi))
                points = int(body.get("points", 800))

                ex = sympify(expr_x_str.replace("^", "**"), locals={"t": t_sym})
                ey = sympify(expr_y_str.replace("^", "**"), locals={"t": t_sym})
                fn_x = lambdify(t_sym, ex, "numpy")
                fn_y = lambdify(t_sym, ey, "numpy")

                t_vals = np.linspace(t_min, t_max, points)
                x_vals = fn_x(t_vals)
                y_vals = fn_y(t_vals)

                self._send_json({
                    "success": True,
                    "t": t_vals.tolist(),
                    "x": [None if np.isnan(v) else float(v) for v in x_vals],
                    "y": [None if np.isnan(v) else float(v) for v in y_vals],
                    "latex_x": latex(ex),
                    "latex_y": latex(ey),
                })

            elif path == "/api/eval_polar":
                expr_r_str = body.get("expr_r", "cos(4*theta)")
                th_min = float(body.get("theta_min", 0))
                th_max = float(body.get("theta_max", 2 * np.pi))
                points = int(body.get("points", 800))

                er = sympify(expr_r_str.replace("^", "**"), locals={"theta": theta_sym, "th": theta_sym})
                fn_r = lambdify(theta_sym, er, "numpy")

                th_vals = np.linspace(th_min, th_max, points)
                r_vals = fn_r(th_vals)
                x_vals = r_vals * np.cos(th_vals)
                y_vals = r_vals * np.sin(th_vals)

                self._send_json({
                    "success": True,
                    "theta": th_vals.tolist(),
                    "r": [None if np.isnan(v) else float(v) for v in r_vals],
                    "x": [None if np.isnan(v) else float(v) for v in x_vals],
                    "y": [None if np.isnan(v) else float(v) for v in y_vals],
                    "latex_r": latex(er),
                })

            elif path == "/api/eval_3d":
                expr_z_str = body.get("expr_z", "sin(sqrt(x^2 + y^2))")
                x_min = float(body.get("x_min", -5))
                x_max = float(body.get("x_max", 5))
                y_min = float(body.get("y_min", -5))
                y_max = float(body.get("y_max", 5))
                grid_size = int(body.get("grid_size", 50))

                clean_str = expr_z_str.replace("^", "**")
                if clean_str.startswith("z="):
                    clean_str = clean_str[2:]
                ez = sympify(clean_str, locals={"x": x_sym, "y": y_sym})

                x_arr = np.linspace(x_min, x_max, grid_size)
                y_arr = np.linspace(y_min, y_max, grid_size)
                X_mesh, Y_mesh = np.meshgrid(x_arr, y_arr)
                Z_mesh = _eval_2d_safe(ez, X_mesh, Y_mesh)

                z_list = []
                for row in Z_mesh:
                    z_list.append([None if np.isnan(v) else float(v) for v in row])

                self._send_json({
                    "success": True,
                    "x": x_arr.tolist(),
                    "y": y_arr.tolist(),
                    "z": z_list,
                    "latex_z": latex(ez),
                })

            elif path == "/api/eval_vector":
                dx_str = body.get("dx", "y")
                dy_str = body.get("dy", "-x - 0.2*y")
                x_min = float(body.get("x_min", -5))
                x_max = float(body.get("x_max", 5))
                y_min = float(body.get("y_min", -5))
                y_max = float(body.get("y_max", 5))
                grid_size = int(body.get("grid_size", 18))

                edx = sympify(dx_str.replace("^", "**"), locals={"x": x_sym, "y": y_sym})
                edy = sympify(dy_str.replace("^", "**"), locals={"x": x_sym, "y": y_sym})

                x_arr = np.linspace(x_min, x_max, grid_size)
                y_arr = np.linspace(y_min, y_max, grid_size)
                X_mesh, Y_mesh = np.meshgrid(x_arr, y_arr)

                U = _eval_2d_safe(edx, X_mesh, Y_mesh)
                V = _eval_2d_safe(edy, X_mesh, Y_mesh)

                vectors = []
                for i in range(grid_size):
                    for j in range(grid_size):
                        px, py = float(X_mesh[i, j]), float(Y_mesh[i, j])
                        u, v = float(U[i, j]), float(V[i, j])
                        if np.isfinite(u) and np.isfinite(v):
                            speed = float(np.sqrt(u**2 + v**2))
                            vectors.append({"x": px, "y": py, "u": u, "v": v, "speed": speed})

                self._send_json({
                    "success": True,
                    "vectors": vectors,
                    "latex_dx": latex(edx),
                    "latex_dy": latex(edy),
                })

            else:
                self._send_json({"error": "Unknown API endpoint"}, status=404)

        except Exception as exc:
            self._send_json({"success": False, "error": str(exc)}, status=400)


def run_server(port: int = 8080):
    os.makedirs(WEB_DIR, exist_ok=True)
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, LocusRequestHandler)
    print(f"Locus Math Web Engine running at http://0.0.0.0:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    run_server(port)
