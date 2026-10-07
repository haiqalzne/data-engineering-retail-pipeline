"""Run the two analysis queries against the learning warehouse."""

import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=ROOT / "output/warehouse.db")
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error("Database not found. Run pipeline.py first.")
    with sqlite3.connect(args.database.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        for query in sorted((ROOT / "queries").glob("*.sql")):
            print(f"\n{query.stem}")
            for row in connection.execute(query.read_text(encoding="utf-8")):
                print(dict(row))
