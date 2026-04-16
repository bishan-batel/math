from numpy.polynomial import Polynomial
import numpy as np


def newtons(z: complex, f: Polynomial, df: Polynomial, relaxed=1.0, **kargs):
    return z - relaxed * (f(z) / df(z))


def secant(z: complex, f: Polynomial, zp: complex, **kwargs):
    df = (f(z) - f(zp)) / (z - zp)
    return z - f(z) / df


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


def is_secant(f):
    return f.__name__ == secant.__name__


def lattes(z: complex, **kwargs):
    denom = 4 * z * (z**2 - 1)
    numer = (z**2 + 1) ** 2

    if denom == 0:
        return numer * 1e10
    return numer / denom


ALL_METHODS = [newtons, halleys, young_oilers, oilers, lattes, secant]


def method_to_mode(f) -> int:
    for i, method in enumerate(ALL_METHODS):
        if method.__name__ == f.__name__:
            return i
    raise Exception("Unknown Method ")
