set working-directory := "."

latest-project := "mat557/oilers/OilersMethod.py"

present-and-render project=latest-project: (render-slide project) (present project)

present project=latest-project *args:
    @echo Presenting ${{ project }}
    uv run manim-slides render {{ args }}

render-slide project=latest-project *args:
    @echo Rendering {{ project }}
    uv run manim-slides render "projects/{{ project }}" {{ args }}
