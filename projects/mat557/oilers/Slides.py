import sys
import os


from manim_slides.slide import Slide
from manimlib import *  # pyright: ignore

from projects.mat557.oilers.common import *
from projects.mat557.oilers.fractal import ROOT_COLORS_BRIGHT, ROOT_COLORS_DEEP


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
    poly: Polynomial = SIMPLE_POLY_EXAMPLES[0]

    def construct(self) -> None:
        newtons_tex = Tex(r"\mathcal N(z)", "=", "z", "-", r"\frac{f(z)}{f'(z)}")

        self.play(Write(newtons_tex, run_time=0.5))

        self.next_slide()

        axes = Axes()
        axes.add_coordinate_labels()

        func = axes.get_graph(function=lambda t: self.poly(t), bind=True)

        self.play(newtons_tex.animate.scale(0.8).to_corner(DL), ShowCreation(axes))
        self.play(ShowCreation(func))

        x_n = ValueTracker(1)

        self.next_slide()

        x_n_marker = always_redraw(
            lambda: VGroup(
                axes.get_v_line_to_graph(x_n.get_value(), func, color=GREY),
                Dot(func.get_point_from_function(x_n.get_value())),
                ArrowTip(
                    angle=PI / 2, width=0.2, length=0.2, fill_color=YELLOW
                ).move_to(axes.x_axis.n2p(x_n.get_value()), UP),
            )
        )

        func.add(x_n_marker)
        self.play(FadeIn(x_n_marker))

        def one_step(speed: float = 0.8):
            x = x_n.get_value()
            f_x = self.poly(x)
            m = self.poly.deriv()(x)

            line_func = axes.get_graph(
                function=lambda t: m * (t - x) + f_x, color=RED, opacity=0.8
            )
            line = line_func
            self.play(ShowCreation(line, lag_ratio=0.5, run_time=speed))

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
        self.wait(1)
        one_step()
        self.wait(1)
        one_step()

        # self.play(FadeOut(func))
        self.poly = Polynomial(np.array([1, -5, 0, 5]))

        self.play(
            TransformMatchingTex(
                newtons_tex,
                Tex(
                    r"\mathcal H(z)",
                    "=",
                    "z",
                    "-",
                    r"\frac{f(z)f'(z)}{ f'(z)^2 + \frac{1}{2}f(z)f''(z) }",
                )
                .scale(0.8)
                .to_corner(DL),
            )
        )

        self.embed(show_animation_progress=False)


from sympy import *


class NewtonCubic(Slide):
    def construct(self) -> None:
        to_isolate = [
            "r_1",
            "r_2",
            "r_3",
            "=",
            "d",
            "f(z)",
            "z",
            "r_{1}",
            "r_{2}",
            "r_{3}",
        ]
        r1, r2, r3 = symbols("r1:4")

        def cubic(z):
            return (z - r1) * (z - r2) * (z - r3)

        z = Symbol("z")

        colors = {
            "r_1": ROOT_COLORS_BRIGHT[0],
            "r_{1}": ROOT_COLORS_BRIGHT[0],
            "r_2": ROOT_COLORS_BRIGHT[1],
            "r_{2}": ROOT_COLORS_BRIGHT[1],
            "r_3": ROOT_COLORS_BRIGHT[2],
            "r_{3}": ROOT_COLORS_BRIGHT[2],
            "z": YELLOW,
        }

        coeff_cubic = Tex(
            "f(z)",
            "=",
            "c_1",
            "+",
            "c_2",
            "x",
            "+",
            "c_3",
            "x^2",
            "+",
            "c_4",
            "x^3",
            isolate=[
                *to_isolate,
            ],
            t2c=colors,
        )

        self.add(coeff_cubic)

        self.next_slide()

        factored_cubic = Tex(
            "f(z)",
            "=",
            "d",
            "(x-r_1)",
            "(x-r_2)",
            "(x-r_3)",
            isolate=to_isolate,
            t2c=colors,
        )

        sym_df = simplify(Derivative(Symbol("d") * cubic(z), z, evaluate=True))
        factored_cubic_deriv = Tex(
            "f'(z)",
            "=",
            latex(sym_df),
            t2c=colors,
            isolate=to_isolate,
        )

        newtons_method = Tex(
            "N(z)",
            "=",
            "z",
            "-",
            r"\frac{f(z)}{f'(z)}",
            isolate=to_isolate,
            t2c=colors,
        )

        self.play(
            TransformMatchingTex(
                coeff_cubic,
                factored_cubic,
            )
        )

        self.frame.save_state()
        self.play(
            Write(factored_cubic_deriv.next_to(factored_cubic, DOWN)),
            self.frame.animate.scale(1.3).shift([0, -0.5, 0]),
        )

        self.next_slide()

        self.play(
            Write(newtons_method.next_to(factored_cubic_deriv, DOWN)),
            self.frame.animate.shift([0, -0.5, 0]),
        )

        self.next_slide()

        sym_f = simplify(Symbol("d") * (z - r1) * (z - r2) * (z - r3))

        newtons_method_substituted = Tex(
            "N(z)",
            "=",
            latex(z - sym_f / sym_df),
            isolate=to_isolate,
            t2c=colors,
        )

        equation = z - sym_f / sym_df

        self.play(
            TransformMatchingTex(
                newtons_method,
                newtons_method_substituted.next_to(factored_cubic_deriv, DOWN, buff=2),
            ),
            self.frame.animate.shift([0, -2, 0]),
        )

        self.next_slide()
        self.play(
            *(Indicate(t) for t in factored_cubic.get_parts_by_tex("d")),
            *(Indicate(t) for t in factored_cubic_deriv.get_parts_by_tex("d")),
        )
        self.next_slide()

        self.play(
            FadeOut(factored_cubic),
            FadeOut(factored_cubic_deriv),
            newtons_method_substituted.animate.center(),
            self.frame.animate.move_to([0, 0, 0]),
        )

        self.next_slide()

        equation = simplify(z - cubic(z) / Derivative(cubic(z), z, evaluate=True))

        newtons_s2 = Tex(
            "N(z)",
            "=",
            latex(equation),
            isolate=to_isolate,
            t2c=colors,
        )

        self.play(
            TransformMatchingTex(
                newtons_method_substituted,
                newtons_s2,
            ),
            self.frame.animate.scale(1.3),
        )

        equation = factor(equation, deep=True)
        newtons_3 = Tex(
            "N(z)",
            "=",
            latex(equation),
            isolate=to_isolate,
            t2c=colors,
        )

        self.play(
            TransformMatchingTex(
                newtons_s2,
                newtons_3,
            ),
            self.frame.animate.scale(0.7),
        )

        # equation = numer(equation) / denom(equation)
        eq_div = Derivative(equation, z, evaluate=True)
        eq_div = factor((eq_div), gaussian=True, deep=True)
        eq_div = simplify(eq_div, ratio=oo)
        # eq_div = numer(eq_div) / factor(denom(eq_div), deep=True)

        newtons_deriv = Tex(
            "N'(z)",
            "=",
            latex(eq_div),
            isolate=to_isolate,
            t2c=colors,
        )
        self.play(
            TransformMatchingTex(
                newtons_3,
                newtons_deriv,
            ),
            self.frame.animate.scale(1.0),
        )

        eq_roots = ((r) for r in dict.keys(roots(numer((eq_div)), z)))

        self.embed()

        self.next_slide()
        self.play(
            Write(
                Tex(f"\\left\\{{ {','.join((latex(r) for r in eq_roots))} \\right\\}}")
            ),
            FadeOut(newtons_deriv),
        )


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
