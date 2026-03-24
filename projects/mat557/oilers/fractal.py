from shader_obj import *
from manimlib import *
from numpy.polynomial import Polynomial
from svgelements import max_depth

ROOT_COLORS_BRIGHT = [RED, GREEN, BLUE, YELLOW, MAROON_B]
ROOT_COLORS_DEEP = ["#440154", "#3b528b", "#21908c", "#5dc963", "#29abca"]
CUBIC_COLORS = [RED_E, TEAL_E, BLUE_E]


MODE_NEWTON = 0
MODE_HALLEY = 1
MODE_OILER = 2


def c2v(a: complex):
    return np.array([np.real(a), np.imag(a)])


class FractalNewton(ShaderMobject):
    def __init__(
        self, roots, degree=3, scale_factor=1, colors=ROOT_COLORS_DEEP, **kwargs
    ):
        super().__init__(shader_folder="newton", **kwargs)

        self.roots = roots
        self.degree = degree
        self.scale_factor = scale_factor

        for i, c in enumerate(colors):
            self.uniforms[f"color{1 + i}"] = np.array(color_to_rgb(c))
        self.set_roots(roots)
        self.set_scale_factor(1)

    def set_scale_factor(self, factor: float):
        self.scale_factor = factor
        self.uniforms["scale_factor"] = factor

    def set_mode(self, m: int = MODE_NEWTON):
        self.mode = m
        self.uniforms["mode"] = self.mode

    def set_roots(self, roots):
        self.roots = roots
        self.coefs = Polynomial.fromroots(self.roots).coef
        for i, c in enumerate(self.coefs):
            self.uniforms[f"coef{i}"] = c2v(c)
        for i, r in enumerate(self.roots):
            self.uniforms[f"root{i + 1}"] = c2v(r)

    def polynomial(self):
        return Polynomial(self.coefs)
