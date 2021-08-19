import pathlib
from python.benchmarks.parse_map import MapParser

this_dir = pathlib.Path(__file__).parent.absolute()


def three_neighbour_squares(grid: list[list[int]]) -> int:
    num = 0

    for y, row in enumerate(grid):
        for x, i in enumerate(row):
            neighbours = 0

            if x > 0 and grid[y][x-1] == 0:
                neighbours += 1
            if y > 0 and grid[y-1][x] == 0:
                neighbours += 1
            if y < len(grid) - 1 and grid[y+1][x] == 0:
                neighbours += 1
            if x < len(row) - 1 and grid[y][x+1] == 0:
                neighbours += 1

            if neighbours >= 3:
                num += 1
    return num

if __name__ == '__main__':
    results_prefix = str(this_dir)

    dirs = []
    for i in this_dir.parent.iterdir():
        if i.is_dir() and i.name.endswith("maps"):
            dirs.append(i)

    for d in dirs:
        with open(f"{results_prefix}/{d.name}.results", "w") as f:
            for dir in d.iterdir():
                if dir.is_dir():
                    numbers = []
                    num_ok = 0
                    for file in dir.iterdir():
                        if file.name.endswith(".map"):
                            p = MapParser(this_dir).parse_map(str(file))

                            num_three_neighbour_squares = three_neighbour_squares(p.grid)
                            numbers.append(num_three_neighbour_squares)

                            if num_three_neighbour_squares >= len(p.starts):
                                num_ok += 1
                            else:
                                print(f"error (possibly unsolvable: {file})")

                    f.write(f"{len(p.starts)}: {numbers} : {num_ok / len(numbers)}\n")