from typing import Any


class Box:
    def __init__(self, value: Any):
        self.value = value

    def __getattr__(self, key: str) -> Any:
        return getattr(self.value, key)
