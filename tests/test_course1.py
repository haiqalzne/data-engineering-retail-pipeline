import json
import tempfile
import unittest
from pathlib import Path

from pipeline import ROOT
from similarity import recommend
from stream import consume
from workflow import execute


class CourseOneTests(unittest.TestCase):
    def test_workflow_lineage_and_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            result = execute(ROOT / "data/source.json", output)
            self.assertEqual(result["status"], "success")
            self.assertEqual(len(result["source_sha256"]), 64)
            self.assertEqual(len(result["tasks"]), 3)
            self.assertTrue((output / result["report_file"]).is_file())
            self.assertEqual(recommend("missing", output / "warehouse.db")["products"][0], "P1")

    def test_failed_workflow_stops_reports_and_records_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            invalid = output / "bad.json"
            invalid.write_text("{}")
            with self.assertRaises(KeyError):
                execute(invalid, output)
            record = json.loads(next(output.glob("run-*.json")).read_text())
            self.assertEqual(record["status"], "failed")
            self.assertNotIn("report_file", record)
            self.assertFalse(list(output.glob("reports-*.json")))

    def test_stream_deduplication_and_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "activity.db"
            result = consume(ROOT / "data/events.jsonl", database)
            self.assertEqual((result["accepted"], result["duplicates"], result["rejected"]), (3, 1, 1))
            replay = consume(ROOT / "data/events.jsonl", database)
            self.assertEqual(replay["accepted"], 0)
            self.assertEqual(replay["duplicates"], 4)
            self.assertEqual(replay["totals"], result["totals"])

    def test_toy_similarity(self):
        self.assertEqual(recommend("P1", "unused.db")["products"][0], "P3")


if __name__ == "__main__":
    unittest.main()
