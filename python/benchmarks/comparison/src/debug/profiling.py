from typing import TypeVar, Callable

import yappi

T = TypeVar("T")
R = TypeVar("R")


def profile(f: Callable[[T], R], *args) -> R:
    yappi.set_clock_type("cpu")
    yappi.start()
    v = f(*args)
    yappi.stop()

    yappi.get_func_stats().print_all()
    print("\n\n\n")

    yappi.clear_stats()

    return v
