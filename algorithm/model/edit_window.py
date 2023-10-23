from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from model.constants import Transformation
from model.note_sequence import NoteSequence
from model.transformed_sequence import TransformedSequence

if TYPE_CHECKING:
    from decimal import Decimal


@dataclass
class EditWindow:
    stream_intervals: List[Optional[int]]
    stream_durations: List[Decimal]
    pattern_intervals: List[Optional[int]]
    pattern_durations: List[Decimal]

    def transform_pattern(self, transformation: Transformation) -> None:
        transformer: TransformedSequence = TransformedSequence(self.pattern_intervals, self.pattern_durations)
        self.pattern_intervals = transformer.get_interval_transformation(transformation)
        self.pattern_durations = transformer.get_duration_transformation(transformation)

    @staticmethod
    def build(
        stream: NoteSequence, pattern: NoteSequence, stream_start: int, padding_factor: int = 2, reverse: bool = False
    ) -> EditWindow:
        pattern_intervals: List[int] = pattern.raw_intervals
        stream_end: int = min(stream_start + int(padding_factor * len(pattern_intervals)) - 1, len(stream) - 1)
        stream_intervals: List[int] = stream.raw_intervals_range(stream_start, stream_end)

        pattern_durations: List[Decimal] = pattern.raw_durations
        stream_durations: List[Decimal] = stream.raw_durations_range(stream_start, stream_end)

        if reverse:
            return EditWindow(
                stream_intervals[::-1], stream_durations[::-1], pattern_intervals[::-1], pattern_durations[::-1]
            )
        return EditWindow(stream_intervals, stream_durations, pattern_intervals, pattern_durations)
