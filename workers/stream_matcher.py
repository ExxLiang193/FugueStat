import logging
import os
from typing import Callable, List, Optional, Tuple

from model.constants import Transformation
from model.note_sequence import NoteSequence
from workers.transformation_matcher import TransformationMatcher

logger = logging.getLogger(os.path.basename(__file__))


class StreamMatcher:
    def __init__(self, stream: NoteSequence, sensitivity: float, min_match: int, metrics: List[Callable]) -> None:
        self.stream: NoteSequence = stream
        self.sensitivity: float = sensitivity
        self.min_match: int = min_match
        self._metrics: List[Callable] = metrics

    def _push_forward(self, pattern: NoteSequence, transformations: List[Transformation], stream_start: int) -> int:
        transformation_matcher: TransformationMatcher = TransformationMatcher(
            self.stream, pattern, transformations, self._metrics
        )
        stream_step, _, _ = transformation_matcher.get_limit(stream_start, forward=True)
        return stream_step

    def _pull_back(
        self, pattern: NoteSequence, transformations: List[Transformation], stream_start: int
    ) -> Tuple[int, NoteSequence, Transformation]:
        transformation_matcher: TransformationMatcher = TransformationMatcher(
            self.stream, pattern, transformations, self._metrics
        )
        stream_step, weight, transformation = transformation_matcher.get_limit(stream_start, forward=False)
        logger.debug(f"MATCH WEIGHT: {weight}")
        if stream_step == 0:
            logger.debug("NOT FOUND")
            logger.debug(f"--> {len(pattern)}")
            return len(pattern), None, None
        if (weight > self.sensitivity) or (stream_step + 1 < self.min_match):
            logger.debug("SKIPPED")
            logger.debug(f"--> {stream_step}")
            return stream_step + 1, None, None
        stream_end: int = stream_start + stream_step + 1
        match_sequence: NoteSequence = NoteSequence(self.stream[stream_start:stream_end])
        logger.debug(f"MATCHED: {match_sequence.raw_intervals}")
        logger.debug(transformation)
        logger.debug(f"--> {stream_step}")
        return stream_step + 1, match_sequence, transformation

    def match_next(
        self, pattern: NoteSequence, transformations: List[Transformation], stream_start: int
    ) -> Tuple[Optional[NoteSequence], Optional[Transformation], int]:
        while (step := self._push_forward(pattern, transformations, stream_start)) and step > 0:
            stream_start += step
        step, match, transformation = self._pull_back(pattern, transformations, stream_start)
        return match, transformation, stream_start + step

    def match_all(
        self, pattern: NoteSequence, transformations: List[Transformation]
    ) -> List[Tuple[NoteSequence, Transformation]]:
        results = list()
        cur_stream_pos: int = 0
        while cur_stream_pos < len(self.stream) - self.min_match:
            match, transformation, cur_stream_pos = self.match_next(pattern, transformations, cur_stream_pos)
            if match is not None:
                results.append((match, transformation))
        return results
