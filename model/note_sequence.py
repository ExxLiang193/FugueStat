from typing import List
from note import Note


class NoteSequence:
    def __init__(self, notes: List[Note]) -> None:
        self.notes: List[Note] = notes

    def __add__(self, other: "NoteSequence") -> "NoteSequence":
        return NoteSequence(self.notes + other.notes)

    def append(self, note: Note) -> None:
        self.notes.append(note)

    def extend(self, other: "NoteSequence") -> None:
        self.notes.extend(other.notes)
