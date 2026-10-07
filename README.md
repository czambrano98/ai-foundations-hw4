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
`PORTKEY_API_KEY`. On first use the backend looks for it in, in order:
`backend/.env`, `Homework 4/env.txt`, then the parent `AI Foundations/env.txt`
(where it already lives). The agent is built lazily, so the rest of the API
(products, auth) runs even without the key.

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
