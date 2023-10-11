from typing import Iterable, List, Callable, Tuple
import numpy as np


class EditDistance:
    def __init__(self, stream: Iterable, pattern: Iterable, metrics: List[Callable]) -> None:
        self.stream: Iterable = stream
        self.pattern: Iterable = pattern
        self.metrics: List[Callable] = metrics
        self._memo: np.array = None

    def _compute_memo(self) -> None:
        S, P = len(self.stream), len(self.pattern)
        memo: np.array = np.zeros((S + 1, P + 1))
        for i in range(1, S + 1):
            for j in range(1, P + 1):
                memo[i][j] = min(metric(memo, self.stream, self.pattern, i, j) for metric in self.metrics)
        self._memo = memo

    def get_memo(self) -> np.array:
        if self._memo is not None:
            return self._memo
        self._compute_memo()
        return self._memo

    def get_rank(self, min_match: int) -> np.array:
        S, P = len(self.stream), len(self.pattern)
        diagonal_offset: int = S - P
        limits: Tuple[int, int] = (
            min(0, -P + min_match - diagonal_offset),
            max(1, S - min_match + 1 - diagonal_offset),
        )

        def get_normalized_diagonal_distance(memo: np.array, offset: int) -> float:
            offset_diag = np.diagonal(memo, offset=offset)
            return offset_diag[-1] / (len(offset_diag) - 1)

        rank: np.array = np.array(
            sorted(
                [
                    (i + diagonal_offset, get_normalized_diagonal_distance(self._memo, i))
                    for i in range(limits[0], limits[1])
                ],
                key=lambda freq_rank: (freq_rank[1], abs(freq_rank[0])),
            )
        )
        return rank

    def extend_stream(self, extension: Iterable) -> None:
        self.stream.extend(extension)
        S, P = len(self.stream), len(self.pattern)
        memo = np.pad(self._memo, [(0, len(extension)), (0, 0)], mode="constant")
        for i in range(S + 1 - len(extension), S + 1):
            for j in range(1, P + 1):
                memo[i][j] = min(metric(memo, self.stream, self.pattern, i, j) for metric in self.metrics)
        self._memo = memo
