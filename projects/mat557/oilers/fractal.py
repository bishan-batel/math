from custom.shader_obj import *
from manimlib import *
from numpy.polynomial import Polynomial
from svgelements import max_depth

ROOT_COLORS_BRIGHT = [RED, GREEN, BLUE, YELLOW, MAROON_B]
ROOT_COLORS_DEEP = ["#440154", "#3b528b", "#21908c", "#5dc963", "#29abca"]
CUBIC_COLORS = [RED_E, TEAL_E, BLUE_E]


def c2v(a: complex):
    return np.array([np.real(a), np.imag(a)])


class FractalNewton(ShaderMobject):
    def __init__(self, roots, scale_factor=1, colors=ROOT_COLORS_DEEP, **kwargs):
        from pathlib import Path

        dir = f"{Path(__file__).resolve().parent}/newton"
        super().__init__(shader_folder=dir, **kwargs)

        self.roots = roots
        self.scale_factor = scale_factor

        for i, c in enumerate(colors):
            self.uniforms[f"u_color{1 + i}"] = np.array(color_to_rgb(c))

        self.set_roots(roots)
        self.set_scale_factor(1)
        self.enable_limit_coloring()
        self.set_seed_space()
        self.set_iteration_coloring()

    def set_scale_factor(self, factor: float):
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
        self.is_parametric = 1 if is_parametric else 0

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
