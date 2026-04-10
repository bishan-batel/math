# pyright: reportGeneralTypeIssues=false

from re import Pattern
import sys
import os


from manim_slides.slide import Slide
from manim_slides.slide.animation import Wipe
from manimlib import *  # pyright: ignore


from custom.portrait import *
from projects.mat557.oilers.common import *
from projects.mat557.oilers.fractal import ROOT_COLORS_BRIGHT, ROOT_COLORS_DEEP
from sympy import *

ADD_WAIT_TIME = False


def add_wait(slide):
    if ADD_WAIT_TIME:
        slide.wait_time_between_slides = 1 if ADD_WAIT_TIME else 0


class FirstTitle(Slide):
    def construct(self):
        add_wait(self)

        text = Title("Dynamics of Rational Root-Finding Methods", font_size=60).center()

        self.play(Write(text))

        author = TexText("Kishan S Patel").next_to(text, BOTTOM).set_opacity(0)

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


class IntroNewtonsMethod(AbstractNewtonsMethodRealVisualisation):
    function: Polynomial = SIMPLE_POLY_EXAMPLES[1]

    def construct(self) -> None:
        add_wait(self)

        title = Title("Newtons", "Method")
        title_newton = title.select_part("Newtons")
        title_method = title.select_part("Method")

        # ====================================================
        #                People Introduction
        # ====================================================

        self.play(Write(title))

        self.add_to_canvas(title=title)

        portrait_newton = Group(
            PortraitWithCaption(
                image_path="./image/isaac_newton.jpg", name="Isaac Newton", caption=""
            ).shift(LEFT * 2.5),
            SurroundingRectangle(title_newton),
            Arrow(),
        )

        portrait_method = Group(
            PortraitWithCaption(
                image_path="./image/isaac_newton.jpg", name="John Method", caption=""
            ).shift(RIGHT * 2.5),
            SurroundingRectangle(title_method),
            Arrow(),
        )

        # arrows
        portrait_newton[2].become(
            Arrow(portrait_newton[1], portrait_newton[0], path_arc=PI / 6)
        )
        portrait_method[2].become(
            Arrow(portrait_method[1], portrait_method[0], path_arc=-PI / 6)
        )

        self.next_slide(
            notes="""This root-finding procedure was made by Isaac newton and John Method ()"""
        )

        self.play(
            ShowCreation(portrait_newton[0], run_time=0.5),
            FadeIn(portrait_newton[1]),
            FadeIn(portrait_newton[0][0]),
            Write(portrait_newton[2]),
        )

        self.play(
            ShowCreation(portrait_method[0], run_time=0.5),
            FadeIn(portrait_method[1]),
            FadeIn(portrait_method[0][0]),
            Write(portrait_method[2]),
        )

        # ====================================================
        #                       Formula
        # ====================================================
        self.next_slide()
        self.play(*(FadeOut(m) for m in self.mobjects_without_canvas))

        tex_kw = {
            "isolate": ["x_{n+1}", "x_n", "z_n", "z_{n+1}", "P", "P'", "f", "(", ")"],
            "t2c": {
                "x_{n+1}": BLUE_B,
                "x_n": BLUE_B,
                "z_{n+1}": BLUE_B,
                "z_\\d": BLUE_B,
                "x_\\d": BLUE_B,
                "z_n": BLUE_B,
                "z": BLUE_B,
                "x": BLUE_B,
            },
        }

        tex_func = Tex("f(x) = 0", **tex_kw)

        self.play(Write(tex_func))

        brace = Brace(tex_func.select_part("f(x)"), buff=0.1)
        brace_question = Tex("x=?", **tex_kw).next_to(brace, DOWN)
        self.play(Write(brace), Write(brace_question))

        self.next_slide(notes="Newtons method is the following sequence")

        self.play(FadeOut(brace), FadeOut(brace_question))

        newtons_tex_seq = Tex(r"x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}", **tex_kw)
        newtons_tex_fn = Tex(r"N(x) = x - \frac{f(x)}{f'(x)}", **tex_kw)

        equations = VGroup(newtons_tex_seq)

        self.play(
            TransformMatchingTex(tex_func, newtons_tex_seq, key_map={"x": "x_{n+1}"})
        )

        self.next_slide(
            notes="Where we take some initial value x0 and iterate this sequence"
        )

        iterative_tex = Tex(
            r"x_0 \longrightarrow  x_1 \longrightarrow x_2 \longrightarrow \cdots",
            isolate=["x_\\d"],
            t2c={"x_0": GREEN_A, "x_1": GREEN_B, "x_2": GREEN_C},
        ).next_to(equations[0], DOWN)

        self.play(
            Write(
                iterative_tex,
            )
        )

        self.next_slide(
            notes="However, for this presentation, it makes more sense for us to shift the language from sequences to composition "
        )

        iterative_tex_fn = Tex(
            r"x_0 \overset{N}{\longrightarrow} x_1 \overset{N}{\longrightarrow} x_2 \overset{N}{\longrightarrow} \cdots",
            isolate=["x_\\d"],
            t2c={"x_0": GREEN_A, "x_1": GREEN_B, "x_2": GREEN_C},
        ).next_to(newtons_tex_fn, DOWN)

        self.play(
            TransformMatchingTex(
                newtons_tex_seq, newtons_tex_fn.move_to(newtons_tex_seq), run_time=0.8
            )
        )
        self.play(TransformMatchingTex(iterative_tex, iterative_tex_fn))

        # ====================================================
        #                Geometric Showcase
        # ====================================================

        self.remove_from_canvas("title")
        self.add_to_canvas(formula=newtons_tex_fn)

        self.next_slide(
            notes="I'll come back to exactly why iterative composition makes this clear, but first just a little geometric review of what newtons method is doing"
        )

        (axes, func_graph, x0, x0_marker, limit_point) = self.setup_graphs()
        func_graph.set_color(RED_B)

        self.play(
            newtons_tex_fn.animate.scale(0.8).to_corner(DL),
            ShowCreation(axes),
            FadeOut(title),
            *(FadeOut(m) for m in self.mobjects_without_canvas),
        )

        self.play(FadeIn(func_graph))

        self.next_slide(note="We start with some initial guess x0")

        x0.set_value(-1)

        x0_label = VGroup(
            Tex("x_0", "=", t2c={"x_0": YELLOW}, alignment="").to_corner(UL),
            DecimalNumber(float(x0.get_value()), num_decimal_places=4),
        )

        def perform_one_step(speed=0.8):
            self.perform_one_step(speed)
            self.play(
                Transform(
                    x0_label[0],
                    Tex(
                        f"x_{self.n}",
                        "=",
                        t2c={
                            f"x_{self.n}": YELLOW,
                        },
                    ).move_to(x0_label[0]),
                    run_time=speed * 0.7,
                )
            )

        # x0_label[0].select_part(r"x_\d").f_always

        (
            x0_label[1]
            .f_always.set_value(lambda: x0.get_value())
            .next_to(lambda: x0_label[0])
            .shift(lambda: UP * 0.05)
        )

        self.play(FadeIn(x0_marker), Write(x0_label))

        self.next_slide(notes="We apply the function")

        perform_one_step()

        self.next_slide(
            notes="And we keep applying the function until we make it to a point",
            loop=False,
        )

        for _ in range(4):
            perform_one_step(0.5)

        self.next_slide(notes="And with only 3 iterations, its pretty good")

        ex_root = Tex(
            f"f(x_{self.n})",
            r"\, \approx \,",
            f"{self.f(x0.get_value()):.8f}\\dots",
            isolate=[f"x_{self.n}"],
            t2c={f"x_{self.n}": YELLOW},
        ).center()

        self.play(
            TransformFromCopy(x0_label[0], ex_root),
            FadeOut(axes),
            FadeOut(func_graph),
            FadeOut(x0_marker),
            FadeOut(x0_label),
        )

        """
        What happens if you move the start point?
        """

        self.next_slide()

        x0_label[0].become(
            Tex("x_0", "=", t2c={"x_0": YELLOW}, alignment="").to_corner(UL),
        )
        x0_label.arrange(RIGHT)

        self.play(
            FadeOut(ex_root),
            FadeIn(axes),
            FadeIn(func_graph),
            FadeIn(x0_marker),
            FadeIn(x0_label),
        )

        self.n = 0

        def make_path():
            values = [float(x0.get_value())]

            arrows = VGroup()

            while np.abs(self.f(values[-1])) > 0.1:
                z = values[-1]
                values.append(z - self.f(z) / self.df(z))

                arrows.add(
                    Arrow(
                        # axes.input_to_graph_point(z, func_graph),
                        axes.c2p(z),
                        axes.c2p(values[-1]),
                        # axes.input_to_graph_point(values[-1], func_graph),
                        path_arc=PI / 2 * np.sign(z) * np.sign(values[-1]),
                        thickness=2,
                        buff=SMALL_BUFF,
                    )
                )

            return arrows

        limiting_path = always_redraw(make_path)

        roots: list[float] = self.function.roots()
        about_roots = [roots[0] - 0.5, roots[1] - 0.4, roots[2] + 0.5]

        self.play(ShowCreation(limiting_path), FadeIn(limit_point))

        self.next_slide()

        def sv(z, run_time=1):
            self.play(x0.animate(run_time=run_time).set_value(z))

        self.next_slide(
            loop=False,
            notes="A thing we can notice is that if we start near a root, it tends to attract to that root",
        )

        for r in about_roots:
            sv(r)
            self.wait(1)

        self.next_slide(
            notes="Complexity arises though if we want to understand what happens when our limiting root changes as we vary x0"
        )

        sv(-0.5)

        self.next_slide(
            notes="This here pretty quickly converges to this middle root, however if we slightly nudge our starting value by just a tenth"
        )

        sv(-0.6)

        self.next_slide(
            notes="The method kinda goes erratic until it flings itself far enough to converge to the leftmost root, we can push this method just a 0.01, a hundreth  to the right and it will converge to the same root but do so significantly quicker"
        )

        sv(-0.59)

        self.next_slide(
            notes="If we push x0 closer however back to -0.5 - we can see that in between those values it actually can go to the last root somehow, but during the transition of limiting points there seems to be a huge decrease of effiency / convergence, and even here we can see that newtons method will actually bounce around a little bit first"
        )

        sv(-0.58)

        self.next_slide(
            notes="And again we can notice that at this sort of boundry between the two limits the function will indeed converge, but do so everso erraticly"
        )

        sv(-0.5781)

        self.next_slide()

        sv(-0.5780)

        self.next_slide()
        self.play(*(FadeOut(m) for m in self.mobjects))


class NewtonsMethodSimplification(AbstractNewtonsMethodRealVisualisation):
    function: Polynomial = SIMPLE_POLY_EXAMPLES[1]

    def construct(self) -> None:
        # (axes, func_graph, x0, x0_marker, limit_point) = self.setup_graphs()

        add_wait(self)

        title = Title("Newtons Method")

        self.play(Write(title))

        tex_kw = {
            "isolate": ["x_{n+1}", "x_n", "z_n", "z_{n+1}", "P", "P'", "f", "f'"],
            "t2c": {
                "x_{n+1}": YELLOW,
                "x_n": YELLOW,
                "z_{n+1}": BLUE_B,
                "z_n": BLUE_B,
            },
        }

        newtons_tex = Tex(
            r"{x_{n+1}}", "=", "{x_n}", "-", r"\frac{f({x_n})}{f'({x_n})}", **tex_kw
        )

        self.play(Write(newtons_tex))

        self.next_slide(
            notes="While newtons method works for any continuous/differentiable function, we are going to focus our view to polynomials"
        )

        newtons_tex_poly = Tex(
            r"{x_{n+1}}", "=", "{x_n}", "-", r"\frac{P({x_n})}{P'({x_n})}", **tex_kw
        )

        generic_polynomial = Tex(
            r"P(x) = c_0 + c_1 x + c_2 x^2 + c_3 x^3 + \cdots",
            isolate=[r"c_\d", r"x", r"z"],
            t2c=tex_kw["t2c"],
        ).next_to(newtons_tex_poly, DOWN)

        self.play(
            TransformMatchingTex(
                newtons_tex, newtons_tex_poly, key_map={"f": "P", "f'": "P'"}
            ),
            Write(newtons_tex),
        )

        self.next_slide()

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


class FixedPointMethod(Slide):
    def construct(self) -> None:
        add_wait(self)

        fixed_point_formula = VGroup(
            Tex(
                r"z_{n+1} = f(z_n)",
                isolate=["=", "\\lim", "n", "z", "z_{n+1}", "z_n"],
            )
        )

        title = Title("Fixed Point Method").fix_in_frame()
        self.add_to_canvas(title=title)
        self.play(Write(title), title.animate.to_edge(UP))

        self.next_slide()

        self.play(Write(fixed_point_formula))

        def gcos(z):
            return 2 * np.cos(z)

        axes = Axes(
            width=FRAME_WIDTH * 0.8,
            height=FRAME_HEIGHT * 0.6,
            # x_range=(-4, 4, 1),
            # y_range=(-2, 2, 1),
            x_range=(-4, 4, 1),
            y_range=(-5, 5, 1),
        ).shift(DOWN * 0.5)

        axes.add_coordinate_labels()

        self.next_slide()
        cos_graph = axes.get_graph(gcos).set_color(RED)
        self.play(
            fixed_point_formula.animate.scale(0.8).to_corner(DL), ShowCreation(axes)
        )

        self.play(ShowCreation(cos_graph))

        z0 = ValueTracker(0)

        t2c = {
            "z_{\\d}": YELLOW,
            "z_{n}": YELLOW,
            "z_{n+1}": YELLOW,
        }

        marker = (
            VGroup(
                ArrowTip(angle=PI / 2, width=0.2, length=0.2, fill_color=YELLOW),
                Tex("z_0", t2c=t2c),
            )
            .arrange(DOWN)
            .add_updater(
                lambda m: m.move_to(axes.coords_to_point(z0.get_value())).shift(
                    DOWN * m.get_height() * 0.5
                )
            )
        )
        always_redraw(
            lambda: VGroup(
                axes.get_v_line_to_graph(z0.get_value(), cos_graph),
                axes.get_h_line_to_graph(z0.get_value(), cos_graph),
            )
        )
        self.play(FadeIn(marker))

        def apply_rule():
            self.play(z0.animate.set_value(gcos(z0.get_value())))

        apply_rule()
        apply_rule()
        apply_rule()
        apply_rule()

        self.next_slide()

        self.play(*(FadeOut(m) for m in self.mobjects_without_canvas))

        holo_title = Title("Holomorphic Dynamics").to_edge(UP).fix_in_frame()

        self.play(Transform(title, holo_title))
        self.add_to_canvas(htitle=holo_title)


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
