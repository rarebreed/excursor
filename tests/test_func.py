
from src.excursor.func import Maybe


def test_maybe():
    fun = Maybe(10)
    fun2: Maybe[int] = fun.map(lambda x: x * 2).map(lambda y: y + 5)

    def add_10(y: int):
        return y + 10

    def null(x: int):
        return None

    fun3 = fun2.map(null).map(add_10)  # type: ignore

    print(fun3.inner)
