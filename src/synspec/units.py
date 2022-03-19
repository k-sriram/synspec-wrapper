from typing import NamedTuple

ElementAbundance = NamedTuple(
    "ElementAbundance", [("atomic_number", int), ("abundance", float)]
)


def read56(text: str) -> list[ElementAbundance]:
    """Reads the contents of a .56 file.
    Returns an iterator over the lines of the file.
    """
    lines = text.splitlines()
    if len(lines) == 0:
        raise ValueError("unit 56 is empty")
    numlines = int(lines[0])
    if len(lines) != numlines + 1:
        raise ValueError(f"unit 56 has {len(lines)} lines, but {numlines} expected")
    return [
        ElementAbundance(int(line.split()[0]), float(line.split()[1]))
        for line in lines[1:]
    ]
