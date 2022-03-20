import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, TextIO


def symlinkf(
    src: str | Path, dst: str | Path, target_is_directory: bool = False
) -> None:
    """Symlink a file. If the file already exists, delete it first."""
    dst = Path(dst)
    if dst.resolve() == Path(src).resolve():
        raise ValueError(f"src and dst are the same: {dst.resolve()}")
    if dst.exists():
        dst.unlink()
    dst.symlink_to(src, target_is_directory=target_is_directory)


@contextmanager
def folderlock(
    path: str | Path | None = None,
    lockfn: str = ".lock",
    unlock_after: int = 60,
    check_at_end: bool = True,
) -> Iterator[Path]:
    """
    Context manager to lock a folder.

    Parameters
    ----------
    path : str | Path
        Path to the folder to lock.
    lockfn : str
        Name of the lock file.
    unlock_after : int
        Time in seconds after which the lock is automatically removed.
    check_at_end : bool
        If True, check if the lock file is still there when the context manager
        exits. Raise RuntimeError if the file is modified.

    Returns
    -------
    path: Path
        Path to the locked folder.

    Raises
    ------
        RuntimeError
            if the lock could not be acquired or optionally if the lcokfile
            was modified midway.
    """
    _check_at_end = False
    if path is None:
        path = Path.cwd()
    else:
        path = Path(path).resolve()
    lockfile = path / lockfn
    id_ = str(uuid.uuid4())
    try:
        if (
            not lockfile.exists()
            or time.time() - lockfile.stat().st_mtime > unlock_after
        ):
            lockfile.write_text(id_)
        if lockfile.read_text() != id_:
            raise RuntimeError("Lockfile could not be acquired.")
        _check_at_end = check_at_end
        yield path
    finally:
        if _check_at_end:
            if not lockfile.exists() or lockfile.read_text() != id_:
                raise RuntimeError("Lockfile was modified")
        lockfile.unlink(missing_ok=True)


def write_to_file(file: Path | str | TextIO, content: str) -> None:
    if isinstance(file, Path):
        file.write_text(content)
    elif isinstance(file, TextIO):
        file.write(content)
    elif isinstance(file, str):
        with open(file, "w") as f:
            f.write(content)
    else:
        raise TypeError(f"file must be a Path, TextIO, or str, not {type(file)}")


def fortfloat(text: str) -> float:
    """Convert Fortran-style float to python float."""
    text = text.strip()
    if text.endswith("d"):
        text = text[:-1]
    text.replace("d", "e")
    try:
        return float(text)
    except ValueError:
        if len(text) > 1 and "-" in text[1:]:
            text = f"{text[0]}{text[1:].replace('-', 'e-')}"
            return float(text)
        else:
            raise
