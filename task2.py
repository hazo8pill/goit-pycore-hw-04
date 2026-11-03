"""Cat records from an "id,name,age" text file."""

from pathlib import Path


def get_cats_info(path: str | Path) -> list[dict[str, str]]:
    """
    Read cat records from a text file.

    Each line of the file holds one cat as "id,name,age", for example
    "60b90c1c13067a15887e1ae1,Tayson,3". Blank lines and malformed lines
    (wrong number of fields, empty field, age not a non-negative integer)
    are skipped.

    Args:
        path: Path to a UTF-8 text file with cat data.

    Returns:
        A list of dicts with keys "id", "name" and "age" (all str), in file
        order. Returns [] if the file is missing, is a directory, cannot be
        read or decoded, or contains no valid lines.

    Raises:
        TypeError: If path is not a str or os.PathLike object.

    Example:
        >>> get_cats_info("cats_file.txt")
        [{'id': '60b90c1c13067a15887e1ae1', 'name': 'Tayson', 'age': '3'}, ...]
    """

    path = Path(path)

    cats = []
    try:
        with open(path, encoding="utf-8") as file:
            for line in file:
                parts = [part.strip() for part in line.split(",")]
                if len(parts) != 3 or not all(parts) or not parts[2].isdecimal():
                    continue
                cat_id, name, age = parts
                cats.append({"id": cat_id, "name": name, "age": age})
    except (OSError, UnicodeDecodeError):
        return []

    return cats

if __name__ == "__main__":
    cats = get_cats_info("cats_file.txt")
    for cat in cats:
        print(f"ID: {cat['id']}, Name: {cat['name']}, Age: {cat['age']}")