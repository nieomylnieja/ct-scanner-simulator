from math import radians, ceil

from bresenham import bresenham
import numpy as np

from components import Scan
from commons import Point


class Converter:

    def __init__(self, step: int, span: float, radius: float, scan: Scan, sinogram: np.ndarray):
        self.radius: float = radius
        self.span: float = radians(span)
        self.step: int = step
        self.center: Point = Point(int(self.radius), int(self.radius))
        self.scan = scan
        self.res = np.zeros(shape=(self.diameter, self.diameter))
        self.sinogram = sinogram.copy()

    @property
    def diameter(self) -> float:
        return self.radius * 2

    def run(self, i: int) -> np.ndarray:
        alpha = i * self.step
        self.scan.emitter.update_position(self.radius, alpha, self.center)
        self.scan.update_detectors_positions(self.radius, alpha, self.center, self.span)
        for j, detector in enumerate(self.scan.detectors):
            brightness = self.sinogram[i][j] / 255
            coordinates = list(bresenham(
                self.scan.emitter.pos.x,
                self.scan.emitter.pos.y,
                detector.pos.x,
                detector.pos.y))
            for c in coordinates:
                self.res[c[0] - 1][c[1] - 1] += brightness
        return self.res.copy()
