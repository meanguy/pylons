from datetime import timedelta

import pytest

from pylons import retry


@pytest.mark.parametrize(
    ("delay", "tries", "expected"),
    [
        [timedelta(seconds=1), 0, timedelta(seconds=0)],
        [timedelta(seconds=1), 1, timedelta(seconds=1)],
        [timedelta(seconds=1), 2, timedelta(seconds=2)],
        [timedelta(seconds=1), 3, timedelta(seconds=3)],
        [timedelta(seconds=1), 4, timedelta(seconds=4)],
        [timedelta(seconds=1), 5, timedelta(seconds=5)],
        [timedelta(seconds=5), 0, timedelta(seconds=0)],
        [timedelta(seconds=5), 1, timedelta(seconds=5)],
        [timedelta(seconds=5), 2, timedelta(seconds=10)],
        [timedelta(seconds=5), 3, timedelta(seconds=15)],
        [timedelta(seconds=5), 4, timedelta(seconds=20)],
        [timedelta(seconds=5), 5, timedelta(seconds=25)],
    ],
)
def test_linear_backoff_strategy(delay, tries, expected):
    strategy = retry.linear_backoff(delay)
    assert strategy(tries, Exception()) == expected


@pytest.mark.parametrize(
    ("delay", "factor", "tries", "expected"),
    [
        [timedelta(seconds=2), 2, 0, timedelta(seconds=0)],
        [timedelta(seconds=2), 2, 1, timedelta(seconds=2)],
        [timedelta(seconds=2), 2, 2, timedelta(seconds=4)],
        [timedelta(seconds=2), 2, 3, timedelta(seconds=8)],
        [timedelta(seconds=2), 2, 4, timedelta(seconds=16)],
        [timedelta(seconds=2), 2, 5, timedelta(seconds=32)],
        [timedelta(seconds=1), 1.5, 0, timedelta(seconds=0)],
        [timedelta(seconds=1), 1.5, 1, timedelta(seconds=1)],
        [timedelta(seconds=1), 1.5, 2, timedelta(seconds=1.5)],
        [timedelta(seconds=1), 1.5, 3, timedelta(seconds=2.25)],
        [timedelta(seconds=1), 1.5, 4, timedelta(seconds=3.375)],
    ],
)
def test_exponential_backoff_strategy(delay, factor, tries, expected):
    strategy = retry.exponential_backoff(delay, factor)
    assert strategy(tries, Exception()) == expected
