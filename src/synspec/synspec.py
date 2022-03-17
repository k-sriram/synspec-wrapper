import subprocess
from pathlib import Path

from synspec import utils


class Synspec:
    def __init__(self, synspecpath: str = "synspec", version: int = 51):
        if version != 51:
            raise NotImplementedError("Only version 51 is supported")
        self.version = version
        self.synspec = synspecpath

    def run(self, model: str) -> None:
        """Runs synspec with the given model"""
        self.check_files(model)
        utils.symlinkf(f"{model}.7", "fort.8")

        with open(f"{model}.5") as modelinput:
            subprocess.run([self.synspec], stdin=modelinput, check=True)

    def check_files(self, model: str) -> None:
        """Checks if the required files exist."""
        files = ["fort.19", "fort.55", "{model}.5", "{model}.7"]
        for file in files:
            if not Path(file.format(model=model)).exists():
                raise FileNotFoundError(f"{file.format(model=model)} not found")
