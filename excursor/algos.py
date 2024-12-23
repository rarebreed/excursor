# Exercises for algorithms
#
# Recusrsion:
# - count items in a list
from random import randint


def count(arr: list, tot: int = 0) -> int:
    if len(arr) == 0:
        return tot
    else:
        tot += 1
        return count(arr[1:], tot)


def max(arr: list[int], m: int | None = None) -> int | None:
    if len(arr) == 0:
        return m
    else:
        head, *tail = arr
        if m is None:
            m = head
        elif head > m:
            m = head
        return max(tail, m)


def partition(arr: list[int], pivot: int) -> tuple[list[int], int, list[int]]:
    p_val = arr.pop(pivot)
    print(f"{p_val=}")
    lesser: list[int] = []
    sz = len(arr)
    for i in range(sz - 1, -1, -1):
        if arr[i] < p_val:
            lesser.append(arr.pop(i))
    print(f"{lesser=} greater={arr}")
    return lesser, p_val, arr


def qs(arr: list[int]):
    # We have two base cases.  If we have 2 elements, sort them trivially
    if len(arr) == 2:
        if arr[0] > arr[1]:
            arr[1], arr[0] = arr[0], arr[1]
        return arr
    # if we have o or 1 element, they are already sorted
    elif len(arr) < 2:
        return arr
    # now we divide up the problem (divide)
    else:
        pivot = randint(0, len(arr) - 1)
        l_arr, p, r_arr = partition(arr, pivot)
        # and conquer
        return qs(l_arr) + [p] + qs(r_arr)
