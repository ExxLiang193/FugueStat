from typing import TYPE_CHECKING, Iterable
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
    @classmethod
    def replacement(cls, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int) -> int:
        return memo[cur_i - 1][cur_j - 1] + abs(x[cur_i - 1] - y[cur_j - 1])

    @classmethod
    def replacement_with_penalty(cls, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int) -> int:
        penalty = 1 if (x[cur_i - 1] < 0) == (y[cur_j - 1] < 0) else 2
        return memo[cur_i - 1][cur_j - 1] + penalty * abs(x[cur_i - 1] - y[cur_j - 1])

    @classmethod
    def insertion_without_expansion(cls, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int) -> int:
        return memo[cur_i][cur_j - 1] + abs(y[cur_j - 1])

    @classmethod
    def insertion_with_expansion(cls, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int) -> int:
        return (
            float("inf")
            if cur_j < 2
            else memo[cur_i - 1][cur_j - 2] + abs((y[cur_j - 2] + y[cur_j - 1]) - x[cur_i - 1])
        )

    @classmethod
    def deletion_without_compression(cls, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int) -> int:
        return memo[cur_i - 1][cur_j] + abs(x[cur_i - 1])

    @classmethod
    def deletion_with_compression(cls, memo: np.array, x: Iterable, y: Iterable, cur_i: int, cur_j: int) -> int:
        return (
            float("inf")
            if cur_i < 2
            else memo[cur_i - 2][cur_j - 1] + abs((x[cur_i - 2] + x[cur_i - 1]) - y[cur_j - 1])
        )
