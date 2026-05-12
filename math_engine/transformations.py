def shift_x(expr, value):
    return expr.subs("x", "x-({})".format(value))
