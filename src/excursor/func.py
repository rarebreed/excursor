
from abc import abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Iterable, Protocol, Self


class Functor[T](Protocol):

    @abstractmethod
    def map[R](self, fun: Callable[[T], R]) -> "Functor[R]":
        ...


class Applicative[T](Functor[T], Protocol):

    @classmethod
    def lift(cls, a: T) -> Self:
        ...


class Monad[T](Functor[T], Protocol):

    # this took a bit of playing with to figure out
    # @abstractmethod
    def flat_map[R, M: "Monad"](self, fun: Callable[[T], M]) -> M:
        ...


@dataclass
class Maybe[T](Monad[T]):
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

    def take(self, until: int | Callable[[T], bool]) -> "Iter[T]":
        """Includes items from until

        If until is a callable, it will include elements up until it gets a False result.  As soon as it gets a single
        False, no other elements will be in the returned Iter.  It is the opposite of drop

        Parameters
        ----------
        until : int | Callable[[T], bool]
            _description_

        Returns
        -------
        Iter[T]
            _description_

        Raises
        ------
        Exception
            if until is less than 1
        """
        match until:
            case int():
                if until < 1:
                    raise Exception("num arg must be >= 1")
                return Iter(inner=(i for ind, i in enumerate(self.inner) if ind < until))
            case fn:
                def gen():
                    for i in self.inner:
                        if not fn(i):
                            yield i
                        else:
                            break
                return Iter(inner=gen())

    def drop(self, until: int | Callable[[T], bool]) -> "Iter[T]":
        """Excludes elements while until returns True.

        If until is a callable, the first time it gets a False result, it will always include any other items in inner.
        It is the opposite of take.

        Parameters
        ----------
        until : int | Callable[[T], bool]
            if an int, up to that many elements excluded. If a callable, stops dropping when evals to False

        Returns
        -------
        Iter[T]
            _description_

        Raises
        ------
        Exception
            if until is negative
        """
        match until:
            case int():
                if until < 0:
                    raise Exception("can not drop negative amount of items")
                return Iter(inner=(x for i, x in enumerate(self.inner) if i >= until))
            case fn:
                def gen():
                    matched = True
                    for i in self.inner:
                        if matched:
                            matched = fn(i)
                        if not matched:
                            yield i
                return Iter(inner=gen())

    def collect[R](self, ret: Callable[[Iterable[Any]], R]) -> R:
        return ret(self.inner)

    def where(self, select: Callable[[T], bool]) -> Self:
        """Returns a new Iter, where each element returned True when passed to the select predicate

        Called a `filter` in other APIs, but filter sounds like you do NOT include the elements,

        Parameters
        ----------
        select : Callable[[T], bool]
            predicate function. If it retuens True, keep the item, else exclude it

        Returns
        -------
        Self
        """
        self.inner = (i for i in self.inner if select(i))
        return self


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
