"""Dependency-aware local batch workflow with checks, lineage, and run records."""

import argparse
import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from pipeline import ROOT, run


def read_reports(database):
    with closing(sqlite3.connect(Path(database).resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Warehouse references failed quality checks")
        return {
            query.stem: [dict(row) for row in connection.execute(query.read_text())]
            for query in sorted((ROOT / "queries").glob("*.sql"))
        }


def execute(source, output):
    """Stop dependent tasks on failure; never serve results from a failed load."""
    source, output = Path(source), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    record = {"run_id": str(uuid4()), "started_at": datetime.now(timezone.utc).isoformat(),
              "status": "running", "tasks": [], "source_sha256": None,
              "schema_version": 1}
    started = perf_counter()
    try:
        # Snapshot first: the fingerprint and processing refer to the same bytes.
        raw = source.read_bytes()
        record["source_sha256"] = hashlib.sha256(raw).hexdigest()
        snapshot = output / f"source-{record['run_id']}.json"
        snapshot.write_bytes(raw)
        record["tasks"].append({"task": "snapshot", "status": "success"})
        record["metrics"] = run(snapshot, output / "warehouse.db")
        record["tasks"].append({"task": "validate_transform_load", "status": "success"})
        reports = read_reports(output / "warehouse.db")
        report_path = output / f"reports-{record['run_id']}.json"
        report_path.write_text(json.dumps(reports, indent=2), encoding="utf-8")
        record["report_file"] = report_path.name
        record["tasks"].append({"task": "quality_check_and_serve", "status": "success"})
        record["status"] = "success"
    except Exception as error:
        record["status"] = "failed"
        # Record the exception category, not input values or credentials.
        record["error_type"] = type(error).__name__
        record["tasks"].append({"task": "workflow", "status": "failed"})
        raise
    finally:
        record["duration_seconds"] = round(perf_counter() - started, 6)
        record["finished_at"] = datetime.now(timezone.utc).isoformat()
        (output / f"run-{record['run_id']}.json").write_text(json.dumps(record, indent=2))
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "data/source.json")
    parser.add_argument("--output", type=Path, default=ROOT / "output")
    args = parser.parse_args()
    try:
        print(json.dumps(execute(args.source, args.output), indent=2))
    except Exception as error:
        print(json.dumps({"status": "failed", "error_type": type(error).__name__,
                          "action": "Inspect the run record and follow docs/INCIDENTS.md."}))
        raise SystemExit(1)
