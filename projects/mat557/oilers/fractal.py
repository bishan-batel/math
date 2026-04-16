from custom.shader_obj import *
from manimlib import *  # pyright: ignore
from numpy.polynomial import Polynomial

ROOT_COLORS_BRIGHT: list[Color] = [
    Color(c) for c in [RED, GREEN, BLUE, YELLOW, MAROON_B]
]

ROOT_COLORS_DEEP: list[Color] = [
    Color(c)
    for c in [
        "#440154",
        "#3b528b",
        "#21908c",
        "#5dc963",
        "#29abca",
    ]
]
CUBIC_COLORS = [RED_E, TEAL_E, BLUE_E]


def c2v(a: complex):
    return np.array([np.real(a), np.imag(a)])


class FractalNewton(ShaderMobject):
    scene: Scene | None = None
    colors: list[Color] = []
    relaxed_newtons: float = 1.0
    is_parametric: bool
    z0: complex
    roots: list[complex]
    iteraiton_coloring: bool

    def __init__(
        self,
        roots,
        scale_factor=1,
        colors=ROOT_COLORS_DEEP,
        opacity=1.0,
        **kwargs,
    ):
        from pathlib import Path

        dir = f"{Path(__file__).resolve().parent}/newton"
        super().__init__(
            shader_folder=dir,
            opacity=opacity,
            **kwargs,
        )

        self.set_max_iterations()
        self.set_roots(roots)
        self.set_color_opacities()
        self.set_colors(colors)
        self.set_infinity_color()
        self.set_cycle_color()
        self.set_scale_factor(scale_factor)
        self.enable_limit_coloring()
        self.set_seed_space()
        self.set_iteration_coloring()
        self.set_epsilon()
        self.set_julia_highlight()
        self.set_relaxed_newtons()

    def pin(self, scene: Scene):
        self.scene = scene
        self.always._pin_update()

    def _pin_update(self):
        if self.scene is None:
            return
        self.replace(self.scene.frame, stretch=True)

    def set_should_break_on_convergence(self, state=True):
        self.uniforms["u_should_break_on_convergence"] = state

    def set_epsilon(self, epsilon: float = 1e-3):
        self.epsilon = epsilon
        self.uniforms["u_epsilon"] = epsilon
        return self

    def get_epsilon(self) -> float:
        return self.epsilon

    def set_max_iterations(self, iterations: int = 100):
        self.max_iterations = iterations
        self.uniforms["u_max_iterations"] = int(iterations)
        return self

    def get_max_iterations(self) -> int:
        return self.max_iterations

    def set_infinity_color(self, color=WHITE):
        self.infinity_color = Color(color)
        self.uniforms["u_color_infinity"] = np.array(color_to_rgba(color))
        return self

    def get_infinity_color(self):
        return self.infinity_color

    def set_cycle_color(self, color=BLACK):
        self.infinity_color = color
        self.uniforms["u_color_cycle"] = np.array(color_to_rgba(color))
        return self

    def get_cycle_color(self):
        return self.infinity_color

    def set_color_opacities(self, opacities: list[float] = [1, 1, 1]):
        self.color_opacities = opacities
        self.set_colors(self.get_colors())
        return self

    def get_color_opacities(self) -> list[float]:
        return self.color_opacities

    def set_colors(self, colors=ROOT_COLORS_DEEP):
        self.colors = list(colors)
        for i, c in enumerate(colors):
            alpha = self.color_opacities[i] if i < len(self.color_opacities) else 1

            self.uniforms[f"u_color{1 + i}"] = np.array(color_to_rgba(c, alpha=alpha))
        return self

    def get_colors(self) -> list[Color]:
        return self.colors

    def set_scale_factor(self, factor=1.0):
        self.scale_factor = factor
        self.uniforms["scale_factor"] = factor
        return self

    def get_scale_factor(self):
        return self.scale_factor

    def set_should_color_cycles(self, should_color=True):
        self.should_color_cycles = should_color
        self.uniforms["u_should_color_cycles"] = 1 if should_color else 0
        return self

    def get_should_color_cycles(self):
        return self.should_color_cycles

    def set_julia_highlight(self, highlight=0.0):
        self.julia_highlight = highlight
        self.uniforms["u_julia_highlight"] = highlight
        return self

    def get_julia_highlight(self):
        return self.julia_highlight

    def set_mode(self, m: int):
        self.mode = m
        self.uniforms["u_mode"] = self.mode
        return self

    def get_mode(self):
        return self.mode

    def enable_domain_coloring(self):
        self.uniforms["u_color_mode"] = 0
        return self

    def enable_limit_coloring(self):
        self.uniforms["u_color_mode"] = 1
        return self

    def set_iteration_coloring(self, color=True):
        self.iteration_coloring = color
        self.uniforms["u_do_iteration_coloring"] = 1 if color else 0
        return self

    def get_iteration_coloring(self):
        self.iteration_coloring = True

    def set_parameter_space(self, is_parametric=True):
        self.is_parametric = is_parametric
        self.uniforms["u_parametric"] = 1 if is_parametric else 0
        return self

    def get_parameter_space(self):
        return self.is_parametric

    def set_seed_space(self, is_seed=True):
        self.set_parameter_space(not is_seed)
        return self

    def get_seed_space(self):
        return not self.is_parametric

    def set_relaxed_newtons(self, relaxed=1.0):
        self.relaxed_newtons = relaxed
        self.uniforms["u_relaxed_newtons"] = relaxed
        return self

    def get_relaxed_newtons(self):
        return self.relaxed_newtons

    def set_roots(self, roots: Iterable[complex]):
        self.roots = list(roots)

        for i, r in enumerate(self.roots):
            self.uniforms[f"u_root{i + 1}"] = c2v(r)

        return self

    def get_roots(self):
        return self.roots

    def set_z0(self, z0: complex):
        self.z0 = z0
        self.uniforms["u_z0"] = c2v(z0)

    def get_z0(self):
        return self.z0

    def set_opacity(self, opacity: float):
        self.opacity = opacity
        self.uniforms["u_opacity"] = opacity
        return self

    def get_opacity(self):
        return self.opacity

    def polynomial(self):
        return Polynomial.fromroots(self.roots)
