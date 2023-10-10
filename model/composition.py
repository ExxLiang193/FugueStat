from typing import Dict
from model.note_sequence import NoteSequence


class Composition:
    def __init__(self, voices: Dict[int, NoteSequence]) -> None:
        self.voices: Dict[int, NoteSequence] = voices
