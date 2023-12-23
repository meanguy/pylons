import pytest

from pylons import retry


@pytest.mark.parametrize(
    ("max_tries", "catchable_exceptions", "tries", "thrown_exception", "expected"),
    [
        [3, (Exception), 0, Exception(), True],
        [3, (Exception), 1, Exception(), True],
        [3, (Exception), 2, Exception(), True],
        [3, (Exception), 3, Exception(), False],
        [3, (Exception), 0, ValueError(), True],
        [3, (ValueError), 0, ValueError(), True],
        [3, (ValueError), 3, ValueError(), False],
        [3, (ValueError), 0, Exception(), False],
        [3, (ValueError, TypeError), 0, ValueError(), True],
        [3, (ValueError, TypeError), 3, ValueError(), False],
        [3, (ValueError, TypeError), 0, TypeError(), True],
        [3, (ValueError, TypeError), 3, TypeError(), False],
        [3, (ValueError, TypeError), 0, Exception(), False],
        [3, (ValueError, TypeError), 0, KeyError(), False],
        [5, (ValueError), 0, ValueError(), True],
        [5, (ValueError), 3, ValueError(), True],
        [5, (ValueError), 6, ValueError(), False],
    ],
)
def test_catchable_exception_retry_strategy(
    max_tries, catchable_exceptions, tries, thrown_exception, expected
):
    strategy = retry.catch_exception(max_tries, catchable_exceptions)
    assert strategy(tries, thrown_exception) == expected


@pytest.mark.parametrize(
    ("max_tries", "tries", "expected"),
    [
        [3, 0, True],
        [3, 1, True],
        [3, 2, True],
        [3, 3, False],
        [5, 0, True],
        [5, 3, True],
        [5, 6, False],
    ],
)
def test_max_tries_retry_strategy(max_tries, tries, expected):
    strategy = retry.max_retries(max_tries)
    assert strategy(tries, Exception()) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("max_tries", "tries", "expected"),
    [
        [3, 0, True],
        [3, 1, True],
        [3, 2, True],
        [3, 3, False],
        [5, 0, True],
        [5, 3, True],
        [5, 6, False],
    ],
)
async def test_max_tries_retry_strategy_async(max_tries, tries, expected):
    strategy = retry.max_retries(max_tries)
    assert strategy(tries, Exception()) == expected


@pytest.mark.asyncio
async def test_retryable_coroutine_no_exceptions():
    @retry.retryable_coroutine()
    async def fn():
        return 1

    assert (await fn()) == 1


@pytest.mark.asyncio
async def test_retryable_coroutine_no_exceptions_with_args():
    @retry.retryable_coroutine()
    async def fn(a, *, b):
        return a + b

    assert (await fn(1, b=2)) == 3


@pytest.mark.asyncio
async def test_retryable_coroutine_thrown_exception():
    @retry.retryable_coroutine()
    async def fn():
        raise Exception()

    with pytest.raises(Exception):
        await fn()


@pytest.mark.asyncio
async def test_retryable_coroutine_throw_exception_eventual_success():
    n_calls = 0

    @retry.retryable_coroutine(retry_strategy=retry.max_retries(5))
    async def fn():
        nonlocal n_calls

        n_calls += 1

        if n_calls < 3:
            raise Exception()

        return n_calls

    assert (await fn()) == 3
