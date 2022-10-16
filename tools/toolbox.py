import sys
import itertools
from pathlib import Path


def human_readable_size(object: object, decimal_places: int = 2) -> tuple[float, str]:
    """Get human readable size of any python object

    Uses `sys.getsizeof()` to get bytes
    Units are SI: 1000, not 1024

    Returns:
        tuple(size:float, units:str)
    """
    size = sys.getsizeof(object)
    for unit in ['B', 'kB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1000.0 or unit == 'PB':
            break
        size /= 1000.0
    return (f'{size:.{decimal_places}f}', unit)


def glob_multiple_patterns(path: Path, patterns: str | list[str]):
    patterns = [patterns] if isinstance(patterns, str) else patterns
    return list(itertools.chain.from_iterable(Path(path).glob(p) for p in patterns))


def tree(
    dir_path: Path,
    prefix: str = '',
    include_glob: str | list[str] = '**/*',
    exclude_glob: str | list[str] = None,
):
    """Create tree structure for path

    Args:
        dir_path (Path): _description_
        prefix (str, optional): _description_. Defaults to ''.
        include_glob (str, optional): _description_. Defaults to '*'.
        exclude_glob (_type_, optional): _description_. Defaults to None.

    Yields:
        _type_: _description_
    """

    # prefix components:
    SPACE = '    '
    BRANCH = '│   '
    # pointers:
    TEE = '├── '
    LAST = '└── '

    contents = glob_multiple_patterns(dir_path, include_glob)
    if exclude_glob:
        exclude = glob_multiple_patterns(dir_path, exclude_glob)
        contents = list(set(contents) - set(exclude))
    # contents each get pointers that are ├── with a final └── :
    pointers = [TEE] * (len(contents) - 1) + [LAST]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir():  # extend the prefix and recurse:
            extension = BRANCH if pointer == TEE else SPACE
            # i.e. SPACE because last, └── , above so no more |
            yield from tree(path, prefix=prefix + extension)
