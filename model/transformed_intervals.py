from typing import List, Optional, Callable, Iterable
from model.constants import Transformation


class TransformedIntervals:
    def __init__(self, default_intervals: List[Optional[int]]) -> None:
        self._default_values: List[Optional[int]] = default_intervals
        self.values: List[Optional[int]] = default_intervals
        self.transformation: Transformation = Transformation.DEFAULT

    def _map_intervals(self, f: Callable, intervals: Iterable[Optional[int]]) -> List[Optional[int]]:
        return [None if interval is None else f(interval) for interval in intervals]

    def get_transformation(self, transformation: Transformation) -> List[Optional[int]]:
        match transformation:
            case Transformation.DEFAULT:
                return self._default_values
            case Transformation.REVERSAL:
                return self._default_values[::-1]
            case Transformation.INVERSION:
                return self._map_intervals(lambda interval: -interval, self._default_values)
            case Transformation.REVERSAL_INVERSION:
                return self._map_intervals(lambda interval: -interval, reversed(self._default_values))
            case _:
                return self._default_values

    def set_transformation(self, transformation: Transformation) -> None:
        self.values = self.get_transformation(transformation)
        self.transformation = transformation
