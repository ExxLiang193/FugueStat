from model.note_sequence import NoteSequence
from algorithm.kmp_soft import KMPSoft
from algorithm.edit_distance import EditDistance
from typing import List, Callable, Tuple, Optional
from collections import namedtuple
from algorithm.edit_distance import RankInfo
from algorithm.model.distance_metrics import ScalingFunctions

TopRank = namedtuple("TopRank", ("best_stream_match", "best_pattern_match", "best_overall_match"))


class StreamMatcher:
    def __init__(
        self, stream: NoteSequence, lps_tolerance: int, sensitivity: float, min_match: int, metrics: List[Callable]
    ) -> None:
        self.stream: NoteSequence = stream
        self.sensitivity: float = sensitivity
        self.min_match: int = min_match
        self.metrics: List[Callable] = metrics
        self._kmp_utility = KMPSoft(lps_tolerance)

    def _get_top_rank(self, match_rank: List[RankInfo]) -> TopRank:
        overall_match: RankInfo = match_rank[0]
        stream_match: RankInfo = next(offset_rank for offset_rank in match_rank if offset_rank.offset > 0)
        pattern_match: RankInfo = next(offset_rank for offset_rank in match_rank if offset_rank.offset <= 0)
        return TopRank(stream_match, pattern_match, overall_match)

    def match_next(self, pattern: NoteSequence, stream_start: int) -> Tuple[Optional[NoteSequence], int]:
        pattern_intervals: List[int] = [
            0 if (value := interval.value) is None else value for interval in pattern.intervals
        ]
        # pattern_lps: List[int] = self._kmp_utility.longest_prefix_suffix(pattern_intervals)
        max_stream_intervals: int = min(stream_start + 2 * len(pattern_intervals), len(self.stream) - 1)
        stream_intervals: List[int] = [
            0 if (value := self.stream.intervals[i].value) is None else value
            for i in range(stream_start, max_stream_intervals)
        ]

        edit_distance: EditDistance = EditDistance(
            stream_intervals, pattern_intervals, self.metrics, ScalingFunctions.sqrt
        )

        while True:
            match_rank: List[RankInfo] = edit_distance.get_rank(self.min_match)
            top_rank: TopRank = self._get_top_rank(match_rank)
            if top_rank.best_overall_match.offset == 0:
                if top_rank.best_overall_match.normalized_distance > self.sensitivity:
                    return None, len(edit_distance.stream)
                result = NoteSequence(self.stream[stream_start : stream_start + len(edit_distance.stream)])
                return result, len(edit_distance.stream)
            elif top_rank.best_overall_match.offset > 0:
                edit_distance.truncate_stream(top_rank.best_overall_match.offset)
            elif top_rank.best_overall_match.offset < 0:
                edit_distance.truncate_pattern(abs(top_rank.best_overall_match.offset))

    def match_all(self, pattern: NoteSequence):
        pass
