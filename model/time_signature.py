from __future__ import annotations
from decimal import Decimal


class TimeSignature:
    DURATION_SCALE: int = Decimal("4")

    def __init__(self, beat_count: int, beat_duration: Decimal) -> None:
        self.beat_count: int = beat_count
        self.beat_duration: Decimal = beat_duration

    @property
    def measure_duration(self) -> Decimal:
        return self.beat_count * self.beat_duration

    @classmethod
    def from_raw(self, beat_count: int, beat_duration: Decimal) -> TimeSignature:
        return TimeSignature(beat_count, beat_duration / self.DURATION_SCALE)
