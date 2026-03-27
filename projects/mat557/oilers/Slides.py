import sys
import os


from manim_slides.slide import Slide
from custom.shader_obj import SlangShaderMobject
from manimlib import *  # pyright: ignore

from projects.mat557.oilers.common import *


class FirstTitle(Slide):
    def construct(self):
        text = TexText("Dynamics of Householder Methods")

        self.play(Write(text))

        author = Text("Kishan S Patel").next_to(text, BOTTOM).set_opacity(0)
        self.play(
            FadeIn(author),
            author.animate.next_to(text, BOTTOM),
            author.animate.set_opacity(1),
        )
        self.next_slide()

        self.embed()


class WhatIsNewtons(Slide):
    poly = Polynomial(coef=[2, -1, 4, -2]) * 0.1

    def construct(self) -> None:
        newtons_tex = Tex(r"\mathcal N(z)", "=", "z", "-", r"\frac{f(z)}{f'(z)}")

        self.play(Write(newtons_tex, run_time=0.5))

        self.next_slide()

        axes = Axes()
        axes.add_coordinate_labels()

        func = axes.get_graph(function=self.poly)

        self.play(newtons_tex.animate.to_corner(UL), ShowCreation(axes))
        self.play(ShowCreation(func))

        x_n = ValueTracker(1)

        self.next_slide()

        self.play(
            ShowCreation(
                always_redraw(
                    lambda: VGroup(
                        axes.get_v_line_to_graph(x_n.get_value(), func, color=GREY),
                        Dot(axes.x_axis.n2p(x_n.get_value()), color=BLUE),
                        Dot(func.get_point_from_function(x_n.get_value())),
                    )
                )
            )
        )

        def one_step(speed: float = 0.8):
            x = x_n.get_value()
            f_x = self.poly(x)
            m = self.poly.deriv()(x)

            line_func = axes.get_graph(
                function=lambda t: m * (t - x) + f_x, color=RED, opacity=0.8
            )
            line = line_func
            self.play(ShowCreation(line, run_time=speed))

            next_x = x - f_x / self.poly.deriv()(x)

            intersection = Dot(line_func.get_point_from_function(next_x), color=RED)

            self.play(ShowCreation(intersection, run_time=speed / 2))
            self.play(x_n.animate(run_time=speed).set_value(next_x))
            self.play(
                FadeOut(line, run_time=speed),
                FadeOut(intersection, run_time=speed),
            )
            self.remove(line, intersection)

        one_step()
        self.embed()
        self.wait(1)
        one_step()
        self.wait(1)
        one_step()

        self.embed(show_animation_progress=False)


class WhatIsOilersMethod(Slide):
    def construct(self) -> None:
        self.next_slide()

        oilers_tex = Tex(
            r"\mathcal{O}(z_{n+1})",
            r"=",
            r"\frac{f(z)"
            + r"f[z_{n-1}, z_{n}] "
            + r"}{ \left( "
            + r"f[z_{n-1},z_{n}] \right)^{2} - f(z_n)f[z_{n-2}, z_n] "
            + r"}",
        )

        self.play(Write(oilers_tex))
        self.embed(close_scene_on_exit=False, show_animation_progress=True)


# df = (f(z) - f(zp)) / (z - zp)
# dfp = (f(zp) - f(zpp)) / (zp - zpp)
# d2f = (df - dfp) / (z - zpp)
# return z - (f(z) * df) / ((df * df) - f(z) * d2f)
