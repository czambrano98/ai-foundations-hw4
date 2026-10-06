"""Campus Customs API.

Read-only access to the product catalogue and inventory, plus a stub chat
endpoint that the Problem 5 agent will replace.

Run from the Homework 4 directory:
    .venv/Scripts/python -m uvicorn backend.main:app --reload --port 8000
"""

import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "campus_customs.db"
IMAGES_DIR = ROOT / "data" / "products"

# Sizes sort alphabetically in SQL, which puts XL before XS and S before XS.
# This is the order a shopper expects to see them in.
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

app = FastAPI(title="Campus Customs API", version="1.0.0")

# The Vite dev server runs on a different port, so the browser treats API calls
# as cross-origin. Dev-only origins; tighten before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


def connect():
    if not DB_PATH.exists():
        raise RuntimeError(f"Database not found at {DB_PATH}. Unzip data.zip first.")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def short_description(description: str, limit: int = 110) -> str:
    """First sentence of the description, trimmed for a product card."""
    first = description.split(". ")[0].rstrip(".")
    if len(first) <= limit:
        return first + "."
    return first[:limit].rsplit(" ", 1)[0] + "..."


def row_to_product(row: sqlite3.Row) -> dict:
    """Shape a catalogue row for the API.

    `colors` and `search_tags` are JSON arrays stored as TEXT, so they are
    parsed here rather than leaking raw JSON strings to the client.
    """
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "category": row["category"],
        "description": row["description"],
        "short_description": short_description(row["description"]),
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "price": row["price"],
        # The DB stores 'products/<slug>.jpg'; the API serves that directory at
        # /images, so strip the prefix and hand the client a usable URL.
        "image_url": f"/images/{Path(row['image_file_path']).name}",
    }


def sized_inventory(con, product_id: str) -> list[dict]:
    rows = con.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    by_size = {r["size"]: r["quantity"] for r in rows}
    return [
        {
            "size": size,
            "quantity": by_size.get(size, 0),
            "in_stock": by_size.get(size, 0) > 0,
        }
        for size in SIZE_ORDER
        if size in by_size
    ]


@app.get("/api/health")
def health():
    with connect() as con:
        n = con.execute("SELECT COUNT(*) FROM catalogue").fetchone()[0]
    return {"status": "ok", "products": n}


@app.get("/api/categories")
def list_categories():
    """Categories with product counts, for the Products page filter bar."""
    with connect() as con:
        rows = con.execute(
            "SELECT category, COUNT(*) AS n FROM catalogue "
            "GROUP BY category ORDER BY n DESC"
        ).fetchall()
    return [{"category": r["category"], "count": r["n"]} for r in rows]


@app.get("/api/products")
def list_products(category: str | None = None, search: str | None = None):
    """Product grid data.

    `category` filters on the derived column added in Problem 2. `search`
    matches name, description and tags, since category alone can't answer
    queries like "something for my mom".
    """
    sql = "SELECT * FROM catalogue"
    clauses, params = [], []

    if category and category != "all":
        clauses.append("category = ?")
        params.append(category)

    if search:
        clauses.append(
            "(LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(search_tags) LIKE ?)"
        )
        term = f"%{search.lower()}%"
        params += [term, term, term]

    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY name"

    with connect() as con:
        rows = con.execute(sql, params).fetchall()
        products = []
        for row in rows:
            product = row_to_product(row)
            total = con.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM inventory WHERE product_id = ?",
                (row["product_id"],),
            ).fetchone()[0]
            product["total_stock"] = total
            product["in_stock"] = total > 0
            products.append(product)

    return {"count": len(products), "products": products}


@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    """Everything the single-item page needs, including per-size stock."""
    with connect() as con:
        row = con.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"No product '{product_id}'")

        product = row_to_product(row)
        product["inventory"] = sized_inventory(con, product_id)

    product["total_stock"] = sum(s["quantity"] for s in product["inventory"])
    product["in_stock"] = product["total_stock"] > 0
    product["available_sizes"] = [s["size"] for s in product["inventory"] if s["in_stock"]]
    return product


class ChatRequest(BaseModel):
    message: str
    user_id: int | None = None


@app.post("/api/chat")
def chat(request: ChatRequest):
    """Stub. Problem 5 replaces this with the real agent.

    Returns the same shape the agent will, so the frontend doesn't change:
    a reply string plus any products to render as cards.
    """
    return {
        "reply": (
            "Thanks for asking! I'm not connected to the shop assistant yet — "
            "that comes in Problem 5. In the meantime you can browse the full "
            "catalogue on the Products page."
        ),
        "products": [],
        "stub": True,
    }
