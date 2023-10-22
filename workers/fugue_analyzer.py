from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Dict, List, Set, Tuple

from algorithm.model.distance_metrics import DistanceMetrics
from model.composition import Composition
from model.note_sequence import NoteSequence
from workers.fugal_element_extractor import FugalElementExtractor
from workers.stream_matcher import StreamMatcher

if TYPE_CHECKING:
    from model.constants import Transformation

logger = logging.getLogger(os.path.basename(__file__))


class FugueAnalyzer:
    def __init__(self, composition: Composition, sensitivity: float, min_match: int) -> None:
        assert sensitivity >= 0
        assert min_match >= 1
        self.composition: Composition = composition
        self.sensitivity: float = sensitivity
        self.min_match: int = min_match
        self._fugal_element_extractor: FugalElementExtractor = FugalElementExtractor(composition.voices)

    def extract_subject(self) -> NoteSequence:
        return self._fugal_element_extractor.extract_subject()

    def match_subject(
        self, subject: NoteSequence, transformations: Set[Transformation]
    ) -> Dict[int, List[Tuple[NoteSequence, Transformation]]]:
        logger.debug(f"SUBJECT: {subject.raw_intervals}")
        DistanceMetrics.set_penalty_factors(rest_penalty_factor=5, inversion_penalty_factor=2)
        metrics = [
            DistanceMetrics.replacement_with_penalty,
            DistanceMetrics.insertion_without_expansion,
            DistanceMetrics.insertion_with_expansion,
            DistanceMetrics.deletion_without_compression,
            DistanceMetrics.deletion_with_compression,
        ]
        all_results = dict()
        for voice in self.composition.voices:
            logger.debug(f"VOICE START: {voice}")
            stream_matcher = StreamMatcher(self.composition.voices[voice], self.sensitivity, self.min_match, metrics)
            all_results[voice] = stream_matcher.match_all(subject, transformations)
        return all_results
