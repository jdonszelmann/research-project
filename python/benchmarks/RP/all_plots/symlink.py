import pathlib
import os

this_dir = pathlib.Path(__file__).parent.absolute()


if __name__ == '__main__':
    dirs = []
    for i in this_dir.parent.iterdir():
        if i.is_dir() and i.name.endswith("maps"):
            dirs.append(i)

    for d in dirs:
        for file in d.iterdir():
            if file.name.endswith(".eps") or file.name.endswith(".png"):
                os.symlink(str(file), this_dir / file.name)