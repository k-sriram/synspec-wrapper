import os
import shutil
import tempfile

import pytest

from synspec.synspec import Synspec

PROJECT_ROOT = os.getcwd()
MODELS_ROOT = f"{PROJECT_ROOT}/tests/models"


def compare_files(file1: str, file2: str) -> bool:
    with open(file1, "r") as f1:
        with open(file2, "r") as f2:
            for line1, line2 in zip(f1, f2):
                if line1 != line2:
                    return False
    return True


def copy_model(model, files, dst):
    # Copy the model to the temporary directory.
    modeldir = f"{MODELS_ROOT}/{model}"
    for file in files:
        shutil.copy(f"{modeldir}/input/{file}".format(model=model), dst)
    os.symlink(f"{modeldir}/data", f"{dst}/data", target_is_directory=True)
    return modeldir


@pytest.fixture(scope="function")
def tempdir():
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            yield tempdir
    finally:
        os.chdir(PROJECT_ROOT)  # Ensure that we are returned to the original directory.


def test_synspec(tempdir):
    model = "hhe35lt"
    files = ["fort.19", "fort.55", "{model}.5", "{model}.7"]

    modeldir = copy_model(model, files, tempdir)

    os.chdir(tempdir)

    # Create a Synspec object.
    synspec = Synspec("synspec", 51)
    synspec.run(model)

    # Check that the output files are correct.
    for unit, ext in [
        ("7", "spec"),
        ("12", "iden"),
        ("16", "eqws"),
        ("17", "cont"),
    ]:
        assert compare_files(
            f"{modeldir}/output/{model}.{ext}", f"{tempdir}/fort.{unit}"
        )
