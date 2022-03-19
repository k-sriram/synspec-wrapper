from pathlib import Path
from typing import NamedTuple

# Unit 56:


class ElementAbundance(NamedTuple):
    atomic_number: int
    abundance: float


def read56(text: str) -> list[ElementAbundance]:
    """Converts the contents of a .56 file to a python list."""
    lines = text.splitlines()
    if len(lines) == 0:
        raise ValueError("unit 56 is empty")
    numlines = int(lines[0])
    if len(lines) != numlines + 1:
        raise ValueError(f"unit 56 has {len(lines)} lines, but {numlines} expected")
    abundances = [
        ElementAbundance(int(line.split()[0]), float(line.split()[1]))
        for line in lines[1:]
    ]
    if len(set(x.atomic_number for x in abundances)) != len(abundances):
        raise ValueError("atomic numbers must be unique")
    return abundances


def read56f(file: Path) -> list[ElementAbundance]:
    """Reads the contents of a .56 file."""
    return read56(file.read_text())


def write56(lines: list[tuple[int, float]]) -> str:
    """Converts a list of ElementAbundance to a string storable in a .56 file."""
    abundances = []
    if len(set(line[0] for line in lines)) != len(lines):
        raise ValueError("atomic numbers must be unique")
    for line in lines:
        if line[0] < 1 or line[0] > 118:
            raise ValueError(f"atomic number {line[0]} out of range")
        if line[1] < 0 or line[1] > 1:
            raise ValueError(f"abundance {line[1]} out of range (0 to 1)")
        abundances.append(f"{line[0]} {line[1]:.6e}\n")
    return f"{len(lines)}\n" + "".join(abundances)
