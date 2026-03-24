from shader_obj import *
from manimlib import *
from numpy.polynomial import Polynomial
from svgelements import max_depth

ROOT_COLORS_BRIGHT = [RED, GREEN, BLUE, YELLOW, MAROON_B]
ROOT_COLORS_DEEP = ["#440154", "#3b528b", "#21908c", "#5dc963", "#29abca"]
CUBIC_COLORS = [RED_E, TEAL_E, BLUE_E]


def c2v(a: complex):
    return np.array([np.real(a), np.imag(a)])


class FractalNewton(ShaderMobject):
    max_depth: int

    def __init__(
        self, roots, degree=3, scale_factor=1, colors=ROOT_COLORS_DEEP, **kwargs
    ):
        super().__init__(shader_folder="newton", **kwargs, height=FRAME_HEIGHT * 10)

        self.roots = roots
        self.degree = degree
        self.scale_factor = scale_factor

        self.uniforms["scale_factor"] = 1
        for i, c in enumerate(colors):
            self.uniforms[f"color{1 + i}"] = color_to_rgb(c)
        self.set_roots(roots)

    def set_roots(self, roots):
        self.roots = roots
        self.coefs = Polynomial.fromroots(self.roots).coef
        for i, c in enumerate(self.coefs):
            self.uniforms[f"coef{i}"] = c2v(c)
        for i, r in enumerate(self.roots):
            self.uniforms[f"root{i + 1}"] = c2v(r)

    def polynomial(self):
        return Polynomial(self.coefs)
