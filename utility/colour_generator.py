import colorsys
from typing import Generator, List

import numpy as np


class ColourGenerator:
    MAX_COLOURS: int = 45
    DEFAULT_COLOUR: str = "#000000"
    in_use: List[str] = list()
    __generator: Generator[str, None, None] = None

    @staticmethod
    def _colour_generator() -> Generator[str, None, None]:
        idx: np.array = np.arange(0.0, 360.0, 360.0 / ColourGenerator.MAX_COLOURS)
        for i in np.random.permutation(idx):
            hue: float = i / 360.0
            lightness: float = (50 + np.random.rand() * 10) / 100.0
            saturation: float = (90 + np.random.rand() * 10) / 100.0
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
            yield f"#{int(r * 256):02X}{int(g * 256):02X}{int(b * 256):02X}"

    @staticmethod
    def get_new_colour() -> str:
        if ColourGenerator.__generator is None:
            ColourGenerator.__generator = ColourGenerator._colour_generator()
        new_colour: str = next(ColourGenerator.__generator, ColourGenerator.DEFAULT_COLOUR)
        ColourGenerator.in_use.append(new_colour)
        return new_colour
