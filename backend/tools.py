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

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "campus_customs.db"

# Shopper-facing size order, not SQL's alphabetical one.
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

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


def get_product_details(product_id: str) -> dict | None:
    """Get full details for one product, including per-size stock.

    Use this when a shopper asks about a specific product: its full
    description, price, colors, and which sizes are actually in stock right
    now.

    Args:
        product_id: The product_id from a search_catalogue result.

    Returns:
        The product's full details, or None if no product has that id. The
        `sizes` field lists each size with its quantity and whether it is in
        stock, and `available_sizes` lists just the sizes a shopper can buy
        today.
    """
    with _connect() as con:
        row = con.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None

        stock_rows = con.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()

    by_size = {r["size"]: r["quantity"] for r in stock_rows}
    sizes = [
        {"size": s, "quantity": by_size[s], "in_stock": by_size[s] > 0}
        for s in SIZE_ORDER
        if s in by_size
    ]
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "category": row["category"],
        "price": row["price"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "sizes": sizes,
        "available_sizes": [s["size"] for s in sizes if s["in_stock"]],
        "total_stock": sum(s["quantity"] for s in sizes),
    }


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
