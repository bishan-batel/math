# pyright: reportGeneralTypeIssues=false

from typing import TYPE_CHECKING


from manim_slides.slide import Slide, ThreeDSlide
from manim_slides.slide.animation import Wipe
from manimlib import *  # pyright:ignore
from manimlib.typing import *  # pyright:ignore

from custom.typings import *  # pyright:ignore
from custom.portrait import *  # pyright:ignore
from projects.mat557.oilers.common import *  # pyright:ignore
from projects.mat557.oilers.fractal import (
    ROOT_COLORS_DEEP,
    FractalNewton,
)

ADD_WAIT_TIME = True


def add_wait(slide: Slide):
    old = slide.on_resize

    if slide.window is not None:
        slide.window.fixed_aspect_ratio = 3024.0 / 1964.0
        slide.window.set_default_viewport()
        slide.show_animation_progress = True
        slide.leave_progress_bars = True

    def on_resize(width: int, height: int):
        if slide.window is not None:
            slide.window.fixed_aspect_ratio = 3024.0 / 1964.0
            slide.window.set_default_viewport()
        old(width, height)

    slide.on_resize = on_resize

    slide.leave_progress_bars = True
    if ADD_WAIT_TIME and slide.window is not None:
        slide.wait_time_between_slides = 2 if ADD_WAIT_TIME else 0


class FirstTitle(Slide):
    def construct(self):
        add_wait(self)

        title = (
            Title(
                "Finding Roots of Complex Polynomials\\\\with Newton's Method",
                font_size=60,
            )
            .center()
            .shift(UP)
        )

        self.play(Write(title))

        presenter = (
            TexText(
                r"Presented by",
                r"\textit{Kishan S Patel}",
                font_size=45,
                t2c={r"\textit{Kishan S Patel}": BLUE_A},
                fill_color=GREY_B,
            )
            .set_opacity(0)
            .next_to(title, DOWN * 2)
        )

        AUTHOR_NAME = "Scott Sutherland"

        author = (
            TexText(
                r"Based on the dissertation written by ",
                f"\\textit{{{AUTHOR_NAME}}}",
                isolate={AUTHOR_NAME},
                t2c={AUTHOR_NAME: GREEN_A},
                fill_color=GREY_B,
                font_size=35,
            )
            .set_opacity(0)
            .next_to(presenter, DOWN)
        )

        self.play(
            AddTextWordByWord(presenter),
            AddTextWordByWord(author),
            presenter.animate.next_to(title, DOWN),
            author.animate.next_to(presenter, DOWN),
            presenter.animate.set_opacity(1),
            author.animate.set_opacity(1),
        )

        self.next_slide(notes="A little goal layout")

        goals_title = Title("Goals").shift(np.array(*DOWN) * 0.5)

        self.play(
            TransformMatchingTex(title, goals_title),
            FadeOut(presenter),
            FadeOut(author),
        )

        goals = BulletedList(
            r"Slight review",
            r"How does Newtons Method work in $\mathbb C$?",
            r"Pretty Fractals ",
            r"Different ways to view Newtons Method",
        ).next_to(goals_title, DOWN * 1.2)

        curr_goal = -1

        self.next_slide()
        curr_goal += 1
        self.next_slide(notes="Some slight review of what Newtons is")

        # newtons method in CC
        self.next_slide(notes="How does newtons method extend to the complex numbers?")
        curr_goal += 1
        self.play(Write(goals[curr_goal]))

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

        curr_goal += 1
        self.play(
            Write(goals[curr_goal]),
            LaggedStart(
                FadeIn(fractals_plane),
                FadeIn(dot1),
                FadeIn(dot2),
                Write(arrows, run_time=1.5),
            ),
        )

        self.play(Swap(dot1, dot2))
        self.play(Swap(dot1, dot2))

        # newtons method fractals
        self.next_slide()

        # curr_goal += 1
        # self.play(
        #     Wipe(
        #         current=(dot1, dot2, arrows, fractals_plane),
        #         shift=DOWN,
        #     ),
        #     Write(goals[curr_goal]),
        # )

        self.next_slide()
        self.wipe(self.mobjects_without_canvas)

        self.embed()


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
            Tex("x_0", "=", t2c={"x_0": YELLOW}).to_corner(UL),
            DecimalNumber(
                float(x0.get_value()),  # pyright:ignore
                num_decimal_places=4,
            ),
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

        (
            x0_label[1]
            .f_always.set_value(lambda: x0.get_value())
            .next_to(lambda: x0_label[0])
            .shift(lambda: UP * 0.05)  # pyright:ignore
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
            f"{self.f(x0.get_value()):.8f}\\dots",  # pyright:ignore
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

        x0_label[0].become(Tex("x_0", "=", t2c={"x_0": YELLOW}, alignment=""))
        x0_label.arrange(RIGHT).to_corner(UL)

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

        roots: list[float] = self.function.roots()  # pyright: ignore
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
            "isolate": [
                "P(x_n)",
                "P'(x_n)",
                "f(x_n)",
                "f'(x_n)",
                "x_{n+1}",
                "x_n",
                "z_n",
                "z_{n+1}",
            ],
            "t2c": {
                "x_{n+1}": BLUE_B,
                "x_n": BLUE_B,
                "x": BLUE_B,
                "z_{n+1}": BLUE_B,
                "z_n": BLUE_B,
            },
        }

        # fomula for newtons method
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
            r"{P}(x) = c_0 + c_1 x + c_2 x^2 + c_3 x^3 + \cdots",
            isolate=[r"c_\d", r"x", r"z"],
            t2c=tex_kw["t2c"],
        ).next_to(newtons_tex_poly, DOWN)

        # specify for polynomials
        self.play(
            TransformMatchingTex(newtons_tex, newtons_tex_poly),
            Write(generic_polynomial),
        )

        self.next_slide(
            notes="Focusing our attention to cubics, although most of what im going to say generalizes to any polnomial",
        )

        self.play(FadeOut(newtons_tex_poly), generic_polynomial.animate.center())

        self.next_slide(
            notes="While we normally deal with polyomials in terms of coefficients, because we are specifically interested in the roots of the polynomial it makes more sense to talk about the factored form of the polynomial"
        )

        root_poly = Tex(
            r"P(x) = (x - r_1)(x - r_2)(x-r_3)",
            isolate=[r"c_\d", r"x", r"z"],
            t2c={
                r"r_1": RED_A,
                r"r_2": GREEN_A,
                r"r_3": BLUE_A,
                r"r_n": GREY,
                "z": BLUE_B,
                "x": BLUE_B,
            },
        )

        self.play(
            TransformMatchingTex(
                generic_polynomial,
                root_poly,
                path_arc=PI / 8,
                key_map={
                    "x": "z",
                    "c_0": "r_1",
                    "c_1": "r_2",
                    "c_2": "r_1",
                    "c_3": "r_n",
                },
            ),
        )

        self.next_slide(
            notes="The factored form has a lot of advantages that makes it nicer to work with, like how it lets us cut down from 4 coefficient variables to 3 roots"
        )

        cut_down_tex = TexText(
            r"$4$ Coefficients $\longrightarrow$ $3$", "roots"
        ).next_to(root_poly, DOWN * 4)

        cut_down_tex.add(
            *(
                Arrow(
                    cut_down_tex.get_part_by_tex("roots"),
                    root_poly.get_part_by_tex(r),
                    fill_color=color,
                    thickness=2,
                    path_arc=a * PI / 3,
                )
                for (r, color, a) in [
                    ("r_1", RED_A, -0.5),
                    ("r_2", GREEN_A, 0),
                    ("r_3", BLUE_A, 1),
                ]
            )
        )

        self.play(
            LaggedStart(
                Write(cut_down_tex),
                ValueTracker(0).animate.set_value(1),
                *(
                    ShowCreationThenDestruction(
                        SurroundingRectangle(root_poly.get_part_by_tex(f"r_{i}"))
                    )
                    for i in range(1, 4)
                ),
                lag_ratio=0.3,
            ),
        )

        self.next_slide(
            notes="Another nice thing is that the factored form has this sort of symettry between each root, meaning each one is swappable"
        )

        self.play(FadeOut(cut_down_tex))

        def swap_roots(i, j):
            self.play(
                Swap(
                    root_poly.get_part_by_tex(f"r_{i}"),
                    root_poly.get_part_by_tex(f"r_{j}"),
                )
            )

        swap_roots(1, 3)
        swap_roots(2, 1)
        swap_roots(3, 1)
        swap_roots(3, 2)

        self.next_slide(
            notes="Using newtons method on this polynomial means trying to actually find what these roots are for the function, and while before I talked about specifically the real value case - as you all know because of the Fundamental thereom of calculus - you can always find these roots if you allow them to take complex values"
        )

        thereom_of_alg = TexText(
            r"Fundamental Thereom of Algebra $\longrightarrow r_1,r_2,r_3 \in \mathbb{C}$",
            isolate=[r"c_\d", r"x", r"z"],
            t2c={
                r"r_1": RED_A,
                r"r_2": GREEN_A,
                r"r_3": BLUE_A,
                r"r_n": GREY,
                "z": BLUE_B,
            },
        ).shift(DOWN * 1)

        self.play(
            Write(thereom_of_alg),
        )
        self.play(
            ShowCreationThenDestruction(
                SurroundingRectangle(
                    thereom_of_alg.get_part_by_tex("Fundamental Thereom of Algebra")
                )
            ),
        )

        self.next_slide()
        self.play(*(FadeOut(m) for m in self.mobjects))


class NewtonComplex(ThreeDSlide):
    roots = [ComplexValueTracker(r) for r in SIMPLE_POLY_EXAMPLES[1].roots()]

    def f(self, z: complex):
        return Polynomial.fromroots([r.get_value() for r in self.roots])(z)

    def df(self, z: complex):
        return Polynomial.fromroots([r.get_value() for r in self.roots]).deriv()(z)

    def construct(self) -> None:
        add_wait(self)
        plane = ComplexPlane(faded_line_ratio=2)
        plane.add_coordinate_labels()
        plane.set_opacity(0.5)

        isolate = ("z", "P'", "P", "=", "N", "r_1", "r_2", "r_3", "N")

        t2c = {
            "z": BLUE_A,
            "r_1": ROOT_COLORS_DEEP[0],
            "r_2": ROOT_COLORS_DEEP[1],
            "r_3": ROOT_COLORS_DEEP[2],
            "P": YELLOW_B,
            "N": YELLOW_B,
            "P'": YELLOW_B,
            "f": YELLOW_B,
        }

        rule = (
            VGroup(
                Tex(
                    r"N(z)= z- \frac{P(z)}{P'(z)} \\ ",
                    t2c=t2c,
                    isolate=isolate,
                    font_size=30,
                ),
                Tex(
                    r"P(z) = (z-r_1)(z-r_2)(z-r_3)",
                    t2c=t2c,
                    font_size=30,
                ),
            )
            .arrange(DOWN, False, aligned_edge=LEFT)
            .to_corner()
        )

        rule_backgrond = BackgroundRectangle(
            rule,
            buff=MED_SMALL_BUFF,
            stroke_color=WHITE,
            stroke_width=5,
            stroke_opacity=1,
        )

        rule_group = VGroup(rule_backgrond, rule)

        # Show the rule in  the conrern and show the complex plane

        self.play(
            ShowCreation(plane),
            ShowCreation(rule_group),
        )

        z0 = ComplexValueTracker(0)

        z0_marker = Dot(
            fill_color=BLUE_A,
            radius=0.08,
        )
        z0_marker.set_z_index(120)
        z0_marker.f_always.move_to(lambda: plane.n2p(z0.get_value()))

        z0_label = Tex("z_0", t2c={"z_0": BLUE_A}, font_size=45)
        z0_label.always.next_to(z0_marker, UP, buff=SMALL_BUFF)
        z0_label.set_z_index(120)

        self.path_iterations = ValueTracker(1)
        self.path_epsilon = 0.2

        def newtons(z: complex):
            return z - self.f(z) / self.df(z)

        def sv(z: complex, run_time=1):
            self.play(z0.animate(run_time=1).set_value(z))

        def make_path():
            lines = VGroup()

            values = [complex(z0.get_value())]

            for i in range(round(self.path_iterations.get_value())):
                z = values[-1]

                zn = newtons(z)
                values.append(zn)

                distances = [
                    np.linalg.norm(plane.n2p(zn) - plane.n2p(r.get_value()))
                    for r in self.roots
                ]

                if min(*distances) < 0.1:
                    break

            for i in range(len(values) - 1):
                lines += Arrow(
                    plane.n2p(values[i]),
                    plane.n2p(values[i + 1]),
                    fill_opacity=0.9,
                    thickness=2 * (1 - float(i) / (len(values) - 1)),
                    path_arc=-PI / 2,
                    fill_color=BLUE_A,
                    buff=0.0,
                )

            lines.set_submobject_colors_by_gradient(
                BLUE_A,
                self.point_to_root_color(values[-1]) or BLUE_A,
            )
            lines.set_z_index(5)
            return lines

        path = make_path().add_updater(lambda m: m.become(make_path()))

        def make_limit_point():
            z = z0.get_value()
            for _ in range(50):
                z = newtons(z)

            color = self.point_to_root_color(z)

            if color is None:
                return VGroup()

            dot = GlowDot(plane.n2p(z), radius=0.5)
            dot.set_z_index(100)
            dot.set_color(color)

            return dot

        limit_point = always_redraw(make_limit_point)

        def make_root_dot(i):
            dot = Dot(
                fill_color=ROOT_COLORS_DEEP[i],
                stroke_color=BLACK,
                stroke_width=3,
                opacity=0.5,
                radius=0.1,
            )

            dot.f_always.move_to(lambda: plane.n2p(self.roots[i].get_value()))

            return dot

        roots = VGroup(*(make_root_dot(i) for i in range(3)))

        roots_tails = VGroup(*(TracingTail(dot, color=dot.fill_color) for dot in roots))

        self.next_slide(
            notes="I will also be adding this little limit point and root points so you know which root is being converged to, and what the roots are"
        )

        self.add(roots_tails)
        self.play(FadeIn(roots))

        self.next_slide(
            notes="Something also I want to note is that we are going to be looking at the same cubic as before, except now as a function from C to C"
        )

        real_axes = Axes(x_range=plane.x_range)
        real_axes.add_coordinate_labels()
        real_axes.rotate(DEG * 90, RIGHT)
        real_graph = real_axes.get_graph(lambda z: self.f(z), bind=True)

        self.play(
            ShowCreation(real_axes),
            FadeIn(real_graph),
            self.frame.animate.rotate(90 * DEG, axis=RIGHT),
        )

        self.next_slide(notes="Returning back, we can see what z0 does")

        self.play(
            self.frame.animate.rotate(-90 * DEG, axis=RIGHT),
            FadeOut(real_axes),
            FadeOut(real_graph),
        )

        self.next_slide(
            notes="Like before in the real number case, we start with some initial 'seed value' z0"
        )

        z0_marker_trail = TracingTail(z0_marker, stroke_color=BLUE_A)
        self.play(FadeIn(z0_marker), FadeIn(z0_label))
        self.add(z0_marker_trail)

        self.next_slide(notes="And we can move around and what not, ")

        self.play(z0.animate.set_value(-0.5))
        self.play(z0.animate.set_value(0.3))
        self.play(z0.animate.set_value(-2))

        self.next_slide(
            notes="Im going to put it here since we know from before its just going to go to tis leftmost root"
        )

        self.play(z0.animate.set_value(-5), CircleIndicate(roots[0]))

        self.next_slide(
            notes="While in the real number graph case we have this nice visual intuition with tangent lines and zeroes - we can still play the same game with complex numbers and take a step"
        )

        self.path_iterations = ValueTracker(1)

        l_path = make_path()
        self.play(Write(l_path))

        self.next_slide(notes="Then another one")
        self.path_iterations.set_value(2)

        l_path2 = make_path()
        self.play(Transform(l_path, l_path2))

        self.next_slide(notes="And so on and so on")

        self.remove(l_path)
        self.remove(l_path2)
        self.add(path)
        self.play(self.path_iterations.animate.set_value(10))

        self.next_slide(
            notes="And I will also make the root that z0 will eventually hit glow"
        )

        self.play(FadeIn(limit_point))

        self.next_slide(
            notes="We can play this same game now except we can see what this will do for an complex starting point"
        )

        self.play(z0.animate.set_value(-2))

        self.play(z0.animate.set_value(-1))

        self.next_slide(
            notes="And we can see this strange slower convergence happens on the boundry again"
        )

        self.path_iterations.set_value(100)

        sv(-0.5)
        sv(-0.6)
        sv(-0.59)
        sv(-0.5781)
        sv(-0.5780)

        self.next_slide(
            notes="If we move around our z value in the complex plane, we can see this 'boundry chaos' seems to persist even there"
        )

        def rotate_z0(rotations=20, rotation_time=8.0, rotation_radius=2):
            for i in range(rotations):
                angle = (float(i + 1) / rotations) * 360 * DEG
                self.play(
                    z0.animate(
                        run_time=(rotation_time / float(rotations)), rate_func=linear
                    ).set_value(rotation_radius * np.exp(1j * angle))
                )

        rotate_z0()

        self.wait(1)
        self.next_slide(
            notes="Now I'm going to do the same thing with a polynomial that does have complex roots"
        )

        self.play(
            *(
                r.animate.set_value(nr)
                for (r, nr) in zip(self.roots, SIMPLE_POLY_EXAMPLES[2].roots())
            ),
        )
        self.wait(1)

        self.next_slide(
            notes="And notice that even with a different polynomial this behavior continues"
        )
        rotate_z0()

        self.wait(1)

        self.next_slide(
            notes="This is where the cool stuff begins, lets see what a whole array of seed values will do, lets spread a bunch of different values across the plane"
        )

        self.remove(z0_marker_trail)

        path.suspend_updating()
        self.play(
            FadeOut(z0_marker),
            FadeOut(z0_label),
            FadeOut(rule_group),
            FadeOut(path),
            FadeOut(limit_point),
        )
        path.resume_updating()

        points_history = [self.make_points()]

        def points2coords(points):
            return [plane.n2p(point) for point in points]

        dots = DotCloud(
            radius=0.04,
            color=WHITE,
            points=points2coords(points_history[-1]),  # pyright: ignore
        )

        def take_step(run_time=0.8, draw_arrows=True):
            points_history.append([newtons(z) for z in points_history[-1]])

            step_dir = [
                (zp, (z - zp)) for z, zp in zip(points_history[-1], points_history[-2])
            ]

            arrows = VGroup()
            if draw_arrows:
                arrows.add(
                    *(
                        Arrow(
                            start=plane.n2p(z),
                            end=plane.n2p(
                                z + (dir / abs(dir)) * max(min(0.3, abs(dir)), 0.0)
                            ),
                            thickness=1,
                            buff=0.00,
                            fill_color=WHITE,
                            fill_opacity=0.5,
                        )
                        for (z, dir) in step_dir
                    )
                )
                self.play(FadeIn(arrows, run_time=run_time))

            self.play(
                dots.animate(run_time=run_time).set_points(
                    points2coords(points_history[-1])
                ),
                FadeOut(arrows, run_time=run_time),
            )

        def unwind(run_time=0.5):
            for points in points_history[::-1]:
                self.play(
                    dots.animate(run_time=run_time).set_points(points2coords(points))
                )

        self.play(ShowCreation(dots))

        self.next_slide(notes="We can see how all the points step forward")

        take_step()

        self.next_slide(
            notes="As we keep iterating, notice how (like as we saw before) points near each root pretty quickly getting nestled in, while some points bounce around and get flung out really far before converging"
        )

        for _ in range(5):
            take_step()

        self.next_slide(
            notes="If we just keep iterating, it seems like most points do hit the roots"
        )

        for _ in range(10):
            take_step(0.5)

        self.next_slide(
            notes="We can color each starting point by what root it converged into"
        )

        def iteration_color_dots(run_time=0.8):
            self.play(
                dots.animate(run_time=run_time).set_color(
                    [
                        self.point_to_root_color(z, epsilon=1e20, if_none=BLACK)
                        for z in points_history[-1]
                    ]
                )
            )

        iteration_color_dots()

        self.next_slide(
            notes="If we sort of 'unwind' all of these points back to there starting positions"
        )

        unwind()

        self.next_slide(
            notes="Something weird shappens at the boundry, the third color seems to be butting in"
        )

        self.frame.save_state()

        self.play(self.frame.animate.scale(0.5).shift(DOWN + RIGHT))
        self.wait(1)
        self.play(self.frame.animate.shift(UP + LEFT * 3))

        self.next_slide(notes="Zooming out however")
        self.play(self.frame.animate.restore())

        self.next_slide(
            notes="This isn't really enough resolution to get the full picture, so lets double the number"
        )

        points_history = [self.make_points(40)]

        self.play(
            dots.animate(run_time=0.5).set_color(WHITE),
            dots.animate.set_points(points2coords(points_history[-1])).set_color(WHITE),
        )

        self.next_slide(notes="We then play this same game of iteration")

        for _ in range(10):
            take_step(0.5)

        self.next_slide(notes="We color and then unwind")

        iteration_color_dots()
        unwind()

        self.next_slide(notes="Even this doesnt seem to be enough resolution")

        points_history = [self.make_points(80)]

        self.play(
            dots.animate(run_time=0.5).set_color(GREY_B),
            dots.animate.set_points(points2coords(points_history[-1])).set_color(
                GREY_B
            ),
        )

        for _ in range(10):
            take_step(0.35, False)
        for _ in range(10):
            take_step(0.1, False)

        self.next_slide(notes="We unwind and color again")

        iteration_color_dots(0.5)
        unwind(0.25)

        self.next_slide(
            notes="This shape at the boundries seems to contain more and more of these blobs, but to get a full appreciation - we need to go to an even higher resolution - if you kepts increasing and increasing the amount of points you sample, doing this game for every single pixel on the screen, this is what you would get"
        )

        fractal = FractalNewton(roots=[0, 0, 0])
        fractal_opacity = ValueTracker(0)
        fractal.f_always.set_roots(lambda: [r.get_value() for r in self.roots])
        fractal.f_always.set_opacity(lambda: fractal_opacity.get_value())
        fractal.set_z_index(-1)
        fractal.set_iteration_coloring(False)

        self.add(fractal)
        self.play(
            FadeOut(dots),
            FadeOut(roots),
            plane.animate.set_opacity(0.15),
            *(dot.animate.set_opacity(0.5) for dot in roots),
            fractal_opacity.animate.set_value(1.0),
        )
        self.embed()

    def make_points(self, density=20) -> Iterable[complex]:
        from sympy import flatten

        RE, IM = np.mgrid[-6 : 6 : density * 1j, -4 : 4 : density * 1j]
        return flatten(RE + IM * 1j)

    def point_to_root_color(
        self,
        z: complex,
        epsilon: float = 1e-1,
        if_none: Color | None = None,
    ):
        d1, d2, d3 = (abs(z - r.get_value()) for r in self.roots)

        if min(d1, d2, d3) > epsilon:
            return if_none

        if d1 < d2 and d1 < d3:
            return ROOT_COLORS_DEEP[0]
        elif d2 < d1 and d2 < d3:
            return ROOT_COLORS_DEEP[1]
        elif d3 < d1 and d3 < d2:
            return ROOT_COLORS_DEEP[2]
        return None


class AbstractNewtonFractal(Slide):
    roots = [ComplexValueTracker(r) for r in SIMPLE_POLY_EXAMPLES[2].roots()]

    plane: ComplexPlane
    fractal: FractalNewton
    z0 = ComplexValueTracker(0)
    root_dots: VGroup[Dot]

    path_iterations: int = 10
    show_path = True

    def f(self, z: complex):
        return Polynomial.fromroots([r.get_value() for r in self.roots])(z)

    def df(self, z: complex):
        return Polynomial.fromroots([r.get_value() for r in self.roots]).deriv()(z)

    def newtons(self, z: complex):
        return z - self.f(z) / self.df(z)

    def make_fractal(self) -> FractalNewton:
        self.fractal = FractalNewton([r.get_value() for r in self.roots])
        self.fractal.f_always.set_roots(lambda: [r.get_value() for r in self.roots])
        self.fractal.set_z_index(-1)
        self.fractal.pin(self)
        return self.fractal

    def make_plane(self) -> ComplexPlane:
        self.plane = ComplexPlane(faded_line_ratio=2)
        self.plane.add_coordinate_labels()
        self.plane.set_opacity(0.15)
        return self.plane

    def make_z0(self, color=BLUE_A, radius=0.08) -> tuple[Dot, TracingTail, Tex]:
        self.z0_marker = Dot(fill_color=color, radius=radius)
        self.z0_marker.f_always.move_to(
            lambda: self.plane.n2p(complex(self.z0.get_value()))
        )
        self.z0_marker.set_z_index(2)

        self.z0_tail = TracingTail(
            self.z0_marker, stroke_color=self.z0_marker.fill_color
        )
        self.z0_tail.set_z_index(1)

        self.z0_label = Tex("z_0")
        self.z0_label.always.next_to(self.z0_marker, RIGHT, buff=SMALL_BUFF)

        return (
            self.z0_marker,
            self.z0_tail,
            self.z0_label,
        )

    fix_z0_to_midpoint = False
    show_path = True

    def make_path(self):
        return always_redraw(lambda: self.updater_make_path())

    def updater_make_path(self, z0: complex | None = None):
        if z0 is not complex:
            z0 = complex(self.z0.get_value())

        if not self.show_path or self.path_iterations < 1:
            return VMobject()

        values = [z0]
        for _ in range(self.path_iterations):
            values.append(self.newtons(values[-1]))
            if abs(values[-1] - values[-2]) < 0.05:
                break

        values = [self.plane.n2p(z) for z in values]

        gradient = list(Color("White").range_to(Color("Red"), len(values)))

        obj = VGroup()

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
                ).set_color(gradient[i]),
                Dot(
                    x,
                    fill_color=gradient[i],
                    stroke_color=gradient[i],
                    radius=0.03 * (1.0 - float(i) / float(len(values))),
                ).set_color(gradient[i]),
            )

        return obj.set_submobject_colors_by_gradient(*gradient)

    def make_root_dots(self, radius=0.07) -> tuple[VGroup, Group[TracingTail]]:

        def make_dot(i: int):
            dot = Dot(
                fill_color=ROOT_COLORS_DEEP[i],
                stroke_color=BLACK,
                stroke_width=2,
                opacity=0.5,
                radius=radius,
            )
            dot.f_always.move_to(
                lambda: self.plane.n2p(complex(self.roots[i].get_value()))
            )
            self.root_trails.add(
                TracingTail(
                    dot,
                    stroke_color=dot.fill_color,
                )
            )
            return dot

        self.root_trails = Group()
        self.root_dots = VGroup(*(make_dot(i) for i in range(3)))
        self.root_dots.set_z_index(5)
        return self.root_dots, self.root_trails

    def construct(self):
        add_wait(self)


class NewtonFractalIntroduction(AbstractNewtonFractal):
    root_opacities = [ValueTracker(1) for _ in range(3)]

    def construct(self):
        super().construct()

        plane = self.make_plane()
        fractal = self.make_fractal()
        fractal.set_should_color_cycles(False)
        fractal.set_iteration_coloring(False)

        fractal.f_always.set_color_opacities(
            lambda: [float(r.get_value()) for r in self.root_opacities],
        )

        self.add(plane, fractal)

        self.frame.save_state()
        self.next_slide(notes="amazing")

        self.play(
            self.frame.animate(run_time=5, rate_func=slow_into)
            .set_width(0.9004003)
            .move_to([-1.4324704e00, 8.6061301e-04, 0]),
        )

        self.next_slide()

        self.play(
            self.frame.animate(run_time=8, rate_func=linear)
            .set_width(0.00478518)
            .move_to([-1.522637, -0.05915671, 0.0]),
        )

        self.next_slide(notes="Zooming back out")
        self.play(self.frame.animate.restore())

        self.next_slide(
            notes="Moving along (or into) just staring at the pretty image - we can additionally color each pixel loosely on *how slow* it converges to said root"
        )

        fractal.set_iteration_coloring(True)

        self.next_slide(
            notes="Zooming in on the chaotic boundry, we can see that it seems like the convergence is slower and slower the closer it is to this fractal boundry"
        )

        self.frame.save_state()

        self.play(
            self.frame.animate(run_time=5, rate_func=linear)
            .set_width(0.00478518)
            .move_to([-1.522637, -0.05915671, 0.0]),
        )

        self.next_slide(notes="And is decreased when we look right near the roots")

        self.play(self.frame.animate.restore())

        root_dots, root_dots_trail = self.make_root_dots()

        self.play(ShowCreation(root_dots))
        self.add(root_dots_trail)

        self.frame.save_state()

        self.play(
            self.frame.animate(run_time=1)
            .set_width(3)
            .move_to(self.plane.n2p(complex(self.roots[0].get_value()))),
        )

        self.next_slide(notes="If we bring back out our little sample point and arrows")

        self.play(self.frame.animate.restore())

        z0 = self.z0
        z0_dot, z0_tail, z0_label = self.make_z0()
        z0.set_value(2 + 1j)

        self.path_iterations = 4
        initial_path = self.updater_make_path()

        self.play(
            ShowCreation(z0_dot),
            Write(initial_path, run_time=2),
            Write(z0_label),
        )

        self.add(z0_tail)

        self.path_iterations = 100
        path = self.make_path()
        self.remove(initial_path)
        self.add(path)

        self.next_slide(
            notes="Moving it along we like before - where it starts to 'blow up' becomes a lot easier to notice"
        )

        circular_z0 = ValueTracker()

        self.circular_z0_radius = 2

        def circular_z0_update(m):
            t = m.get_value()
            circle_value = self.circular_z0_radius * np.exp(2j * PI * t)
            self.z0.set_value(circle_value)
            path.become(self.updater_make_path(circle_value))
            return m

        circular_z0.add_updater(circular_z0_update, call=False)

        self.play(
            self.z0.animate.set_value(2),
        )

        self.add(circular_z0)

        def wiggle_cz0(wiggle=0.01, run_time=1.0, **kwargs):
            t = float(circular_z0.get_value())
            self.play(
                circular_z0.animate(run_time=run_time, **kwargs).set_value(t + wiggle)
            )
            self.play(
                circular_z0.animate(run_time=run_time, **kwargs).set_value(t - wiggle)
            )
            self.play(
                circular_z0.animate(run_time=run_time, **kwargs).set_value(t + 0.0)
            )

        self.play(circular_z0.animate(run_time=2).set_value(0 + 1 / 6))
        wiggle_cz0(run_time=0.5)

        self.wait(1.4)
        self.play(circular_z0.animate(run_time=1).set_value(1 / 3 + 1 / 6))
        wiggle_cz0(run_time=0.5)

        self.wait(1.4)
        self.play(circular_z0.animate(run_time=1).set_value(2 / 3 + 1 / 6))
        wiggle_cz0(run_time=0.5)

        self.remove(circular_z0)

        self.next_slide(
            notes="This fractal isn't just a one off case for this polynomial"
        )

        tri_poly = Tex("P(z) = z^3 - 1", isolate=["z"], t2c={"z": BLUE_B}).to_corner(UL)

        path.suspend_updating()
        self.play(
            Write(tri_poly),
            FadeOut(path),
            FadeOut(z0_label),
            FadeOut(z0_dot),
        )

        self.next_slide(
            notes="If we move around the roots of this polynomial it seems like the fractal boundries never truly go away"
        )

        self.play(FadeOut(tri_poly))

        def set_roots(roots=[0, 0, 0], **kwargs):
            self.play(
                *(
                    root.animate(**kwargs).set_value(nr)
                    for root, nr in zip(self.roots, roots)
                )
            )

        self.next_slide(
            notes="In a sense, a way we can study and understand when newtons method acts chaotically by studying the boundry of this fractal"
        )

        r1, r2, r3 = self.roots

        set_roots(roots=[1, 1j, -1])
        self.wait(1)
        set_roots([4 + 0.5j, -3 + 1j, 1 - 2j])

        self.wait(1)
        set_roots([-2, 0, 2])

        self.wait(1)
        set_roots(SIMPLE_POLY_EXAMPLES[0].roots())

        self.wait(1)

        set_roots([r2.get_value(), r3.get_value(), r1.get_value()])

        self.wait(1)

        chaos_relation = TexText(r"Chaos $\longrightarrow$ Fractal").to_edge(UP)

        fractal.set_z_index(-2)
        julia_fractal = fractal.copy().set_julia_highlight(1e-2).set_z_index(-1)

        fractal_opacity, julia_fractal_opacity = ValueTracker(1), ValueTracker(0)
        fractal.f_always.set_opacity(lambda: fractal_opacity.get_value())
        julia_fractal.f_always.set_opacity(lambda: julia_fractal_opacity.get_value())

        self.add(julia_fractal)

        self.play(
            Write(chaos_relation),
            FadeOut(root_dots),
            fractal_opacity.animate.set_value(0.2),
            julia_fractal_opacity.animate.set_value(1.0),
        )

        self.next_slide(
            notes="To get the fractal we could use a vibes based 'just move the roots and see the picture', maybe try seeing how the fractal behaves as we apply symettries over the roots",
        )

        self.play(
            fractal_opacity.animate.set_value(1),
            julia_fractal_opacity.animate.set_value(0.0),
            FadeIn(root_dots),
        )

        self.remove(julia_fractal)

        def apply_to_roots(func: Callable[[complex], complex], **kwargs):
            set_roots([func(complex(r.get_value())) for r in self.roots], **kwargs)

        apply_to_roots(lambda z: z * np.exp(2j * PI / 3))

        self.wait(1)

        apply_to_roots(lambda z: z + 1j, run_time=0.5)
        apply_to_roots(lambda z: z + 1, run_time=0.5)
        apply_to_roots(lambda z: z - 1j, run_time=0.5)
        apply_to_roots(lambda z: z - 1, run_time=0.5)

        self.embed()


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
            return 1 * np.cos(z)

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


class NewtonCubic(Slide):
    def construct(self) -> None:
        from sympy import symbols, roots, numer, Symbol, Derivative, simplify, expand

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

        from sympy import oo, latex, factor

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
