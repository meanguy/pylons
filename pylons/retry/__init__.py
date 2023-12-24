from collections.abc import Callable
from datetime import timedelta

from pylons.retry._backoff import BackoffStrategy, ExponentialBackoffStrategy, LinearBackoffStrategy
from pylons.retry._retry import CatchableExceptionRetryStrategy, MaxTriesRetryStrategy, RetryStrategy
from pylons.retry._retryable import Retryable, RetryableCoroutine

__all__ = [
    "BackoffStrategy",
    "RetryStrategy",
    "catch_exception",
    "exponential_backoff",
    "linear_backoff",
    "max_retries",
    "retryable",
    "retryable_coroutine",
]


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
) -> Callable:
    return Retryable(retry_strategy, backoff_strategy)


def retryable_coroutine(
    *,
    retry_strategy: RetryStrategy = max_retries(3),
    backoff_strategy: BackoffStrategy = linear_backoff(timedelta()),
) -> Callable:
    return RetryableCoroutine(retry_strategy, backoff_strategy)
