"""Total and average developer salary from a "Name,Salary" text file."""

from pathlib import Path


def total_salary(path: str | Path) -> tuple[int, float]:
    """
    Calculate the total and average monthly salary of developers.

    Each line of the file holds one developer as "Name,Salary", for example
    "Alex Korp,3000". Blank lines and malformed lines (no comma, extra fields,
    empty name, non-integer salary) are skipped, so the average counts only
    valid lines.

    Args:
        path: Path to a UTF-8 text file with salary data.

    Returns:
        A tuple (total, average), where total is the sum of all salaries and
        average is total divided by the number of valid lines. Returns (0, 0)
        if the file is missing, is a directory, cannot be read or decoded,
        or contains no valid lines.

    Raises:
        TypeError: If path is not a str or os.PathLike object.

    Example:
        >>> total, average = total_salary("salary_file.txt")
        >>> print(f"Total: {total}, Average: {average}")
        Total: 6000, Average: 2000.0
    """

    path = Path(path)

    salaries = []
    try:
        with open(path, encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) != 2 or not parts[0].strip():
                    continue
                try:
                    salaries.append(int(parts[1]))
                except ValueError:
                    continue
    except (OSError, UnicodeDecodeError):
        return (0, 0)

    if not salaries:
        return (0, 0)

    total = sum(salaries)
    return (total, total / len(salaries))

if __name__ == "__main__":
    total, average = total_salary("salary_file.txt")
    print(f"Total: {total}, Average: {average}")