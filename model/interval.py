from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.position import Position


class Interval:
    def __init__(self, left_position: Position, right_position: Position) -> None:
        self.value: int = right_position.abs_position - left_position.abs_position

    def __repr__(self) -> str:
        return f"<{self.value}>"
