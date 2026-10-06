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

Sample each product photo's own background color into an `image_bg` column, so
the storefront can paint every card tile to match its image:

```bash
.venv/Scripts/python scripts/add_image_bg.py
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
| `POST /api/auth/signup` | Create an account; returns a session token |
| `POST /api/auth/login` | Log in; returns a session token |
| `GET /api/auth/me` | Current user from the `Bearer` token |
| `POST /api/chat` | **Stub.** Returns a fixed reply; Problem 5 replaces it |

Interactive docs at http://localhost:8000/docs while the backend runs.

## Layout

```
backend/main.py          FastAPI app
backend/auth.py          Password hashing (PBKDF2) and signed session tokens
scripts/add_category.py  Problem 2a category normalization
scripts/add_image_bg.py  Per-photo background color sampling
frontend/src/
  api.ts                 fetch helpers, price/label formatting, auth calls
  auth.tsx               React auth context (login/signup/logout, session)
  types.ts               shared TypeScript interfaces
  components/            NavBar, ProductCard, ChatPanel
  pages/                 Home, Products, ProductDetail, About, Login, SignUp
output/harness.md        Running design + data notes
AI_prompts.md            Prompt log for the assignment
```

## Accounts

Create-account and login are built (Problem 4). Passwords are stored as
PBKDF2-HMAC-SHA256 hashes with a per-user salt; plaintext is never stored. See
`output/harness.md` for the full design. The seeded test user
`test@campuscustoms.yale.edu` / `password` can be used to log in.

## Not built yet

- **Chat is a stub.** The panel, message history and product-card rendering all
  work; `POST /api/chat` returns a canned reply until Problem 5.
- **No cart or checkout.** The database has no orders table.
