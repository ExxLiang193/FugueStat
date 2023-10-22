import math
from functools import lru_cache
from typing import Callable, List, Optional, Any

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
    REST_PENALTY_FACTOR = 5
    INVERSION_PENALTY_FACTOR = 2
    REPLACEMENT_TOLERANCE = 1
    BASE_INSERTION_PENALTY = 0
    BASE_DELETION_PENALTY = 0

    @staticmethod
    def set_penalty_factors(rest_penalty_factor: int, inversion_penalty_factor: int) -> None:
        DistanceMetrics.REST_PENALTY_FACTOR = rest_penalty_factor
        DistanceMetrics.INVERSION_PENALTY_FACTOR = inversion_penalty_factor

    @staticmethod
    @lru_cache(maxsize=128)
    def _safe_sub(val_1: Optional[float], val_2: Optional[float]) -> float:
        match (val_1, val_2):
            case (None, None):
                return 0.0
            case (None, _):
                return DistanceMetrics.REST_PENALTY_FACTOR * abs(val_2)
            case (_, None):
                return DistanceMetrics.REST_PENALTY_FACTOR * abs(val_1)
            case (_, _):
                penalty = 1 if (val_1 < 0) == (val_2 < 0) else DistanceMetrics.INVERSION_PENALTY_FACTOR
                return penalty * max(0, abs(val_1 - val_2) - DistanceMetrics.REPLACEMENT_TOLERANCE)

    @staticmethod
    def replacement_with_penalty(
        memo: np.array,
        x: List[Optional[int]],
        y: List[Optional[int]],
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        return memo[cur_i - 1][cur_j - 1] + scale(DistanceMetrics._safe_sub(x[cur_i - 1], y[cur_j - 1]))

    @staticmethod
    def insertion_without_expansion(
        memo: np.array,
        x: List[Optional[int]],
        y: List[Optional[int]],
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        return (
            sentinel
            if y[cur_j - 1] is None
            else memo[cur_i][cur_j - 1] + scale(abs(y[cur_j - 1])) + DistanceMetrics.BASE_INSERTION_PENALTY
        )

    @staticmethod
    def insertion_with_expansion(
        memo: np.array,
        x: List[Optional[int]],
        y: List[Optional[int]],
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        if cur_j < 2:
            return sentinel
        if y[cur_j - 2] is None or y[cur_j - 1] is None or x[cur_i - 1] is None:
            return sentinel
        return (
            memo[cur_i - 1][cur_j - 2]
            + scale(abs((y[cur_j - 2] + y[cur_j - 1]) - x[cur_i - 1]))
            + DistanceMetrics.BASE_INSERTION_PENALTY
        )

    @staticmethod
    def deletion_without_compression(
        memo: np.array,
        x: List[Optional[int]],
        y: List[Optional[int]],
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        return (
            sentinel
            if x[cur_i - 1] is None
            else memo[cur_i - 1][cur_j] + scale(abs(x[cur_i - 1])) + DistanceMetrics.BASE_DELETION_PENALTY
        )

    @staticmethod
    def deletion_with_compression(
        memo: np.array,
        x: List[Optional[int]],
        y: List[Optional[int]],
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        if cur_i < 2:
            return sentinel
        if x[cur_i - 2] is None or x[cur_i - 1] is None or y[cur_j - 1] is None:
            return sentinel
        return (
            memo[cur_i - 2][cur_j - 1]
            + scale(abs((x[cur_i - 2] + x[cur_i - 1]) - y[cur_j - 1]))
            + DistanceMetrics.BASE_DELETION_PENALTY
        )
