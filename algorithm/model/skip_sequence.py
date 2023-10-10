from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Iterable
from decimal import Decimal
from itertools import accumulate, chain
import pprint

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
    def __init__(self, voices: Dict[int, NoteSequence]) -> None:
        self.head: List[Dict[int, SkipNode]] = self._parse_sequences(voices)

    def __getitem__(self, i: int) -> Dict[int, SkipNode]:
        return self.head[i]

    def __repr__(self) -> str:
        return pprint.pformat([(f"#{i}", voices) for i, voices in enumerate(self.head)], indent=4)

    def _parse_sequences(self, voices: Dict[int, NoteSequence]) -> List[Dict[int, SkipNode]]:
        for voice in voices.values():
            voice.optimize()

        timestamp_sequences: Iterable[Iterable[Decimal]] = (
            accumulate(
                voice.notes,
                lambda cur_timestamp, note: cur_timestamp + note.duration.raw_duration,
                initial=Decimal("0.0"),
            )
            for voice in voices.values()
        )
        unique_timestamps: List[Decimal] = sorted(set(chain.from_iterable(timestamp_sequences)))
        timestamp_by_idx: Dict[int, Decimal] = {timestamp: idx for idx, timestamp in enumerate(unique_timestamps)}

        result: List[Dict[int, SkipNode]] = [dict() for _ in unique_timestamps]
        for voice_idx, note_sequence in voices.items():
            cur_time = Decimal("0.0")
            for i in range(len(voices[voice_idx].notes)):
                result[timestamp_by_idx[cur_time]][voice_idx] = SkipNode(
                    note_sequence.notes[i], timestamp_by_idx[cur_time + note_sequence.notes[i].duration.raw_duration]
                )
                cur_time += note_sequence.notes[i].duration.raw_duration

        return result

    def is_solo(self, moment: int) -> bool:
        return len(self.head[moment]) == 1

    def get_note(self, moment: int, voice: int) -> Note:
        return self.head[moment][voice].note

    def next_moment(self, cur_moment: int, voice: int) -> int:
        return self.head[cur_moment][voice].next_idx

    def next_note(self, cur_moment: int, voice: int) -> int:
        while (
            (next_idx := self.next_moment(cur_moment, voice))
            and (next_skip_node := self.head[next_idx].get(voice))
            and next_skip_node.note.is_rest()
        ):
            cur_moment = next_idx

        if next_skip_node is None:
            return -1
        return next_idx

    def next_rest(self, cur_moment: int, voice: int) -> int:
        while (
            (next_idx := self.next_moment(cur_moment, voice))
            and (next_skip_node := self.head[next_idx].get(voice))
            and not next_skip_node.note.is_rest()
        ):
            cur_moment = next_idx

        if next_skip_node is None:
            return -1
        return next_idx
