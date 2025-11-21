"""CSV comparison utilities."""

import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

COMPARISON_CONFIG = {
    "join_key": "cusip",
    "files": {
        "localdetail": "assetdetaillocal.csv",
        "custody": "assetdetailcustody.csv",
        "w360": "w360.csv",
    },
}


def _load_csv_by_key(csv_path: Path, key: str) -> Dict[str, Dict[str, str]]:
    """Load a CSV into a dict keyed by the join key, normalizing header names."""
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = [name.strip().lower() for name in (reader.fieldnames or [])]
        reader.fieldnames = fieldnames
        if key not in reader.fieldnames:
            raise ValueError(f"Missing join key '{key}' in {csv_path.name}")

        rows: Dict[str, Dict[str, str]] = {}
        for row in reader:
            normalized_row = {k.strip().lower(): (v or "").strip() for k, v in row.items()}
            key_value = normalized_row.get(key, "")
            if not key_value:
                continue
            rows[key_value] = normalized_row
        return rows


def _parse_decimal(row: Optional[Dict[str, str]], column: Optional[str]) -> Optional[Decimal]:
    """Parse a decimal value from a row/column, returning None if missing or invalid."""
    if row is None or not column:
        return None
    raw = (row.get(column.lower(), "") or "").strip()
    if not raw:
        return None
    raw = raw.replace(",", "")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return None


def _values_match(left: Optional[Decimal], right: Optional[Decimal]) -> bool:
    """Return True when both values are present and equal."""
    return left is not None and right is not None and left == right


def _write_cusip_file(path: Path, cusips: Iterable[str]) -> None:
    """Write a single-column CSV of cusips."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([COMPARISON_CONFIG["join_key"]])
        for cusip in cusips:
            writer.writerow([cusip])


def _write_result_file(path: Path, rows: Iterable[tuple[str, str]]) -> None:
    """Write comparison results with difference column."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([COMPARISON_CONFIG["join_key"], "difference"])
        for row in rows:
            writer.writerow(row)


def _compare_and_write(
    *,
    base_filename: str,
    left_rows: Dict[str, Dict[str, str]],
    left_column: str,
    right_rows: Dict[str, Dict[str, str]],
    right_column: str,
    output_dir: Path,
) -> None:
    """Compare two datasets on a column and write match/error CSVs."""
    all_keys = set(left_rows) | set(right_rows)
    matches: List[tuple[str, str]] = []
    errors: List[tuple[str, str]] = []

    for key in sorted(all_keys):
        left_val = _parse_decimal(left_rows.get(key), left_column)
        right_val = _parse_decimal(right_rows.get(key), right_column)

        diff_str = ""
        if left_val is not None and right_val is not None:
            diff = left_val - right_val
            diff_str = str(diff)

        if left_val is not None and right_val is not None and _values_match(left_val, right_val):
            matches.append((key, diff_str))
        else:
            errors.append((key, diff_str))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    match_path = output_dir / f"{base_filename}_matches_{timestamp}.csv"
    error_path = output_dir / f"{base_filename}_errors_{timestamp}.csv"
    _write_result_file(match_path, matches)
    _write_result_file(error_path, errors)

    print(f"[{base_filename}] Wrote {len(matches)} matches to {match_path.name}")
    print(f"[{base_filename}] Wrote {len(errors)} errors to {error_path.name}")


def compare_files(data_dir: Path, output_dir: Path) -> None:
    """
    Read source CSVs, run targeted comparisons, and emit timestamped match/error files.

    Args:
        data_dir: Directory where the CSV files live (also where output files are written).
        output_dir: Directory for comparison results (unused for now).
    """
    config = COMPARISON_CONFIG
    key = config["join_key"]
    paths = config["files"]

    local_rows = _load_csv_by_key(data_dir / paths["localdetail"], key)
    custody_rows = _load_csv_by_key(data_dir / paths["custody"], key)
    w360_rows = _load_csv_by_key(data_dir / paths["w360"], key)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1) Custody shares vs w360 shares
    _compare_and_write(
        base_filename="assetdetaicustodyl_w360_cost_compare",
        left_rows=custody_rows,
        left_column="shares",
        right_rows=w360_rows,
        right_column="no of shares",
        output_dir=output_dir,
    )

    # 2) Local cost vs w360 native cost
    _compare_and_write(
        base_filename="assetdetaillocal_w360_cost_compare",
        left_rows=local_rows,
        left_column="local cost",
        right_rows=w360_rows,
        right_column="natve cost",
        output_dir=output_dir,
    )
