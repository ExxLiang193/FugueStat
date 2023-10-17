from model.note_sequence import NoteSequence
from algorithm.adaptive_edit_distance import AdaptiveEditDistance
from typing import List, Callable, Tuple, Optional
from algorithm.model.distance_metrics import ScalingFunctions
from workers.stream_interval_matcher import StreamIntervalMatcher

import pprint

pp = pprint.PrettyPrinter(indent=4)


class StreamMatcher:
    def __init__(
        self, stream: NoteSequence, lps_tolerance: int, sensitivity: float, min_match: int, metrics: List[Callable]
    ) -> None:
        self.stream: NoteSequence = stream
        self.sensitivity: float = sensitivity
        self.min_match: int = min_match
        self.metrics: List[Callable] = metrics
        self._stream_interval_matcher = StreamIntervalMatcher(stream.raw_intervals, sensitivity, metrics)

    def _extract_intervals(
        self, pattern: NoteSequence, stream_start: int, padding_factor: int
    ) -> Tuple[List[int], List[int]]:
        pattern_intervals: List[int] = pattern.raw_intervals
        max_stream_intervals: int = min(stream_start + padding_factor * len(pattern_intervals), len(self.stream) - 1)
        stream_intervals: List[int] = [
            None if (interval := self.stream.intervals[i]) is None else interval.value
            for i in range(stream_start, max_stream_intervals)
        ]
        return pattern_intervals, stream_intervals

    def _push_forward(self, pattern: NoteSequence, stream_start: int):
        pattern_intervals, stream_intervals = self._extract_intervals(pattern, stream_start, 1)

        backward_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals[::-1], pattern_intervals[::-1], self.metrics, ScalingFunctions.sqrt
        )
        backward_stream_limit, _, _ = backward_edit_distance.get_limits()
        return len(stream_intervals) - backward_stream_limit

    def _pull_back(self, pattern: NoteSequence, stream_start: int):
        pattern_intervals, stream_intervals = self._extract_intervals(pattern, stream_start, 2)

        forward_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals, pattern_intervals, self.metrics, ScalingFunctions.sqrt
        )
        forward_stream_limit, _, weight = forward_edit_distance.get_limits()
        if forward_stream_limit == 0:
            return None, len(pattern)
        if weight > self.sensitivity:
            return None, forward_stream_limit
        stream_end: int = stream_start + forward_stream_limit + 1
        return NoteSequence(self.stream[stream_start:stream_end]), forward_stream_limit

    def match_next(self, pattern: NoteSequence, stream_start: int) -> Tuple[Optional[NoteSequence], int]:
        while (step := self._push_forward(pattern, stream_start)) and step > 0:
            stream_start += step
        match, step = self._pull_back(pattern, stream_start)
        return match, stream_start + step

    def match_all(self, pattern: NoteSequence) -> List[NoteSequence]:
        results = list()
        cur_stream_pos: int = 0
        while cur_stream_pos < len(self.stream) - self.min_match:
            match, cur_stream_pos = self.match_next(pattern, self.stream.next_note_idx(cur_stream_pos))
            if match is not None:
                pp.pprint(match.notes)
                results.append(match)
        return results
