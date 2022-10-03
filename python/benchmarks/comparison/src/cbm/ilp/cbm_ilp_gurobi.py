from typing import Optional

import gurobipy as gp

_env: Optional[gp.Env] = None


def get_env() -> gp.Env:
    global _env
    if _env is None:
        _env = gp.Env(empty=True)
        _env.setParam("LogToConsole", 0)
        _env.setParam("Threads", 1)
        _env.setParam("TimeLimit", 120)
        _env.start()

    return _env
