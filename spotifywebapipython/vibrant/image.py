import io
import os
from typing import List, Optional, Tuple, Union
import requests
from PIL import Image
from PIL.Image import Image as PILImage

from .models import Props, Swatch


class VibrantImage:
    def __init__(
        self,
        src: Union[
            bytes,
            str,
            io.BytesIO,
            io.BufferedReader,
            PILImage,
            "VibrantImage",
        ],
        props: Optional[Props] = Props(),
    ) -> None:
        self.image: Image = None
        self.props: Props = props

        if isinstance(src, str):
            if src.startswith("http"):
                src = requests.get(src).content
            if not os.path.exists(src):
                raise FileNotFoundError("Image doesn't exist at given path - %s." % src)

        if isinstance(src, bytes):
            src = io.BytesIO(src)

        if isinstance(src, PILImage):
            self.image = src
        else:
            self.image = Image.open(src)

    @classmethod
    def from_url(cls, src: str) -> "VibrantImage":
        src = requests.get(src).content
        src = io.BytesIO(src)
        return cls(Image.open(src))

    @classmethod
    def from_path(cls, src: str) -> "VibrantImage":
        if os.path.exists(src):
            return cls(Image.open(src))
        raise FileNotFoundError("Image doesn't exist at given path - %s." % src)

    @classmethod
    def from_bytes(cls, src: bytes) -> "VibrantImage":
        src = io.BytesIO(src)
        return cls(Image.open(src))

    @classmethod
    def from_fp(cls, fp: io.BufferedReader) -> "VibrantImage":
        return cls(Image.open(fp))

    def scale_down(self):
        ...

    def _swatch_filter(self, swatch: List[int]) -> bool:
        r, g, b = swatch.rgb
        return not (r > 250 and g > 250 and b > 250)

    def _parse_swatches(
        self,
        raw_swatches: List,
        swatch_populations: List[Tuple[int, int]],
    ) -> List[Swatch]:
        swatches = []
        curr_idx = 0
        for idx in range(0, len(raw_swatches), 3):
            if idx + 2 <= (len(raw_swatches) - 1):
                swatches.append(
                    Swatch(
                        rgb=[
                            raw_swatches[idx],
                            raw_swatches[idx + 1],
                            raw_swatches[idx + 2],
                        ],
                        population=swatch_populations[curr_idx][0],
                    )
                )
                curr_idx += 1
        return swatches

    def quantize(self) -> List[Swatch]:
        self.image = self.image.quantize(self.props.color_count)
        raw_swatches = self.image.getpalette()
        raw_swatches = list(filter(lambda x: x != 0, raw_swatches))
        swatch_populations = self.image.getcolors(self.props.color_count)
        swatches = self._parse_swatches(
            raw_swatches=raw_swatches,
            swatch_populations=swatch_populations,
        )
        return swatches
