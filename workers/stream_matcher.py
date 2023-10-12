from model.note_sequence import NoteSequence
from algorithm.kmp_soft import KMPSoft
from algorithm.adaptive_edit_distance import AdaptiveEditDistance
from typing import List, Callable, Tuple, Optional
from collections import namedtuple
from algorithm.adaptive_edit_distance import RankInfo
from algorithm.model.distance_metrics import ScalingFunctions

TopRank = namedtuple("TopRank", ("best_stream_match", "best_pattern_match", "best_overall_match"))


class StreamMatcher:
    PADDING_FACTOR = 2

    def __init__(
        self, stream: NoteSequence, lps_tolerance: int, sensitivity: float, min_match: int, metrics: List[Callable]
    ) -> None:
        self.stream: NoteSequence = stream
        self.sensitivity: float = sensitivity
        self.min_match: int = min_match
        self.metrics: List[Callable] = metrics
        self._kmp_utility = KMPSoft(lps_tolerance)

    def _extract_intervals(self, pattern: NoteSequence, stream_start: int) -> Tuple[List[int], List[int]]:
        pattern_intervals: List[int] = [0 if interval is None else interval.value for interval in pattern.intervals]
        max_stream_intervals: int = min(
            stream_start + self.PADDING_FACTOR * len(pattern_intervals), len(self.stream) - 1
        )
        stream_intervals: List[int] = [
            0 if (interval := self.stream.intervals[i]) is None else interval.value
            for i in range(stream_start, max_stream_intervals)
        ]
        return pattern_intervals, stream_intervals

    def _get_top_rank(self, match_rank: List[RankInfo]) -> TopRank:
        overall_match: RankInfo = match_rank[0]
        stream_match: RankInfo = next(offset_rank for offset_rank in match_rank if offset_rank.offset > 0)
        pattern_match: RankInfo = next(offset_rank for offset_rank in match_rank if offset_rank.offset <= 0)
        return TopRank(stream_match, pattern_match, overall_match)

    def _push_forward(self, pattern: NoteSequence, stream_start: int) -> int:
        pattern_intervals, stream_intervals = self._extract_intervals(pattern, stream_start)
        edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals[::-1], pattern_intervals[::-1], self.metrics, ScalingFunctions.sqrt
        )

        while True:
            match_rank: List[RankInfo] = edit_distance.get_rank(self.min_match)
            top_rank: TopRank = self._get_top_rank(match_rank)
            if top_rank.best_overall_match.offset == 0:
                return len(stream_intervals) - len(edit_distance.stream)
            elif top_rank.best_overall_match.offset > 0:
                edit_distance.truncate_stream(top_rank.best_overall_match.offset)
            elif top_rank.best_overall_match.offset < 0:
                edit_distance.truncate_pattern(abs(top_rank.best_overall_match.offset))

    def _pull_back(self, pattern: NoteSequence, stream_start: int) -> Tuple[Optional[NoteSequence], int]:
        pattern_intervals, stream_intervals = self._extract_intervals(pattern, stream_start)
        edit_distance: AdaptiveEditDistance = AdaptiveEditDistance(
            stream_intervals, pattern_intervals, self.metrics, ScalingFunctions.sqrt
        )

        while True:
            match_rank: List[RankInfo] = edit_distance.get_rank(self.min_match)
            top_rank: TopRank = self._get_top_rank(match_rank)
            if top_rank.best_overall_match.offset == 0:
                if top_rank.best_overall_match.normalized_distance > self.sensitivity:
                    return None, len(edit_distance.stream) - 1
                result = NoteSequence(self.stream[stream_start : stream_start + len(edit_distance.stream) + 1])
                return result, len(edit_distance.stream) - 1
            elif top_rank.best_overall_match.offset > 0:
                edit_distance.truncate_stream(top_rank.best_overall_match.offset)
            elif top_rank.best_overall_match.offset < 0:
                edit_distance.truncate_pattern(abs(top_rank.best_overall_match.offset))

    def match_next(self, pattern: NoteSequence, stream_start: int) -> Tuple[Optional[NoteSequence], int]:
        while (push_amount := self._push_forward(pattern, stream_start)) > 0:
            stream_start += push_amount
        match, pull_amount = self._pull_back(pattern, stream_start)
        stream_start += pull_amount
        return match, stream_start

    def match_all(self, pattern: NoteSequence) -> List[NoteSequence]:
        results = list()
        cur_stream_pos: int = 0
        while cur_stream_pos < len(self.stream) - self.min_match:
            match, cur_stream_pos = self.match_next(pattern, self.stream.next_note_idx(cur_stream_pos))
            if match is not None:
                results.append(match)
        return results
