from pathlib import Path


def symlinkf(
    src: str | Path, dst: str | Path, target_is_directory: bool = False
) -> None:
    """Symlink a file. If the file already exists, delete it first."""
    dst = Path(dst)
    if dst.exists():
        dst.unlink()
    dst.symlink_to(src, target_is_directory=target_is_directory)
