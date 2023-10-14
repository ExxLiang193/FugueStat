from model.note_sequence import NoteSequence
from algorithm.kmp_soft import KMPSoft
from algorithm.adaptive_edit_distance import AdaptiveEditDistance
from typing import List, Callable, Tuple, Optional
from algorithm.model.distance_metrics import ScalingFunctions


class StreamMatcher:
    def __init__(
        self, stream: NoteSequence, lps_tolerance: int, sensitivity: float, min_match: int, metrics: List[Callable]
    ) -> None:
        self.stream: NoteSequence = stream
        self.sensitivity: float = sensitivity
        self.min_match: int = min_match
        self.metrics: List[Callable] = metrics
        self._kmp_utility = KMPSoft(lps_tolerance)

    def _extract_intervals(
        self, pattern: NoteSequence, stream_start: int, padding_factor: int
    ) -> Tuple[List[int], List[int]]:
        pattern_intervals: List[int] = [None if interval is None else interval.value for interval in pattern.intervals]
        max_stream_intervals: int = min(stream_start + padding_factor * len(pattern_intervals), len(self.stream) - 1)
        stream_intervals: List[int] = [
            None if (interval := self.stream.intervals[i]) is None else interval.value
            for i in range(stream_start, max_stream_intervals)
        ]
        return pattern_intervals, stream_intervals

    def _converge_window(self, pattern: NoteSequence, stream_start: int):
        pattern_intervals, stream_intervals = self._extract_intervals(pattern, stream_start, 2)

        forward_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals, pattern_intervals, self.metrics, ScalingFunctions.sqrt
        )
        forward_stream_limit, forward_pattern_limit = forward_edit_distance.get_limits()
        forward_flag: bool = forward_stream_limit == 0
        forward_stream_limit = len(stream_intervals) if forward_flag else forward_stream_limit
        forward_pattern_limit = len(pattern_intervals) if forward_flag else forward_pattern_limit
        stream_intervals = stream_intervals[:forward_stream_limit][::-1]
        pattern_intervals = pattern_intervals[:forward_pattern_limit][::-1]

        backward_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals, pattern_intervals, self.metrics, ScalingFunctions.sqrt
        )
        backward_stream_limit, backward_pattern_limit = backward_edit_distance.get_limits()
        backward_flag: bool = backward_stream_limit == 0
        backward_stream_limit = len(stream_intervals) if backward_flag else backward_stream_limit
        backward_pattern_limit = len(pattern_intervals) if backward_flag else backward_pattern_limit
        stream_intervals = stream_intervals[:backward_stream_limit][::-1]
        pattern_intervals = pattern_intervals[:backward_pattern_limit][::-1]

        if forward_flag and backward_flag:
            return None, 1
        elif forward_flag:
            return None, forward_stream_limit - backward_stream_limit
        match_start = stream_start + forward_stream_limit - backward_stream_limit
        match_end = stream_start + forward_stream_limit
        return (
            NoteSequence(self.stream[match_start : match_end + 1]),
            forward_stream_limit,
        )

    def match_next(self, pattern: NoteSequence, stream_start: int) -> Tuple[Optional[NoteSequence], int]:
        while (results := self._converge_window(pattern, stream_start)) and (results[0] is None) and (results[1] != 0):
            stream_start += results[1]
        return results[0], stream_start + results[1]

    def match_all(self, pattern: NoteSequence) -> List[NoteSequence]:
        results = list()
        cur_stream_pos: int = 0
        while cur_stream_pos < len(self.stream) - self.min_match:
            match, cur_stream_pos = self.match_next(pattern, self.stream.next_note_idx(cur_stream_pos))
            if match is not None:
                results.append(match)
        return results
