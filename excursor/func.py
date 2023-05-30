
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, Self, TypeAlias, TypeVar


T = TypeVar("T")
R = TypeVar("R")

MaybeT: TypeAlias = T | None


class Functor(ABC, Generic[T]):
    inner: T

    @abstractmethod
    def map(self, fun: Callable[[T], R]) -> "Functor[R]":
        ...


@dataclass
class Maybe(Generic[T], Functor[T]):
    inner: T | None

    def map(self, fun: Callable[[T], R]) -> "Maybe[R]":
        match self.inner:
            case None:
                return Maybe(None)
            case inner:
                return Maybe(inner=fun(inner))


class Iter(Generic[T], Functor[T]):
    inner: Iterable[T]

    def map(self, fun: Callable[[T], R]) -> "Iter[R]":
        return Iter(inner=[fun(x) for x in self.inner])

    def take(self, num: int):
        ...


if __name__ == "__main__":
    fun = Maybe(10)
    fun2 = fun.map(lambda x: x * 2).map(lambda y: y + 5)
    fun3 = fun2.map(lambda x: None).map(lambda y: y + 10)

    print(fun2.inner)
    print(fun3.inner)
