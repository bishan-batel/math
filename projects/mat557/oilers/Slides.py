from re import Pattern
import sys
import os


from manim_slides.slide import Slide
from manim_slides.slide.animation import Wipe
from manimlib import *  # pyright: ignore

from projects.mat557.oilers.common import *
from projects.mat557.oilers.fractal import ROOT_COLORS_BRIGHT, ROOT_COLORS_DEEP

ADD_WAIT_TIME = False


def add_wait(slide):
    if ADD_WAIT_TIME:
        slide.wait_time_between_slides = 1 if ADD_WAIT_TIME else 0


class FirstTitle(Slide):
    def construct(self):
        add_wait(self)

        text = Title("Dynamics of Rational Root-Finding Methods", font_size=60).center()

        self.play(Write(text))

        author = Text("Kishan S Patel").next_to(text, BOTTOM).set_opacity(0)

        self.play(
            Write(author),
            author.animate.next_to(text, BOTTOM),
            author.animate.set_opacity(1),
        )

        self.next_slide()

        goals_title = Title("Goals").shift(DOWN * 0.5)

        self.play(FadeOut(text), FadeOut(author), Write(goals_title))

        goals = BulletedList(
            r"How does Newtons Method work in $\mathbb C$?",
            r"When does Newtons Method fail?",
            r"Pretty Fractals ",
            r"Why should we care?",
            r"How can this apply to other fractals?",
        ).next_to(goals_title, DOWN * 1.2)

        # newtons method in CC
        self.next_slide()
        self.play(Write(goals[0]))

        # newtons method fails
        self.next_slide()

        fractals_plane = (
            ComplexPlane(
                x_range=(-2, 2, 1),
                y_range=(-2, 2, 1),
                faded_line_ratio=1,
                width=3.5,
                height=3.5,
                background_line_style={"stroke_width": 1.5, "stroke_opacity": 0.8},
            )
            .center()
            .shift(DOWN * 1)
        )

        dot1, dot2 = (
            Dot(fractals_plane.n2p(pos), radius=0.1, fill_color=BLUE)
            for pos in [-0.5 + 1.5j, 1.5 - 1.5j]
        )
        kw = {"path_arc": PI / 3, "buff": 0.1, "thickness": 2.0}

        arrows = VGroup(
            Arrow(dot1, dot2, **kw, fill_color=BLUE_A),
            Arrow(dot2, dot1, **kw, fill_color=BLUE_A),
        )

        self.play(
            Write(goals[1]),
            LaggedStart(
                FadeIn(fractals_plane),
                FadeIn(dot1),
                FadeIn(dot2),
                ShowCreation(arrows, run_time=1.5),
            ),
        )

        self.play(Swap(dot1, dot2))
        self.play(Swap(dot1, dot2))

        # newtons method fractals
        self.next_slide()

        self.play(
            Wipe(
                current=(dot1, dot2, arrows, fractals_plane),
                shift=DOWN,
            ),
            Write(goals[2]),
        )

        # why should we care
        self.next_slide()
        self.play(Write(goals[3]))

        # How can we apply to other fractals
        self.next_slide()
        self.play(Write(goals[4]))

        self.next_slide()
        self.wipe(self.mobjects_without_canvas)


class AbstractNewtonsMethodRealVisualisation(Slide):
    function = SIMPLE_POLY_EXAMPLES[0]
    x0 = ValueTracker(0)
    axes: Axes
    func_graph: ParametricCurve
    limit_point: VGroup

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

    def make_function(self, function=None, bind=False):
        if function is not None:
            self.function = function

        self.func_graph = self.axes.get_graph(
            function=lambda t: self.function(t), bind=True
        )
        return self.func_graph

    def make_axes(self):
        self.axes = Axes().shift(RIGHT * 0.2)
        self.axes.add_coordinate_labels()
        return self.axes

    def perform_one_step(self, speed: float = 0.8):
        x = float(self.x0.get_value())
        f_x = self.function(x)
        m = self.function.deriv()(x)

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

            f = self.function
            df = self.function.deriv()

            for _ in range(40):
                z = points[-1]
                points.append(z - f(z) / df(z))

            return z

        # self.limit_point.f_always.move_to(
        #     lambda: self.func_graph.get_point_from_function(
        #         np.real(limit_behavior(self.x0.get_value()))
        #     )
        # )
        return self.limit_point


class WhatIsNewtons(AbstractNewtonsMethodRealVisualisation):
    function: Polynomial = SIMPLE_POLY_EXAMPLES[0]

    def construct(self) -> None:
        (axes, func_graph, x0, x0_marker, limit_point) = self.setup_graphs()

        add_wait(self)

        method_title = Text("Newtons Method")

        self.play(FadeIn(method_title))

        tex_kw = {
            "isolate": ["x_{n+1}", "x_n", "z_n", "z_{n+1}", "P", "P'"],
            "t2c": {
                "x_{n+1}": YELLOW,
                "x_n": YELLOW,
                "z_{n+1}": BLUE_B,
                "z_n": BLUE_B,
            },
        }

        self.next_slide()

        newtons_tex = Tex(
            r"{x_{n+1}}", "=", "{x_n}", "-", r"\frac{P({x_n})}{P'({x_n})}", **tex_kw
        )

        self.play(
            method_title.animate.to_edge(UP),
            Write(newtons_tex),
        )

        self.next_slide()

        self.play(
            method_title.animate.to_corner(UL),
            newtons_tex.animate.scale(0.8).to_corner(DL),
            method_title.animate.set_opacity(0.8),
            ShowCreation(axes, run_time=2),
        )
        self.play(FadeIn(func_graph, run_time=1))

        self.next_slide()

        self.play(FadeIn(x0_marker))

        def iterate_alot():
            for _ in range(6):
                self.perform_one_step(0.01)

        self.perform_one_step()
        self.perform_one_step()
        self.perform_one_step()

        # self.add(limit_point)

        # self.embed()

        self.next_slide()

        self.play(
            FadeOut(x0_marker),
            FadeOut(axes),
            FadeOut(func_graph),
            newtons_tex.animate.center(),
        )

        self.remove(x0_marker, axes, func_graph)

        self.next_slide()

        generic_polynomial = Tex(
            r"P(x) = c_0 + c_1 x + c_2 x^2 + c_3 x^3 + \cdots",
            isolate=[r"c_\d", r"x", r"z"],
        )

        self.next_slide()

        self.play(newtons_tex.animate.to_corner(), Write(generic_polynomial))

        question = TexText(
            r"What happens if $x_n , x_{n+1}$ are complex?", **tex_kw
        ).next_to(generic_polynomial, DOWN)
        self.play(Write(question))

        self.next_slide()

        self.play(
            *(Indicate(part) for part in generic_polynomial.get_parts_by_tex("x"))
        )

        complex_poly = Tex(
            r"P(z) = c_0 + c_1 z + c_2 z^2 + c_3 z^3 + \cdots",
            isolate=[r"c_\d", r"x", r"z"],
            t2c={"z": BLUE_B},
        )

        self.play(
            TransformMatchingTex(
                generic_polynomial, complex_poly, key_map={"x": "z"}, run_time=0.5
            )
        )

        self.next_slide()

        complex_root_poly = Tex(
            r"P(z) = (z - r_1)(z - r_2)(z-r_3) \cdots (z-r_n)",
            isolate=[r"c_\d", r"x", r"z"],
            t2c={
                r"r_1": RED_A,
                r"r_2": GREEN_A,
                r"r_3": BLUE_A,
                r"r_n": GREY,
            },
        )
        self.play(
            TransformMatchingTex(
                complex_poly,
                complex_root_poly,
                # path_arc=PI / 2,
                key_map={
                    "x": "z",
                    "c_0": "r_1",
                    "c_1": "r_2",
                    "c_2": "r_1",
                    "c_3": "r_n",
                },
            )
        )

        self.next_slide()

        def swap_roots(i, j):
            self.play(
                Swap(
                    complex_root_poly.get_part_by_tex(f"r_{i}"),
                    complex_root_poly.get_part_by_tex(f"r_{j}"),
                )
            )

        swap_roots(1, 3)
        swap_roots(2, 1)
        swap_roots(3, 1)
        swap_roots(3, 2)

        self.embed()


from sympy import *


class NewtonCubic(Slide):
    def construct(self) -> None:
        add_wait(self)

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
            "r_1": RED_A,
            "r_{1}": RED_A,
            "r_2": GREEN_A,
            "r_{2}": GREEN_A,
            "r_3": BLUE_A,
            "r_{3}": BLUE_A,
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

        self.play(Write(coeff_cubic))

        self.next_slide()

        factored_cubic = Tex(
            "f(z)",
            "=",
            "d",
            "(z-r_{1})",
            "(z-r_{2})",
            "(z-r_{3})",
            isolate=to_isolate,
            t2c=colors,
        )

        sym_df = simplify(
            Derivative(Symbol("d") * cubic(z), z, evaluate=True), ratio=oo
        )
        factored_cubic_deriv = Tex(
            "f'(z)",
            "=",
            latex(sym_df),
            t2c=colors,
            isolate=to_isolate,
        )

        newtons_method = Tex(
            "\\mathcal N(z)",
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
            "\\mathcal{N}(z)",
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
            "\\mathcal{N}(z)",
            "=",
            latex(equation),
            isolate=to_isolate,
            t2c=colors,
        )

        self.play(
            TransformMatchingTex(
                newtons_method_substituted,
                newtons_s2,
                path_arc=10 * DEGREES,
            ),
            self.frame.animate.scale(1.3),
        )

        equation = factor(equation, deep=True)
        newtons_3 = Tex(
            "\\mathcal{N}(z)",
            "=",
            latex(equation),
            isolate=to_isolate,
            t2c=colors,
        )

        self.play(
            TransformMatchingTex(
                newtons_s2,
                newtons_3,
                path_arc=10 * DEGREES,
            ),
            self.frame.animate.scale(0.7),
        )

        # equation = numer(equation) / denom(equation)
        eq_div = Derivative(equation, z, evaluate=True)
        eq_div = factor((eq_div), gaussian=True, deep=True)
        eq_div = simplify(eq_div, ratio=oo)
        # eq_div = numer(eq_div) / factor(denom(eq_div), deep=True)

        newtons_deriv = Tex(
            "\\mathcal{N}'(z)",
            "=",
            latex(eq_div),
            isolate=to_isolate,
            t2c=colors,
        )
        self.play(
            TransformMatchingTex(
                newtons_3,
                newtons_deriv,
                path_arc=10 * DEGREES,
            ),
            self.frame.animate.scale(1.0),
        )

        #
        eq_roots = dict.keys(roots(numer((eq_div)), z))

        self.next_slide()
        self.play(
            Write(
                Tex(f"\\left\\{{ {','.join((latex(r) for r in eq_roots))} \\right\\}}")
            ),
            FadeOut(newtons_deriv),
        )


# SYM_CUBIC_FN = (
#     (Symbol("z") - Symbol("r_1"))
#     * (Symbol("z") - Symbol("r_2"))
#     * (Symbol("z") - Symbol("r_3"))
# )
#
# SYM_CUBIC_FN_DERIV = simplify(Derivative(SYM_CUBIC_FN, evaluate=True), ratio=oo)
#
# SYM_NEWTONS = Symbol("z") - Function("f")(Symbol("z")) / Derivative(
#     Function("f")(Symbol("z")), Symbol("z")
# )
#
# SYM_NEWTONS_CUBIC = Symbol("z") - SYM_CUBIC_FN / SYM_CUBIC_FN_DERIV
# SYM_NEWTONS_CUBIC_DERIV = simplify(
#     factor(Derivative(SYM_NEWTONS_CUBIC, Symbol("z"), evaluate=True), deep=True),
#     ratio=oo,
# )


class MontelsThereom(Slide):
    def construct(self) -> None:
        add_wait(self)

        title = TexText("\\emph{Montels Thereom}").center()
        self.play(Write(title))

        self.next_slide()

        montel_desc = TexText(
            r"A family of holomorphic functions $\mathcal{F}: U \to \mathbb{C} \setminus \{a, b\}, U \subseteq{\mathbb{C}}$",
            " is normal",
            font_size=34,
            isolate=["\\mathbb{C}"],
            t2c={"normal": RED_A, "\\mathbb{C}": RED_A},
        ).center()

        self.play(Write(montel_desc), title.animate.next_to(montel_desc, UP))


class WhatIsOilersMethod(Slide):
    def construct(self) -> None:
        add_wait(self)

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


# df = (f(z) - f(zp)) / (z - zp)
# dfp = (f(zp) - f(zpp)) / (zp - zpp)
# d2f = (df - dfp) / (z - zpp)
# return z - (f(z) * df) / ((df * df) - f(z) * d2f)
