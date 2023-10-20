import logging
import os
from typing import Callable, List, Optional, Set, Tuple

from algorithm.adaptive_edit_distance import AdaptiveEditDistance
from algorithm.model.distance_metrics import ScalingFunctions
from model.constants import Transformation
from model.note_sequence import NoteSequence
from model.transformed_intervals import TransformedIntervals
from utility.string_format import format_array

logger = logging.getLogger(os.path.basename(__file__))


class TransformationMatcher:
    def __init__(
        self,
        stream: NoteSequence,
        pattern: NoteSequence,
        transformations: Set[Transformation],
        metrics: List[Callable],
    ) -> None:
        self.stream: NoteSequence = stream
        self.pattern: NoteSequence = pattern
        self._transformations: Set[Transformation] = transformations
        self._metrics: List[Callable] = metrics

    def _extract_intervals(self, stream_start: int, padding_factor: float) -> Tuple[List[int], List[int]]:
        pattern_intervals: List[int] = self.pattern.raw_intervals
        max_stream_intervals: int = min(
            stream_start + int(padding_factor * len(pattern_intervals)), len(self.stream) - 1
        )
        stream_intervals: List[int] = [
            None if (interval := self.stream.intervals[i]) is None else interval.value
            for i in range(stream_start, max_stream_intervals)
        ]
        return stream_intervals, pattern_intervals

    def _get_transformation_limits(
        self,
        stream_intervals: List[Optional[int]],
        pattern_intervals: List[Optional[int]],
        transformation: Transformation,
        forward: bool,
    ) -> Tuple[int, float, Transformation]:
        transformed_pattern_intervals = TransformedIntervals(pattern_intervals).get_transformation(transformation)

        if forward:
            logger.debug(f"FORWARD : {format_array(stream_intervals)}")
        else:
            logger.debug(f"BACKWARD: {format_array(stream_intervals)}")
        logger.debug(f"PATTERN : {format_array(transformed_pattern_intervals)}")

        directional_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals, transformed_pattern_intervals, self._metrics, ScalingFunctions.sqrt
        )
        directional_stream_limit, weight = directional_edit_distance.get_limits(pattern_complete=forward)
        return directional_stream_limit, weight, transformation

    def get_limit(self, stream_start: int, forward: bool = False) -> Tuple[int, float, Transformation]:
        stream_intervals, pattern_intervals = self._extract_intervals(stream_start, 2)
        if forward:
            stream_intervals, pattern_intervals = stream_intervals[::-1], pattern_intervals[::-1]

        logger.debug("")
        transformation_limits: List[Tuple[int, float, Transformation]] = [
            self._get_transformation_limits(stream_intervals, pattern_intervals, transformation, forward)
            for transformation in self._transformations
        ]
        best_stream_limit, best_weight, best_transformation = sorted(
            transformation_limits, key=lambda limit_info: limit_info[1]
        )[0]
        if forward:
            logger.debug(f"--> {len(stream_intervals) - best_stream_limit}")
            return len(stream_intervals) - best_stream_limit, best_weight, best_transformation
        else:
            return best_stream_limit, best_weight, best_transformation
