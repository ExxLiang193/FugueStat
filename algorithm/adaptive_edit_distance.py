from typing import List, Callable, Tuple
import numpy as np
from collections import namedtuple

RankInfo = namedtuple("RankInfo", ("offset", "normalized_distance"))


class AdaptiveEditDistance:
    def __init__(
        self,
        stream: List[int],
        pattern: List[int],
        metrics: List[Callable],
        scaling_func: Callable,
    ) -> None:
        self.stream: List[int] = stream
        self.pattern: List[int] = pattern
        self.metrics: List[Callable] = metrics
        self.scale: Callable = scaling_func
        self._memo: np.array = self._compute_memo()

    def _compute_memo(self) -> None:
        S, P = len(self.stream), len(self.pattern)
        memo: np.array = np.zeros((S + 1, P + 1))
        for j in range(1, P + 1):
            memo[0, j] = abs(self.pattern[j - 1])
        for i in range(1, S + 1):
            for j in range(1, P + 1):
                memo[i, j] = min(metric(memo, self.stream, self.pattern, i, j, self.scale) for metric in self.metrics)
        return memo

    def get_limits(self) -> Tuple[int, int]:
        S, P = len(self.stream), len(self.pattern)
        i = S - np.argmin(np.flip(self._memo[:, -1]))
        j = P
        while i > 0 and j > 0:
            if self._memo[i - 1][j] < self._memo[i][j]:
                i -= 1
            elif self._memo[i][j - 1] < self._memo[i][j]:
                j -= 1
            else:
                break
        return i, j
