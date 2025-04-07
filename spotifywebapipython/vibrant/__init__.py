# "vibrant" namespace was imported from "vibrant-python" namespace (https://github.com/totallynotadi/vibrant-python)
# had to import it, as the "vibrant-python" version has a dependency that was not compatible with current version of Home Assistant:
# - "vibrant-python==0.1.6 depends on pillow>=10.1.0,<11.0.0"

# import all classes from the namespace.
from .image import VibrantImage
from .main import Vibrant
from .models import Palette, Props, Swatch
from .utils import hsl_to_rgb, rgb_to_hsl

# all classes to import when "import *" is specified.
__all__ = [
    'VibrantImage',
    'Vibrant',
    'Palette',
    'Swatch',
]