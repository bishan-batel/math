from numpy.polynomial import Polynomial
import numpy as np


def newtons(z: complex, f: Polynomial, df: Polynomial, **kargs):
    return z - f(z) / df(z)


def halleys(z: complex, f: Polynomial, df: Polynomial, d2f: Polynomial, **kwargs):
    return z - (f(z) * df(z)) / ((df(z) ** 2) - 0.5 * f(z) * d2f(z))


def young_oilers(z: complex, f: Polynomial, zp: complex, zpp: complex, **kwargs):
    df = (f(z) - f(zp)) / (z - zp)
    dfp = (f(zp) - f(zpp)) / (zp - zpp)
    d2f = (df - dfp) / (z - zpp)

    return z - (f(z) * df) / ((df * df) - f(zp) * d2f)


def oilers(z: complex, f: Polynomial, zp: complex, zpp: complex, **kwargs):
    df = (f(z) - f(zp)) / (z - zp)
    dfp = (f(zp) - f(zpp)) / (zp - zpp)
    d2f = (df - dfp) / (z - zpp)

    return z - (f(z) * df) / ((df * df) - f(z) * d2f)


def is_oiler_fan(f):
    return f.__name__ == oilers.__name__ or f.__name__ == young_oilers.__name__


# METHOD_TO_MODE = {newtons: 0, halleys: 1, oilers: 2}

ALL_METHODS = [newtons, halleys, young_oilers, oilers]


def method_to_mode(f) -> int:
    for i, method in enumerate(ALL_METHODS):
        if method.__name__ == f.__name__:
            return i
    raise Exception("Unknown Method ")
