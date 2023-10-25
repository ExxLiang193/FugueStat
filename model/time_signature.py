from __future__ import annotations
from decimal import Decimal


class TimeSignature:
    DURATION_SCALE: int = Decimal("4")

    def __init__(self, beat_count: int, real_beat_duration: Decimal) -> None:
        self.beat_count: int = beat_count
        self.real_beat_duration: Decimal = real_beat_duration

    @property
    def real_measure_duration(self) -> Decimal:
        return self.beat_count * self.real_beat_duration

    @classmethod
    def from_raw(self, beat_count: int, beat_duration: Decimal) -> TimeSignature:
        return TimeSignature(beat_count, self.DURATION_SCALE / beat_duration)
