
from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Callable, Coroutine, Generic, Iterable, Self, TypeAlias, TypeVar


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

    def map(self, fun: Callable[[T], R | None]) -> "Maybe[R]":
        match self.inner:
            case None:
                return Maybe(inner=None)
            case _:
                result = fun(self.inner)
                match result:
                    case None:
                        return Maybe(None)
                    case res:
                        return Maybe(inner=res)

    def flat_map(self, fun: Callable[[T], "Maybe[R]"]) -> "Maybe[R]":
        match self.inner:
            case None:
                return Maybe(None)
            case inner:
                result = fun(inner)
                match result:
                    case None:
                        return Maybe(inner=None)
                    case _:
                        return result

    def map_async(self, fn: Callable[[T], Coroutine[None, None, R]]) -> "Maybe[R]":
        match self.inner:
            case None:
                return Maybe(inner=None)
            case _:
                with asyncio.Runner() as runner:
                    result = runner.run(fn(self.inner))
                match result:
                    case None:
                        return Maybe(None)
                    case res:
                        return Maybe(inner=res)

    def flat_map_async(self, fn: Callable[[T], Coroutine[None, None, "Maybe[R]"]]) -> "Maybe[R]":
        """"""
        match self.inner:
            case None:
                return Maybe(None)
            case inner:
                # In order to figure out what the inner Maybe type is, we need to await
                with asyncio.Runner() as runner:
                    result = runner.run(fn(inner))
                match result:
                    case None:
                        maybe = Maybe(inner=None)
                        return maybe
                    case _:
                        return result

    def do(self, fn: Callable[[T], T]) -> Self:
        match self.inner:
            case None:
                return Maybe(inner=None)
            case arg:
                self.inner = fn(arg)
                return self


@dataclass
class Iter(Generic[T], Functor[T]):
    inner: Iterable[T]
    # g: Generator[T, Any, None] = field(init=False, repr=False)

    def __post_init__(self):
        self.inner = (item for item in self.inner)

    def map(self, fun: Callable[[T], R]) -> "Iter[R]":
        return Iter(inner=(fun(x) for x in self.inner))

    def take(self, num: int):
        if num < 1:
            raise Exception("num arg must be >= 1")
        return Iter(inner=(i for ind, i in enumerate(self.inner) if ind < num))


if __name__ == "__main__":
    def doubler(x: int) -> int | None:
        if x < 10:
            return None
        else:
            return 2 * x

    fun = Maybe(3)
    fun2 = fun.map(lambda x: x * 2).map(lambda y: y + 5)
    fun3 = fun2.map(doubler).map(lambda y: y + 10)

    print(fun2.inner)
    print(fun3.inner)
