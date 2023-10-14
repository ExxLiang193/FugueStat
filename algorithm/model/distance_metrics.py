from typing import Iterable, Callable, Optional
from functools import lru_cache
import math
import numpy as np


class ScalingFunctions:
    @classmethod
    @lru_cache(maxsize=32)
    def sqrt(cls, value: int, scale: int = 1) -> float:
        return math.sqrt(scale * value)

    @classmethod
    @lru_cache(maxsize=32)
    def floored_sqrt(cls, value: int, scale: int = 1) -> float:
        return math.floor(math.sqrt(scale * value))


class DistanceMetrics:
    def __init__(self, rest_penalty_factor: int = 10, inversion_penalty_factor: int = 2) -> None:
        self._rest_penalty_factor: int = rest_penalty_factor
        self._inversion_penalty_factor: int = inversion_penalty_factor

    def _safe_sub(self, val_1: float, val_2: float) -> float:
        match (val_1, val_2):
            case (None, None):
                return 0.0
            case (None, _):
                return self._rest_penalty_factor * abs(val_2)
            case (_, None):
                return self._rest_penalty_factor * abs(val_1)
            case (_, _):
                penalty = 1 if (val_1 < 0) == (val_2 < 0) else self._inversion_penalty_factor
                return penalty * abs(val_1 - val_2)

    def _safe_add(self, val_1: float, val_2: float) -> Optional[float]:
        return None if val_1 is None or val_2 is None else val_1 + val_2

    def replacement_with_penalty(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        return memo[cur_i - 1][cur_j - 1] + scale(self._safe_sub(x[cur_i - 1], y[cur_j - 1]))

    def insertion_without_expansion(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        return memo[cur_i][cur_j - 1] + scale(abs(y[cur_j - 1] or 0.0))

    def insertion_with_expansion(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        return (
            float("inf")
            if cur_j < 2
            else memo[cur_i - 1][cur_j - 2]
            + scale(self._safe_sub(self._safe_add(y[cur_j - 2], y[cur_j - 1]), x[cur_i - 1]))
        )

    def deletion_without_compression(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        return memo[cur_i - 1][cur_j] + scale(abs(x[cur_i - 1] or 0.0))

    def deletion_with_compression(
        self, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int, scale: Callable
    ) -> int:
        return (
            float("inf")
            if cur_i < 2
            else memo[cur_i - 2][cur_j - 1]
            + scale(self._safe_sub(self._safe_add(x[cur_i - 2], x[cur_i - 1]), y[cur_j - 1]))
        )
