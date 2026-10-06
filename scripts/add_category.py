"""Add a derived `category` column to catalogue.

The raw `garment_type` field uses 22 inconsistent labels for 102 products
(e.g. 'short-sleeve t-shirt' vs 'short-sleeve T-shirt' vs 't-shirt'), which
makes it useless as a filter. This maps those labels onto 7 canonical
categories.

`garment_type` is left untouched; `category` is added alongside it. Safe to
re-run.

Usage:  python add_category.py [path/to/campus_customs.db]
"""

import sqlite3
import sys
from pathlib import Path

# Raw garment_type label -> canonical category.
# Every one of the 22 labels present in the data is listed explicitly; nothing
# is inferred by fuzzy matching, so the mapping is auditable at a glance.
CATEGORY_MAP = {
    # t-shirt (25)
    "short-sleeve t-shirt": "t-shirt",
    "short-sleeve T-shirt": "t-shirt",
    "t-shirt": "t-shirt",
    "heavyweight short-sleeve t-shirt": "t-shirt",
    "short-sleeve crew-neck t-shirt": "t-shirt",
    # crewneck (28)
    "crewneck sweatshirt": "crewneck",
    "crewneck": "crewneck",
    "raglan crewneck sweatshirt": "crewneck",
    # hoodie (25)
    "pullover hoodie": "hoodie",
    "hoodie": "hoodie",
    "hooded sweatshirt": "hoodie",
    "hooded pullover sweatshirt": "hoodie",
    # quarter-zip (11)
    "quarter-zip pullover sweatshirt": "quarter-zip",
    "quarter-zip pullover": "quarter-zip",
    # jacket (8)
    "full-zip fleece jacket": "jacket",
    "fleece jacket": "jacket",
    "jacket": "jacket",
    "bomber jacket": "jacket",
    # sweatshirt (3) -- sweatshirts that are neither a plain crewneck nor a
    # pullover hoodie: the mockneck collar and the full-zip hooded styles.
    "mockneck sweatshirt": "sweatshirt",
    "full-zip hooded sweatshirt": "sweatshirt",
    # long-sleeve-shirt (2)
    "long-sleeve performance shirt": "long-sleeve-shirt",
    "men's long-sleeve performance shirt": "long-sleeve-shirt",
}

EXPECTED = {
    "crewneck": 28,
    "hoodie": 25,
    "t-shirt": 25,
    "quarter-zip": 11,
    "jacket": 8,
    "sweatshirt": 3,
    "long-sleeve-shirt": 2,
}


def main(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Fail loudly if the data contains a label the map does not cover, rather
    # than silently leaving those products uncategorised.
    found = {r[0] for r in cur.execute("SELECT DISTINCT garment_type FROM catalogue")}
    unmapped = found - CATEGORY_MAP.keys()
    if unmapped:
        raise SystemExit(f"ERROR: unmapped garment_type values: {sorted(unmapped)}")

    columns = {r[1] for r in cur.execute("PRAGMA table_info(catalogue)")}
    if "category" not in columns:
        cur.execute("ALTER TABLE catalogue ADD COLUMN category TEXT")
        print("Added column catalogue.category")
    else:
        print("Column catalogue.category already exists -- repopulating")

    for raw, category in CATEGORY_MAP.items():
        cur.execute(
            "UPDATE catalogue SET category = ? WHERE garment_type = ?", (category, raw)
        )

    missing = cur.execute(
        "SELECT COUNT(*) FROM catalogue WHERE category IS NULL"
    ).fetchone()[0]
    if missing:
        raise SystemExit(f"ERROR: {missing} products still have no category")

    counts = dict(
        cur.execute("SELECT category, COUNT(*) FROM catalogue GROUP BY category")
    )
    if counts != EXPECTED:
        raise SystemExit(f"ERROR: counts {counts} do not match expected {EXPECTED}")

    con.commit()

    total = sum(counts.values())
    print(f"\n{total} products categorised:\n")
    for category, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {category:<20} {n:>3}")
    con.close()


if __name__ == "__main__":
    default = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
    main(sys.argv[1] if len(sys.argv) > 1 else default)
