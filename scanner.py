from math import floor, radians, ceil, pi
from statistics import mean

import numpy as np
from scipy import signal
from bresenham import bresenham

from commons import Point
from components import Scan


class Scanner:

    def __init__(self, image: np.ndarray, span: int, n_steps: int, steps: int, scan: Scan):
        self.image: np.ndarray = image
        self.center: Point = Point(floor(image.shape[0] / 2), floor(image.shape[1] / 2))
        self.radius: float = floor(min(image.shape[0] / 2, image.shape[1] / 2))
        self.span: float = radians(span)
        self.step: int = n_steps
        self.scan = scan
        self.sinogram = np.empty(shape=(steps, self.scan.detectors_count))

    def run(self, i: int) -> np.ndarray:
        return self._create_sinogram(i)

    def _create_sinogram(self, i: int) -> np.ndarray:
        alpha = i * self.step
        self.scan.emitter.update_position(self.radius, alpha, self.center)
        self.scan.update_detectors_positions(self.radius, alpha, self.center, self.span)
        for j, detector in enumerate(self.scan.detectors):
            coordinates = list(bresenham(
                self.scan.emitter.pos.x,
                self.scan.emitter.pos.y,
                detector.pos.x,
                detector.pos.y))
            brightness = [self.image.item(c[0] - 1, c[1] - 1) for c in coordinates]
            self.sinogram[i][j] = mean(brightness)
        return self._convolve_sinogram(self.sinogram.copy())

    @staticmethod
    def _convolve_sinogram(sinogram: np.ndarray) -> np.ndarray:
        conv_square = np.zeros(shape=(5, 5))
        for j in range(conv_square.shape[0]):
            for k in range(conv_square.shape[1]):
                if k == 0:
                    conv_square[j][k] = 1
                elif k % 2 != 0:
                    conv_square[j][k] = (-4 / pi ** 2) / (k ** 2)
        return signal.convolve2d(sinogram, conv_square, mode="full")
