# -*- coding: utf-8 -*-
"""
صف مزدوج (Deque) مع دعم الحد الأقصى للطول.
يُستخدم لإدارة المحادثة والذاكرة في مساعد RAG.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, Iterable, Iterator, Optional


class DequeInterface:
    """صف مزدوج (Double-Ended Queue) مع واجهة برمجية غنية."""

    def __init__(self, maxlen: Optional[int] = None) -> None:
        self._data: Deque[Any] = deque(maxlen=maxlen)
        self._history: list[str] = []

    def push_front(self, item: Any) -> None:
        self._data.appendleft(item)
        self._history.append(f"push_front({item!r})")

    def push_back(self, item: Any) -> None:
        self._data.append(item)
        self._history.append(f"push_back({item!r})")

    def pop_front(self) -> Any:
        if self.is_empty():
            raise IndexError("الصف فارغ، لا يمكن الحذف من الأمام.")
        item = self._data.popleft()
        self._history.append(f"pop_front() -> {item!r}")
        return item

    def pop_back(self) -> Any:
        if self.is_empty():
            raise IndexError("الصف فارغ، لا يمكن الحذف من الخلف.")
        item = self._data.pop()
        self._history.append(f"pop_back() -> {item!r}")
        return item

    def peek_front(self) -> Any:
        if self.is_empty():
            raise IndexError("الصف فارغ.")
        return self._data[0]

    def peek_back(self) -> Any:
        if self.is_empty():
            raise IndexError("الصف فارغ.")
        return self._data[-1]

    def size(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def is_full(self) -> bool:
        if self._data.maxlen is None:
            return False
        return len(self._data) >= self._data.maxlen

    def clear(self) -> None:
        self._data.clear()
        self._history.append("clear()")

    def to_list(self) -> list[Any]:
        return list(self._data)

    @classmethod
    def from_list(
        cls, items: Iterable[Any], maxlen: Optional[int] = None
    ) -> DequeInterface:
        instance = cls(maxlen=maxlen)
        for item in items:
            instance.push_back(item)
        return instance

    def set_maxlen(self, maxlen: Optional[int]) -> None:
        new_data = deque(self._data, maxlen=maxlen)
        self._data = new_data
        self._history.append(f"set_maxlen({maxlen!r})")

    def maxlen(self) -> Optional[int]:
        return self._data.maxlen

    def rotate(self, n: int = 1) -> None:
        self._data.rotate(n)
        self._history.append(f"rotate({n})")

    def reverse(self) -> None:
        self._data.reverse()
        self._history.append("reverse()")

    def count(self, item: Any) -> int:
        return self._data.count(item)

    def remove(self, item: Any) -> None:
        self._data.remove(item)
        self._history.append(f"remove({item!r})")

    def extend_front(self, items: Iterable[Any]) -> None:
        for item in reversed(list(items)):
            self.push_front(item)

    def extend_back(self, items: Iterable[Any]) -> None:
        for item in items:
            self.push_back(item)

    def history(self) -> list[str]:
        return list(self._history)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __reversed__(self) -> Iterator[Any]:
        return reversed(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, item: Any) -> bool:
        return item in self._data

    def __getitem__(self, index: int) -> Any:
        return self._data[index]

    def __bool__(self) -> bool:
        return len(self._data) > 0

    def __repr__(self) -> str:
        return (
            f"DequeInterface({list(self._data)}, maxlen={self._data.maxlen})"
        )

    def __str__(self) -> str:
        items = " <-> ".join(repr(item) for item in self._data)
        return f"DequeInterface([{items}])"