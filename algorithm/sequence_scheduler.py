from typing import List, Tuple
from collections import namedtuple

from model.note_sequence import NoteSequence

ScheduleItem = namedtuple("ScheduleItem", ("sequence_id", "weight", "start", "end"))


class SequenceScheduler:
    def __init__(self, weighted_sequences: List[Tuple[NoteSequence, float]]) -> None:
        assert len(weighted_sequences) > 0
        self.weighted_sequences: List[Tuple[NoteSequence, float]] = weighted_sequences
        self._max_weight: float = max(match_info[1] for match_info in self.weighted_sequences)

    def _compute_memo(self, items: List[ScheduleItem]) -> List[int]:
        R: int = len(self.weighted_sequences)
        memo: List[int] = [0] * R
        memo[0] = self._max_weight - items[0].weight
        for j in range(1, R):
            for i in range(j):
                if items[i].end < items[j].start:
                    memo[j] = max(memo[j], memo[i] + (self._max_weight - items[j].weight))
        return memo

    def _compute_schedule(self, items: List[ScheduleItem], memo: List[int]) -> List[int]:
        R: int = len(self.weighted_sequences)
        max_idx = max((i for i in range(R - 1, -1, -1)), key=lambda i: memo[i])
        schedule: List[int] = [items[max_idx].sequence_id]
        for i in range(max_idx - 1, -1, -1):
            if (
                items[i].end < items[max_idx].start
                and abs(memo[i] - (memo[max_idx] - (self._max_weight - items[max_idx].weight))) <= 0.001
            ):
                schedule.append(items[i].sequence_id)
                max_idx = i
        return schedule[::-1]

    def get_schedule(self) -> List[int]:
        items: List[ScheduleItem] = [
            ScheduleItem(sequence_id, weight, sequence[0].ids[0], sequence[-1].ids[-1])
            for sequence_id, (sequence, weight) in enumerate(self.weighted_sequences)
        ]
        items.sort(key=lambda entry: entry.end)
        memo: List[int] = self._compute_memo(items)
        return self._compute_schedule(items, memo)
