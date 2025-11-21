# CSV Compare CLI

Command-line utility to compare key fields across three CSV exports and report matching/failed rows by CUSIP.

## How it works
- Reads three source files from `data/`:
  - `assetdetailcustody.csv`
  - `assetdetaillocal.csv`
  - `w360.csv`
- Joins records by `cusip` (headers are normalized and BOM-stripped).
- Two comparisons are performed:
  1. Custody `shares` vs w360 `no of shares`
  2. Local `local cost` vs w360 `natve cost`
- For each comparison, two outputs are written to `output/` with a timestamp suffix:
  - `..._matches_YYYYMMDD_HHMMSS.csv`
  - `..._errors_YYYYMMDD_HHMMSS.csv`
  - Each file contains one `cusip` per row.

## Setup
Requires Python 3.11+ (standard library only).

## Usage
From the project root:
```bash
python3 -m src.main --data-dir data --output-dir output
```
Flags are optional; defaults point to `data/` and `output/` under the project root.

## File locations
- Source code: `src/main.py`, `src/compare.py`
- Inputs: `data/`
- Outputs: `output/`
