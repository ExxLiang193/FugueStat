from __future__ import annotations
from model.duration import Duration
from model.position import Position
from decimal import Decimal
from typing import Optional, List
from model.note import Note


class TaggedNote(Note):
    def __init__(self, position: Optional[Position], duration: Duration, ids: List[int]) -> None:
        super().__init__(position, duration)
        self.ids: List[int] = ids

    def __repr__(self) -> str:
        return f"{'TaggedRest' if self.is_rest() else 'TaggedNote'}({self.position}{{{self.duration}}})@{self.ids}"

    @classmethod
    def from_raw(cls, abs_position: Optional[int], raw_duration: Decimal, ids: List[int]) -> Note:
        return cls(None if abs_position is None else Position(abs_position), Duration(raw_duration), ids)

    def extend_duration(self, other: TaggedNote) -> None:
        assert self.position == other.position
        self.duration += other.duration
        self.ids.extend(other.ids)
