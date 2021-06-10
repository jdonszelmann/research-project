import sys


def get_src_modules():
    modules = sys.modules
    srcs = []
    for i in sys.modules:
        if "src" in i:
            srcs.append(i)
    for i in srcs:
        del sys.modules[i]

    return modules


def solve_with_modules(modules, fn):
    old = sys.modules
    sys.modules = modules
    res = fn()
    sys.modules = old
    return res
