import functools
import shutil
import subprocess
import tempfile
from contextlib import _GeneratorContextManager, contextmanager
from pathlib import Path
from typing import Callable, Iterator

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
        outfile: str | None = None,
    ) -> None:
        """Runs synspec with the given model.
        rundir: directory to run synspec in.
                defaults to running in the current directory.
                if explicitly set to None, a temporary directory is used.
        outdir: directory to copy the output files to.
        outfile: name (without extension) of the output files.
        """

        if rundir is None:
            if outdir is None:
                outdir = Path.cwd()
            rdprovider: Callable[[], _GeneratorContextManager[Path]] = tempdir
        else:
            rundir = Path(rundir).resolve()
            rundir.mkdir(exist_ok=True)
            rdprovider = functools.partial(
                utils.folderlock, path=rundir, lockfn="synspec.lock"
            )
        with rdprovider() as rundir:
            self._copy_to_rundir(model, rundir)
            self._check_files(model, rundir)
            self._run(model, rundir)
            self._extract_outfiles(model, rundir, outdir, outfile)

    def _run(self, model: str, rundir: Path) -> None:
        utils.symlinkf(f"{model}.7", rundir / "fort.8")
        with open(rundir / f"{model}.5") as modelinput, open(
            rundir / "fort.log", "w"
        ) as log:
            subprocess.run(
                [self.synspec], stdin=modelinput, stdout=log, cwd=rundir, check=True
            )

    def _extract_outfiles(
        self, model: str, rundir: Path, outdir: Path | str | None, outfile: str | None
    ) -> None:
        if outdir is None:
            outdir = rundir
        else:
            outdir = Path(outdir).resolve()
        outdir.mkdir(exist_ok=True)

        if outfile is None:
            outfile = model

        for unit, ext in [
            ("7", "spec"),
            ("12", "iden"),
            ("16", "eqws"),
            ("17", "cont"),
        ]:
            shutil.copyfile(rundir / f"fort.{unit}", outdir / f"{outfile}.{ext}")
        shutil.copyfile(rundir / "fort.log", outdir / f"{outfile}.log")

    def _copy_to_rundir(self, model: str, rundir: Path) -> None:
        for dst, src in self.linkfiles.items():
            src = Path(str(src).format(model=model)).resolve()
            if (
                rundir != Path.cwd().resolve()
                or src != Path(str(dst).format(model=model)).resolve()
            ):
                utils.symlinkf(src, rundir / dst.format(model=model))

    def _check_files(self, model: str, rundir: Path) -> None:
        """Checks if the required files exist."""
        files = ["fort.19", "fort.55", "{model}.5", "{model}.7"]
        for file in files:
            if not Path(fn := rundir / file.format(model=model)).exists():
                raise FileNotFoundError(f"{fn} not found")


@contextmanager
def tempdir() -> Iterator[Path]:
    """Context manager for temporary directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir).resolve()
