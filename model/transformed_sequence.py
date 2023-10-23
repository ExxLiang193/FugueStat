from decimal import Decimal
from typing import Callable, Iterable, List, Optional

from model.constants import Transformation


class TransformedSequence:
    def __init__(self, default_intervals: List[Optional[int]], default_durations: List[Decimal]) -> None:
        self._default_interval_values: List[Optional[int]] = default_intervals
        self._default_duration_values: List[Decimal] = default_durations
        self.interval_values: List[Optional[int]] = default_intervals
        self.duration_values: List[Decimal] = default_durations
        self.transformation: Transformation = Transformation.DEFAULT

    def _map_intervals(self, f: Callable, intervals: Iterable[Optional[int]]) -> List[Optional[int]]:
        return [None if interval is None else f(interval) for interval in intervals]

    def get_interval_transformation(self, transformation: Transformation) -> List[Optional[int]]:
        match transformation:
            case Transformation.REVERSAL:
                return self._default_interval_values[::-1]
            case Transformation.INVERSION:
                return self._map_intervals(lambda interval: -interval, self._default_interval_values)
            case Transformation.REVERSAL_INVERSION:
                return self._map_intervals(lambda interval: -interval, reversed(self._default_interval_values))
            case _:
                return self._default_interval_values

    def set_interval_transformation(self, transformation: Transformation) -> None:
        self.interval_values = self.get_interval_transformation(transformation)
        self.transformation = transformation

    def get_duration_transformation(self, transformation: Transformation) -> List[Decimal]:
        match transformation:
            case Transformation.REVERSAL:
                return self._default_duration_values[::-1]
            case Transformation.REVERSAL_INVERSION:
                return self._default_duration_values[::-1]
            case Transformation.AUGMENTATION:
                return [value * 2 for value in self._default_duration_values]
            case Transformation.DIMINUTION:
                return [value / 2 for value in self._default_duration_values]
            case _:
                return self._default_duration_values

    def set_duration_transformation(self, transformation: Transformation) -> None:
        self.duration_values = self.get_duration_transformation(transformation)
        self.transformation = transformation
