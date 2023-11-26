from typing import Protocol


class RetryStrategy(Protocol):
    """
    RetryStrategy is a callable that takes the number of tries and the exception raised by a `retryable`
    function and returns a boolean indicating whether the function should be retried.
    """

    def __call__(self, tries: int, exception: Exception) -> bool:
        ...


class MaxTriesRetryStrategy:
    def __init__(self, tries: int):
        self.tries = tries

    def __call__(self, tries: int, exception: Exception) -> bool:
        return tries < self.tries


class CatchableExceptionRetryStrategy:
    def __init__(self, tries: int, exceptions: type[Exception] | tuple[type[Exception], ...] = (Exception,)):
        self.exceptions = exceptions
        self.tries = tries

    def __call__(self, tries: int, exception: Exception) -> bool:
        return tries < self.tries and (
            isinstance(exception, self.exceptions) or issubclass(type(exception), self.exceptions)
        )
