import sys
import os

sys.path.append(os.getcwd())

import numpy as np
from manim_slides.slide import Slide  # pyright: ignore
from manimlib import *
from numpy.polynomial import Polynomial

from fractal import FractalNewton, ShaderMobject


def newtons(z: complex, f: Polynomial, df: Polynomial):
    return z - f(z) / df(z)


def halleys(z: complex, f: Polynomial, df: Polynomial, d2f: Polynomial):
    return z - (f(z) * df(z)) / ((df(z) ** 2) - 0.5 * f(z) * d2f(z))


COLORS = [BLUE, GREEN_D, RED_D, PURPLE_D]


class FirstTitle(Slide):
    skip_reversing = True

    def construct(self):
        text = Tex("Oilers' Method")
        self.next_slide()
        self.play(FadeIn(text))


class NF(Slide):
    skip_reversing = True
    trackers = []

    def construct(self):
        if not hasattr(self, "next_slide"):

            def next_slide(**kargs):
                pass

            self.next_slide = next_slide
        self.plane = ComplexPlane(x_range=(-5, 5), y_range=(-6, 6), faded_line_ratio=2)
        self.plane.add_coordinate_labels(font_size=24)
        self.plane.opacity = 0.6
        self.plane.set_opacity(0.8)

        # self.camera.frame.set_width(self.plane.get_width())

        self.add(self.plane)

        # polynomial & roots
        LAMBDA = 5
        COEFFICIENTS = np.array([-LAMBDA, LAMBDA - 1, 0, 1])
        # COEFFICIENTS = np.array([2, -2, 0, 1])
        # f = np.polynomial.Polynomial(COEFFICIENTS)
        # df = f.deriv()
        # d2f = df.deriv()

        roots = [
            ComplexValueTracker().set_value(root)
            for root in np.roots(COEFFICIENTS[::-1])
        ]

        self.roots = roots

        # Create a shader mobject (a self.plane with shader code)
        shader_obj = FractalNewton(roots=np.roots(COEFFICIENTS[::-1]))

        shader_obj.set_z_index(-20)

        shader_obj.f_always.set_roots(lambda: [root.get_value() for root in roots])

        self.add(shader_obj)

        def current_method(z: complex):
            f = shader_obj.polynomial()
            df = f.deriv()
            return newtons(z, f=f, df=df)

        # fractal = gen_fractal_image(self.plane, roots=roots_num(), method=current_method)

        def root_updater(tracker):
            return lambda m: m.move_to(self.plane.n2p(tracker.get_value()))

        root_dots = [
            Tex(f"r_{i + 1}").set_z_index(5).add_updater(root_updater(root))
            for (i, root) in enumerate(roots)
        ]

        self.add(*root_dots)

        self.next_slide()

        def make_path(z: complex):
            values = [z]

            for _ in range(40):
                values.append(current_method(values[-1]))

            points = [Dot(self.plane.n2p(z), radius=0.05) for z in values]

            lines = VGroup()
            for i in range(len(points) - 1):
                line = Line(
                    points[i].get_center(),
                    points[i + 1].get_center(),
                    stroke_width=4,
                    color=BLUE,
                )
                lines.add(line)
            lines.add(*points)
            return lines

        # initial value
        z0 = ComplexValueTracker()
        self.tracker = roots[0]
        z0.set_value(1j)

        self.z0 = z0

        z0_marker = (
            Tex("z_0")
            .set_z_index(10)
            .set_color(RED)
            .add_updater(lambda m: m.move_to(self.plane.n2p(z0.get_value())))
        )

        z0_path = always_redraw(lambda: make_path(z0.get_value()))
        self.add(z0_marker, z0_path)
        self.next_slide(loop=True)

        for v, run_time in [
            (0 + 1j, 2),
            (-0.5 + 2j, 2),
            (1 - 2.02j, 3),
            (-0.5 - 0.8j, 2),
            (0.0 - 0.0, 3),
            (0.2 - 0.0, 3),
            (-1.0 - 0.0, 3),
        ]:
            self.play(z0.animate(run_time=run_time).set_value(v))  # pyright: ignore
            self.wait(0.5)

        self.play(z0.animate(run_time=1).set_value(1j))  # pyright: ignore

        self.next_slide()

        n = 30
        xspace = np.linspace(
            self.plane.x_range[0] * 0.5, self.plane.x_range[1] * 0.5, n
        )
        yspace = np.linspace(
            self.plane.y_range[0] * 0.5, self.plane.y_range[1] * 0.5, n
        )

        points: list[complex] = []
        point_dots: list[Dot] = []
        for x in xspace:
            for y in yspace:
                points.append(x + 1j * y)
                point_dots.append(Dot(radius=0.03).move_to(self.plane.n2p(x + 1j * y)))

        self.play(*(ShowCreation(dot) for dot in point_dots))

        for _ in range(20):
            for i, z in enumerate(points):
                points[i] = current_method(z)
            self.wait(1)
            self.play(
                *(
                    dot.animate.move_to(self.plane.n2p(points[i]))
                    for i, dot in enumerate(point_dots)
                    if np.min([np.abs(points[i] - r.get_value()) for r in roots]) > 1e-3
                )
            )

        self.next_slide(loop=True, auto_next=True)

        for _ in range(10):
            for i, z in enumerate(points):
                points[i] = current_method(z)
            self.wait(1)
            self.play(
                *(
                    dot.animate.move_to(self.plane.n2p(points[i]))
                    for i, dot in enumerate(point_dots)
                    if np.min([np.abs(points[i] - r.get_value()) for r in roots]) > 1e-3
                )
            )

        self.next_slide()

    def on_mouse_drag(self, point, d_point, buttons: int, modifiers: int):
        p = point[0] + 1j * point[1]

        min_tracker = None
        min_dist = 1000
        for tracker in [self.z0, *self.roots]:
            dist = abs(tracker.get_value() - p)
            if dist < min_dist:
                min_tracker = tracker
                min_dist = dist
        if min_tracker is not None:
            min_tracker.set_value(p)
