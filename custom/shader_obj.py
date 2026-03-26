from manimlib import *
import numpy as np


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


class SpirVShaderMobject(Mobject):
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

            with open(filepath, "rb") as f:
                refreshed_code = f.read()

            # taken directly from 3b1b/manim
            # insertions = re.findall(
            #     r"^#INSERT .*\.glsl$", refreshed_code, flags=re.MULTILINE
            # )

            # for line in insertions:
            #     inserted_code = get_shader_code_from_file(
            #         os.path.join("inserts", line.replace("#INSERT ", ""))
            #     )
            #     refreshed_code = refreshed_code.replace(line, inserted_code)

            self.shader_wrapper.program_code[f"{shader_type}_shader"] = refreshed_code
            self.shader_wrapper.init_vertex_objects()
            self.shader_wrapper.init_program()
            self.shader_wrapper.refresh_id()
