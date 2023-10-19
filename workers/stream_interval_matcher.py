from typing import Callable, List, Tuple

from algorithm.adaptive_edit_distance import AdaptiveEditDistance
from algorithm.model.distance_metrics import ScalingFunctions


class StreamIntervalMatcher:
    def __init__(self, stream_intervals: List[int], sensitivity: float, metrics: List[Callable]) -> None:
        self.stream_intervals: List[int] = stream_intervals
        self.sensitivity: float = sensitivity
        self.metrics: List[Callable] = metrics

    def _get_stream_intervals(
        self, pattern_intervals: List[int], stream_start: int, padding_factor: int
    ) -> Tuple[List[int], List[int]]:
        max_stream_intervals: int = min(
            stream_start + padding_factor * len(pattern_intervals), len(self.stream_intervals)
        )
        return self.stream_intervals[stream_start:max_stream_intervals]

    def _push_forward(self, pattern_intervals: List[int], stream_start: int) -> int:
        stream_intervals = self._get_stream_intervals(pattern_intervals, stream_start, 1)

        backward_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals[::-1], pattern_intervals[::-1], self.metrics, ScalingFunctions.sqrt
        )
        backward_stream_limit, _, _ = backward_edit_distance.get_limits()
        return len(stream_intervals) - backward_stream_limit

    def _pull_back(self, pattern_intervals: List[int], stream_start: int) -> Tuple[bool, int]:
        stream_intervals = self._get_stream_intervals(pattern_intervals, stream_start, 2)

        forward_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals, pattern_intervals, self.metrics, ScalingFunctions.sqrt
        )
        forward_stream_limit, _, weight = forward_edit_distance.get_limits()
        if forward_stream_limit == 0:
            return False, len(pattern_intervals) + 1
        if weight > self.sensitivity:
            return False, forward_stream_limit
        return True, forward_stream_limit

    def try_match_next(self, pattern_intervals: List[int], stream_start: int) -> Tuple[bool, int, int]:
        while (step := self._push_forward(pattern_intervals, stream_start)) and step > 0:
            stream_start += step
        found, step = self._pull_back(pattern_intervals, stream_start)
        return found, stream_start, stream_start + step
