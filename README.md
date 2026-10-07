# Data Engineering Retail Pipeline

An original local learning project applying data engineering lifecycle concepts.
It is not an official course assignment, solution, or copied course implementation.
All customer and transaction records are synthetic; prices use one fictional currency.

## Business questions

- Which product lines generate the most sales revenue?
- How are sales distributed across countries?

## Run

Python 3.12 or newer is sufficient. There are no third-party dependencies,
cloud services, credentials, or API keys. Run from this project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python pipeline.py
python report.py
python -m unittest discover -s tests -v
```

The generated SQLite file is `output/warehouse.db` and is excluded from Git.
Each run replaces the project warehouse's contents with the current source snapshot.
Only point `--database` at a database dedicated to this project, never an unrelated database.

## Lifecycle and files

1. **Extract:** read `data/source.json`.
2. **Transform:** validate references, reject duplicate IDs, standardize dates,
   exclude cancelled orders, and calculate line revenue in integer cents.
3. **Load:** write a star schema into SQLite with foreign-key checks and a transaction.
4. **Serve:** run the SQL files in `queries/` using `report.py`.

`pipeline.py` implements ETL; `tests/test_pipeline.py` checks totals, reruns,
invalid input, and preservation of previous data after validation failures.

## Star schema

`fact_sales` has one row per completed order line, identified by order ID and line number.
It connects to `dim_customer`, `dim_product`, and `dim_date`.
Measures are quantity, unit price, and revenue; dimensions provide country,
product line, and calendar context. This row-level meaning is called the **grain**.

## Expected results

- Three sales lines, six units, one cancelled order excluded.
- Total revenue: **16,500 cents**.
- Product lines: Cars **12,500**, Boats **4,000** cents.
- Countries: Malaysia **9,000**, South Korea **7,500** cents.

## Limits

Small batch demonstration only: no scheduling, streaming, refunds, taxes,
currency conversion, incremental loading, access control, or cloud deployment.
The source already contains fixed prices, and revenue is simply quantity times price.
Future lessons can extend this with orchestration, monitoring, and a cloud architecture.
