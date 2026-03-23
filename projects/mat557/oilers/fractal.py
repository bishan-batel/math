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
        super().__init__(shader_folder="newton", **kwargs)

        self.roots = roots
        self.degree = degree
        self.scale_factor = scale_factor

        self.f_always.set_uniforms(
            lambda: {
                "scale_factor": 1,
                "color1": color_to_rgb(colors[0]),
                "color2": color_to_rgb(colors[1]),
                "color3": color_to_rgb(colors[2]),
            }
        )
        self.set_roots(roots)

    def set_roots(self, roots):
        self.roots = roots
        self.coefs = Polynomial.fromroots(self.roots).coef
        self.set_uniforms(
            {
                "coef0": c2v(self.coefs[0]),
                "coef1": c2v(self.coefs[1]),
                "coef2": c2v(self.coefs[2]),
                "coef3": c2v(self.coefs[3]),
                "root1": c2v(self.roots[0]),
                "root2": c2v(self.roots[1]),
                "root3": c2v(self.roots[2]),
            }
        )

    def polynomial(self):
        return Polynomial(self.coefs)
