from manimlib import *
from typing import *
import numpy as np
from numpy.polynomial import Polynomial

from manim_slides.slide import Slide

SIMPLE_POLY_EXAMPLES = [
    Polynomial(coef=[2, -1, 4, -2]) * 0.1,
]

FIXED_POINT_EXAMPLES: list[tuple[complex, complex, complex]] = [
    (
        0.24299045366570837 + 1.061487013346528j,
        2.536106612677487 - 2.453937060212436j,
        -0.0687982322242251 - 3.1253909770756554j,
    ),
    (-1 + 1j, -1 - 1j, 1.9539),
]


class AbstractNewtonsMethodRealVisualisation(Slide):
    function: Callable[[float], float] = SIMPLE_POLY_EXAMPLES[0]
    function_deriv: None | Callable[[float], float] = None
    x0 = ValueTracker(0)
    axes: Axes
    func_graph: ParametricCurve
    limit_point: GlowDot
    n = 0

    def setup_graphs(self):
        self.make_axes()
        self.make_function()
        self.x0
        self.make_x0_marker()
        self.make_limiting_marker()

        return (self.axes, self.func_graph, self.x0, self.x0_marker, self.limit_point)

    def make_x0_marker(self):

        v_line = self.axes.get_v_line_to_graph(
            self.x0.get_value(), self.func_graph, color=GREY
        )

        v_line.f_always.become(
            lambda: self.axes.get_v_line_to_graph(
                self.x0.get_value(), self.func_graph, color=GREY
            )
        )

        self.x0_marker = VGroup(
            v_line,
            Dot().add_updater(
                lambda d: d.move_to(
                    self.func_graph.get_point_from_function(self.x0.get_value())
                )
            ),
            ArrowTip(
                angle=PI / 2, width=0.2, length=0.2, fill_color=YELLOW
            ).add_updater(
                lambda m: m.move_to(self.axes.x_axis.n2p(self.x0.get_value()), UP)
            ),
        )
        return self.x0_marker

    def make_function(self, function=None, bind=True):
        if function is not None:
            self.function = function

        self.func_graph = self.axes.get_graph(
            function=lambda t: self.function(t), bind=bind
        )
        return self.func_graph

    def f(self, z: float) -> float:
        return self.function(z)

    def df(self, z: float) -> float:
        deriv = self.function_deriv
        if deriv is not None:
            return deriv(z)

        if self.function.deriv != None:
            return self.function.deriv()(z)

        raise Exception("No derivative")

    def make_axes(self):
        self.axes = Axes().shift(RIGHT * 0.2)
        self.axes.add_coordinate_labels()
        return self.axes

    def perform_one_step(self, speed: float = 0.8):
        self.n += 1
        x = float(self.x0.get_value())
        f_x = self.f(x)
        m = self.df(x)

        line_func = self.axes.get_graph(
            function=lambda t: m * (t - x) + f_x, color=RED, opacity=0.8
        )
        line = line_func
        self.play(ShowCreation(line, lag_ratio=0.5, run_time=speed))

        next_x = x - f_x / m

        intersection = Dot(line_func.get_point_from_function(next_x), color=RED)

        self.play(ShowCreation(intersection, run_time=speed / 2))
        self.play(self.x0.animate(run_time=speed).set_value(next_x))
        self.play(
            FadeOut(line, run_time=speed),
            FadeOut(intersection, run_time=speed),
        )
        self.remove(line, intersection)

    def make_limiting_marker(self):
        self.limit_point = GlowDot()

        def limit_behavior(z):
            points = [z]

            for _ in range(40):
                z = points[-1]
                points.append(z - self.f(z) / self.df(z))

            return z

        self.limit_point.f_always.move_to(
            lambda: self.axes.input_to_graph_point(
                np.real(limit_behavior(self.x0.get_value())), self.func_graph
            )
        )
        return self.limit_point
