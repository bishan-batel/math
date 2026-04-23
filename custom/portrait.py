from manimlib import *


class PortraitWithCaption(Group):
    def __init__(
        self,
        image_path,
        name="Name",
        caption: str | None = None,
        image_size=3,
        name_size=24,
        caption_size=14,
        name_color=WHITE,
        caption_color=WHITE,
        outline_color=BLUE_B,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.image = ImageMobject(image_path)
        self.image.set_height(image_size)
        # self.image_rect = SurroundingRectangle(
        #     self.image, color=outline_color, buff=MED_SMALL_BUFF
        # )

        self.name_text = TexText(name, font_size=name_size)
        self.name_text.set_color(name_color)

        self.caption_text = (
            TexText(caption, font_size=caption_size)
            if caption is not None
            else VMobject()
        )
        self.caption_text.set_color(caption_color)

        self.text_group = VGroup(self.name_text, self.caption_text)
        self.text_group.arrange(DOWN, buff=0.2)
        self.text_group.next_to(self.image, DOWN, buff=0.3)

        self.add(self.image, self.text_group)
