from manim import *  # pyright: ignore
from manim.utils.color.BS381 import DARK_CRIMSON, DARK_GREEN, DARK_VIOLET
from manim_slides.slide import Slide # pyright: ignore
import numpy as np

roots = np.array([
    1+0j, 
    -0.5 + 0.866j, 
    -0.5 - 0.866j
])

def f(z):
    return z**3 - 1

def df(z):
    return 3 * z ** 2

def d2f(z):
    return 6 * z

def newtons(z):
    return z - f(z)/df(z)

def halleys(z):
    return z - (f(z)*df(z))/((df(z)**2) - 0.5 * f(z) * d2f(z))

method = newtons

COLORS = [DARK_BROWN, DARK_GREEN, DARK_CRIMSON, DARK_VIOLET]

class Title(Slide):
    plane: ComplexPlane

    def gen_fractal_image(self,steps: int):
        # Image resolution

        n = 20_00

        # Define complex plane region
        x = np.linspace(self.plane.x_range[0], self.plane.x_range[1], n)
        y = np.linspace(self.plane.y_range[0], self.plane.y_range[1], n)
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
            mask = (closest == i)
            img_data[mask] = COLORS[i].to_int_rgb()

        img_data[np.min(distances, axis=0) > 1e-3] = BLACK.to_int_rgb()

        # Convert to ImageMobject
        fractal_image = ImageMobject(img_data.astype(np.uint8))
        fractal_image.width = self.plane.width
        fractal_image.height = self.plane.height
        fractal_image.z_index = -1

        return fractal_image
        

    def construct(self):
        self.plane = ComplexPlane(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            background_line_style={ }
        ).add_coordinates()
        self.plane.z_index = -1

        # self.play(Create(title_text))

        # self.next_slide()

        # self.play(Transform(title_text, self.plane))
        # self.play(Create(self.plane))
        self.add(self.plane)

        # self.next_slide()

        fractal = self.gen_fractal_image(30)
        self.add(fractal)
        # self.play(FadeIn(fractal))

        root_dots = [
            Dot(self.plane.n2p(root)).set_color(WHITE) for root in roots
        ]

        for i in range(len(roots)):
            dot = root_dots[i]
            dot.add(MathTex(f"r{i+1}").scale(0.5).next_to(dot,direction=UP,buff=0.0))

        self.add(*root_dots)

        self.next_slide(loop=True)

        x0 = ComplexValueTracker()
        x0.set_value(1j)

        marker = Dot()
        marker.add_updater(lambda m: m.move_to(self.plane.n2p(x0.get_value())))
        self.add(marker)


        def make_path():
            values = [x0.get_value()]

            for _ in range(40):
                z_prev = values[-1]
                z = method(z_prev)
                values.append(z)

            points = [Dot(self.plane.n2p(z)).scale(0.5) for z in values]

            lines = VGroup()
            for i in range(len(points) - 1):
                line = Line(
                    points[i].get_center(),
                    points[i+1].get_center(),
                    stroke_width=2,
                    color=BLUE
                )
                lines.add(line)
            lines.add(*points)
            return lines

        self.add(always_redraw(make_path));

        # self.add(ParametricFunction(lambda x: self.plane.n2p(np.e ** (0.9 * 1j * x)) , t_range=(0, 10)))

        self.play(x0.animate(run_time=1).set_value(0+1j))
        self.play(x0.animate(run_time=1).set_value(-0.5 + 2j))
        self.play(x0.animate(run_time=1).set_value(5 + 2j))
        self.play(x0.animate(run_time=1).set_value(-2 + 0j))
        self.play(x0.animate(run_time=1).set_value(1j))

        self.next_slide()

        # for quality in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]:
        #     n = self.gen_fractal_image(quality)
        #     self.next_slide()
        #     self.remove(fractal)
        #     self.add(n)
        #     fractal = n
