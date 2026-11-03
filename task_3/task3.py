"""Print a colored directory tree.

Usage: python task3.py /path/to/directory
"""

import sys
from pathlib import Path

from colorama import Fore, Style, just_fix_windows_console

INDENT = "    "
DIR_COLOR = Fore.BLUE
FILE_COLOR = Fore.GREEN
ERROR_COLOR = Fore.RED


def directory_tree(path: str | Path) -> list[str]:
    """
    Build colored lines that show a directory and everything inside it.

    Directories are blue with a trailing "/", files are green. Each nesting
    level is indented by 4 spaces. Entries are sorted by name, ignoring case.
    Subdirectories that cannot be read are shown as a red marker instead of
    crashing. Symlinked directories are listed but not followed, so a symlink
    loop cannot cause infinite recursion.

    Args:
        path: Path to an existing directory.

    Returns:
        A list of lines (with colorama color codes), the root directory first.

    Raises:
        TypeError: If path is not a str or os.PathLike object.
        ValueError: If path is an empty or blank string.
        FileNotFoundError: If path does not exist (or contains a null byte).
        NotADirectoryError: If path exists but is not a directory.

    Example:
        >>> print("\\n".join(directory_tree("picture")))
        picture/
            bot-icon.png
            Logo/
                IBM+Logo.png
        ...
    """

    if isinstance(path, str) and not path.strip():
        raise ValueError("Path must not be empty")

    root = Path(path)  
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    root_name = root.resolve().name or str(root)
    lines = [f"{DIR_COLOR}{root_name}/{Style.RESET_ALL}"]
    _walk(root, 1, lines)
    return lines


def _walk(directory: Path, depth: int, lines: list[str]) -> None:
    """Recursively append lines for the contents of directory."""

    prefix = INDENT * depth
    try:
        entries = sorted(directory.iterdir(), key=lambda entry: entry.name.lower())
    except OSError as error: 
        lines.append(f"{prefix}{ERROR_COLOR}[cannot read: {error.strerror}]{Style.RESET_ALL}")
        return

    for entry in entries:
        if entry.is_dir():
            lines.append(f"{prefix}{DIR_COLOR}{entry.name}/{Style.RESET_ALL}")
            if not entry.is_symlink():
                _walk(entry, depth + 1, lines)
        else:
            lines.append(f"{prefix}{FILE_COLOR}{entry.name}{Style.RESET_ALL}")


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""

    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(f"{ERROR_COLOR}Usage: python task3.py <directory>{Style.RESET_ALL}", file=sys.stderr)
        return 2

    try:
        lines = directory_tree(args[0])
    except (ValueError, OSError) as error:
        print(f"{ERROR_COLOR}Error: {error}{Style.RESET_ALL}", file=sys.stderr)
        return 1

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
