from manimlib import *
from numpy.polynomial import Polynomial
from svgelements import max_depth

ROOT_COLORS_BRIGHT = [RED, GREEN, BLUE, YELLOW, MAROON_B]
ROOT_COLORS_DEEP = ["#440154", "#3b528b", "#21908c", "#5dc963", "#29abca"]
CUBIC_COLORS = [RED_E, TEAL_E, BLUE_E]


def c2v(a: complex):
    return np.array([np.real(a), np.imag(a)])


class ShaderMobject(Mobject):
    def __init__(
        self,
        shader_folder: str,
        data_dtype: np.dtype = [("point", np.float32, (3,))],
        height: float = FRAME_HEIGHT,
        aspect_ratio: float = 16 / 9,
        **kwargs,
    ):
        self.aspect_ratio = aspect_ratio
        self.shader_folder = shader_folder
        self.data_dtype = data_dtype

        super().__init__(**kwargs)
        self.set_height(height, stretch=True)
        self.set_width(height * aspect_ratio, stretch=True)

    def init_data(self, length: int = 4) -> None:
        super().init_data(length=length)
        self.data["point"][:] = [UL, DL, UR, DR]

    def set_color(self, *args, **kwargs):
        return self

    @Mobject.affects_data
    def refresh(self) -> None:
        """
        This is used to reload the shaders files
        (frag.glsl, vert.glsl, geom.glsl) in the embed mode.
        """

        for shader_type in ["fragment", "vertex", "geometry"]:
            file_name = f"{shader_type[:4]}.glsl"
            filepath = os.path.join(self.shader_folder, file_name)

            if not os.path.exists(filepath):
                if shader_type == "geometry":
                    # most of the time, geom.glsl is not required
                    continue
                else:
                    raise FileNotFoundError(
                        f"{file_name} isn't found at the specified location."
                    )

            with open(filepath, "r") as f:
                refreshed_code = f.read()

            # taken directly from 3b1b/manim
            insertions = re.findall(
                r"^#INSERT .*\.glsl$", refreshed_code, flags=re.MULTILINE
            )

            for line in insertions:
                inserted_code = get_shader_code_from_file(
                    os.path.join("inserts", line.replace("#INSERT ", ""))
                )
                refreshed_code = refreshed_code.replace(line, inserted_code)

            self.shader_wrapper.program_code[f"{shader_type}_shader"] = refreshed_code
            self.shader_wrapper.init_vertex_objects()
            self.shader_wrapper.init_program()
            self.shader_wrapper.refresh_id()


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
