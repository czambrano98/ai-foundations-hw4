# Campus Customs

A Yale apparel storefront built on the Homework 4 dataset: a FastAPI backend
reading `data/campus_customs.db`, and a React + Vite + TypeScript frontend.

## First-time setup

Unzip the data (creates `data/campus_customs.db` and `data/products/`):

```bash
unzip data.zip
```

Add the derived `category` column (see `output/harness.md`, Problem 2a):

```bash
.venv/Scripts/python scripts/add_category.py
```


Install dependencies:

```bash
# backend
python -m venv .venv
.venv/Scripts/python -m pip install -r backend/requirements.txt

# frontend
cd frontend && npm install && cd ..
```

## Running

Two terminals, both from the `Homework 4` directory.

**Terminal 1 — API (port 8000):**

```bash
.venv/Scripts/python -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — site (port 5173):**

```bash
cd frontend && npm run dev
```

Then open **http://localhost:5173**.

Vite proxies `/api` and `/images` to the backend, so the browser sees a single
origin and there are no CORS issues in development.

## API

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Liveness plus product count |
| `GET /api/categories` | The 7 categories with counts, for the filter bar |
| `GET /api/products` | Product grid. Optional `?category=` and `?search=` |
| `GET /api/products/{id}` | Single product including per-size stock |
| `GET /images/{file}.jpg` | Product photography from `data/products/` |
| `POST /api/chat` | **Stub.** Returns a fixed reply; Problem 5 replaces it |

Interactive docs at http://localhost:8000/docs while the backend runs.

## Layout

```
backend/main.py          FastAPI app
scripts/add_category.py  Problem 2a category normalization
frontend/src/
  api.ts                 fetch helpers, price/label formatting
  types.ts               shared TypeScript interfaces
  components/            NavBar, ProductCard, ChatPanel
  pages/                 Home, Products, ProductDetail, About, Login, SignUp
output/harness.md        Running design + data notes
AI_prompts.md            Prompt log for the assignment
```

## Not built yet

- **Chat is a stub.** The panel, message history and product-card rendering all
  work; `POST /api/chat` returns a canned reply until Problem 5.
- **Auth is a stub.** Log in and Create account render and validate, but submit
  to nothing. The `users` table already holds PBKDF2-hashed passwords.
- **No cart or checkout.** The database has no orders table.
