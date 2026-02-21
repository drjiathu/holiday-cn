from pathlib import Path

__dirname__: Path = Path(__file__).parents[1].absolute()


def workspace_path(*other) -> Path:
    return __dirname__.joinpath(*other)


def dataspace_path(*other) -> Path:
    return __dirname__.joinpath("data", *other)
