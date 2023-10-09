from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Iterable
from decimal import Decimal
from itertools import accumulate, chain

if TYPE_CHECKING:
    from model.note_sequence import NoteSequence
    from model.note import Note


class SkipNode:
    def __init__(self, note: Note, next_idx: int) -> None:
        self.note: Note = note
        self.next_idx: int = next_idx

    def __repr__(self) -> str:
        return f"{self.note}->#{self.next_idx}"


class SkipSequence:
    def __init__(self, voices: List[NoteSequence]) -> None:
        self.head: List[Dict[int, SkipNode]] = self._parse_sequences(voices)

    def _parse_sequences(self, voices: List[NoteSequence]) -> List[Dict[int, SkipNode]]:
        timestamp_sequences: Iterable[Iterable[Decimal]] = (
            accumulate(
                voice.notes,
                lambda cur_timestamp, note: cur_timestamp + note.duration.raw_duration,
                initial=Decimal("0.0"),
            )
            for voice in voices
        )
        unique_timestamps: List[Decimal] = sorted(set(chain.from_iterable(timestamp_sequences)))
        timestamp_by_idx: Dict[int, Decimal] = {timestamp: idx for idx, timestamp in enumerate(unique_timestamps)}

        result: List[Dict[int, SkipNode]] = [dict() for _ in unique_timestamps]
        for voice_idx, note_sequence in enumerate(voices):
            cur_time = Decimal("0.0")
            for i in range(len(voices[voice_idx].notes)):
                result[timestamp_by_idx[cur_time]][voice_idx] = SkipNode(
                    note_sequence.notes[i], timestamp_by_idx[cur_time + note_sequence.notes[i].duration.raw_duration]
                )
                cur_time += note_sequence.notes[i].duration.raw_duration

        return result
