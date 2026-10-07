import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from pipeline import ROOT, run, transform


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads((ROOT / "data/source.json").read_text())

    def test_totals_and_idempotency(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "warehouse.db"
            for _ in range(2):
                result = run(ROOT / "data/source.json", database)
                self.assertEqual(result, {"loaded_lines": 3,
                                         "cancelled_orders_excluded": 1,
                                         "revenue_cents": 16500})
            with sqlite3.connect(database) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0], 3)
                self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
                country = dict((r[0], r[2]) for r in connection.execute(
                    (ROOT / "queries/sales_by_country.sql").read_text()))
                self.assertEqual(country, {"Malaysia": 9000, "South Korea": 7500})
                lines = dict((r[0], r[2]) for r in connection.execute(
                    (ROOT / "queries/sales_by_product_line.sql").read_text()))
                self.assertEqual(lines, {"Cars": 12500, "Boats": 4000})

    def test_bad_data_rejected(self):
        for field, value in (("quantity", 0), ("unit_price_cents", -1),
                             ("product_id", "missing")):
            with self.subTest(field=field):
                source = copy.deepcopy(self.source)
                source["orders"][0]["items"][0][field] = value
                with self.assertRaises(ValueError):
                    transform(source)

    def test_duplicate_order_rejected(self):
        self.source["orders"].append(copy.deepcopy(self.source["orders"][0]))
        with self.assertRaises(ValueError):
            transform(self.source)

    def test_failed_validation_preserves_existing_data(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "warehouse.db"
            run(ROOT / "data/source.json", database)
            self.source["orders"][0]["customer_id"] = "missing"
            bad_source = Path(folder) / "bad.json"
            bad_source.write_text(json.dumps(self.source))
            with self.assertRaises(ValueError):
                run(bad_source, database)
            with sqlite3.connect(database) as connection:
                self.assertEqual(connection.execute("SELECT SUM(revenue_cents) FROM fact_sales").fetchone()[0], 16500)


if __name__ == "__main__":
    unittest.main()
