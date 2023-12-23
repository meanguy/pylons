import asyncio
import functools
import time
from collections.abc import Awaitable, Callable
from datetime import timedelta

from pylons.retry._backoff import BackoffStrategy, ExponentialBackoffStrategy, LinearBackoffStrategy
from pylons.retry._retry import CatchableExceptionRetryStrategy, MaxTriesRetryStrategy, RetryStrategy
from pylons.typing import Params, Typename


def linear_backoff(delay: timedelta) -> BackoffStrategy:
    return LinearBackoffStrategy(delay)


def exponential_backoff(delay: timedelta, factor: float = 2) -> BackoffStrategy:
    return ExponentialBackoffStrategy(delay, factor)


def max_retries(tries: int) -> RetryStrategy:
    return MaxTriesRetryStrategy(tries)


def catch_exception(tries: int, exceptions: type[Exception] | tuple[type[Exception], ...]) -> RetryStrategy:
    return CatchableExceptionRetryStrategy(tries, exceptions)


def retryable(
    *,
    retry_strategy: RetryStrategy = max_retries(3),
    backoff_strategy: BackoffStrategy = linear_backoff(timedelta()),
) -> Callable[[Callable[Params, Typename]], Callable[Params, Typename]]:
    def decorator(fn_: Callable[Params, Typename]) -> Callable[Params, Typename]:
        @functools.wraps(fn_)
        def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Typename:
            tries = 0
            while True:
                try:
                    return fn_(*args, **kwargs)
                except Exception as e:
                    if not retry_strategy(tries, e):
                        raise
                    tries += 1

                    time.sleep(backoff_strategy(tries, e).total_seconds())

        return wrapper

    return decorator


def retryable_coroutine(
    *,
    retry_strategy: RetryStrategy = max_retries(3),
    backoff_strategy: BackoffStrategy = linear_backoff(timedelta()),
) -> Callable[[Callable[Params, Awaitable[Typename]]], Callable[Params, Awaitable[Typename]]]:
    def decorator(coro_: Callable[Params, Awaitable[Typename]]) -> Callable[Params, Awaitable[Typename]]:
        @functools.wraps(coro_)
        async def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Typename:
            tries = 0
            while True:
                try:
                    return await coro_(*args, **kwargs)
                except Exception as e:
                    if not retry_strategy(tries, e):
                        raise
                    tries += 1

                    await asyncio.sleep(backoff_strategy(tries, e).total_seconds())

        return wrapper

    return decorator
