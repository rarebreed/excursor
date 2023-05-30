
from excursor.func import Maybe


def test_maybe():
    fun = Maybe(10)
    fun2 = fun.map(lambda x: x * 2).map(lambda y: y + 5)
    fun3 = fun2.map(lambda x: None).map(lambda y: y + 10)

    print(fun3.inner)
