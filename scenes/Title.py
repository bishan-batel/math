from manim import *  # pyright: ignore
from manim.utils.color.BS381 import DARK_GREEN
from manim_slides.slide import Slide # pyright: ignore
import numpy as np

r1, r2, r3 = 1+0j, -0.5 + 0.866j, -0.5 - 0.866j

def f(z):
    return z**3 - 1

def df(z):
    return 3 * z ** 2

COLORS = [ DARK_BLUE, DARK_BROWN, DARK_GREEN ]

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
            z = z - f(z) / df(z)

        # Color based on convergence (3 roots for z^3-1)
        img_data = np.zeros((n, n, 3))
        # Roots of z^3-1 are 1, -0.5+0.866j, -0.5-0.866j


        def dist(r): 
            return np.abs(z - r)
        
        # Assign colors
        img_data[dist(r1) < np.minimum(dist(r2), dist(r3))] = COLORS[0].to_int_rgb() # Red
        img_data[dist(r2) < np.minimum(dist(r1), dist(r3))] = COLORS[1].to_int_rgb() # Green
        img_data[dist(r3) < np.minimum(dist(r1), dist(r2))] = COLORS[2].to_int_rgb() # Blue
        
        # Convert to ImageMobject
        fractal_image = ImageMobject(img_data.astype(np.uint8))
        fractal_image.width = self.plane.width
        fractal_image.height = self.plane.height
        fractal_image.z_index = -1

        return fractal_image
        

    def construct(self):
        title_text = Text("Oilers' Method")
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
            Dot(self.plane.n2p(r1)).set_color(WHITE), 
            Dot(self.plane.n2p(r2)).set_color(WHITE), 
            Dot(self.plane.n2p(r3)).set_color(WHITE)
        ]

        for i in range(3):
            dot = root_dots[i]
            dot.add(MathTex(f"r{i+1}").next_to(dot,direction=UP).scale(0.5))
            # root_dots[i].add()

        self.add(*root_dots)

        x0 = ComplexValueTracker()
        x0.set_value(1j)

        marker = Dot()
        marker.add_updater(lambda m: m.move_to(self.plane.n2p(x0.get_value())))
        self.add(marker)


        def make_path():
            values = [x0.get_value()]

            for _ in range(40):
                z_prev = values[-1]
                z = z_prev - f(z_prev)/df(z_prev)
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
            return lines

        always_redraw(make_path);

        # self.add(ParametricFunction(lambda x: self.plane.n2p(np.e ** (0.9 * 1j * x)) , t_range=(0, 10)))

        self.play(x0.animate.set_value(0+1j))
        self.play(x0.animate.set_value(-0.5 + 2j))
        self.play(x0.animate.set_value(5 + 2j))
        self.play(x0.animate.set_value(-2 + 0j))

        self.wait(0.5)

        self.next_slide()

        # for quality in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]:
        #     n = self.gen_fractal_image(quality)
        #     self.next_slide()
        #     self.remove(fractal)
        #     self.add(n)
        #     fractal = n
