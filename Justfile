start_dir := absolute_path("./")

set working-directory := "."

latest-project := "mat557/oilers/OilersMethod.py"
slides := "Title NewtonsFractal"

alias pr := present-and-render
alias p := present
alias r := render

default: (present-and-render latest-project)

present-and-render project=latest-project scene=slides: (render project) (present scene)

@present scene=slides:
    echo Presenting {{ scene }}
    @uv run manim-slides present {{ scene }}

[arg('high-quality', short="h", value="true")]
[arg('preview', short="p", value="true")]
[arg('slides', short="s")]
@render project=latest-project high-quality="false" preview="false" slides=slides *args:
    echo Rendering {{ project }}
    @uv run manim-slides render "projects/{{ project }}" \
        {{ args }} \
        {{ if high-quality != "false" { "-qk" } else { "-ql --fps=12" } }} \
        {{ if preview != "false" { "-p" } else { "" } }} \
        {{ slides }}
