from __future__ import annotations

import logging
import os
from typing import Callable, List, Tuple

import numpy as np

from algorithm.model.distance_metrics import DistanceMetrics
from algorithm.model.edit_window import EditWindow

logger = logging.getLogger(os.path.basename(__file__))


class AdaptiveEditDistance:
    def __init__(
        self,
        edit_window: EditWindow,
        metrics: List[Callable],
        scaling_func: Callable,
    ) -> None:
        self.edit_window: EditWindow = edit_window
        self.metrics: List[Callable] = metrics
        self.scale: Callable = scaling_func
        self._memo: np.array = self._compute_memo()

    def _compute_memo(self) -> None:
        S, P = len(self.edit_window.stream_intervals), len(self.edit_window.pattern_intervals)
        memo: np.array = np.zeros((S + 1, P + 1))
        for j in range(1, P + 1):
            memo[0, j] = DistanceMetrics.insertion_without_expansion(
                memo, self.edit_window, 0, j, self.scale, sentinel=0.0
            )
        for i in range(1, S + 1):
            for j in range(1, P + 1):
                memo[i, j] = min(metric(memo, self.edit_window, i, j, self.scale) for metric in self.metrics)
        return memo

    def get_limits(self, pattern_complete=False) -> Tuple[int, float]:
        S, P = len(self.edit_window.stream_intervals), len(self.edit_window.pattern_intervals)
        i = S - np.argmin(np.flip(self._memo[:, -1]))
        j = P
        logger.debug(f"\n{self._memo}")
        while i > 0 and j > 0:
            if self._memo[i - 1][j] < self._memo[i][j]:
                i -= 1
            elif self._memo[i][j - 1] < self._memo[i][j]:
                if pattern_complete:
                    break
                j -= 1
            else:
                break
        return i, self._memo[i, j] / (i + 1)
