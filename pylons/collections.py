from typing import Any


class Box[T]:
    def __init__(self, value: T):
        self.value = value

    def __getattr__(self, key: str) -> Any:
        return getattr(self.value, key)
