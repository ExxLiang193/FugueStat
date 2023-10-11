from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional
from model.note import Note

if TYPE_CHECKING:
    from model.interval import Interval


class NoteSequence:
    def __init__(self, notes: List[Note] = None) -> None:
        self.notes: List[Note] = notes or list()

    def __add__(self, other: NoteSequence) -> NoteSequence:
        return NoteSequence(self.notes + other.notes)

    def __repr__(self) -> str:
        return repr(self.notes)

    @property
    def intervals(self) -> List[Optional[Interval]]:
        def parse(left_note: Note, right_note: Note) -> Optional[Interval]:
            if left_note.is_rest() or right_note.is_rest():
                return None
            return right_note.position - left_note.position

        return [parse(self.notes[i - 1], self.notes[i]) for i in range(1, len(self.notes))]

    def append_note(self, note: Note) -> None:
        self.notes.append(note)

    def extend_notes(self, other: NoteSequence) -> None:
        self.notes.extend(other.notes)

    def merge_last_note(self, other: Note) -> None:
        self.notes[-1].extend_duration(other)

    def optimize(self) -> NoteSequence:
        if len(self.notes) <= 0:
            return self
        result: List[Note] = [self.notes[0]]
        for i in range(1, len(self.notes)):
            if self.notes[i].is_rest() and result[-1].is_rest():
                result[-1].extend_duration(self.notes[i])
            else:
                result.append(self.notes[i])
        self.notes = result
        return self
