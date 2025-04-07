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

    @property
    def rgb_hex(self) -> str:
        """ 
        The RGB value expressed in displayable hex string format (e.g. "#ff560a").  
        """
        return f"#{self.rgb[0]:02x}{self.rgb[1]:02x}{self.rgb[2]:02x}"

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'rgb_hex': self.rgb_hex,
            'rgb': self.rgb,
            'population': self.population,
            'hsl': self.hsl
        }
        return result

    def ToString(self, includeTitle:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeTitle (str):
                True to include the class name title prefix.
        """
        msg:str = ''
        if includeTitle: 
            msg = 'Swatch:'
        
        msg = '%s RGBHex="%s"' % (msg, self.rgb_hex)
        msg = '%s RGB=%s' % (msg, str(self.rgb))
        msg = '%s Population=%s' % (msg, str(self.population))
        msg = '%s HSL=%s' % (msg, str(self.hsl))
        return msg 


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
