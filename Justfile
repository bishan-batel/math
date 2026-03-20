start_dir := absolute_path("./")

set working-directory := "."

latest-project := "mat557/oilers/OilersMethod.py"

alias pr := present-and-render
alias p := present
alias r := render

@default: (present-and-render latest-project)

@present-and-render project=latest-project: (render project) (present project)

@present project=latest-project:
    @echo Presenting {{ project }}
    uv run manim-slides present

[arg('high-quality', short="h", value="true")]
@render project=latest-project high-quality="false" *args:
    @echo Rendering {{ project }}
    uv run manim-slides render "projects/{{ project }}" {{ args }} {{ if high-quality != "false" { "-qh" } else { "-pql --fps=12" } }}
