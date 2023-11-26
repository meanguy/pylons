import functools
from datetime import datetime, timedelta
from threading import Lock
from typing import Callable, Hashable

from pylons.typing import Params, Typename


def cache_for(
    fn: Callable[Params, Typename] | None = None,
    *,
    expires: timedelta | None = None,
    max_size: int = 0,
) -> Callable[Params, Typename] | Callable[[Callable[Params, Typename]], Callable[Params, Typename]]:
    max_size = max(max_size, 0)
    cache_entries: dict[tuple[Hashable, ...], tuple[Typename, datetime]] = {}
    lock = Lock()

    def decorator(fn: Callable[Params, Typename]) -> Callable[Params, Typename]:
        @functools.wraps(fn)
        def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Typename:
            key = (
                args,
                tuple(sorted(kwargs.items())),
            )

            with lock:
                cached_keys = list(cache_entries.keys())
                if key in cached_keys:
                    entry = cache_entries[key]
                    entry_age = datetime.now() - entry[1]

                    if expires is not None and entry_age > expires:
                        del cache_entries[key]

                if max_size > 0 and len(cached_keys) >= max_size:
                    del cache_entries[cached_keys.pop(0)]

                if key not in cache_entries:
                    cache_entries[key] = fn(*args, **kwargs), datetime.now()

                return cache_entries[key][0]

        return wrapper

    if fn is None:
        return decorator
    else:
        return decorator(fn)
