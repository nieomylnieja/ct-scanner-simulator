from math import floor, radians, ceil, pi
from statistics import mean

import numpy as np
from scipy import signal
from bresenham import bresenham

from commons import Point
from components import Scan


class Scanner:

    def __init__(self, image: np.ndarray, span: int, step: int):
        self.image: np.ndarray = image
        self.center: Point = Point(floor(image.shape[0] / 2), floor(image.shape[1] / 2))
        self.radius: float = floor(min(image.shape[0] / 2, image.shape[1] / 2))
        self.span: float = radians(span)
        self.step: int = step

    @property
    def steps(self) -> int:
        return int(ceil(360 / self.step) + 1)

    def run(self, scan: Scan) -> np.ndarray:
        sinogram = self._create_sinogram(scan)
        sinogram = self._convolve_sinogram(sinogram)
        return sinogram

    def _create_sinogram(self, scan: Scan) -> np.ndarray:
        sinogram = np.empty(shape=(self.steps, scan.detectors_count))
        for i in range(self.steps):
            alpha = i * self.step
            scan.emitter.update_position(self.radius, alpha, self.center)
            scan.update_detectors_positions(self.radius, alpha, self.center, self.span)
            for j, detector in enumerate(scan.detectors):
                coordinates = list(bresenham(
                    scan.emitter.pos.x,
                    scan.emitter.pos.y,
                    detector.pos.x,
                    detector.pos.y))
                brightness = [self.image.item(c[0] - 1, c[1] - 1) for c in coordinates]
                sinogram[i][j] = mean(brightness)
        return sinogram

    @staticmethod
    def _convolve_sinogram(sinogram: np.ndarray) -> np.ndarray:
        conv_square = np.zeros(shape=(5, 5))
        for i in range(conv_square.shape[0]):
            for j in range(conv_square.shape[1]):
                if j == 0:
                    conv_square[i][j] = 1
                elif j % 2 != 0:
                    conv_square[i][j] = (-4 / pi ** 2) / (j ** 2)
        return signal.convolve2d(sinogram, conv_square, mode="full")