import pytest
import numpy as np
from algorithm.model.distance_metrics import DistanceMetrics
from unittest import mock
from typing import Final, List
from workers.stream_interval_matcher import StreamIntervalMatcher


BASE_PATH: Final[str] = "workers.stream_matcher"

test_rest_penalty_factor: Final[int] = 5
test_inversion_penalty_factor: Final[int] = 1
test_sensitivity: Final[float] = 0.3

test_stream_intervals_raw: Final[List[int]] = [
    None, 2, 2, 1, 2, -2, -1, 5, -7, 5,             # 0
    2, -2, -2, -1, 1, -2, -1, 5, -7, 5,             # 10
    None, None, 2, 1, 2, -7, None, None, 2, 2,      # 20
    1, 2, -2, -1, 5, -7, 5, 2, -2, -2,              # 30
    -1, 5, -2, -2, -1, 1, -3, 7, -2, -2,            # 40
    -1, 1, -3, 2, 1, 2, -2, -1, -2, -2,             # 50
    None, None, 2, 2, 1, 2, -2, -1, 4, -6,          # 60
    5, 1, -1, -2, -1, 1, -1, 1, None, None,         # 70
    2, 2, 1, 2, -2, -1, 5, -7, 5, -7,               # 80
    7, -2, -3, 7, -2, None, None, 2, 2, 1,          # 90
    2, -2, -2, 5, -6, 5, 1, -1, -2, -1,             # 100
    None, None, 2, 2, 1, 2, -2, -2, 6, -7,          # 110
    5, 0, 2, -2, -2, -2, 2, -2, -1, -2,             # 120
    -2, 2, -3, 1, 4, 1, 2, 2, 1, -1,                # 130
    -2, 5, -7, 5, 2, -2, -1, -2, 2, -2,             # 140
    -7, 0, -7, 2, 2, 1, 2, -2, -1, 5,               # 150
    -7, 5, 2, -2, -2, -1, -2, 2, 1, 2,              # 160
    2, 1, -3, 2, -5, 1, 2, 2, 2, 1,                 # 170
    -3, 2, 1                                        # 180
]
test_pattern_intervals_raw: Final[List[int]] = [2, 2, 1, 2, -2, -1, 5, -7, 5, 2, -2, -2, -1, 1]
test_pattern_intervals_short: Final[List[int]] = [2, 3, 1, 2, -2]
test_pattern_intervals_long: Final[List[int]] = [2, 3, 1, 2, -2, -1, 5, -7, 5, 2]


class TestStreamIntervalMatcher:
    @pytest.fixture(scope="class")
    def distance_metrics(self) -> DistanceMetrics:
        return DistanceMetrics(test_rest_penalty_factor, test_inversion_penalty_factor)

    @pytest.fixture(scope="function")
    def stream_interval_matcher(self, request, distance_metrics: DistanceMetrics) -> StreamIntervalMatcher:
        return StreamIntervalMatcher(
            request.param,
            test_sensitivity,
            [
                distance_metrics.replacement_with_penalty,
                distance_metrics.insertion_without_expansion,
                distance_metrics.insertion_with_expansion,
                distance_metrics.deletion_without_compression,
                distance_metrics.deletion_with_compression,
            ],
        )

    # STREAM = PATTERN

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 5)]
    )
    def test_short_stream_equal_to_pattern_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -2, -1, 5, -7, 5, 2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 10)]
    )
    def test_long_stream_equal_to_pattern_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    # STREAM = PATTERN except 1 small substitution

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -3]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 5)]
    )
    def test_short_stream_near_pattern_small_substitution_at_end_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -2, -1, 5, -7, 5, 3]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 10)]
    )
    def test_long_stream_near_pattern_small_substitution_at_end_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, -1, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 5)]
    )
    def test_short_stream_near_pattern_small_substitution_somewhere_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 1, -2, -1, 5, -7, 5, 2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 10)]
    )
    def test_long_stream_near_pattern_small_substitution_somewhere_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[1, 3, 1, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 5)]
    )
    def test_short_stream_near_pattern_small_substitution_at_start_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[1, 3, 1, 2, -2, -1, 5, -7, 5, 2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 10)]
    )
    def test_long_stream_near_pattern_small_substitution_at_start_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    # STREAM = PATTERN except 1 big substitution

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -1]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 5)]
    )
    def test_short_stream_near_pattern_big_substitution_at_end_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -2, -1, 5, -7, 5, 1]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 10)]
    )
    def test_long_stream_near_pattern_big_substitution_at_end_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, -2, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 5)]
    )
    def test_short_stream_near_pattern_big_substitution_somewhere_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 5, -2, -1, 5, -7, 5, 2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 10)]
    )
    def test_long_stream_near_pattern_big_substitution_somewhere_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[5, 3, 1, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 5)]
    )
    def test_short_stream_near_pattern_big_substitution_at_start_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[4, 3, 1, 2, -2, -1, 5, -7, 5, 2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 10)]
    )
    def test_long_stream_near_pattern_big_substitution_at_start_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    # STREAM = PATTERN except 1 very big substitution

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -6]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 4)]
    )
    def test_short_stream_near_pattern_very_big_substitution_at_end_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -2, -1, 5, -7, 5, 6]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 9)]
    )
    def test_long_stream_near_pattern_very_big_substitution_at_end_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, -5, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, False, 0, 5)]
    )
    def test_short_stream_near_pattern_very_big_substitution_somewhere_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.xfail
    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 7, -2, -1, 5, -7, 5, 2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 4, 10)]
    )
    def test_long_stream_near_pattern_very_big_substitution_somewhere_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[7, 3, 1, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 1, 5)]
    )
    def test_short_stream_near_pattern_very_big_substitution_at_start_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[6, 3, 1, 2, -2, -1, 5, -7, 5, 2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 1, 10)]
    )
    def test_long_stream_near_pattern_very_big_substitution_at_start_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    # STREAM = PATTERN except 1 deletion

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 0, -1]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 4)]
    )
    def test_short_stream_near_pattern_one_deletion_at_end_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -2, -1, 5, -7, 7, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 9)]
    )
    def test_long_stream_near_pattern_one_deletion_at_end_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 4, 2, -2, -1]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 4)]
    )
    def test_short_stream_near_pattern_one_deletion_somewhere_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 3, -2, -1, 5, -7, 5, 2, -4]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 9)]
    )
    def test_long_stream_near_pattern_one_deletion_somewhere_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[5, 1, 2, -2, -1]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 4)]
    )
    def test_short_stream_near_pattern_one_deletion_at_start_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[5, 1, 2, -2, -1, 5, -7, 5, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 9)]
    )
    def test_long_stream_near_pattern_one_deletion_at_start_matches_partial(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    # STREAM = PATTERN except 1 insertion

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, 1, -3]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 6)]
    )
    def test_short_stream_near_pattern_one_insertion_at_end_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, 2, -2, -1, 5, -7, 5, -2, 4]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 11)]
    )
    def test_long_stream_near_pattern_one_insertion_at_end_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, -2, 3, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 6)]
    )
    def test_short_stream_near_pattern_one_insertion_somewhere_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[2, 3, 1, -1, 3, -2, -1, 5, -7, 5, 2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 11)]
    )
    def test_long_stream_near_pattern_one_insertion_somewhere_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[3, -1, 3, 1, 2, -2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 6)]
    )
    def test_short_stream_near_pattern_one_insertion_at_start_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_short, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [[4, -2, 3, 1, 2, -2, -1, 5, -7, 5, 2]], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 0, 11)]
    )
    def test_long_stream_near_pattern_one_insertion_at_start_matches_full(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_long, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.parametrize("stream_interval_matcher", [test_stream_intervals_raw], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(1, True, 1, 15)]
    )
    def test_stream_equal_to_pattern(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_raw, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.xfail
    @pytest.mark.parametrize("stream_interval_matcher", [test_stream_intervals_raw], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(0, True, 1, 15)]
    )
    def test_stream_equal_to_pattern_with_leading_rest_lstrips_rests(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_raw, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.xfail
    @pytest.mark.parametrize("stream_interval_matcher", [test_stream_intervals_raw], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(22, True, 28, 41)]
    )
    def test_stream_equal_to_pattern_with_padding_and_rests_both_sides_strips_rests(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_raw, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )

    @pytest.mark.xfail
    @pytest.mark.parametrize("stream_interval_matcher", [test_stream_intervals_raw], indirect=True)
    @pytest.mark.parametrize(
        "stream_start, expected_found, expected_match_start, expected_match_end", [(97, True, 97, 111)]
    )
    def test_stream_equal_to_pattern_with_two_patterns_matches_first(
        self,
        stream_interval_matcher: StreamIntervalMatcher,
        stream_start,
        expected_found,
        expected_match_start,
        expected_match_end,
    ):
        actual_found, actual_match_start, actual_match_end = stream_interval_matcher.try_match_next(
            test_pattern_intervals_raw, stream_start
        )
        assert (actual_found, actual_match_start, actual_match_end) == (
            expected_found,
            expected_match_start,
            expected_match_end,
        )
