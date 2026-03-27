from manimlib import *
import numpy as np

import slangpy as slang
import tempfile
import subprocess


def compile_slang_to_glsl(shader_file, entry, stage):
    with tempfile.NamedTemporaryFile(suffix=".spv", delete=False) as tmp:
        spv_path = tmp.name
    with tempfile.NamedTemporaryFile(suffix=".glsl", delete=False) as tmp:
        glsl_output = tmp.name

    subprocess.run(
        [
            "slangc",
            shader_file,
            "-entry",
            entry,
            "-stage",
            stage,
            "-target",
            "spirv",
            "-O0",
            "-profile",
            "spirv_1_5",
            "-o",
            spv_path,
        ],
        check=True,
    )

    subprocess.run(
        [
            "spirv-cross",
            spv_path,
            "--version",
            "410",
            # "--glsl-emit-ubo-as-plain-uniforms",
            # # "--glsl-force-flattened-io-blocks",
            # "--flatten-ubo",
            # "--es",
            "--output",
            glsl_output,
        ]
    )
    # subprocess.run(
    #     [
    #         "slangc",
    #         shader_file,
    #         "-entry",
    #         entry,
    #         "-stage",
    #         stage,
    #         "-target",
    #         "glsl",
    #         "-profile",
    #         "glsl_410",
    #         "-o",
    #         glsl_output,
    #     ],
    #     check=True,
    # )

    with open(glsl_output, "r") as f:
        src = f.read()

    return fix_glsl_for_manim(src, stage)


def fix_glsl_for_manim(src: str, stage: str) -> str:
    import re

    # ensure version
    if not src.startswith("#version"):
        src = "#version 410\n" + src

    # fix attribute naming (VERY IMPORTANT)

    # optional: strip layout qualifiers that break GL 3.3
    # src = src.replace("layout(location = 0)", "")
    # src = src.replace("layout(binding = 0, std140)", "")
    # src = src.replace("} globalParams;", "};")
    # src = src.replace("globalParams.", "")

    src = re.sub(
        r"layout\(binding = \d+,",
        r"layout(",
        src,
        count=0,
        flags=0,
    )
    if stage == "vertex":
        src = src.replace("out float gl_ClipDistance[4];", "")
        src = src.replace("POSITION", "point")
        src = src.replace("input_point", "point")
        src = src.replace("entryPointParam_vs_main_xyz_coords", "input_xyz_coords")
        src = src.replace("layout(row_major)", "")

        # src = re.sub(
        #     r"layout(binding = \d+, std140) uniform",
        #     r"uniform",
        #     src,
        #     count=0,
        #     flags=0,
        # )
        # src = src.replace("uniform GlobalParams_std140\n{", "")
        # src = src.replace("\n};", "")

    return src


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


class SlangShaderMobject(Mobject):
    def __init__(
        self,
        shader_file: str,
        data_dtype: np.dtype = [("point", np.float32, (3,))],
        height: float = FRAME_HEIGHT,
        aspect_ratio: float = 16 / 9,
        scale_factor=1,
        **kwargs,
    ):
        self.aspect_ratio = aspect_ratio
        self.shader_file = shader_file
        self.data_dtype = data_dtype
        self.shader_folder = ""

        super().__init__(**kwargs)
        self.set_height(height, stretch=True)
        self.set_width(height * aspect_ratio, stretch=True)
        self.set_scale_factor(scale_factor)

    def init_data(self, length: int = 4) -> None:
        super().init_data(length=length)
        self.data["point"][:] = [UL, DL, UR, DR]

    def set_color(self, *args, **kwargs):
        return self

    def set_scale_factor(self, factor: float):
        self.uniforms["scale_factor"] = factor
        self.scale_factor = factor

    @Mobject.affects_data
    def refresh(self) -> None:
        if not os.path.exists(self.shader_file):
            raise FileNotFoundError(self.shader_file)

        wrapper: ShaderWrapper = self.shader_wrapper

        vertex_shader = compile_slang_to_glsl(self.shader_file, "vs_main", "vertex")
        fragment_shader = compile_slang_to_glsl(self.shader_file, "fs_main", "fragment")
        print("Vertex: ", vertex_shader)
        print("Fragment: ", fragment_shader)

        ctx: moderngl.Context = wrapper.ctx
        print("Context=", ctx.version_code)

        wrapper.init_vertex_objects()
        wrapper.program = ctx.program(
            vertex_shader=vertex_shader, fragment_shader=fragment_shader
        )
        wrapper.vert_format = moderngl.detect_format(
            wrapper.program, wrapper.vert_attributes
        )
        wrapper.programs = [wrapper.program]
        wrapper.refresh_id()
