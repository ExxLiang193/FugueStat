from constants import OCTAVE_SUBDIVISIONS
from interval import Interval


class Position:
    def __init__(self, abs_position: int) -> None:
        self.abs_position = abs_position
        self.octave, self.rel_position = divmod(self.abs_position, OCTAVE_SUBDIVISIONS)

    def __sub__(self, other: "Position") -> Interval:
        return Interval(self, other)
