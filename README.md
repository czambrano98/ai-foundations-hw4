# Campus Customs

A Yale apparel storefront built on the Homework 4 dataset: a FastAPI backend
reading `data/campus_customs.db`, and a React + Vite + TypeScript frontend.

## First-time setup

**1. Place the data pack.** The database and product images are not in this repo.
Put the provided `data.zip` in the project root and unzip it (this creates
`data/campus_customs.db` and `data/products/`):

```bash
unzip data.zip
```

**2. Install dependencies:**

```bash
# backend (Python)
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt

# frontend (Node)
cd frontend && npm install && cd ..
```

**3. Prepare the database.** Add the derived `category` column (harness Problem
2a) and sample each photo's background color into `image_bg`:

```bash
.venv/Scripts/python scripts/add_category.py
.venv/Scripts/python scripts/add_image_bg.py
```

**4. Set the API key.** Copy `.env.example` to `.env` and fill in your
`PORTKEY_API_KEY` (the agent needs it; products and auth work without it):

```bash
cp .env.example .env   # then edit .env
```

## Running

**Terminal 1 — API (port 8000), from the `backend/` folder:**

```bash
cd backend
uvicorn main:app --reload --port 8000
# or, using the project venv explicitly:
# ../.venv/Scripts/python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 — site (port 5173), from `frontend/`:**

```bash
cd frontend && npm run dev
```

Then open **http://localhost:5173**.

Vite proxies `/api` and `/images` to the backend, so the browser sees a single
origin and there are no CORS issues in development.

### Agent API key

The chat agent calls a model through the Portkey gateway and needs
`PORTKEY_API_KEY`. On first use the backend looks for it in this order:
the environment, `backend/.env`, the project-root `.env` (copy from
`.env.example`), then an `env.txt` in the root or its parent. The agent is built
lazily, so the rest of the API (products, auth) runs even without the key.

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
| `POST /api/chat` | Shop agent: returns a reply plus product cards |

Interactive docs at http://localhost:8000/docs while the backend runs.

## Layout

```
backend/main.py          FastAPI app (run: uvicorn main:app from backend/)
backend/auth.py          Password hashing (PBKDF2) and signed session tokens
backend/agent.py         Shop chat agent: prompt + Portkey model + tools wiring
backend/tools.py         Read-only catalogue tools the agent can call
backend/models.py        Pydantic / PydanticAI types (chat reply, product card)
backend/audit.py         Append-only agent-loop audit trail
backend/prompts/prompt.md  System prompt (voice + safety rules)
scripts/add_category.py  Problem 2a category normalization
scripts/add_image_bg.py  Per-photo background color sampling
frontend/src/
  api.ts                 fetch helpers, price/label formatting, auth calls
  auth.tsx               React auth context (login/signup/logout, session)
  types.ts               shared TypeScript interfaces
  components/            NavBar, ProductCard, ChatPanel
  pages/                 Home, Products, ProductDetail, About, Login, SignUp
output/harness.md        Running design + data notes + system reference
output/audit_trail.json  Append-only log of agent tool calls and stop reasons
output/usability.md      Problem 9 usability write-up
output/design.md         Problem 10 design write-up
output/app_check.html    Problem 11 live-site checks (open in a browser)
AI_prompts.md            Prompt log for the assignment
```

## Accounts

Create-account and login are built (Problem 4). Passwords are stored as
PBKDF2-HMAC-SHA256 hashes with a per-user salt; plaintext is never stored. See
`output/harness.md` for the full design. The seeded test user
`test@campuscustoms.yale.edu` / `password` can be used to log in.

## Chat agent

The shop assistant (Problem 5) is a PydanticAI agent in `backend/agent.py`,
loaded from `backend/prompts/prompt.md` and backed by `gpt-4o` through Portkey.
It can call read-only catalogue tools (`backend/tools.py`) to look up products,
prices, and per-size stock, and returns a reply plus the product ids to show as
cards. The API hydrates those ids into real cards, so prices and stock are
always from the database, never the model. See `output/harness.md` for the data
flow and safety notes.

## Not built yet

- **No cart or checkout.** The database has no orders table.
