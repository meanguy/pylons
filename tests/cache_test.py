from datetime import timedelta
from typing import Callable

import pytest

from pylons.cache import cache_for


class Box[T]:
    def __init__(self, value: T):
        self.value = value


def n_calls_fn_noargs() -> tuple[Callable[[int], int], Box[int]]:
    box = Box(0)

    @cache_for()
    def fn(i: int = 0) -> int:
        nonlocal box

        box.value += 1

        return i

    return fn, box


def n_calls_fn(*args, **kwargs) -> tuple[Callable[[int], int], Box[int]]:
    box = Box(0)

    @cache_for(*args, **kwargs)
    def fn(i: int = 0) -> int:
        nonlocal box

        box.value += 1

        return i

    return fn, box


@pytest.mark.parametrize(
    ("fn", "box", "args", "n_calls_expected"),
    [
        (*n_calls_fn_noargs(), [1], 1),
        (*n_calls_fn_noargs(), [1, 1], 1),
        (*n_calls_fn_noargs(), [1, 2], 2),
        (*n_calls_fn_noargs(), [1, 2, 2], 2),
        (*n_calls_fn_noargs(), [1, 2, 1], 2),
        (*n_calls_fn_noargs(), [1, 2, 3], 3),
        (*n_calls_fn(), [1], 1),
        (*n_calls_fn(), [1, 1], 1),
        (*n_calls_fn(), [1, 2], 2),
        (*n_calls_fn(), [1, 2, 2], 2),
        (*n_calls_fn(), [1, 2, 1], 2),
        (*n_calls_fn(), [1, 2, 3], 3),
        (*n_calls_fn(expires=timedelta(microseconds=-1)), [1], 1),
        (*n_calls_fn(expires=timedelta(microseconds=-1)), [1, 1], 2),
        (*n_calls_fn(expires=timedelta(microseconds=-1)), [1, 2], 2),
        (*n_calls_fn(expires=timedelta(microseconds=-1)), [1, 2, 1], 3),
        (*n_calls_fn(expires=timedelta(days=1)), [1], 1),
        (*n_calls_fn(expires=timedelta(days=1)), [1, 1], 1),
        (*n_calls_fn(expires=timedelta(days=1)), [1, 2], 2),
        (*n_calls_fn(expires=timedelta(days=1)), [1, 2, 1], 2),
        (*n_calls_fn(max_size=1), [1], 1),
        (*n_calls_fn(max_size=1), [1, 2], 2),
        (*n_calls_fn(max_size=1), [1, 1], 2),
    ],
)
def test_cache_for(fn: Callable[[int], int], box: Box[int], args: list[int], n_calls_expected: int):
    for arg in args:
        fn(arg)

    assert n_calls_expected == box.value


def test_cache_for_with_mixed_args_kwargs():
    n_calls = 0

    @cache_for()
    def fn(f: float, i: int = 0) -> int:
        nonlocal n_calls

        n_calls += 1

        return i

    assert fn(1.0) == 0
    assert fn(1.0) == 0
    assert n_calls == 1

    assert fn(1.0, 1) == 1
    assert fn(1.0, 1) == 1
    assert n_calls == 2


def test_cache_for_with_unhashable_types():
    n_calls = 0

    @cache_for()
    def fn(l: list[int], t: tuple[int, ...], d: dict[str, int]) -> int:
        nonlocal n_calls

        n_calls += 1

        return sum(l) + sum(t) + sum(d.values())

    with pytest.raises(TypeError):
        fn([1, 2, 3], (4, 5, 6), {"a": 7, "b": 8, "c": 9})
        fn([1, 2, 3], (4, 5, 6), {"a": 7, "b": 8, "c": 9})
