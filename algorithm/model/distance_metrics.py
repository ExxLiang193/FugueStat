import math
from decimal import Decimal
from functools import lru_cache
from typing import Any, Callable, Optional

import numpy as np

from algorithm.model.edit_window import EditWindow


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
    DURATION_WEIGHT = 1

    @staticmethod
    def set_penalty_factors(rest_penalty_factor: int, inversion_penalty_factor: int) -> None:
        DistanceMetrics.REST_PENALTY_FACTOR = rest_penalty_factor
        DistanceMetrics.INVERSION_PENALTY_FACTOR = inversion_penalty_factor

    @classmethod
    @lru_cache(maxsize=128)
    def _safe_sub(cls, val_1: Optional[float], val_2: Optional[float]) -> float:
        match (val_1, val_2):
            case (None, None):
                return 0.0
            case (None, _):
                return cls.REST_PENALTY_FACTOR * abs(val_2)
            case (_, None):
                return cls.REST_PENALTY_FACTOR * abs(val_1)
            case (_, _):
                penalty = 1 if (val_1 < 0) == (val_2 < 0) else cls.INVERSION_PENALTY_FACTOR
                return penalty * max(0, abs(val_1 - val_2) - cls.REPLACEMENT_TOLERANCE)

    @classmethod
    @lru_cache(maxsize=64)
    def _abs_mul(cls, val_1: Decimal, val_2: Decimal) -> Decimal:
        return val_1 / val_2 if val_1 >= val_2 else val_2 / val_1

    @classmethod
    def _combine_costs(cls, interval_cost: float, duration_cost: Decimal, scale: Callable) -> float:
        match (interval_cost, duration_cost):
            case (0, 1):
                return 0.0
            case (0, _):
                return scale(Decimal(str(cls.DURATION_WEIGHT)) * duration_cost)
            case (_, _):
                return scale(Decimal(str(cls.DURATION_WEIGHT)) * interval_cost * duration_cost)

    @classmethod
    def replacement_with_penalty(
        cls,
        memo: np.array,
        edit_window: EditWindow,
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        interval_cost = cls._safe_sub(edit_window.stream_intervals[cur_i - 1], edit_window.pattern_intervals[cur_j - 1])
        duration_cost = cls._abs_mul(edit_window.stream_durations[cur_i - 1], edit_window.pattern_durations[cur_j - 1])
        return memo[cur_i - 1][cur_j - 1] + cls._combine_costs(interval_cost, duration_cost, scale)

    @classmethod
    def insertion_without_expansion(
        cls,
        memo: np.array,
        edit_window: EditWindow,
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        if edit_window.pattern_intervals[cur_j - 1] is None:
            return sentinel
        return (
            memo[cur_i][cur_j - 1]
            + cls._combine_costs(
                abs(edit_window.pattern_intervals[cur_j - 1]), edit_window.pattern_durations[cur_j - 1], scale
            )
            + cls.BASE_INSERTION_PENALTY
        )

    @classmethod
    def insertion_with_expansion(
        cls,
        memo: np.array,
        edit_window: EditWindow,
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        if cur_j < 2:
            return sentinel
        if any(
            value is None
            for value in (
                edit_window.pattern_intervals[cur_j - 2],
                edit_window.pattern_intervals[cur_j - 1],
                edit_window.stream_intervals[cur_i - 1],
            )
        ):
            return sentinel
        interval_cost = abs(
            (edit_window.pattern_intervals[cur_j - 2] + edit_window.pattern_intervals[cur_j - 1])
            - edit_window.stream_intervals[cur_i - 1]
        )
        duration_cost = cls._abs_mul(
            edit_window.pattern_durations[cur_j - 2] + edit_window.pattern_durations[cur_j - 1],
            edit_window.stream_durations[cur_i - 1],
        )
        return (
            memo[cur_i - 1][cur_j - 2]
            + cls._combine_costs(interval_cost, duration_cost, scale)
            + cls.BASE_INSERTION_PENALTY
        )

    @classmethod
    def deletion_without_compression(
        cls,
        memo: np.array,
        edit_window: EditWindow,
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        if edit_window.stream_intervals[cur_i - 1] is None:
            return sentinel
        return (
            memo[cur_i - 1][cur_j]
            + cls._combine_costs(
                abs(edit_window.stream_intervals[cur_i - 1]), edit_window.stream_durations[cur_i - 1], scale
            )
            + cls.BASE_DELETION_PENALTY
        )

    @classmethod
    def deletion_with_compression(
        cls,
        memo: np.array,
        edit_window: EditWindow,
        cur_i: int,
        cur_j: int,
        scale: Callable,
        sentinel: Any = float("inf"),
    ) -> float:
        if cur_i < 2:
            return sentinel
        if any(
            value is None
            for value in (
                edit_window.stream_intervals[cur_i - 2],
                edit_window.stream_intervals[cur_i - 1],
                edit_window.pattern_intervals[cur_j - 1],
            )
        ):
            return sentinel
        interval_cost = abs(
            (edit_window.stream_intervals[cur_i - 2] + edit_window.stream_intervals[cur_i - 1])
            - edit_window.pattern_intervals[cur_j - 1]
        )
        duration_cost = cls._abs_mul(
            edit_window.stream_durations[cur_i - 2] + edit_window.stream_durations[cur_i - 1],
            edit_window.pattern_durations[cur_j - 1],
        )
        return (
            memo[cur_i - 2][cur_j - 1]
            + cls._combine_costs(interval_cost, duration_cost, scale)
            + cls.BASE_DELETION_PENALTY
        )
