from datetime import timedelta
from typing import Protocol


class BackoffStrategy(Protocol):
    """
    BackoffStrategy is a callable that takes the number of tries and the exception raised by a `retryable`
    function and returns a timedelta indicating how long to wait before retrying.
    """

    def __call__(self, tries: int, exception: Exception) -> timedelta:
        ...


class LinearBackoffStrategy:
    def __init__(self, delay: timedelta):
        self.delay = delay

    def __call__(self, tries: int, exception: Exception) -> timedelta:
        return self.delay * tries


class ExponentialBackoffStrategy:
    def __init__(self, delay: timedelta, factor: float):
        self.delay = delay
        self.factor = factor

    def __call__(self, tries: int, exception: Exception) -> timedelta:
        if tries == 0:
            return timedelta()
        return self.delay * self.factor ** (tries - 1)
