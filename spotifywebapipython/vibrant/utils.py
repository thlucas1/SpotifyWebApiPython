from math import ceil
from typing import List


def rgb_to_hsl(rgb: List[int]) -> List[float]:
    r, g, b = rgb
    r /= 255
    g /= 255
    b /= 255
    min_val = min(r, g, b)
    max_val = max(r, g, b)

    l = (max_val + min_val) / 2

    if min_val == max_val:
        s = 0
    elif l <= 0.5:
        s = (max_val - min_val) / (max_val + min_val)
    elif l > 0.5:
        s = (max_val - min_val) / (2.0 - max_val - min_val)

    if max_val - min_val == 0:
        h = 0
    elif max_val == r:
        h = ((g - b) / (max_val - min_val)) % 6
    elif max_val == g:
        h = (2.0) + (b - r) / (max_val - min_val)
    else:
        h = 4.0 + (r - g) / (max_val - min_val)
    h = h * 60
    h = h + 360 if h < 0 else h

    return [round(val, 3) for val in (h, s, l)]


def hsl_to_rgb(hsl: List[float]) -> List[int]:
    h, s, l = hsl
    c = (1 - abs((2 * l) - 1)) * s
    x = c * (1 - abs(((h / 60) % 2) - 1))
    m = l - c / 2

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x

    r, g, b = (r + m) * 255, (g + m) * 255, (b + m) * 255
    return [ceil(val) for val in (r, g, b)]
