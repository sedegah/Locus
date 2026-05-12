import numpy as np


def numerical_derivative(func, x, h=1e-5):
    return (func(x + h) - func(x - h)) / (2 * h)


def linspace(start=-10, stop=10, points=1000):
    return np.linspace(start, stop, points)
