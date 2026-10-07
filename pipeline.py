"""Extract JSON, transform order lines, and load a SQLite star schema."""

import argparse
import json
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def index_rows(rows, label):
    result = {}
    for row in rows:
        identifier = row["id"]
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError(f"Invalid {label} ID")
        if identifier in result:
            raise ValueError(f"Duplicate {label} ID: {identifier}")
        result[identifier] = row
    return result


def transform(source):
    """Validate first; produce one fact row per completed order line."""
    customers = index_rows(source["customers"], "customer")
    products = index_rows(source["products"], "product")
    orders = index_rows(source["orders"], "order")
    for customer in customers.values():
        if not isinstance(customer["country"], str) or not customer["country"].strip():
            raise ValueError("Customer country must be nonblank text")
    for product in products.values():
        for field in ("name", "line"):
            if not isinstance(product[field], str) or not product[field].strip():
                raise ValueError(f"Product {field} must be nonblank text")
    facts = []
    dates = set()
    skipped = 0
    for order in orders.values():
        if order["status"] not in {"completed", "cancelled"}:
            raise ValueError(f"Unknown order status: {order['status']}")
        if order["customer_id"] not in customers:
            raise ValueError(f"Unknown customer: {order['customer_id']}")
        day = date.fromisoformat(order["date"]).isoformat()
        if not isinstance(order["items"], list) or not order["items"]:
            raise ValueError("An order must contain items")
        for number, item in enumerate(order["items"], start=1):
            if item["product_id"] not in products:
                raise ValueError(f"Unknown product: {item['product_id']}")
            quantity, price = item["quantity"], item["unit_price_cents"]
            if type(quantity) is not int or quantity <= 0:
                raise ValueError("Quantity must be a positive integer")
            if type(price) is not int or price < 0:
                raise ValueError("Price must be a nonnegative integer in cents")
            if order["status"] == "completed":
                facts.append((order["id"], number, order["customer_id"],
                              item["product_id"], day, quantity, price, quantity * price))
                dates.add(day)
        skipped += order["status"] == "cancelled"
    return customers, products, dates, facts, skipped


def run(source_path, database_path):
    source = json.loads(Path(source_path).read_text(encoding="utf-8"))
    customers, products, dates, facts, skipped = transform(source)
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS dim_customer (
                customer_id TEXT PRIMARY KEY, country TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS dim_product (
                product_id TEXT PRIMARY KEY, name TEXT NOT NULL, product_line TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS dim_date (
                date_key TEXT PRIMARY KEY, year INTEGER NOT NULL, month INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS fact_sales (
                order_id TEXT NOT NULL, line_number INTEGER NOT NULL,
                customer_id TEXT NOT NULL REFERENCES dim_customer(customer_id),
                product_id TEXT NOT NULL REFERENCES dim_product(product_id),
                date_key TEXT NOT NULL REFERENCES dim_date(date_key),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents >= 0),
                revenue_cents INTEGER NOT NULL CHECK(revenue_cents = quantity * unit_price_cents),
                PRIMARY KEY(order_id, line_number));
        """)
        # Full snapshot refresh in one transaction: reruns do not duplicate sales.
        with connection:
            for table in ("fact_sales", "dim_customer", "dim_product", "dim_date"):
                connection.execute(f"DELETE FROM {table}")
            connection.executemany("INSERT INTO dim_customer VALUES (?, ?)",
                                   [(c["id"], c["country"].strip()) for c in customers.values()])
            connection.executemany("INSERT INTO dim_product VALUES (?, ?, ?)",
                                   [(p["id"], p["name"].strip(), p["line"].strip())
                                    for p in products.values()])
            connection.executemany("INSERT INTO dim_date VALUES (?, ?, ?)",
                                   [(d, date.fromisoformat(d).year, date.fromisoformat(d).month)
                                    for d in sorted(dates)])
            connection.executemany("INSERT INTO fact_sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)", facts)
    return {"loaded_lines": len(facts), "cancelled_orders_excluded": skipped,
            "revenue_cents": sum(row[-1] for row in facts)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "data/source.json")
    parser.add_argument("--database", type=Path, default=ROOT / "output/warehouse.db")
    args = parser.parse_args()
    print(json.dumps(run(args.source, args.database), indent=2))
