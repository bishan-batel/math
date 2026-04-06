from custom.shader_obj import *
from manimlib import *
from numpy.polynomial import Polynomial
from svgelements import max_depth

ROOT_COLORS_BRIGHT = [RED, GREEN, BLUE, YELLOW, MAROON_B]
ROOT_COLORS_DEEP = [
    "#440154",
    "#3b528b",
    "#21908c",
    "#5dc963",
    "#29abca",
]
CUBIC_COLORS = [RED_E, TEAL_E, BLUE_E]


def c2v(a: complex):
    return np.array([np.real(a), np.imag(a)])


class FractalNewton(ShaderMobject):
    def __init__(self, roots, scale_factor=1, colors=ROOT_COLORS_DEEP, **kwargs):
        from pathlib import Path

        dir = f"{Path(__file__).resolve().parent}/newton"
        super().__init__(shader_folder=dir, **kwargs)

        self.set_max_iterations()
        self.set_roots(roots)
        self.set_colors(colors)
        self.set_infinity_color()
        self.set_cycle_color()
        self.set_scale_factor(scale_factor)
        self.enable_limit_coloring()
        self.set_seed_space()
        self.set_iteration_coloring()
        self.set_epsilon()

    def set_epsilon(self, epsilon=1e-5):
        self.epsilon = epsilon
        self.uniforms["u_epsilon"] = epsilon

    def set_max_iterations(self, iterations=100):
        self.max_iterations = iterations
        self.uniforms["u_max_iterations"] = iterations

    def set_infinity_color(self, color=WHITE):
        self.infinity_color = color
        self.uniforms["u_color_infinity"] = np.array(color_to_rgb(color))

    def set_cycle_color(self, color=BLACK):
        self.infinity_color = color
        self.uniforms["u_color_cycle"] = np.array(color_to_rgb(color))

    def set_colors(self, colors=ROOT_COLORS_DEEP):
        self.colors = list(colors)
        for i, c in enumerate(colors):
            self.uniforms[f"u_color{1 + i}"] = np.array(color_to_rgb(c))

    def set_scale_factor(self, factor=1.0):
        self.scale_factor = factor
        self.uniforms["scale_factor"] = factor

    def set_mode(self, m: int):
        self.mode = m
        self.uniforms["u_mode"] = self.mode

    def enable_domain_coloring(self):
        self.uniforms["u_color_mode"] = 0

    def enable_limit_coloring(self):
        self.uniforms["u_color_mode"] = 1

    def set_iteration_coloring(self, color=True):
        self.uniforms["u_do_iteration_coloring"] = 1 if color else 0

    def set_parameter_space(self, is_parametric=True):
        self.uniforms["u_parametric"] = is_parametric
        self.is_parametric = np.uint(1 if is_parametric else 0)

    def set_seed_space(self, is_seed=True):
        self.set_parameter_space(not is_seed)

    def set_roots(self, roots):
        self.roots = roots

        for i, r in enumerate(self.roots):
            self.uniforms[f"u_root{i + 1}"] = c2v(r)

    def set_z0(self, z0: complex):
        self.uniforms["u_z0"] = c2v(z0)

    def polynomial(self):
        return Polynomial.fromroots(self.roots)
