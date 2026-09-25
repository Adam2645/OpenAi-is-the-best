from __future__ import annotations

import threading
from typing import Generic, TypeVar

T = TypeVar("T")


# najnowsza wartość przekazywana między wątkami bez kolejki, bo pętla ruchu potrzebuje tylko aktualnego odczytu
class LatestValue(Generic[T]):
    # wartość początkowa pozwala czytać przed pierwszym zapisem bez sprawdzania wyjątków
    def __init__(self, initial: T | None = None) -> None:
        self._value = initial
        self._lock = threading.Lock()

    # zapis z wątku percepcji lub audio podmienia wartość atomowo
    def set(self, value: T) -> None:
        with self._lock:
            self._value = value

    # odczyt zwraca ostatnią wartość bez blokowania pętli sterowania na dłużej
    def get(self) -> T | None:
        with self._lock:
            return self._value
