from __future__ import annotations
from model.constants import BaseNoteName, OCTAVE_SUBDIVISIONS
from model.position import Position
from model.accidental import Accidental
from typing import Optional


class NoteName:
    NAME_MAP = {
        BaseNoteName.C: 0,
        BaseNoteName.D: 2,
        BaseNoteName.E: 4,
        BaseNoteName.F: 5,
        BaseNoteName.G: 7,
        BaseNoteName.A: 9,
        BaseNoteName.B: 11,
    }

    def __init__(self, name: str, accidental: Accidental) -> None:
        self.name: BaseNoteName = name
        self.accidental: Accidental = accidental

    def __repr__(self) -> str:
        return f"{self.name}{self.accidental}"

    @classmethod
    def from_raw(cls, name: str, alter: Optional[int]) -> NoteName:
        return NoteName(name, Accidental(alter))

    @property
    def rel_position(self) -> int:
        return (self.NAME_MAP[self.name] + self.accidental.alter) % OCTAVE_SUBDIVISIONS

    def as_position(self, octave: int) -> Position:
        return Position(octave * OCTAVE_SUBDIVISIONS + self.rel_position)
