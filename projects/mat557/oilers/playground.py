import sys
import os

from sympy import limit
from sympy.polys.polyoptions import Frac

from custom.shader_obj import *

from manimlib import *  # pyright: ignore
from numpy.polynomial import Polynomial
import numpy as np
from manim_slides.slide import Slide

from projects.mat557.oilers.fractal import ROOT_COLORS_DEEP, FractalNewton, c2v
from projects.mat557.oilers.methods import *
from projects.mat557.oilers.common import *

GOLDEN_RATIO = (1 + np.sqrt(5.0)) / 2.0

SECANT_OFFSET = 0.01


class Playground(Slide):
    drag_to_pan = False
    degree = 3
    roots: list[ComplexValueTracker]
    trackers: list[ComplexValueTracker] = []

    def construct(self):
        self.plane = (
            ComplexPlane(x_range=(-10, 10), y_range=(-6, 6), faded_line_ratio=2)
            .add_coordinate_labels()
            .set_opacity(0.3)
        )

        self.add(self.plane)

        self.method = newtons

        # DEFAULT_COEFFICIENTS = np.array([-5, 4, 0, 1])
        # COEFFICIENTS = np.array([2, -2, 0, 1])

        relaxed = ValueTracker(1)

        self.roots = [
            ComplexValueTracker(
                np.exp(1j * float(i) / FractalNewton.MAX_DEGREE * 2 * PI)
            )
            for i in range(0, FractalNewton.MAX_DEGREE)
        ]

        for root, value in zip(self.roots, FIXED_POINT_EXAMPLES[0]):
            root.set_value(value)

        def set_coefs(c0, c1, c2, c3):
            new_roots = Polynomial((c0, c1, c2, c3)).roots()
            for r, n_r in zip(self.roots, new_roots):
                r.set_value(n_r)

        # Create a shader mobject (a self.plane with shader code)
        scale_factor = ValueTracker(1)
        fractal = self.fractal = FractalNewton(
            roots=[r.get_value() for r in self.roots]
        )
        fractal.set_z_index(-20)
        fractal.pin(self)
        fractal.f_always.set_scale_factor(lambda: scale_factor.get_value())
        fractal.f_always.set_roots(
            lambda: [root.get_value() for root in self.roots], lambda: self.degree
        )
        fractal.f_always.set_mode(lambda: method_to_mode(self.method))
        fractal.f_always.set_relaxed_newtons(lambda: relaxed.get_value())
        self.add(fractal)

        def current_method(z: complex, zp: complex, zpp: complex, relaxed=1):
            f = fractal.polynomial()
            df = f.deriv()
            return self.method(
                z, zp=zp, zpp=zpp, f=f, df=df, d2f=df.deriv(), relaxed=relaxed
            )

        # fractal = gen_fractal_image(self.plane, roots=roots_num(), method=current_method)

        def root_updater(tracker, i: int):
            return lambda m: m.move_to(self.plane.n2p(tracker.get_value())).set_opacity(
                1.0 if i < self.degree else 0.0
            )

        root_dots = [
            # Tex(f"r_{i + 1}").set_z_index(5).add_updater(root_updater(root))
            Dot(
                fill_color=ROOT_COLORS_DEEP[i],
                stroke_color=BLACK,
                stroke_width=3,
                opacity=0.5,
                radius=0.05,
            )
            .set_z_index(5)
            .add_updater(root_updater(root, i))
            for (i, root) in enumerate(self.roots)
        ]

        self.add(*root_dots)

        self.next_slide()

        self.fix_z0_to_midpoint = False
        self.show_path = True
        self.path_iterations = 20

        def make_path(z: complex):
            if self.fix_z0_to_midpoint:
                self.z0.set_value(
                    sum(r.get_value() for r in self.curr_roots()) / float(self.degree)
                )
            if not self.show_path:
                return VMobject()

            values = [z]
            if is_oiler_fan(self.method):
                f = fractal.polynomial()
                zpp = z
                zp = zpp + GOLDEN_RATIO
                z = zp - f(zp) / ((f(zp) - f(zpp)) / (zp - zpp))
                values = [zpp, zp, z]
            elif is_secant(self.method):
                zp = z
                z = z + SECANT_OFFSET
                values = [zp, z]

            # c = z
            # values = [c]

            for _ in range(self.path_iterations):
                zp = 0
                zpp = 0
                if is_oiler_fan(self.method):
                    zp = values[-2]
                    zpp = values[-3]
                elif is_secant(self.method):
                    zp = values[-2]

                values.append(
                    current_method(
                        z=values[-1],
                        zp=zp,
                        zpp=zpp,
                        relaxed=fractal.get_relaxed_newtons(),
                    )
                )
                if abs(values[-1] - values[-2]) < 0.05:
                    break

            values = [self.plane.n2p(z) for z in values]

            gradient = list(Color("White").range_to(Color("Red"), len(values)))

            obj = VMobject(stroke_width=1.0, color=BLUE)

            for i in range(len(values) - 1):
                x = values[i]
                xn = values[i + 1]
                obj.add(
                    Arrow(
                        x,
                        xn,
                        buff=0.01,
                        thickness=2 * (1 - float(i) / (len(values) - 1)),
                        path_arc=PI / 4 / 4,
                    )
                )

            obj.add(
                *(
                    Dot(
                        z,
                        fill_color=gradient[i],
                        stroke_color=gradient[i],
                        radius=0.03 * (1.0 - float(i) / float(len(values))),
                    ).set_color(gradient[i])
                    for i, z in enumerate(values)
                )
            )

            return obj.set_submobject_colors_by_gradient(*gradient)

        # initial value
        self.tracker = self.roots[0]

        z0 = ComplexValueTracker()
        self.z0 = z0

        fractal.f_always.set_z0(lambda: self.z0.get_value())

        z0_marker = (
            Tex("z_0")
            .set_z_index(10)
            .scale(0.5)
            .set_color(RED)
            .add_updater(lambda m: m.move_to(self.plane.n2p(self.z0.get_value())))
        )

        z0_path = always_redraw(lambda: make_path(z0.get_value()))
        self.add(z0_marker, z0_path)

        def randomize_roots(scale=2.5, speed=0.5):
            self.play(
                *(
                    root.animate(run_time=speed).set_value(
                        np.exp(random.random() * 2 * PI * 1j)
                        * np.log(1e-3 + random.random())
                        * scale
                    )
                    for root in self.roots
                )
            )

        self.embed()

    def curr_roots(self) -> list[ComplexValueTracker]:
        return self.roots[0 : self.degree]

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        # if self.window is not None:
        #     self.window.fixed_aspect_ratio = float(FRAME_WIDTH) / float(FRAME_HEIGHT)
        #     self.window.set_default_viewport()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)

        if symbol == 97 and self.fractal is not None:
            self.fractal.set_parameter_space(not self.fractal.get_parameter_space())

    def on_mouse_drag(self, point, d_point, buttons: int, modifiers: int):
        super().on_mouse_drag(point, d_point, buttons, modifiers)

        # point = self.mouse_point.get_center()
        # print(self.mouse_drag_point.get_center())

        p = point[0] + 1j * point[1]

        min_tracker = None
        min_dist = 1000
        for tracker in [self.z0, *self.curr_roots()]:
            dist = abs(tracker.get_value() - p)
            if dist < min_dist:
                min_tracker = tracker
                min_dist = dist
        if min_tracker is not None:
            min_tracker.set_value(p)
