import logging
import os
from typing import Callable, List, Optional, Tuple

from algorithm.adaptive_edit_distance import AdaptiveEditDistance
from algorithm.model.distance_metrics import ScalingFunctions
from algorithm.model.edit_window import EditWindow
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

    def _extract_intervals(self, stream_start: int, padding_factor: float) -> EditWindow:
        return EditWindow.build(self.stream, self.pattern, stream_start, padding_factor)

    def _get_transformation_limits(
        self,
        edit_window: EditWindow,
        transformation: Transformation,
        forward: bool,
    ) -> Tuple[int, Transformation, float]:
        edit_window.transform_pattern(transformation)

        if forward:
            logger.debug(f"FORWARD : {format_array(edit_window.stream_intervals)}")
        else:
            logger.debug(f"BACKWARD: {format_array(edit_window.stream_intervals)}")
        logger.debug(f"PATTERN : {format_array(edit_window.pattern_intervals)}")

        directional_edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            edit_window, self._metrics, ScalingFunctions.sqrt
        )
        directional_stream_limit, weight = directional_edit_distance.get_limits(pattern_complete=forward)
        return directional_stream_limit, transformation, weight

    def get_limit(self, stream_start: int, forward: bool = False) -> Tuple[int, float, Transformation]:
        edit_window: EditWindow = EditWindow.build(
            self.stream, self.pattern, stream_start, padding_factor=2, reverse=forward
        )

        logger.debug("")
        best_stream_limit, best_transformation, best_weight = self._get_transformation_limits(
            edit_window, self._transformation, forward
        )
        if forward:
            logger.debug(f"--> {len(edit_window.stream_intervals) - best_stream_limit}")
            return len(edit_window.stream_intervals) - best_stream_limit, best_weight, best_transformation
        else:
            return best_stream_limit, best_weight, best_transformation
