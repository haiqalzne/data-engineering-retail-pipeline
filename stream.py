"""Replay synthetic activity one event at a time; no network broker or real-time SLA."""

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from time import perf_counter

from pipeline import ROOT


def consume(event_path, database_path):
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    counts = {"accepted": 0, "duplicates": 0, "rejected": 0}
    started = perf_counter()
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS activity (
            event_id TEXT PRIMARY KEY, user_id TEXT NOT NULL,
            product_id TEXT NOT NULL, action TEXT NOT NULL)""")
        with Path(event_path).open(encoding="utf-8") as source:
            for line in source:
                try:
                    event = json.loads(line)
                    fields = ("event_id", "user_id", "product_id", "action")
                    if set(event) != set(fields):
                        raise ValueError("Unexpected event structure")
                    if any(not isinstance(event[key], str) or not event[key].strip() for key in fields):
                        raise ValueError("Blank or invalid field")
                    if event["action"] not in {"view", "cart", "purchase"}:
                        raise ValueError("Unknown action")
                except (ValueError, TypeError, KeyError):
                    counts["rejected"] += 1
                    continue
                # One transaction per event: arrivals can be consumed independently.
                with connection:
                    cursor = connection.execute("INSERT OR IGNORE INTO activity VALUES (?, ?, ?, ?)",
                                                tuple(event[key] for key in fields))
                counts["accepted" if cursor.rowcount else "duplicates"] += 1
        totals = [dict(zip(("product_id", "events"), row)) for row in connection.execute(
            "SELECT product_id, COUNT(*) FROM activity GROUP BY product_id ORDER BY product_id")]
    return {**counts, "processing_seconds": round(perf_counter() - started, 6), "totals": totals}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=ROOT / "data/events.jsonl")
    parser.add_argument("--database", type=Path, default=ROOT / "output/activity.db")
    args = parser.parse_args()
    print(json.dumps(consume(args.events, args.database), indent=2))
