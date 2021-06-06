from abc import ABCMeta, abstractmethod
from math import radians, cos, sin, pi

from commons import Point


class Component(metaclass=ABCMeta):

    def __init__(self, x: int = 0, y: int = 0):
        self.pos: Point = Point(x, y)

    @abstractmethod
    def update_position(self, *args):
        raise NotImplementedError


class Emitter(Component):

    def update_position(self, radius: float, alpha: int, center: Point):
        self.pos.x = int(radius * cos(radians(alpha)) + center.x)
        self.pos.y = int(radius * sin(radians(alpha)) + center.y)


class Detector(Component):

    def update_position(self, radius: float, center: Point, arg: float):
        self.pos.x = int(radius * cos(arg)) + center.x
        self.pos.y = int(radius * sin(arg)) + center.y


class Scan:
    emitter = Emitter()

    def __init__(self, detectors_count: int):
        self.detectors: list[Detector] = [Detector() for _ in range(detectors_count)]

    def update_detectors_positions(self, radius: float, alpha: int, center: Point, span: float):
        [self.detectors[i].update_position(radius, center, self.detector_pos_arg(alpha, span, i))
         for i in range(self.detectors_count)]

    def detector_pos_arg(self, alpha: int, span: float, detector_index: int) -> float:
        return (radians(alpha) + pi) - (span / 2) + (detector_index * (span / (self.detectors_count - 1)))

    @property
    def detectors_count(self) -> int:
        return len(self.detectors)
