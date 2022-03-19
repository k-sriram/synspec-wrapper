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


def test_read56f() -> None:
    file = Path("tests/models/EHeT30g4/fort.56")
    assert units.read56f(file) == [(8, 3.847575e-03)]
