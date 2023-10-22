from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from model.note import Note

if TYPE_CHECKING:
    from model.duration import Duration
    from model.interval import Interval


class NoteSequence:
    def __init__(self, notes: List[Note] = None) -> None:
        self.notes: List[Note] = notes or list()

    def __getitem__(self, idx) -> Note:
        return self.notes[idx]

    def __len__(self) -> int:
        return len(self.notes)

    def __add__(self, other: NoteSequence) -> NoteSequence:
        return NoteSequence(self.notes + other.notes)

    @property
    def first_note(self) -> Note:
        return next(note for note in self.notes if not note.is_rest())

    @property
    def last_note(self) -> Note:
        return next(note for note in reversed(self.notes) if not note.is_rest())

    @property
    def intervals(self) -> List[Optional[Interval]]:
        def parse(left_note: Note, right_note: Note) -> Optional[Interval]:
            if left_note.is_rest() or right_note.is_rest():
                return None
            return right_note.position - left_note.position

        return [parse(self.notes[i - 1], self.notes[i]) for i in range(1, len(self.notes))]

    @property
    def durations(self) -> List[Duration]:
        return [self.notes[i].duration for i in range(len(self.notes))]

    @property
    def raw_intervals(self) -> List[Optional[int]]:
        def parse(left_note: Note, right_note: Note) -> Optional[int]:
            if left_note.is_rest() or right_note.is_rest():
                return None
            return (right_note.position - left_note.position).value

        return [parse(self.notes[i - 1], self.notes[i]) for i in range(1, len(self.notes))]

    @property
    def raw_durations(self) -> List[Decimal]:
        return [self.notes[i].duration.raw_duration for i in range(len(self.notes))]

    def raw_intervals_range(self, low: int, high: int) -> List[Optional[int]]:
        """[low, high]"""
        assert low >= 0
        assert high < len(self.notes)

        def parse(left_note: Note, right_note: Note) -> Optional[int]:
            if left_note.is_rest() or right_note.is_rest():
                return None
            return (right_note.position - left_note.position).value

        return [parse(self.notes[i - 1], self.notes[i]) for i in range(low + 1, high + 1)]

    def raw_durations_range(self, low: int, high: int) -> List[Decimal]:
        """[low, high]"""
        assert low >= 0
        assert high < len(self.notes)
        return [self.notes[i].duration.raw_duration for i in range(low, high + 1)]

    def append_note(self, note: Note) -> None:
        self.notes.append(note)

    def extend_notes(self, other: NoteSequence) -> None:
        self.notes.extend(other.notes)

    def merge_last_note(self, other: Note) -> None:
        self.notes[-1].extend_duration(other)

    def next_note_idx(self, start: int = 0) -> Optional[int]:
        ref = start + 1
        while ref < len(self.notes):
            if not self.notes[ref].is_rest():
                return ref
            ref += 1
        return None

    def next_rest_idx(self, start: int = 0) -> Optional[int]:
        ref = start + 1
        while ref < len(self.notes):
            if self.notes[ref].is_rest():
                return ref
            ref += 1
        return None

    def lstrip_rests(self) -> None:
        strip_idx = self.next_note_idx(0)
        if not self.notes[0].is_rest() and strip_idx == 1:
            return
        del self.notes[:strip_idx]

    def optimize(self) -> NoteSequence:
        if len(self.notes) <= 0:
            return self
        result: List[Note] = [self.notes[0]]
        for i in range(1, len(self.notes)):
            if self.notes[i].is_rest() and result[-1].is_rest():
                if self.notes[i].is_tagged() == result[-1].is_tagged():
                    result[-1].extend_duration(self.notes[i])
                else:
                    result.append(self.notes[i])
            else:
                result.append(self.notes[i])
        self.notes = result
        return self
