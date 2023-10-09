from __future__ import annotations
from decimal import Decimal
from model.constants import RawDuration
from typing import List


class Duration:
    PARTITIONS = (
        RawDuration.NoteWhole,
        RawDuration.NoteHalf,
        RawDuration.NoteQuarter,
        RawDuration.Note8th,
        RawDuration.Note16th,
        RawDuration.Note32th,
        RawDuration.Note64th,
    )

    def __init__(self, raw_duration: Decimal) -> None:
        self.raw_duration: Decimal = raw_duration
        self.parts: List[Decimal] = self._build_parts(raw_duration)

    def __add__(self, other: Duration) -> Duration:
        return Duration(self.raw_duration + other.raw_duration)

    def __sub__(self, other: Duration) -> Duration:
        return Duration((self.raw_duration - other.raw_duration).abs())

    def __repr__(self) -> str:
        def format_ratio(numerator: int, denominator: int) -> str:
            return str(numerator) if denominator == 1 else f"{numerator}/{denominator}"

        return "+".join(format_ratio(*part.as_integer_ratio()) for part in self.parts)

    def _build_parts(cls, raw_duration: Decimal) -> List[RawDuration]:
        parts = list()
        for partition in cls.PARTITIONS:
            if partition <= raw_duration:
                raw_duration -= partition
                parts.append(partition)
        return parts

    @property
    def is_compound(self):
        return len(self.parts) > 1
