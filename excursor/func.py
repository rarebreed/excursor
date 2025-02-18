
from abc import abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Callable, Coroutine, Iterable, Protocol


class Functor[T](Protocol):

    @abstractmethod
    def map[R](self, fun: Callable[[T], R]) -> "Functor[R]":
        ...


@dataclass
class Maybe[T](Functor[T]):
    inner: T | None

    def map[R](self, fun: Callable[[T], R | None]) -> "Maybe[R]":
        match self.inner:
            case None:
                return Maybe(inner=None)
            case _:
                return Maybe(inner=fun(self.inner))

    def flat_map[R](self, fun: Callable[[T], "Maybe[R]"]) -> "Maybe[R]":
        match self.inner:
            case None:
                return Maybe(None)
            case inner:
                return fun(inner)

    def map_async[R](self, fn: Callable[[T], Coroutine[None, None, R | None]]) -> "Maybe[R]":
        match self.inner:
            case None:
                return Maybe(inner=None)
            case _:
                with asyncio.Runner() as runner:
                    return Maybe(inner=runner.run(fn(self.inner)))

    def flat_map_async[R](self, fn: Callable[[T], Coroutine[None, None, "Maybe[R]"]]) -> "Maybe[R]":
        """"""
        match self.inner:
            case None:
                return Maybe(None)
            case inner:
                # In order to figure out what the inner Maybe type is, we need to await
                with asyncio.Runner() as runner:
                    return runner.run(fn(inner))

    def do(self, fn: Callable[[T], T]) -> "Maybe[T]":
        match self.inner:
            case None:
                return Maybe(inner=None)
            case arg:
                self.inner = fn(arg)
                return self


@dataclass
class Iter[T](Functor[T]):
    inner: Iterable[T]
    # g: Generator[T, Any, None] = field(init=False, repr=False)

    def __post_init__(self):
        self.inner = (item for item in self.inner)

    def map[R](self, fun: Callable[[T], R]) -> "Iter[R]":
        return Iter(inner=(fun(x) for x in self.inner))

    def take(self, num: int):
        if num < 1:
            raise Exception("num arg must be >= 1")
        return Iter(inner=(i for ind, i in enumerate(self.inner) if ind < num))


print(f"{__name__}")

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
