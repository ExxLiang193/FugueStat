import math
from functools import lru_cache
from typing import Callable, Iterable, Optional

import numpy as np


class ScalingFunctions:
    @classmethod
    @lru_cache(maxsize=64)
    def sqrt(cls, value: int, scale: int = 1) -> float:
        return math.sqrt(scale * value)

    @classmethod
    @lru_cache(maxsize=64)
    def floored_sqrt(cls, value: int, scale: int = 1) -> float:
        return math.floor(math.sqrt(scale * value))


class DistanceMetrics:
    REPLACEMENT_TOLERANCE = 1
    INSERTION_PENALTY = 0
    DELETION_PENALTY = 1

    def __init__(self, rest_penalty_factor: int = 10, inversion_penalty_factor: int = 2) -> None:
        self._rest_penalty_factor: int = rest_penalty_factor
        self._inversion_penalty_factor: int = inversion_penalty_factor

    @lru_cache(maxsize=128)
    def _safe_sub(self, val_1: Optional[float], val_2: Optional[float]) -> float:
        match (val_1, val_2):
            case (None, None):
                return 0.0
            case (None, _):
                return self._rest_penalty_factor * abs(val_2)
            case (_, None):
                return self._rest_penalty_factor * abs(val_1)
            case (_, _):
                penalty = 1 if (val_1 < 0) == (val_2 < 0) else self._inversion_penalty_factor
                return penalty * max(0, abs(val_1 - val_2) - self.REPLACEMENT_TOLERANCE)

    def replacement_with_penalty(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        return memo[cur_i - 1][cur_j - 1] + scale(self._safe_sub(x[cur_i - 1], y[cur_j - 1]))

    def insertion_without_expansion(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        return (
            float("inf")
            if y[cur_j - 1] is None
            else memo[cur_i][cur_j - 1] + scale(abs(y[cur_j - 1])) + self.INSERTION_PENALTY
        )

    def insertion_with_expansion(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        if cur_j < 2:
            return float("inf")
        if y[cur_j - 2] is None or y[cur_j - 1] is None or x[cur_i - 1] is None:
            return float("inf")
        return (
            memo[cur_i - 1][cur_j - 2]
            + scale(abs((y[cur_j - 2] + y[cur_j - 1]) - x[cur_i - 1]))
            + self.INSERTION_PENALTY
        )

    def deletion_without_compression(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        return (
            float("inf")
            if x[cur_i - 1] is None
            else memo[cur_i - 1][cur_j] + scale(abs(x[cur_i - 1])) + self.DELETION_PENALTY
        )

    def deletion_with_compression(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        if cur_i < 2:
            return float("inf")
        if x[cur_i - 2] is None or x[cur_i - 1] is None or y[cur_j - 1] is None:
            return float("inf")
        return (
            memo[cur_i - 2][cur_j - 1]
            + scale(abs((x[cur_i - 2] + x[cur_i - 1]) - y[cur_j - 1]))
            + self.DELETION_PENALTY
        )
