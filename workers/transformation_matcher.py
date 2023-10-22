import logging
import os
from typing import Callable, List, Optional, Tuple

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
        transformation: Transformation,
        metrics: List[Callable],
    ) -> None:
        self.stream: NoteSequence = stream
        self.pattern: NoteSequence = pattern
        self._transformation: Transformation = transformation
        self._metrics: List[Callable] = metrics

    def _extract_intervals(self, stream_start: int, padding_factor: float) -> Tuple[List[int], List[int]]:
        pattern_intervals: List[int] = self.pattern.raw_intervals
        stream_end: int = min(stream_start + int(padding_factor * len(pattern_intervals)) - 1, len(self.stream) - 1)
        stream_intervals: List[int] = self.stream.raw_intervals_range(stream_start, stream_end)
        return stream_intervals, pattern_intervals

    def _get_transformation_limits(
        self,
        stream_intervals: List[Optional[int]],
        pattern_intervals: List[Optional[int]],
        transformation: Transformation,
        forward: bool,
    ) -> Tuple[int, Transformation, float]:
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
        return directional_stream_limit, transformation, weight

    def get_limit(self, stream_start: int, forward: bool = False) -> Tuple[int, float, Transformation]:
        stream_intervals, pattern_intervals = self._extract_intervals(stream_start, 2)
        if forward:
            stream_intervals, pattern_intervals = stream_intervals[::-1], pattern_intervals[::-1]

        logger.debug("")
        best_stream_limit, best_transformation, best_weight = self._get_transformation_limits(
            stream_intervals, pattern_intervals, self._transformation, forward
        )
        if forward:
            logger.debug(f"--> {len(stream_intervals) - best_stream_limit}")
            return len(stream_intervals) - best_stream_limit, best_weight, best_transformation
        else:
            return best_stream_limit, best_weight, best_transformation
