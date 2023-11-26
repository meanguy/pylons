import functools
import time
from datetime import timedelta
from typing import Callable

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
    fn: Callable[Params, Typename] | None = None,
    *,
    retry_strategy: RetryStrategy = max_retries(3),
    backoff_strategy: BackoffStrategy = linear_backoff(timedelta()),
) -> Callable[Params, Typename] | Callable[[Callable[Params, Typename]], Callable[Params, Typename]]:
    def decorator(fn: Callable[Params, Typename]) -> Callable[Params, Typename]:
        @functools.wraps(fn)
        def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Typename:
            tries = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if not retry_strategy(tries, e):
                        raise
                    tries += 1

                    time.sleep(backoff_strategy(tries, e).total_seconds())

        return wrapper

    if fn is None:
        return decorator
    else:
        return decorator(fn)
