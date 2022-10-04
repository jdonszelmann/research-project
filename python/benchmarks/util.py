import pathlib
from typing import Optional

def read_from_file(filename: pathlib.Path, wanted_num_agents: int) -> list[Optional[float]]:
    with open(filename, "r") as f:
        for l in [l.strip() for l in f.readlines() if l.strip() != ""]:
            before, after = l.split(":")
            after_list = eval(after)
            num_agents = int(before)
            if num_agents == wanted_num_agents:
                return after_list

    raise Exception("number of agents not found in file")


def output_data(file: pathlib.Path, data: dict[int, list[float]]):
    with open(file, "w") as f:
        for i, r in sorted([(a, b) for a, b in data.items()], key=lambda x: x[0]):
            f.write(f"{i}: {r}\n")
