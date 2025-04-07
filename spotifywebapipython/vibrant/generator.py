from typing import List

from .models import GeneratorOpts, Palette, Swatch, hsl_to_rgb

generator_opts = GeneratorOpts(
    target_dark_luma=0.26,
    max_dark_luma=0.45,
    min_light_luma=0.55,
    target_light_luma=0.74,
    min_normal_luma=0.3,
    target_normal_luma=0.5,
    max_normal_luma=0.7,
    target_muted_saturation=0.3,
    max_muted_saturation=0.4,
    target_vibrant_saturation=1.0,
    min_vibrant_saturation=0.35,
    weight_saturation=3,
    weight_luma=6.5,
    weight_population=0.5,
)


def find_max_population(swatches: List[Swatch]) -> int:
    p = 0
    for swatch in swatches:
        p = max(p, swatch.population)
    return p


def is_already_selected(palette: Palette, swatch: Swatch) -> bool:
    return (
        palette.vibrant == swatch
        or palette.dark_vibrant == swatch
        or palette.light_vibrant == swatch
        or palette.muted == swatch
        or palette.dark_muted == swatch
        or palette.light_muted == swatch
    )


def create_comparison_value(
    saturation: int,
    targetSaturation: int,
    luma: int,
    targetLuma: int,
    population: int,
    maxPopulation: int,
    opts: GeneratorOpts,
) -> int:
    def weighted_mean(values: List[int]):
        sum = 0
        weight_sum = 0
        for i in range(0, len(values), 2):
            value = values[i]
            weight = values[i + 1]
            sum += value * weight
            weight_sum += weight

        return sum / weight_sum

    def invert_diff(value: int, target_value: int) -> int:
        return 1 - abs(value - target_value)

    return weighted_mean(
        [
            invert_diff(saturation, targetSaturation),
            opts.weight_saturation,
            invert_diff(luma, targetLuma),
            opts.weight_luma,
            population // maxPopulation,
            opts.weight_population,
        ]
    )


def find_color_variation(
    palette: Palette,
    swatches: List[Swatch],
    max_population: int,
    target_luma: int,
    min_luma: int,
    max_luma: int,
    target_saturation: int,
    min_saturation: int,
    max_saturation: int,
    opts: GeneratorOpts,
) -> Swatch:
    max_swatch: Swatch = None
    max_value = 0

    for swatch in swatches:
        h, s, l = swatch.hsl
        if (
            s >= min_saturation
            and s <= max_saturation
            and l >= min_luma
            and l <= max_luma
            and not is_already_selected(palette, swatch)
        ):
            value = create_comparison_value(
                s,
                target_saturation,
                l,
                target_luma,
                swatch.population,
                max_population,
                opts,
            )
            if max_swatch == None or value > max_value:
                max_swatch = swatch
                max_value = value

    return max_swatch


def generate_variation_colors(
    swatches: List[Swatch], maxPopulation: int, opts: GeneratorOpts
) -> Palette:
    palette: Palette = Palette()

    palette.vibrant = find_color_variation(
        palette,
        swatches,
        maxPopulation,
        opts.target_normal_luma,
        opts.min_normal_luma,
        opts.max_normal_luma,
        opts.target_vibrant_saturation,
        opts.min_vibrant_saturation,
        1,
        opts,
    )

    palette.light_vibrant = find_color_variation(
        palette,
        swatches,
        maxPopulation,
        opts.target_light_luma,
        opts.min_light_luma,
        1,
        opts.target_vibrant_saturation,
        opts.min_vibrant_saturation,
        1,
        opts,
    )

    palette.dark_vibrant = find_color_variation(
        palette,
        swatches,
        maxPopulation,
        opts.target_dark_luma,
        0,
        opts.max_dark_luma,
        opts.target_vibrant_saturation,
        opts.min_vibrant_saturation,
        1,
        opts,
    )

    palette.muted = find_color_variation(
        palette,
        swatches,
        maxPopulation,
        opts.target_normal_luma,
        opts.min_normal_luma,
        opts.max_normal_luma,
        opts.target_muted_saturation,
        0,
        opts.max_muted_saturation,
        opts,
    )

    palette.light_muted = find_color_variation(
        palette,
        swatches,
        maxPopulation,
        opts.target_light_luma,
        opts.min_light_luma,
        1,
        opts.target_muted_saturation,
        0,
        opts.max_muted_saturation,
        opts,
    )

    palette.dark_muted = find_color_variation(
        palette,
        swatches,
        maxPopulation,
        opts.target_dark_luma,
        0,
        opts.max_dark_luma,
        opts.target_muted_saturation,
        0,
        opts.max_muted_saturation,
        opts,
    )

    return palette


def generate_empty_swatches(palette: Palette, opts: GeneratorOpts) -> None:
    if (
        palette.vibrant is None
        and palette.dark_vibrant is None
        and palette.light_vibrant is None
    ):
        if palette.dark_vibrant is None and palette.dark_muted is not None:
            [h, s, l] = palette.dark_muted.hsl
            l = opts.target_dark_luma
            palette.dark_vibrant = Swatch(hsl_to_rgb([h, s, l]), 0)

        if palette.light_vibrant is None and palette.light_muted is not None:
            [h, s, l] = palette.light_muted.hsl
            l = opts.target_dark_luma
            palette.dark_vibrant = Swatch(hsl_to_rgb([h, s, l]), 0)

    if palette.vibrant is None and palette.dark_vibrant is not None:
        [h, s, l] = palette.dark_vibrant.hsl
        l = opts.target_normal_luma
        palette.vibrant = Swatch(hsl_to_rgb([h, s, l]), 0)
    elif palette.vibrant is None and palette.light_vibrant is not None:
        [h, s, l] = palette.light_vibrant.hsl
        l = opts.target_normal_luma
        palette.vibrant = Swatch(hsl_to_rgb([h, s, l]), 0)

    if palette.dark_vibrant is None and palette.vibrant is not None:
        [h, s, l] = palette.vibrant.hsl
        l = opts.target_dark_luma
        palette.dark_vibrant = Swatch(hsl_to_rgb([h, s, l]), 0)

    if palette.light_vibrant is None and palette.vibrant is not None:
        [h, s, l] = palette.vibrant.hsl
        l = opts.target_light_luma
        palette.light_vibrant = Swatch(hsl_to_rgb([h, s, l]), 0)

    if palette.muted is None and palette.vibrant is not None:
        [h, s, l] = palette.vibrant.hsl
        l = opts.target_muted_saturation
        palette.muted = Swatch(hsl_to_rgb([h, s, l]), 0)

    if palette.dark_muted is None and palette.dark_vibrant is not None:
        h, s, l = palette.dark_vibrant.hsl
        l = opts.target_muted_saturation
        palette.dark_muted = Swatch(hsl_to_rgb([h, s, l]), 0)

    if palette.light_muted is None and palette.light_vibrant is not None:
        h, s, l = palette.light_vibrant.hsl
        l = opts.target_muted_saturation
        palette.light_muted = Swatch(hsl=[h, s, l], population=0)


def generate(swatches: List[Swatch]) -> Palette:
    max_poplation = find_max_population(swatches)

    palette: Palette = generate_variation_colors(
        swatches, max_poplation, generator_opts
    )
    generate_empty_swatches(palette, generator_opts)

    return palette
