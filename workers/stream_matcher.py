import logging
import os
from typing import Callable, List, Optional, Tuple

from algorithm.adaptive_edit_distance import AdaptiveEditDistance
from algorithm.model.distance_metrics import ScalingFunctions
from model.note_sequence import NoteSequence
from utility.string_format import format_array
from workers.stream_interval_matcher import StreamIntervalMatcher

logger = logging.getLogger(os.path.basename(__file__))


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
        pattern_intervals, stream_intervals = self._extract_intervals(pattern, stream_start, 2)
        logger.debug("")
        logger.debug(f"FORWARD: {format_array(stream_intervals)}")
        logger.debug(f"PATTERN: {format_array(pattern.raw_intervals)}")

        backward_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals[::-1], pattern_intervals[::-1], self.metrics, ScalingFunctions.sqrt
        )
        backward_stream_limit, _, _ = backward_edit_distance.get_limits(pattern_complete=True)
        logger.debug(f"--> {len(stream_intervals) - backward_stream_limit}")
        return len(stream_intervals) - backward_stream_limit

    def _pull_back(self, pattern: NoteSequence, stream_start: int):
        pattern_intervals, stream_intervals = self._extract_intervals(pattern, stream_start, 2)
        logger.debug(f"BACKWARD: {format_array(stream_intervals)}")
        logger.debug(f"PATTERN : {format_array(pattern.raw_intervals)}")

        forward_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals, pattern_intervals, self.metrics, ScalingFunctions.sqrt
        )
        forward_stream_limit, _, weight = forward_edit_distance.get_limits()
        logger.debug(f"MATCH WEIGHT: {weight}")
        if forward_stream_limit == 0:
            logger.debug("NOT FOUND")
            logger.debug(f"--> {len(pattern)}")
            return None, len(pattern)
        if (weight > self.sensitivity) or (forward_stream_limit + 1 < self.min_match):
            logger.debug("SKIPPED")
            logger.debug(f"--> {forward_stream_limit}")
            return None, forward_stream_limit
        stream_end: int = stream_start + forward_stream_limit + 1
        match_sequence: NoteSequence = NoteSequence(self.stream[stream_start:stream_end])
        logger.debug(f"MATCHED: {match_sequence.raw_intervals}")
        logger.debug(f"--> {forward_stream_limit}")
        return match_sequence, forward_stream_limit

    def match_next(self, pattern: NoteSequence, stream_start: int) -> Tuple[Optional[NoteSequence], int]:
        while (step := self._push_forward(pattern, stream_start)) and step > 0:
            stream_start += step
        match, step = self._pull_back(pattern, stream_start)
        return match, stream_start + step

    def match_all(self, pattern: NoteSequence) -> List[NoteSequence]:
        results = list()
        cur_stream_pos: int = 0
        while cur_stream_pos < len(self.stream) - self.min_match:
            match, cur_stream_pos = self.match_next(pattern, cur_stream_pos)
            if match is not None:
                results.append(match)
        return results
