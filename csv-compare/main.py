"""Command line entrypoint for the CSV comparison tool."""

from argparse import ArgumentParser
from pathlib import Path

from compare import compare_files


def parse_args() -> tuple[Path, Path]:
    """Parse CLI arguments and return data/output directories."""
    parser = ArgumentParser(description="Compare CSV files and write results.")
    parser.add_argument(
        "--data-dir",
        default=Path("data"),
        type=Path,
        help="Directory containing input CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        default=Path("output"),
        type=Path,
        help="Directory to write comparison results.",
    )
    args = parser.parse_args()
    return args.data_dir, args.output_dir


def main() -> None:
    data_dir, output_dir = parse_args()
    output_dir.mkdir(parents=True, exist_ok=True)
    compare_files(data_dir, output_dir)


if __name__ == "__main__":
    main()
