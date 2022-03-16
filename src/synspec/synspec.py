import os
import subprocess


class Synspec:
    def __init__(self, synspecpath: str = "synspec", version: int = 51):
        if version != 51:
            raise NotImplementedError("Only version 51 is supported")
        self.version = version
        self.synspec = synspecpath

    def run(self, model: str) -> None:
        """Runs synspec with the given model"""
        unit8 = "fort.8"
        if os.path.exists(unit8):
            os.remove(unit8)
        os.symlink(f"{model}.7", unit8)

        with open(f"{model}.5") as modelinput:
            subprocess.run([self.synspec], stdin=modelinput, check=True)
