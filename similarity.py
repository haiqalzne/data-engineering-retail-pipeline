"""Toy numeric-vector similarity and a popularity fallback; not an AI model."""

import math
import sqlite3
from contextlib import closing
from pathlib import Path

from pipeline import ROOT

# Manually assigned features: [car category, boat category, size score].
# These explain vector search; they are not trained embeddings or a vector database.
FEATURES = {"P1": (1, 0, 0.3), "P2": (0, 1, 0.7), "P3": (1, 0, 0.4)}


def recommend(product_id, database_path):
    if product_id in FEATURES:
        query = FEATURES[product_id]
        scored = []
        for candidate, vector in FEATURES.items():
            if candidate != product_id:
                score = sum(a * b for a, b in zip(query, vector)) / (
                    math.sqrt(sum(a * a for a in query)) * math.sqrt(sum(b * b for b in vector)))
                scored.append((score, candidate))
        return {"method": "toy_similarity", "products": [p for _, p in sorted(scored, reverse=True)]}
    # Unknown products use the batch sales data as a simple fallback.
    with closing(sqlite3.connect(Path(database_path).resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        products = [row[0] for row in connection.execute(
            "SELECT product_id FROM fact_sales GROUP BY product_id ORDER BY SUM(quantity) DESC, product_id")]
    return {"method": "popularity_fallback", "products": products}


if __name__ == "__main__":
    import json
    print(json.dumps(recommend("P1", ROOT / "output/warehouse.db"), indent=2))
    print(json.dumps(recommend("unknown", ROOT / "output/warehouse.db"), indent=2))
