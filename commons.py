from dataclasses import dataclass
from io import BytesIO
from typing import Union

from PIL import Image
import numpy as np


@dataclass
class Point:
    x: int
    y: int


@dataclass
class SimulationResults:
    Scan: np.ndarray
    Result: np.ndarray


def to_image(img_array: np.ndarray) -> Image:
    return Image.fromarray(np.uint8(img_array * 255), "L")


def open_image(img: Union[str, BytesIO]):
    return np.divide(np.array(Image.open(img).convert("L"),
                              dtype=float), 255.0)
