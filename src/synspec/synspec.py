import shutil
import subprocess
from pathlib import Path

from synspec import utils


class Synspec:
    def __init__(self, synspecpath: str = "synspec", version: int = 51):
        if version != 51:
            raise NotImplementedError("Only version 51 is supported")
        self.version = version
        self.synspec = synspecpath
        self.linkfiles: dict[str, str | Path] = {  # default links
            "fort.19": "fort.19",
            "fort.55": "fort.55",
            "{model}.5": "{model}.5",
            "{model}.7": "{model}.7",
        }

    def add_link(self, linkfrom: str, linkto: str = None) -> None:
        """Adds a link from the given file to the given file."""
        if linkto is None:
            linkto = linkfrom
        self.linkfiles[linkto] = linkfrom

    def run(
        self,
        model: str,
        rundir: str | Path | None = ".",
        outdir: str | Path | None = None,
    ) -> None:
        """Runs synspec with the given model. If rundir is given, the files are
        linked to that directory and synspec is run there."""

        rundir = self.copy_to_rundir(model, rundir)

        self.check_files(model, rundir)
        utils.symlinkf(f"{model}.7", rundir / "fort.8")

        with open(rundir / f"{model}.5") as modelinput, open(
            rundir / "fort.log", "w"
        ) as log:
            subprocess.run(
                [self.synspec], stdin=modelinput, stdout=log, cwd=rundir, check=True
            )

        if outdir is None:
            outdir = rundir
        else:
            outdir = Path(outdir).resolve()
        outdir.mkdir(exist_ok=True)

        for unit, ext in [
            ("7", "spec"),
            ("12", "iden"),
            ("16", "eqws"),
            ("17", "cont"),
        ]:
            shutil.copyfile(rundir / f"fort.{unit}", outdir / f"{model}.{ext}")
        shutil.copyfile(rundir / "fort.log", outdir / f"{model}.log")

    def copy_to_rundir(self, model: str, rundir: str | Path | None) -> Path:
        if rundir is None:
            return Path.cwd()
        rundir = Path(rundir).resolve()
        if rundir != Path.cwd().resolve():
            rundir.mkdir(exist_ok=True)
            for dst, src in self.linkfiles.items():
                src = Path(str(src).format(model=model)).resolve()
                utils.symlinkf(src, rundir / dst.format(model=model))
        return rundir

    def check_files(self, model: str, rundir: Path) -> None:
        """Checks if the required files exist."""
        files = ["fort.19", "fort.55", "{model}.5", "{model}.7"]
        for file in files:
            if not Path(fn := rundir / file.format(model=model)).exists():
                raise FileNotFoundError(f"{fn} not found")
