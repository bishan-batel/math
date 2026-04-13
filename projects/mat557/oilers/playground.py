import sys
import os

from sympy import limit

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

        self.roots = [
            ComplexValueTracker().set_value(root) for root in FIXED_POINT_EXAMPLES[0]
        ]

        def set_coefs(c0, c1, c2, c3):
            new_roots = Polynomial((c0, c1, c2, c3)).roots()
            for r, n_r in zip(self.roots, new_roots):
                r.set_value(n_r)

        # Create a shader mobject (a self.plane with shader code)
        scale_factor = ValueTracker(1)
        fractal = FractalNewton(roots=[r.get_value() for r in self.roots])
        fractal.set_z_index(-20)
        fractal.pin(self)
        fractal.f_always.set_scale_factor(lambda: scale_factor.get_value())
        fractal.f_always.set_roots(lambda: [root.get_value() for root in self.roots])
        fractal.f_always.set_mode(lambda: method_to_mode(self.method))
        self.add(fractal)

        def current_method(z: complex, zp: complex, zpp: complex):
            f = fractal.polynomial()
            df = f.deriv()
            return self.method(z, zp=zp, zpp=zpp, f=f, df=df, d2f=df.deriv())

        # fractal = gen_fractal_image(self.plane, roots=roots_num(), method=current_method)

        def root_updater(tracker):
            return lambda m: m.move_to(self.plane.n2p(tracker.get_value()))

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
            .add_updater(root_updater(root))
            for (i, root) in enumerate(self.roots)
        ]

        self.add(*root_dots)

        self.next_slide()

        self.fix_z0_to_midpoint = False
        self.show_path = True
        self.path_iterations = 20

        def make_path(z: complex):
            if self.fix_z0_to_midpoint:
                self.z0.set_value(sum(r.get_value() for r in self.roots) / 3.0)
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

                values.append(current_method(z=values[-1], zp=zp, zpp=zpp))
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

        self.embed()

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

        self.next_slide(loop=True, auto_next=True)

    def on_resize(self, width: int, height: int) -> None:
        if self.window is not None:
            self.window.fixed_aspect_ratio = float(FRAME_WIDTH) / float(FRAME_HEIGHT)
            self.window.set_default_viewport()

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
