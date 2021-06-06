from math import radians, ceil

from bresenham import bresenham
import numpy as np

from components import Scan
from commons import Point


class Converter:

    def __init__(self, step: int, span: float, radius: float):
        self.radius: float = radius
        self.span: float = radians(span)
        self.step: int = step
        self.center: Point = Point(int(self.radius), int(self.radius))

    @property
    def diameter(self) -> float:
        return self.radius * 2

    @property
    def steps(self) -> int:
        return int(ceil(360 / self.step) + 1)

    def run(self, sinogram: np.ndarray, scan: Scan) -> np.ndarray:
        res = np.zeros(shape=(self.diameter, self.diameter))
        for i in range(self.steps):
            alpha = i * self.step
            scan.emitter.update_position(self.radius, alpha, self.center)
            scan.update_detectors_positions(self.radius, alpha, self.center, self.span)
            for j, detector in enumerate(scan.detectors):
                brightness = sinogram[i][j] / 255
                coordinates = list(bresenham(
                    scan.emitter.pos.x,
                    scan.emitter.pos.y,
                    detector.pos.x,
                    detector.pos.y))
                for c in coordinates:
                    res[c[0] - 1][c[1] - 1] += brightness
        return res
