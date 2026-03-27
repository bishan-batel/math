import sys
import os

from custom.shader_obj import *

from manimlib import *  # pyright: ignore
from numpy.polynomial import Polynomial
import numpy as np
from manim_slides.slide import Slide

from projects.mat557.oilers.fractal import ROOT_COLORS_DEEP, FractalNewton, c2v
from projects.mat557.oilers.methods import *
from projects.mat557.oilers.common import *


class Playground(Slide):
    trackers: list[ComplexValueTracker] = []

    def construct(self):
        if not hasattr(self, "next_slide"):

            def next_slide(**kargs):
                pass

            self.next_slide = next_slide

        self.plane = (
            ComplexPlane(x_range=(-5, 5), y_range=(-6, 6), faded_line_ratio=2)
            .add_coordinate_labels()
            .set_opacity(0.3)
        )

        self.add(self.plane)

        self.method = newtons

        # DEFAULT_COEFFICIENTS = np.array([-5, 4, 0, 1])
        # COEFFICIENTS = np.array([2, -2, 0, 1])

        def anim_stream(*zs):
            if is_oiler_fan(self.method):
                return zs

            # z = z_p[0] + 1j * z_p[1]
            return np.array(map(lambda z: [-z[1], z[0]], zs))

            z = current_method(z, zp=0, zpp=0)
            return np.array([np.real(z), np.imag(z)])

        self.roots = [
            ComplexValueTracker().set_value(root) for root in FIXED_POINT_EXAMPLES[0]
        ]

        # Create a shader mobject (a self.plane with shader code)
        scale_factor = ValueTracker(1)
        shader_obj = FractalNewton(roots=[r.get_value() for r in self.roots])
        shader_obj.set_z_index(-20)
        shader_obj.f_always.set_scale_factor(lambda: scale_factor.get_value())
        shader_obj.f_always.set_roots(lambda: [root.get_value() for root in self.roots])
        shader_obj.f_always.set_mode(lambda: method_to_mode(self.method))
        self.add(shader_obj)

        def current_method(z: complex, zp: complex, zpp: complex):
            f = shader_obj.polynomial()
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

        def make_path(z: complex):
            values = [z]
            if is_oiler_fan(self.method):
                f = shader_obj.polynomial()
                zpp = z
                zp = zpp + ((1 + np.sqrt(5.0)) / 2.0)
                z = zp - f(zp) / ((f(zp) - f(zpp)) / (zp - zpp))
                values = [zpp, zp, z]

            # c = z
            # values = [c]

            for _ in range(100):
                zp = 0
                zpp = 0
                if is_oiler_fan(self.method):
                    zp = values[-2]
                    zpp = values[-3]

                values.append(current_method(z=values[-1], zp=zp, zpp=zpp))

            values = [self.plane.n2p(z) for z in values]

            return (
                VMobject(stroke_width=1.5, color=BLUE)
                .set_points_as_corners(values)
                .add(*(Dot(z, radius=0.03) for z in values))
            )

        # initial value
        self.tracker = self.roots[0]
        z0 = ComplexValueTracker()
        z0.set_value(1j)

        self.z0 = z0

        shader_obj.f_always.set_uniforms(lambda: {"z0": c2v(self.z0.get_value())})

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
