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


def copy_model(model: str, files: list[str], dst: str) -> str:
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


def test_synspec(tempdir: str) -> None:
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


@pytest.mark.parametrize(
    "missingfile",
    [
        "fort.19",
        "fort.55",
        "{model}.5",
        "{model}.7",
    ],
)
def test_with_missing_files(missingfile: str, tempdir: str) -> None:
    model = "hhe35lt"
    files = ["fort.19", "fort.55", "{model}.5", "{model}.7"]
    files.remove(missingfile)

    _ = copy_model(model, files, tempdir)

    os.chdir(tempdir)

    # Create a Synspec object.
    synspec = Synspec("synspec", 51)
    with pytest.raises(FileNotFoundError):
        synspec.run(model)


def test_synspec_indir(tempdir: str) -> None:
    model = "hhe35lt"
    files = ["fort.19", "fort.55", "{model}.5", "{model}.7"]

    modeldir = copy_model(model, files, tempdir)

    os.chdir(tempdir)
    rundir = f"{tempdir}/run"

    # Create a Synspec object.
    synspec = Synspec("synspec", 51)
    synspec.add_link("data")
    synspec.run(model, rundir=rundir)

    # Check that the output files are correct.
    for unit, ext in [
        ("7", "spec"),
        ("12", "iden"),
        ("16", "eqws"),
        ("17", "cont"),
    ]:
        assert compare_files(
            f"{modeldir}/output/{model}.{ext}", f"{rundir}/fort.{unit}"
        )


@pytest.mark.parametrize(
    "outdir",
    [
        None,
        "{tempdir}/output",
        "{tempdir}",
    ],
)
def test_synspec_outdir(tempdir: str, outdir: str) -> None:
    model = "hhe35lt"
    files = ["fort.19", "fort.55", "{model}.5", "{model}.7"]

    modeldir = copy_model(model, files, tempdir)

    os.chdir(tempdir)
    if outdir is not None:
        outdir = outdir.format(tempdir=tempdir)

    # Create a Synspec object.
    synspec = Synspec("synspec", 51)
    synspec.run(model, outdir=outdir)

    # Check that the output files are correct.
    for ext in ["spec", "iden", "eqws", "cont", "log"]:
        assert compare_files(
            f"{modeldir}/output/{model}.{ext}", f"{outdir}/{model}.{ext}"
        )
