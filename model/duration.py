from __future__ import annotations

from decimal import Decimal
from typing import List

from model.constants import RawDuration


class Duration:
    SCALE: Decimal = Decimal("1")
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

        return "+".join(format_ratio(*(part / Duration.SCALE).as_integer_ratio()) for part in self.parts)

    @staticmethod
    def set_scale(value: Decimal) -> None:
        Duration.SCALE = value

    @property
    def real_duration(self) -> Decimal:
        return self.raw_duration / Duration.SCALE

    @property
    def is_compound(self):
        return len(self.parts) > 1

    def _build_parts(cls, raw_duration: Decimal) -> List[RawDuration]:
        parts = list()
        for real_partition in cls.PARTITIONS:
            scaled_partition = real_partition * Duration.SCALE
            if real_partition <= raw_duration:
                count: Decimal = raw_duration // scaled_partition
                raw_duration -= count * scaled_partition
                parts.extend([scaled_partition for _ in range(int(count))])
        return parts
