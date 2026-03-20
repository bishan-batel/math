from manim.typing import Point2D_Array, Point2DLike
import numpy as np
from manim import *  # pyright: ignore
from manim.opengl import *  # pyright: ignore
from manim_slides.slide import Slide  # pyright: ignore
from manim.utils.color.BS381 import DARK_CRIMSON, DARK_GREEN, DARK_VIOLET
from numpy.polynomial import Polynomial


def newtons(z: complex, f: Polynomial, df: Polynomial):
    return z - f(z) / df(z)


def halleys(z: complex, f: Polynomial, df: Polynomial, d2f: Polynomial):
    return z - (f(z) * df(z)) / ((df(z) ** 2) - 0.5 * f(z) * d2f(z))


COLORS = [DARK_BROWN, DARK_GREEN, DARK_CRIMSON, DARK_VIOLET]


def gen_fractal_image(
    plane: ComplexPlane,
    roots,
    steps=30,
    method=newtons,
    COLORS=COLORS,
    resolution=3_000,
):
    n = resolution
    # Image resolution

    # Define complex plane region
    x = np.linspace(plane.x_range[0], plane.x_range[1], n)
    y = np.linspace(plane.y_range[0], plane.y_range[1], n)
    X, Y = np.meshgrid(x, y)
    z = X + 1j * Y

    # Newton iteration
    for _ in range(steps):
        z = method(z)

    # Color based on convergence (3 roots for z^3-1)
    img_data = np.zeros((n, n, 3))
    # Roots of z^3-1 are 1, -0.5+0.866j, -0.5-0.866j

    img_data[True] = BLACK.to_int_rgb()

    distances = np.abs(z[np.newaxis, :, :] - roots[:, np.newaxis, np.newaxis])
    closest = np.argmin(distances, axis=0)

    for i in range(len(roots)):
        mask = closest == i
        img_data[mask] = COLORS[i].to_int_rgb()

    img_data[np.min(distances, axis=0) > 1e-3] = BLACK.to_int_rgb()

    # Convert to ImageMobject
    fractal_image = ImageMobject(img_data.astype(np.uint8))
    fractal_image.width = plane.width
    fractal_image.height = plane.height
    fractal_image.z_index = -1

    return fractal_image


class Title(Slide):
    skip_reversing = True

    def construct(self):
        text = Tex("Oilers' Method")
        self.next_slide()
        self.play(FadeIn(text))


class NewtonsFractal(Slide):
    skip_reversing = True

    def construct(self):
        plane = ComplexPlane(
            x_range=[-5, 5, 1], y_range=[-5, 5, 1], background_line_style={}
        ).add_coordinates()
        plane.z_index = -1

        # polynomial & roots
        LAMBDA = 5
        COEFFICIENTS = np.array([-LAMBDA, LAMBDA - 1, 0, 1])
        COEFFICIENTS = np.array([2, -2, 0, 1])
        f = np.polynomial.Polynomial(COEFFICIENTS)
        df = f.deriv()
        d2f = df.deriv()

        roots = [
            ComplexValueTracker().set_value(root)
            for root in np.roots(COEFFICIENTS[::-1])
        ]

        roots_num = lambda: np.array([r.get_value() for r in roots])

        def current_method(z: complex):
            return newtons(z, f=f, df=df)

        fractal = gen_fractal_image(plane, roots=roots_num(), method=current_method)

        self.play(Create(plane), FadeIn(fractal))

        def root_updater(tracker):
            return lambda m: m.move_to(plane.n2p(tracker.get_value()))

        root_dots = [
            MathTex(f"r_{i + 1}")
            .set_z_index(5)
            .scale(0.5)
            .add_updater(root_updater(root))
            for (i, root) in enumerate(roots)
        ]

        self.play(*(Create(root) for root in root_dots))

        self.next_slide()

        def make_path(z: complex):
            values = [z]

            for _ in range(40):
                values.append(current_method(values[-1]))

            points = [Dot(plane.n2p(z)).scale(0.5) for z in values]

            lines = VGroup()
            for i in range(len(points) - 1):
                line = Line(
                    points[i].get_center(),
                    points[i + 1].get_center(),
                    stroke_width=2,
                    color=BLUE,
                )
                lines.add(line)
            lines.add(*points)
            return lines

        # initial value
        z0 = ComplexValueTracker()
        z0.set_value(1j)

        z0_marker = (
            MathTex("z_0")
            .set_z_index(10)
            .scale(0.5)
            .set_color(RED)
            .add_updater(lambda m: m.move_to(plane.n2p(z0.get_value()) + UP * 0.1))
        )

        z0_path = always_redraw(lambda: make_path(z0.get_value()))
        self.play(Create(z0_marker), FadeIn(z0_path))

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

        def flow(pos):
            z = plane.p2n(pos)

            w = current_method(z) - z
            return plane.n2p(w)

        stream_lines = StreamLines(
            func=flow, stroke_width=1.5, max_anchors_per_line=30, dt=1
        )
        stream_lines.start_animation(warm_up=True, flow_speed=0.7, time_width=0.1)
        self.add(stream_lines)
        self.wait(15)
        self.play(stream_lines.animate.set_opacity(0.4))

        self.next_slide(auto_next=True)

        n = 30
        xspace = np.linspace(plane.x_range[0] * 0.5, plane.x_range[1] * 0.5, n)
        yspace = np.linspace(plane.y_range[0] * 0.5, plane.y_range[1] * 0.5, n)

        points: list[complex] = []
        point_dots: list[Dot] = []
        for x in xspace:
            for y in yspace:
                points.append(x + 1j * y)
                point_dots.append(Dot(radius=0.03).move_to(plane.n2p(x + 1j * y)))

        self.play(*(Create(dot) for dot in point_dots))

        for _ in range(20):
            for i, z in enumerate(points):
                points[i] = current_method(z)
            self.wait(1)
            self.play(
                *(
                    dot.animate.move_to(plane.n2p(points[i]))
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
                    dot.animate.move_to(plane.n2p(points[i]))
                    for i, dot in enumerate(point_dots)
                    if np.min([np.abs(points[i] - r.get_value()) for r in roots]) > 1e-3
                )
            )

        self.next_slide()
