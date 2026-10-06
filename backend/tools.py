"""Tools the Campus Customs agent can call.

Each function is a tool the agent may invoke to read real data from
`data/campus_customs.db`. The docstrings matter: the model reads them to decide
when and how to call each tool, so they describe behaviour in plain terms.

Everything here is read-only. The agent can look things up; it cannot change the
catalogue, inventory, or any account.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from models import (
    ProductDescription,
    ProductPrice,
    SizeStock,
    StockReport,
)

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "campus_customs.db"

# Shopper-facing size order, not SQL's alphabetical one.
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

# Spoken size words the agent might pass through, mapped to catalogue sizes.
_SIZE_ALIASES = {
    "XS": "XS", "EXTRA SMALL": "XS", "XSMALL": "XS", "X-SMALL": "XS",
    "S": "S", "SMALL": "S",
    "M": "M", "MEDIUM": "M", "MED": "M",
    "L": "L", "LARGE": "L",
    "XL": "XL", "EXTRA LARGE": "XL", "XLARGE": "XL", "X-LARGE": "XL",
    "XXL": "XXL", "2XL": "XXL", "XX-LARGE": "XXL", "DOUBLE XL": "XXL",
}


def _normalize_size(size: str) -> str | None:
    """Map a free-text size to a catalogue size, or None if unrecognized."""
    return _SIZE_ALIASES.get(size.strip().upper().replace("  ", " "))

# Query words that carry no product meaning, so matching on them only adds
# noise. Price and quantity words are dropped too (the caller filters on price
# from the returned values, not via text search).
_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "with", "to", "in", "on", "of", "my",
    "me", "i", "you", "your", "please", "show", "have", "has", "do", "does",
    "what", "which", "any", "some", "something", "about", "around", "up",
    "under", "over", "below", "above", "than", "less", "more", "most", "least",
    "cheap", "cheaper", "cheapest", "price", "priced", "cost", "costs", "dollar",
    "dollars", "buck", "bucks", "gift", "looking", "want", "need", "like",
}


def _tokens(query: str) -> list[str]:
    """Break a free-text query into meaningful search tokens.

    Drops stopwords and bare numbers, and adds a crude singular form so a
    plural like "hoodies" still matches the catalogue's "hoodie".
    """
    tokens: set[str] = set()
    for word in re.findall(r"[a-z0-9]+", query.lower()):
        if len(word) < 3 or word.isdigit() or word in _STOPWORDS:
            continue
        tokens.add(word)
        if word.endswith("s") and len(word) > 3:
            tokens.add(word[:-1])
    return sorted(tokens)


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _short_description(description: str, limit: int = 110) -> str:
    first = description.split(". ")[0].rstrip(".")
    if len(first) <= limit:
        return first + "."
    return first[:limit].rsplit(" ", 1)[0] + "..."


def _summary(row: sqlite3.Row, total_stock: int) -> dict:
    """Compact product view for the agent to reason over."""
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "category": row["category"],
        "price": row["price"],
        "colors": json.loads(row["colors"]),
        "short_description": _short_description(row["description"]),
        "in_stock": total_stock > 0,
    }


def search_catalogue(
    query: str, category: str | None = None, max_results: int = 6
) -> list[dict]:
    """Search the Campus Customs catalogue for products matching free text.

    Matches the query against product names, descriptions, and search tags, so
    it handles both garment words ("navy hoodie") and intent words ("gift for
    my mom", "Harvard-Yale game"). Optionally narrow to one category.

    Args:
        query: What the shopper is looking for, in their own words.
        category: Optional exact category to filter to. Valid values come from
            list_categories (e.g. "hoodie", "crewneck", "t-shirt",
            "quarter-zip", "jacket", "sweatshirt", "long-sleeve-shirt"). Leave
            empty to search all categories.
        max_results: Maximum number of products to return (default 6).

    Returns:
        A list of matching products, each with product_id, name, category,
        price, colors, a short description, and whether it is in stock. May be
        empty if nothing matches.
    """
    limit = max(1, min(max_results, 24))
    clauses, params = [], []

    if category:
        clauses.append("category = ?")
        params.append(category)

    # Match any meaningful token against name, description, or tags. Matching on
    # ANY token (rather than the whole phrase) means intent queries like
    # "hoodies under $70" still find hoodies instead of matching nothing.
    tokens = _tokens(query) if query else []
    if tokens:
        per_token = "(LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(search_tags) LIKE ?)"
        clauses.append("(" + " OR ".join([per_token] * len(tokens)) + ")")
        for token in tokens:
            term = f"%{token}%"
            params += [term, term, term]

    sql = "SELECT * FROM catalogue"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY name LIMIT ?"
    params.append(limit)

    with _connect() as con:
        rows = con.execute(sql, params).fetchall()

        # If the text tokens knocked everything out but a category was given,
        # fall back to the category listing: "show me hoodies" with noisy
        # wording should still return hoodies.
        if not rows and category:
            rows = con.execute(
                "SELECT * FROM catalogue WHERE category = ? ORDER BY name LIMIT ?",
                (category, limit),
            ).fetchall()

        out = []
        for row in rows:
            total = con.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM inventory WHERE product_id = ?",
                (row["product_id"],),
            ).fetchone()[0]
            out.append(_summary(row, total))
    return out


def get_product_description(product_id: str) -> ProductDescription | str:
    """Look up what a product is: its full description, category, and colors.

    Use this for questions about what a product looks like, what it is made of,
    or what colors it comes in. Does not include price or stock (use get_price
    and get_stock for those).

    Args:
        product_id: The product_id from a search_catalogue result.

    Returns:
        A ProductDescription, or an error string if no product has that id.
    """
    with _connect() as con:
        row = con.execute(
            "SELECT product_id, name, category, description, colors "
            "FROM catalogue WHERE product_id = ?",
            (product_id,),
        ).fetchone()
    if row is None:
        return f"No product has the id '{product_id}'."
    return ProductDescription(
        product_id=row["product_id"],
        name=row["name"],
        category=row["category"],
        description=row["description"],
        colors=json.loads(row["colors"]),
    )


def get_price(product_id: str) -> ProductPrice | str:
    """Look up the price of a product, from the database.

    Use this for any price question. Never state a price without calling this
    (or reading it from a search_catalogue result); do not estimate or round.

    Args:
        product_id: The product_id from a search_catalogue result.

    Returns:
        A ProductPrice, or an error string if no product has that id.
    """
    with _connect() as con:
        row = con.execute(
            "SELECT product_id, name, price FROM catalogue WHERE product_id = ?",
            (product_id,),
        ).fetchone()
    if row is None:
        return f"No product has the id '{product_id}'."
    return ProductPrice(
        product_id=row["product_id"], name=row["name"], price=row["price"]
    )


def get_stock(product_id: str, size: str | None = None) -> StockReport | str:
    """Look up how many units of a product are in stock, by size.

    Use this for any availability question. When the shopper names a size, pass
    it (e.g. "M" or "medium") and the report focuses on that size; always check
    here before telling a shopper a size is available. When no size is named,
    the report covers the full size run.

    `available_sizes` always lists every size currently in stock, so if the
    requested size is sold out you can offer the sizes that are not. A size with
    quantity 0 is out of stock and must be described as such, clearly.

    Args:
        product_id: The product_id from a search_catalogue result.
        size: Optional size the shopper asked about (XS, S, M, L, XL, XXL, or a
            word like "medium"). Leave empty to report all sizes.

    Returns:
        A StockReport, or an error string if the product id or size is not
        recognized.
    """
    with _connect() as con:
        row = con.execute(
            "SELECT product_id, name FROM catalogue WHERE product_id = ?",
            (product_id,),
        ).fetchone()
        if row is None:
            return f"No product has the id '{product_id}'."
        stock_rows = con.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?",
            (product_id,),
        ).fetchall()

    by_size = {r["size"]: r["quantity"] for r in stock_rows}
    all_sizes = [
        SizeStock(size=s, quantity=by_size[s], in_stock=by_size[s] > 0)
        for s in SIZE_ORDER
        if s in by_size
    ]
    available = [s.size for s in all_sizes if s.in_stock]
    total = sum(s.quantity for s in all_sizes)

    requested = None
    sizes = all_sizes
    if size is not None:
        requested = _normalize_size(size)
        if requested is None:
            return (
                f"'{size}' is not a size we recognize. Sizes are "
                f"{', '.join(SIZE_ORDER)}."
            )
        sizes = [s for s in all_sizes if s.size == requested]

    return StockReport(
        product_id=row["product_id"],
        name=row["name"],
        sizes=sizes,
        available_sizes=available,
        total_stock=total,
        in_stock=(sizes[0].in_stock if requested else total > 0),
        requested_size=requested,
    )


def list_categories() -> list[dict]:
    """List the product categories with how many products each has.

    Use this to ground category filters or to answer "what kinds of things do
    you sell". Returns each category with its product count.
    """
    with _connect() as con:
        rows = con.execute(
            "SELECT category, COUNT(*) AS n FROM catalogue "
            "GROUP BY category ORDER BY n DESC"
        ).fetchall()
    return [{"category": r["category"], "count": r["n"]} for r in rows]
