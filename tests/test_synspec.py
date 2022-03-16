import os
import shutil
import tempfile
from synspec.synspec import Synspec


def compare_files(file1: str, file2: str) -> bool:
    with open(file1, "r") as f1:
        with open(file2, "r") as f2:
            for line1, line2 in zip(f1, f2):
                if line1 != line2:
                    return False
    return True


def test_synspec():
    cwd = os.getcwd()

    # Create a temporary directory to test in.
    with tempfile.TemporaryDirectory() as tdir:
        model = "hhe35lt"

        shutil.copytree(f"models/{model}/input", f"{tdir}")
        os.symlink("models/{model}/data", f"{tdir}/data", target_is_directory=True)

        os.chdir(tdir)

        # Create a Synspec object.
        synspec = Synspec("synspec", 51)
        synspec.run(model)

        os.chdir(cwd)
        # Check that the output files are correct.
        for unit, ext in [
            ("7", "spec"),
            ("12", "iden"),
            ("16", "eqws"),
            ("17", "cont"),
        ]:
            assert compare_files(
                f"models/{model}/output/{model}.{ext}", f"{tdir}/fort.{unit}"
            )
