import io
from typing import Union

from PIL.Image import Image as PILImage

from .generator import generate
from .image import VibrantImage
from .models import Palette, Props


class Vibrant:
    props: Props

    def __init__(self, color_count=64, quality=5) -> None:
        self.props = Props(color_count=color_count, quality=quality)

    def get_palette(
        self,
        src: Union[
            bytes,
            str,
            io.BytesIO,
            io.BufferedReader,
            PILImage,
            VibrantImage,
        ],
    ) -> Palette:
        image = src
        if not isinstance(src, VibrantImage):
            image = VibrantImage(src, self.props)
        image.scale_down()
        swatches = image.quantize()
        palette = generate(swatches)
        return palette
