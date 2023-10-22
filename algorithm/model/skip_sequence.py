from __future__ import annotations

import pprint
from decimal import Decimal
from itertools import accumulate, chain
from typing import TYPE_CHECKING, Dict, Iterable, List, Tuple

if TYPE_CHECKING:
    from model.note import Note
    from model.note_sequence import NoteSequence


class SkipNode:
    def __init__(self, note: Note, next_idx: int) -> None:
        self.note: Note = note
        self.next_idx: int = next_idx

    def __repr__(self) -> str:
        return f"{self.note}->#{self.next_idx}"


class SkipSequence:
    def __init__(self, voices: Dict[int, NoteSequence]) -> None:
        self.head: List[Dict[int, SkipNode]] = self._parse_sequences(voices)
        self.voices: Dict[int, NoteSequence] = voices

    def __getitem__(self, i: int) -> Dict[int, SkipNode]:
        return self.head[i]

    def __repr__(self) -> str:
        return pprint.pformat([(f"#{i}", voices) for i, voices in enumerate(self.head)], indent=4)

    # def _auto_join(self, skip_seq: List[Dict[int, SkipNode]]) -> List[Dict[int, SkipNode]]:
    #     most_recent_notes: Dict[int, SkipNode] = {voice: node for voice, node in skip_seq[0].items()}
    #     for i in range(1, len(skip_seq)):
    #         # detached_voices =
    #         for voice, node in skip_seq[i].items():
    #             if most_recent_notes[voice].next_idx != i:
    #                 continue
    #             if skip_seq[i][voice].note.is_rest() != most_recent_notes[voice].note.is_rest():
    #                 pass

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
            for i in range(len(voices[voice_idx])):
                result[timestamp_by_idx[cur_time]][voice_idx] = SkipNode(
                    note_sequence[i], timestamp_by_idx[cur_time + note_sequence[i].duration.raw_duration]
                )
                cur_time += note_sequence[i].duration.raw_duration

        return result

    def is_solo(self, moment: int, target_voice: int) -> bool:
        return all(node.note.is_rest() for voice, node in self.head[moment].items() if voice != target_voice)

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
