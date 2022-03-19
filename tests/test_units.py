import tempfile
from pathlib import Path

import pytest

from synspec import units


def test_read56_1() -> None:
    text = """1
8 3.847575e-03
"""
    assert units.read56(text) == [(8, 3.847575e-03)]


def test_read56_2() -> None:
    text = """0
"""
    assert units.read56(text) == []


def test_read56_3() -> None:
    text = """"""
    with pytest.raises(ValueError):
        units.read56(text)


def test_read56_4() -> None:
    text = """3
1 1.2e-04
2 1.4e-04
"""
    with pytest.raises(ValueError):
        units.read56(text)


def test_read56_5() -> None:
    """Atomic numbers must be unique."""
    with pytest.raises(ValueError):
        units.read56("2\n1 1.0e-2\n1 1.0e-3")


def test_read56f() -> None:
    file = Path("tests/models/EHeT30g4/fort.56")
    assert units.read56f(file) == [(8, 3.847575e-03)]


# units.write56


def test_write56_1() -> None:
    assert (
        units.write56([(8, 2.245623525e-03), (6, 1.2345e-04)])
        == "2\n8 2.245624e-03\n6 1.234500e-04\n"
    )


def test_write56_2() -> None:
    assert units.write56([]) == "0\n"


def test_write56_3() -> None:
    """Abundances must be less than 1.0."""
    with pytest.raises(ValueError):
        units.write56([(1, 2.0)])


def test_write56_4() -> None:
    """Abundances must be positive."""
    with pytest.raises(ValueError):
        units.write56([(1, 1.0e-2), (2, -1.0e-5)])


def test_write56_5() -> None:
    """Atomic numbers must be unique."""
    with pytest.raises(ValueError):
        units.write56([(1, 1.0e-2), (1, 1.0e-3)])


def test_write56f() -> None:
    try:
        _, fn = tempfile.mkstemp(suffix=".56")
        f = Path(fn)
        units.write56f(f, [(8, 3.847575e-03)])

        assert f.read_text() == "1\n8 3.847575e-03\n"
    finally:
        f.unlink()
