import sys
import os

import scipy.integrate

from custom.shader_obj import *

from manimlib import *  # pyright: ignore
from numpy.polynomial import Polynomial
import numpy as np
from manim_slides.slide import Slide


def c(k: int):
    return lambda x: np.cos(2 * PI * k * x)


def inner_prod(f, g, a=0, b=1):
    return scipy.integrate.quad(lambda t: f(t) * g(t), a, b)


def project(v, u):
    v2 = inner_prod(v, v)


c0 = c(0)
c1 = c(1)
c2 = c(2)
c3 = c(3)


class Fourier(Scene):
    n = ValueTracker(1)

    def square(self, k, x):
        return (4 / (PI * (2 * k + 1))) * np.sin(2 * PI * (k + 1) * x)

    def square_wave(self, x: float):
        sum = 0
        for k in range(0, int(self.n.get_value())):
            sum += self.square(k, x)
        return sum

    def construct(self):
        axes = Axes(x_range=(0, 2, 1), y_range=(-2, 2, 1), width=FRAME_WIDTH * 0.8)
        axes.add_coordinate_labels()
        self.add(axes)

        self.add(
            VGroup(
                Tex("N="),
                DecimalNumber(0, num_decimal_places=0).add_updater(
                    lambda x: x.set_value(self.n.get_value())
                ),
            )
            .arrange(RIGHT)
            .to_corner(UL)
        )
        self.add(axes.get_graph(lambda x: self.square_wave(x), bind=True))

        self.embed()
