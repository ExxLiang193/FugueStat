from typing import List, Callable, Tuple
import numpy as np
from collections import namedtuple

RankInfo = namedtuple("RankInfo", ("offset", "normalized_distance"))


class AdaptiveEditDistance:
    def __init__(self, stream: List[int], pattern: List[int], metrics: List[Callable], scaling_func: Callable) -> None:
        self.stream: List[int] = stream
        self.pattern: List[int] = pattern
        self.metrics: List[Callable] = metrics
        self.scale: Callable = scaling_func
        self._memo: np.array = self._compute_memo()

    def _compute_memo(self) -> None:
        S, P = len(self.stream), len(self.pattern)
        memo: np.array = np.zeros((S + 1, P + 1))
        for i in range(1, S + 1):
            for j in range(1, P + 1):
                memo[i][j] = min(metric(memo, self.stream, self.pattern, i, j, self.scale) for metric in self.metrics)
        return memo

    def get_rank(self, min_match: int) -> List[RankInfo]:
        S, P = len(self.stream), len(self.pattern)
        diagonal_offset: int = S - P
        limits: Tuple[int, int] = (min(-1, -P + min_match), max(2, S - min_match + 1))

        def normalized_diagonal_distance(memo: np.array, offset: int) -> float:
            offset_diag = np.diagonal(memo, offset=offset)
            return offset_diag[-1] / (len(offset_diag) - 1)

        return sorted(
            [
                RankInfo(i, normalized_diagonal_distance(self._memo, i - diagonal_offset))
                for i in range(limits[0], limits[1])
            ],
            key=lambda rank_info: (rank_info.normalized_distance, abs(rank_info.offset)),
        )

    def truncate_pattern(self, amount: int) -> None:
        assert amount >= 0
        del self.pattern[-amount:]
        self._memo = self._memo[:, :-amount]

    def truncate_stream(self, amount: int) -> None:
        assert amount >= 0
        del self.stream[-amount:]
        self._memo = self._memo[:-amount, :]

    def extend_stream(self, extension: List[int]) -> None:
        self.stream.extend(extension)
        new_S, P = len(self.stream), len(self.pattern)
        memo = np.pad(self._memo, [(0, len(extension)), (0, 0)], mode="constant")
        for i in range(new_S + 1 - len(extension), new_S + 1):
            for j in range(1, P + 1):
                memo[i][j] = min(metric(memo, self.stream, self.pattern, i, j) for metric in self.metrics)
        self._memo = memo
