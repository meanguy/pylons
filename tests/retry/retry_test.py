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


def test_retryable_no_exceptions():
    @retry.retryable()
    def fn():
        return 1

    assert fn() == 1


def test_retryable_no_exceptions_with_args():
    @retry.retryable()
    def fn(a, *, b):
        return a + b

    assert fn(1, b=2) == 3


def test_retryable_thrown_exception():
    @retry.retryable()
    def fn():
        raise Exception()

    with pytest.raises(Exception):
        fn()


def test_retryable_throw_exception_eventual_success():
    n_calls = 0

    @retry.retryable(retry_strategy=retry.max_retries(5))
    def fn():
        nonlocal n_calls

        n_calls += 1

        if n_calls < 3:
            raise Exception()

        return n_calls

    assert fn() == 3


def test_retryable_object_method():
    class Foo:
        def __init__(self):
            self.n_calls = 0

        @retry.retryable()
        def fn(self):
            self.n_calls += 1
            if self.n_calls < 3:
                raise Exception()

            return self.n_calls

    foo = Foo()
    assert foo.fn() == 3


def test_retryable_class_method():
    class Foo:
        n_calls = 0

        @classmethod
        @retry.retryable()
        def fn(cls):
            cls.n_calls += 1
            if cls.n_calls < 3:
                raise Exception()

            return cls.n_calls

    assert Foo.fn() == 3


def test_retryable_static_method():
    class Foo:
        n_calls = 0

        @staticmethod
        @retry.retryable()
        def fn():
            Foo.n_calls += 1
            if Foo.n_calls < 3:
                raise Exception()

            return Foo.n_calls

    assert Foo.fn() == 3


@pytest.mark.asyncio
async def test_retryable_coroutine_no_exceptions():
    @retry.retryable_coroutine()
    async def fn():
        return 1

    assert (await fn()) == 1


@pytest.mark.asyncio
async def test_retryable_coroutine_no_exceptions_with_args():
    @retry.retryable_coroutine()
    async def fn(a: int, *, b: int):
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


@pytest.mark.asyncio
async def test_retryable_coroutine_object_method():
    class Foo:
        def __init__(self):
            self.n_calls = 0

        @retry.retryable_coroutine()
        async def fn(self):
            self.n_calls += 1
            if self.n_calls < 3:
                raise Exception()

            return self.n_calls

    foo = Foo()
    assert (await foo.fn()) == 3


@pytest.mark.asyncio
async def test_retryable_coroutine_class_method():
    class Foo:
        n_calls = 0

        @classmethod
        @retry.retryable_coroutine()
        async def fn(cls):
            cls.n_calls += 1
            if cls.n_calls < 3:
                raise Exception()

            return cls.n_calls

    assert (await Foo.fn()) == 3


@pytest.mark.asyncio
async def test_retryable_coroutine_static_method():
    class Foo:
        n_calls = 0

        @staticmethod
        @retry.retryable_coroutine()
        async def fn():
            Foo.n_calls += 1
            if Foo.n_calls < 3:
                raise Exception()

            return Foo.n_calls

    assert (await Foo.fn()) == 3
