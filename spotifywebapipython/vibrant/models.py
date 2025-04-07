from dataclasses import dataclass
from typing import List, Optional

from .utils import hsl_to_rgb, rgb_to_hsl


@dataclass(frozen=True)
class Swatch:
    rgb: List[int]
    population: int
    hsl: Optional[List[float]]

    def __init__(self, rgb=[], population=0, hsl=[]):
        super().__init__()
        if rgb and not hsl:
            object.__setattr__(self, "rgb", rgb)
            object.__setattr__(self, "hsl", rgb_to_hsl(rgb))
        elif hsl and not rgb:
            object.__setattr__(self, "hsl", hsl)
            object.__setattr__(self, "rgb", hsl_to_rgb(hsl))
        object.__setattr__(self, "population", population)


@dataclass
class Palette:
    vibrant: Swatch = None
    dark_vibrant: Swatch = None
    light_vibrant: Swatch = None
    muted: Swatch = None
    dark_muted: Swatch = None
    light_muted: Swatch = None


@dataclass
class Props:
    color_count: int = 64
    quality: int = 5


@dataclass
class GeneratorOpts:
    target_dark_luma: int
    max_dark_luma: int
    min_light_luma: int
    target_light_luma: int
    min_normal_luma: int
    target_normal_luma: int
    max_normal_luma: int
    target_muted_saturation: int
    max_muted_saturation: int
    target_vibrant_saturation: int
    min_vibrant_saturation: int
    weight_saturation: int
    weight_luma: int
    weight_population: int
