PROJECTS_DIR := source_dir()
project := "mat557/oilers/OilersMethod.py"
scenes := "Title NewtonsFractal"
render-subcommand := "render"

# mani command

manim := "manim"
renderer := "cairo"

alias pr := present-and-render
alias p := present
alias r := render

present-and-render project=project scenes=scenes: (render project) (present scenes)

@present scenes=scenes:
    @cd {{ PROJECTS_DIR }}
    echo Presenting {{ scenes }}
    @uv run manim-slides present {{ scenes }}

[arg('high-quality', short="h", value="true")]
[arg('medium', short="m", value="true")]
[arg('preview', short="p", value="true")]
[arg('scenes', short="s")]
[arg('manim-subcommand', long="subcmd")]
@render project=project high-quality="false" medium="false" preview="false" scenes=scenes manim=manim manim-subcommand=render-subcommand args="":
    @cd {{ PROJECTS_DIR }}
    echo Rendering {{ project }}
    @uv run {{ manim }} {{ manim-subcommand }} "{{ PROJECTS_DIR }}/projects/{{ project }}" \
        {{ args }} \
        --renderer={{ renderer }} \
        {{ if high-quality != "false" { "-qk" } else if medium != "false" { "-qm" } else { "-ql --fps=12" } }} \
        {{ if preview != "false" { "-p --enable_gui" } else { "" } }} \
        {{ scenes }}
