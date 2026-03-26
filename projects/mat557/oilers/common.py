from manimlib import *
import numpy as np
from numpy.polynomial import Polynomial

FIXED_POINT_EXAMPLES: list[tuple[complex, complex, complex]] = [
    (
        0.24299045366570837 + 1.061487013346528j,
        2.536106612677487 - 2.453937060212436j,
        -0.0687982322242251 - 3.1253909770756554j,
    ),
    (-1 + 1j, -1 - 1j, 1.9539),
]
