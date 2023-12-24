import asyncio
import functools
import time
from collections.abc import Awaitable, Callable
from typing import Any

from pylons.retry._backoff import BackoffStrategy
from pylons.retry._retry import RetryStrategy


class Retryable:
    def __init__(self, retry_strategy: RetryStrategy, backoff_strategy: BackoffStrategy):
        self._retry_strategy = retry_strategy
        self._backoff_strategy = backoff_strategy

    def __call__(self, fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            tries = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if not self._retry_strategy(tries, e):
                        raise
                    tries += 1

                    time.sleep(self._backoff_strategy(tries, e).total_seconds())

        return wrapper


class RetryableCoroutine:
    def __init__(self, retry_strategy: RetryStrategy, backoff_strategy: BackoffStrategy):
        self._retry_strategy = retry_strategy
        self._backoff_strategy = backoff_strategy

    def __call__(self, coro_: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        @functools.wraps(coro_)
        async def wrapper(*args: Any, **kwargs: Any) -> Awaitable:
            tries = 0
            while True:
                try:
                    return await coro_(*args, **kwargs)
                except Exception as e:
                    if not self._retry_strategy(tries, e):
                        raise
                    tries += 1

                    await asyncio.sleep(self._backoff_strategy(tries, e).total_seconds())

        return wrapper
