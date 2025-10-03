"""Minimal subset of cachetools providing :class:`LRUCache` for offline environments.

This lightweight implementation is sufficient for python-telegram-bot's
CallbackDataCache usage within the FlyzexBot test environment where installing
the optional dependency is not possible due to network restrictions.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Iterable, Iterator, MutableMapping, Tuple, TypeVar

KT = TypeVar("KT")
VT = TypeVar("VT")


class LRUCache(MutableMapping[KT, VT]):
    """A simple least-recently-used cache compatible with cachetools' API."""

    def __init__(self, maxsize: int = 128) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        self.maxsize = maxsize
        self._store: "OrderedDict[KT, VT]" = OrderedDict()

    def __getitem__(self, key: KT) -> VT:
        value = self._store[key]
        self._store.move_to_end(key)
        return value

    def __setitem__(self, key: KT, value: VT) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self.maxsize:
            self._store.popitem(last=False)

    def __delitem__(self, key: KT) -> None:
        del self._store[key]

    def __iter__(self) -> Iterator[KT]:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def clear(self) -> None:
        self._store.clear()

    def items(self) -> Iterable[Tuple[KT, VT]]:
        return self._store.items()

    def values(self) -> Iterable[VT]:
        return self._store.values()

    def pop(self, key: KT, default: VT | None = None) -> VT:
        if key in self._store:
            value = self._store.pop(key)
            return value
        if default is not None:
            return default
        raise KeyError(key)

    def popitem(self) -> Tuple[KT, VT]:
        return self._store.popitem()

    def get(self, key: KT, default: VT | None = None) -> VT | None:
        if key in self._store:
            return self[key]
        return default

    def __repr__(self) -> str:
        items = list(self._store.items())
        return f"LRUCache(maxsize={self.maxsize}, items={items})"


__all__ = ["LRUCache"]
