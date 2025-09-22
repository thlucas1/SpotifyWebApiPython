# Copyright 2025-2025 JiangLong Jia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
__version__ = '1.1.0'

import functools
from typing import Dict, Callable, List, Tuple, Optional, Union

import colorsys
import io
import numpy as np
from PIL import Image
import requests


class ColorThiefFast:
    """
    Color thief main class.
    """
    RGB = Tuple[int, int, int]

    def __init__(self, image: Union[str, Image.Image, np.ndarray], return_percent: bool = False):
        self.image: np.ndarray = self.process_image(image)
        self.return_percent = return_percent


    def process_image(
        self, 
        image
        ) -> np.ndarray:

        if isinstance(image, str):
            try:
                if (image.startswith("http:")) or (image.startswith("https:")):
                    image = requests.get(image).content
                    image = io.BytesIO(image)
                    image = Image.open(image)
                else:
                    image = Image.open(image)
                image = image.convert('RGBA')
                image = np.array(image)
            except FileNotFoundError:
                raise ValueError(f"File {image} not found.")

        elif isinstance(image, Image.Image):
            image = image.convert('RGBA')
            image = np.array(image)

        elif not isinstance(image, np.ndarray):
            raise TypeError("Input must be a http/https url, file path, a PIL Image, or a numpy array.")

        if image.ndim == 2:
            alpha = np.full_like(image, 255, dtype=np.uint8)
            image = np.stack((image, image, image, alpha), axis=-1)
        elif image.ndim == 3:
            if image.shape[2] == 1:
                alpha = np.full_like(image[:, :, 0], 255, dtype=np.uint8)
                image = np.repeat(image, 3, axis=2)
                image = np.dstack((image, alpha))
            elif image.shape[2] == 3:
                alpha = np.full((image.shape[0], image.shape[1]), 255, dtype=np.uint8)
                image = np.dstack((image, alpha))
            elif image.shape[2] != 4:
                raise ValueError("Unsupported number of channels in the numpy array.")
        else:
            raise ValueError("The input image is incorrect")

        return image


    def get_color(
        self, 
        quality: int = 10
        ) -> Union[Tuple[int, int, int], Tuple[int, int, int, int]]:
        """
        Get the dominant color.

        Args:
            quality:
                quality settings, 1 is the highest quality, the bigger
                the number, the faster a color will be returned but
                the greater the likelihood that it will not be the
                visually most dominant color.

        Returns:
            tuple: (r, g, b) or (r, g, b, percent)
        """
        palette = self.get_palette(5, quality)
        return palette[0]


    def get_palette(
        self,
        color_count: int = 10,
        quality: int = 10,
        brightness_filter_low: int = None,
        brightness_filter_high: int = None,
        hue_distance_filter: int = None,
        custom_processing: Callable[[np.ndarray], np.ndarray] = None
        ) -> Union[List[Tuple[int, int, int]], List[Tuple[int, int, int, int]]]:
        """
        Build a color palette.  We are using the median cut algorithm to
        cluster similar colors.

        Args:
            color_count:
                The size of the palette, max number of colors.  
                Default is 10.  
            quality:
                Quality settings, 1 is the highest quality, the bigger
                the number, the faster the palette generation, but the
                greater the likelihood that colors will be missed.  
                Default is 10.  
            brightness_filter_low (int):
                Remove colors that are too dark based on their brightness value.  
                Default is None.  
            brightness_filter_high (int):
                Remove colors that are too light based on their brightness value.  
                Default is None.  
            hue_distance_filter (int):
                Remove colors that are too close to each other for the specified hue.
                This keeps the colors looking fairly distinct.  
                Default is None.  
            custom_processing:
                Customize pixel processing functions.  
        Returns:
            list: a list of tuple in the form (r, g, b) or (r, g, b, percent)

        The returned list of RGB values will always have a length value that
        matches the `color_count` argument.  If colors are filtered, then the
        list is padded with black (e.g. 0,0,0) RGB entries.  This ensures that
        the list length always matches the requested color count.

        If the `brightness_filter_x` values are specified, each color in the
        returned array is converted to a brightness value (R+G+B=brightness, 0-765)
        and will be filtered out based on the high / low filter arguments.

        If the `hue_distance_filter` is specified, each color in the returned array
        is converted to a hue value and will be filtered out based on the distance
        between in and the next color.
        """
        # validations.
        if custom_processing is None:
            custom_processing = PixelsProcessor.get_valid_pixels

        if (not isinstance(color_count, int)) \
        or (color_count < 0):
            color_count = 10

        image_array = np.reshape(self.image, (-1, 4))
        image_array = image_array[::quality, :]

        valid_pixels = custom_processing(image_array)

        # Send array to quantize function which clusters values using median cut algorithm
        cmap = MMCQ.quantize(valid_pixels, color_count + 1)
        cmap.return_percent = self.return_percent
        result = cmap.palette

        # if brightness filters specified, then apply them.
        if (brightness_filter_low is not None) or (brightness_filter_high is not None):
            result = self.filter_colors_by_brightness(result, low=brightness_filter_low, high=brightness_filter_high)

        if (hue_distance_filter is not None):
            result = self.filter_colors_by_hue(result, min_distance=hue_distance_filter)

        # ensure number of palette entries returned matches requested color count.
        palette_len:int = len(result or [])
        if palette_len < color_count:
            for i in range(palette_len, color_count):
                result.append([0,0,0])

        # return result to caller.
        return result
    

    def rgb_brightness(
        self,
        rgb: List[RGB]
        ) -> int:
        """
        Return brightness as sum of R+G+B (0-765).
        """
        r, g, b = rgb
        return r + g + b


    def filter_colors_by_brightness(
        self,
        colors: List[RGB], 
        low: int = 200, 
        high: int = 600
        ) -> List[RGB]:
        """
        Keep only colors with brightness between [low, high].
        Brightness is R+G+B, range 0-765.
        """
        # validations.
        if low is None:
            low = 0
        if high is None:
            high = 765

        # validations - brightness filter can only be between 0-765 (R+G+B=brightness).
        if isinstance(low, int):
            if low < 0:
                low = 0
        if isinstance(high, int):
            if high > 765:
                high = 765

        # process brightness filter.
        return [c for c in colors if low <= self.rgb_brightness(c) <= high]


    def rgb_to_hue(
        self,
        rgb: RGB
        ) -> float:
        """
        Convert RGB (0-255 each) to hue in range 0-360 degrees.
        """
        r, g, b = [x / 255.0 for x in rgb]
        h, _, _ = colorsys.rgb_to_hsv(r, g, b)  # h in [0.0, 1.0)
        return h * 360


    def circular_distance(
        self,
        h1: float, 
        h2: float
        ) -> float:
        """
        Return the circular distance between two hue angles (0-360).
        """
        diff = abs(h1 - h2)
        return min(diff, 360 - diff)


    def filter_colors_by_hue(
        self,
        colors: List[RGB], 
        min_distance: float = 20.0
        ) -> List[RGB]:
        """
        Keep only colors whose hue is at least `min_distance` apart.
        Uses circular distance around the color wheel.
        """
        # validations.
        if min_distance is None:
            min_distance = 20

        # validations - hue min distance filter can only be between 0-255.
        if isinstance(min_distance, int):
            if min_distance < 0:
                min_distance = 0
            if min_distance > 255:
                min_distance = 255

        kept: List[ColorThiefFast.RGB] = []
        kept_hues: List[float] = []

        for c in colors:
            hue = self.rgb_to_hue(c)
            if all(self.circular_distance(hue, kh) >= min_distance for kh in kept_hues):
                kept.append(c)
                kept_hues.append(hue)
        return kept    


class PixelsProcessor:
    def get_valid_pixels(
        image_array: np.ndarray
        ) -> np.ndarray:
        """
        Default method to obtain valid pixels.
        """
        condition = ((image_array[..., 3] >= 125) &
                     ~((image_array[..., 0] > 250) & (image_array[..., 1] > 250) & (image_array[..., 2] > 250)))

        valid_pixels = image_array[condition][:, :3]
        return valid_pixels


class MMCQ:
    """
    Basic Python port of the MMCQ (modified median cut quantization)
    algorithm from the Leptonica library (http://www.leptonica.com/).
    """
    SIGBITS = 5
    RSHIFT = 8 - SIGBITS
    MAX_ITERATION = 1000
    FRACT_BY_POPULATIONS = 0.75

    @staticmethod
    def get_color_index(r, g, b):
        """
        Each quantified (r,g,b) will calculate a unique index value.
        """
        return (r << (2 * MMCQ.SIGBITS)) + (g << MMCQ.SIGBITS) + b

    @staticmethod
    def get_histo(
        pixels: np.ndarray
        ) -> Dict[int, int]:
        """
        Calculate the number of pixels in each quantized region of the color space,
        and save it in histo dict.
        """
        pixels = pixels.astype(np.uint32)

        r = np.right_shift(pixels[:, 0], MMCQ.RSHIFT)
        g = np.right_shift(pixels[:, 1], MMCQ.RSHIFT)
        b = np.right_shift(pixels[:, 2], MMCQ.RSHIFT)
        color_index_array = MMCQ.get_color_index(r, g, b)

        unique_indices, counts = np.unique(color_index_array, return_counts=True)
        histo = {i: int(count) for i, count in zip(unique_indices, counts) if count != 0}
        return histo

    @staticmethod
    def vbox_from_pixels(pixels: np.ndarray, histo: Dict[int, int]) -> "VBox":
        rval = np.right_shift(pixels[:, 0], MMCQ.RSHIFT)
        gval = np.right_shift(pixels[:, 1], MMCQ.RSHIFT)
        bval = np.right_shift(pixels[:, 2], MMCQ.RSHIFT)
        rmin = rval.min()
        rmax = rval.max()
        gmin = gval.min()
        gmax = gval.max()
        bmin = bval.min()
        bmax = bval.max()
        return VBox(rmin, rmax, gmin, gmax, bmin, bmax, histo, pixels.shape[0])

    @staticmethod
    def median_cut_apply(histo, vbox: "VBox"):
        if not vbox.count:
            return (None, None)

        rw = vbox.r2 - vbox.r1 + 1
        gw = vbox.g2 - vbox.g1 + 1
        bw = vbox.b2 - vbox.b1 + 1
        maxw = max([rw, gw, bw])

        # only one pixel, no split
        if vbox.count == 1:
            return (vbox.copy, None)

        # Find the partial sum arrays along the selected axis.
        partial_sum = {}
        lookahead_sum = {}

        if maxw == rw:
            do_cut_color = 'r'
            column_num = 0
        elif maxw == gw:
            do_cut_color = 'g'
            column_num = 1
        else:
            do_cut_color = 'b'
            column_num = 2

        rgb_array, color_index_array = vbox.get_rgb_array_and_color_index_array()
        color_num_list = [histo.get(index, 0) for index in color_index_array]
        unique_values, indices = np.unique(rgb_array[:, column_num], return_inverse=True)
        color_sum_array = np.bincount(indices, weights=color_num_list)

        total_array = np.cumsum(color_sum_array, dtype=np.int32)
        for i, t in zip(unique_values, total_array):
            partial_sum[i] = t

        total = total_array[-1]
        for i, d in partial_sum.items():
            lookahead_sum[i] = total - d

        # determine the cut planes
        dim1 = do_cut_color + '1'
        dim2 = do_cut_color + '2'
        dim1_val = getattr(vbox, dim1)
        dim2_val = getattr(vbox, dim2)
        for i in range(dim1_val, dim2_val + 1):
            if partial_sum[i] > (total / 2):
                vbox1 = vbox.copy
                vbox2 = vbox.copy
                left = i - dim1_val
                right = dim2_val - i
                if left <= right:
                    d2 = min([dim2_val - 1, int(i + right / 2)])
                else:
                    d2 = max([dim1_val, int(i - 1 - left / 2)])

                # avoid 0-count boxes
                while not partial_sum.get(d2, False):
                    d2 += 1
                count2 = lookahead_sum.get(d2)
                while not count2 and partial_sum.get(d2 - 1, False):
                    d2 -= 1
                    count2 = lookahead_sum.get(d2)

                # set dimensions
                setattr(vbox1, dim2, d2)
                setattr(vbox2, dim1, getattr(vbox1, dim2) + 1)
                return (vbox1, vbox2)
        return (None, None)

    @staticmethod
    def quantize(pixels: np.ndarray, max_color: int):
        """
        Pixels quantize.

        Args:
            pixels: a array of pixel in the form (r, g, b)
            max_color: max number of colors

        Returns:

        """
        if pixels.shape[0] == 0:
            raise Exception('Empty pixels when quantize.')
        if max_color < 2 or max_color > 256:
            raise Exception('Wrong number of max colors when quantize.')

        histo = MMCQ.get_histo(pixels)

        # get the beginning vbox from the colors
        vbox = MMCQ.vbox_from_pixels(pixels, histo)
        pq = PQueue(lambda x: x.count)
        pq.push(vbox)

        # inner function to do the iteration
        def iter_(lh: "PQueue", target: Union[int, float]):
            n_color = 1
            n_iter = 0
            while n_iter < MMCQ.MAX_ITERATION:
                vbox = lh.pop()
                if not vbox.count:  # just put it back
                    lh.push(vbox)
                    n_iter += 1
                    continue

                # do the cut
                vbox1, vbox2 = MMCQ.median_cut_apply(histo, vbox)
                if not vbox1:
                    raise Exception("vbox1 not defined; shouldn't happen!")
                lh.push(vbox1)

                if vbox2:  # vbox2 can be null
                    lh.push(vbox2)
                    n_color += 1
                if n_color >= target:
                    return
                if n_iter > MMCQ.MAX_ITERATION:
                    return
                n_iter += 1

        # first set of colors, sorted by population
        iter_(pq, MMCQ.FRACT_BY_POPULATIONS * max_color)

        # Re-sort by the product of pixel occupancy times the size in color space.
        pq2 = PQueue(lambda x: x.count * x.volume)
        while pq.size():
            pq2.push(pq.pop())

        # next set - generate the median cuts using the (npix * vol) sorting.
        iter_(pq2, max_color - pq2.size())

        # calculate the actual colors
        cmap = CMap()
        while pq2.size():
            cmap.push(pq2.pop())
        return cmap


class VBox:
    """
    3D color space box.
    """
    def __init__(self, r1, r2, g1, g2, b1, b2, histo: Dict[int, int], total_pixel_count: int):
        self.r1 = int(r1)
        self.r2 = int(r2)
        self.g1 = int(g1)
        self.g2 = int(g2)
        self.b1 = int(b1)
        self.b2 = int(b2)
        self.histo = histo
        self.total_pixel_count = total_pixel_count

        self._rgb_array: Optional[np.ndarray] = None
        self._color_index: Optional[np.ndarray] = None

    @functools.cached_property
    def volume(self) -> int:
        """
        The volume of pixels in VBox.
        """
        sub_r = self.r2 - self.r1
        sub_g = self.g2 - self.g1
        sub_b = self.b2 - self.b1
        return (sub_r + 1) * (sub_g + 1) * (sub_b + 1)

    @property
    def copy(self) -> "VBox":
        return VBox(self.r1, self.r2, self.g1, self.g2, self.b1, self.b2, self.histo, self.total_pixel_count)

    @functools.cached_property
    def avg(self) -> Tuple[int, int, int]:
        """
        Calculate the color avg of VBox.
        """
        mult = 1 << (8 - MMCQ.SIGBITS)
        rgb_array, color_index_array = self.get_rgb_array_and_color_index_array()
        histo_num = np.array([self.histo.get(c, 0) for c in color_index_array], dtype=np.int32)
        r_sum = np.sum(histo_num * (rgb_array[:, 0] + 0.5) * mult)
        g_sum = np.sum(histo_num * (rgb_array[:, 1] + 0.5) * mult)
        b_sum = np.sum(histo_num * (rgb_array[:, 2] + 0.5) * mult)

        total = histo_num.sum()
        if total:
            r_avg = r_sum / total
            g_avg = g_sum / total
            b_avg = b_sum / total
        else:
            r_avg = mult * (self.r1 + self.r2 + 1) / 2
            g_avg = mult * (self.g1 + self.g2 + 1) / 2
            b_avg = mult * (self.b1 + self.b2 + 1) / 2

        r_avg = int(np.clip(r_avg, 0, 255))
        g_avg = int(np.clip(g_avg, 0, 255))
        b_avg = int(np.clip(b_avg, 0, 255))
        return r_avg, g_avg, b_avg

    @functools.cached_property
    def count(self) -> int:
        """
        The number of pixels in VBox.
        """
        rgb_array, color_index_array = self.get_rgb_array_and_color_index_array()
        npix_list = [self.histo.get(i, 0) for i in color_index_array]
        npix = sum(npix_list)
        return npix

    @functools.cached_property
    def percent(self) -> int:
        """
        The percentage of VBox pixels to all pixels.
        """
        return int(self.count / self.total_pixel_count * 100)

    def get_rgb_array(self):
        return np.mgrid[self.r1: self.r2 + 1, self.g1: self.g2 + 1, self.b1: self.b2 + 1].T.reshape(-1, 3)

    def get_rgb_array_and_color_index_array(self):
        if self._rgb_array is None:
            rgb_array = np.mgrid[self.r1: self.r2 + 1, self.g1: self.g2 + 1, self.b1: self.b2 + 1].T.reshape(-1, 3)
            self._rgb_array = rgb_array
            self._color_index_array = MMCQ.get_color_index(rgb_array[:, 0], rgb_array[:, 1], rgb_array[:, 2])
        return self._rgb_array, self._color_index_array


class CMap:
    """
    Color map.
    """
    def __init__(self, return_percent: bool = False):
        self.pqueue: "PQueue" = PQueue(lambda x: x['vbox'].count * x['vbox'].volume)
        self.return_percent = return_percent

    @property
    def palette(self) -> List:
        if self.return_percent:
            return self.pqueue.map(lambda x: x['color'] + (x['percent'],))
        else:
            return self.pqueue.map(lambda x: x['color'])

    def push(self, vbox: "VBox"):
        self.pqueue.push({
            'vbox': vbox,
            'color': vbox.avg,
            'percent': vbox.percent,
        })

    def size(self):
        return self.pqueue.size()


class PQueue:
    """
    Simple priority queue.
    """
    def __init__(self, sort_key: Callable):
        self.sort_key = sort_key
        self.contents: List = []
        self._sorted = False

    def sort(self):
        self.contents.sort(key=self.sort_key)
        self._sorted = True

    def push(self, o):
        self.contents.append(o)
        self._sorted = False

    def pop(self):
        if not self._sorted:
            self.sort()
        return self.contents.pop()

    def size(self) -> int:
        return len(self.contents)

    def map(self, f: Callable) -> List:
        return list(map(f, self.contents))
