from duration import Duration
from position import Position
from decimal import Decimal
from typing import Optional


class Note:
    def __init__(self, position: Optional[Position], duration: Duration):
        self.position: Optional[Position] = position
        self.duration: Duration = duration

    @classmethod
    def from_raw(cls, abs_position: Optional[int], raw_duration: Decimal) -> "Note":
        return cls(None if abs_position is None else Position(abs_position), Duration(raw_duration))

    @property
    def is_rest(self):
        return self.position is None
