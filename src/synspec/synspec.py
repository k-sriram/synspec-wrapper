import subprocess
from pathlib import Path


class Synspec:
    def __init__(self, synspecpath: str = "synspec", version: int = 51):
        if version != 51:
            raise NotImplementedError("Only version 51 is supported")
        self.version = version
        self.synspec = synspecpath

    def run(self, model: str) -> None:
        """Runs synspec with the given model"""
        symlinkf(f"{model}.7", "fort.8")

        with open(f"{model}.5") as modelinput:
            subprocess.run([self.synspec], stdin=modelinput, check=True)


# Utils


def symlinkf(
    src: str | Path, dst: str | Path, target_is_directory: bool = False
) -> None:
    """Symlink a file. If the file already exists, delete it first."""
    dst = Path(dst)
    if dst.exists():
        dst.unlink()
    dst.symlink_to(src, target_is_directory=target_is_directory)
