import pytest
import numpy as np
from algorithm.model.distance_metrics import DistanceMetrics
from unittest import mock
from typing import Final


BASE_PATH: Final[str] = "algorithm.model.distance_metrics"

dummy_rest_penalty_factor: Final[int] = 1
dummy_inversion_penalty_factor: Final[int] = 1


class TestDistanceMetrics:
    @pytest.fixture(scope="class")
    def mock_increment(self):
        return mock.MagicMock(side_effect=lambda x: x + 1)

    @pytest.fixture(scope="class")
    def distance_metrics(self):
        yield DistanceMetrics(dummy_rest_penalty_factor, dummy_inversion_penalty_factor)

    @pytest.mark.parametrize("memo", [(np.array([[1, 2, 3], [4, 5, 6]]))])
    @pytest.mark.parametrize(
        "x, y, i, j, expected_value",
        [
            (list(), [10, 11], 0, 1, 12),
            (list(), [-8, 11], 0, 1, 10),
            (list(), [None, 11], 1, 1, float("inf")),
        ],
    )
    def test_insertion_without_expansion(self, distance_metrics, memo, x, y, i, j, expected_value, mock_increment):
        assert expected_value == distance_metrics.insertion_without_expansion(memo, x, y, i, j, mock_increment)

    @pytest.mark.parametrize("memo", [(np.array([[1, 2, 3, 4], [5, 6, 7, 8]]))])
    @pytest.mark.parametrize(
        "x, y, i, j, expected_value",
        [
            ([5], [-10, 11, 12], 0, 1, float("inf")),
            ([5], [None, 11, 12], 0, 2, float("inf")),
            ([5], [-10, None, 12], 0, 2, float("inf")),
            ([5], [None, None, 12], 0, 2, float("inf")),
            ([None], [-10, 11, 12], 1, 2, float("inf")),
            ([7], [-10, 15, 12], 1, 2, 5),
        ],
    )
    def test_insertion_with_expansion(self, distance_metrics, memo, x, y, i, j, expected_value, mock_increment):
        assert expected_value == distance_metrics.insertion_with_expansion(memo, x, y, i, j, mock_increment)

    @pytest.mark.parametrize("memo", [(np.array([[1, 2, 3], [4, 5, 6]]))])
    @pytest.mark.parametrize(
        "x, y, i, j, expected_value",
        [
            ([10, 11], list(), 1, 0, 12),
            ([-8, 11], list(), 1, 0, 10),
            ([None, 11], list(), 1, 1, float("inf")),
        ],
    )
    def test_deletion_without_compression(self, distance_metrics, memo, x, y, i, j, expected_value, mock_increment):
        assert expected_value == distance_metrics.deletion_without_compression(memo, x, y, i, j, mock_increment)

    @pytest.mark.parametrize("memo", [(np.array([[1, 2], [3, 4], [5, 6], [7, 8]]))])
    @pytest.mark.parametrize(
        "x, y, i, j, expected_value",
        [
            ([-10, 11, 12], [5], 1, 0, float("inf")),
            ([None, 11, 12], [5], 2, 0, float("inf")),
            ([-10, None, 12], [5], 2, 0, float("inf")),
            ([None, None, 12], [5], 2, 0, float("inf")),
            ([-10, 11, 12], [None], 2, 1, float("inf")),
            ([-10, 15, 12], [7], 2, 1, 4),
        ],
    )
    def test_deletion_with_compression(self, distance_metrics, memo, x, y, i, j, expected_value, mock_increment):
        assert expected_value == distance_metrics.deletion_with_compression(memo, x, y, i, j, mock_increment)
