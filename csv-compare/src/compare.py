"""CSV comparison utilities."""

from pathlib import Path
import csv


def _count_data_rows(csv_path: Path) -> int:
    """Count data rows in a CSV, skipping the header if present."""
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)  # skip header row
        return sum(1 for _ in reader)


def compare_files(data_dir: Path, output_dir: Path) -> None:
    """
    Load target CSV files and print how many data rows each contains.

    Args:
        data_dir: Directory where the CSV files live.
        output_dir: Directory for comparison results (unused for now).
    """
    targets = ["localdetail.csv", "custody.csv", "w360.csv"]
    for name in targets:
        csv_path = data_dir / name
        row_count = _count_data_rows(csv_path)
        print(f"{name}: {row_count} data rows")
