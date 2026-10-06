"""Campus Customs API.

Read-only access to the product catalogue and inventory, plus a stub chat
endpoint that the Problem 5 agent will replace.

Run from the Homework 4 directory:
    .venv/Scripts/python -m uvicorn backend.main:app --reload --port 8000
"""

import json
import re
import sqlite3
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import auth

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
        # The photo's own background color, sampled by scripts/add_image_bg.py.
        # The frontend paints each card tile with it so the image blends into
        # its frame; the catalogue mixes black and white backgrounds. Falls back
        # to white when the column is absent, so the API still works on a
        # database where that script has not been run.
        "image_bg": (row["image_bg"] if "image_bg" in row.keys() else None) or "#ffffff",
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


# --- Accounts -------------------------------------------------------------

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def public_user(row: sqlite3.Row) -> dict:
    """A user shaped for the client. Never includes password_hash."""
    return {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "name": row["name"],
        "email": row["email"],
    }


def current_user(authorization: str | None = Header(default=None)):
    """FastAPI dependency: resolve the bearer token to a user row, or 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = auth.read_token(authorization.removeprefix("Bearer ").strip())
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    with connect() as con:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    return row


@app.post("/api/auth/signup")
def signup(request: SignupRequest):
    first = request.first_name.strip()
    last = request.last_name.strip()
    email = request.email.strip().lower()

    if not first or not last:
        raise HTTPException(status_code=400, detail="First and last name are required")
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Please enter a valid email address")
    if len(request.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
        )
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Hash before touching the database: the plaintext password never reaches
    # a query, a log, or a stored column.
    password_hash = auth.hash_password(request.password)
    full_name = f"{first} {last}"

    with connect() as con:
        existing = con.execute(
            "SELECT 1 FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            raise HTTPException(
                status_code=409, detail="An account with that email already exists"
            )
        cursor = con.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) "
            "VALUES (?, ?, ?, ?, ?)",
            (full_name, email, password_hash, first, last),
        )
        con.commit()
        row = con.execute(
            "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    return {"token": auth.make_token(row["id"]), "user": public_user(row)}


@app.post("/api/auth/login")
def login(request: LoginRequest):
    email = request.email.strip().lower()
    with connect() as con:
        row = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    # Same error whether the email is unknown or the password is wrong, so the
    # response does not reveal which emails have accounts. verify_password is
    # still called on a dummy hash when the user is missing, to keep the timing
    # of the two cases similar.
    if row is None:
        auth.verify_password(request.password, auth.hash_password("dummy"))
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not auth.verify_password(request.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return {"token": auth.make_token(row["id"]), "user": public_user(row)}


@app.get("/api/auth/me")
def me(user: sqlite3.Row = Depends(current_user)):
    return {"user": public_user(user)}


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
            "Thanks for asking! I'm not connected to the shop assistant yet. "
            "That comes in Problem 5. In the meantime you can browse the full "
            "catalogue on the Products page."
        ),
        "products": [],
        "stub": True,
    }
