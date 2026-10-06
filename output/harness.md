# Campus Customs — Build Harness

Working notes on the Homework 4 data and the shop/chatbot built on top of it.
Grows as the assignment progresses.

Database: `data/campus_customs.db` (SQLite) · Images: `data/products/` (102 `.jpg` files)

---

## Problem 2 — Database Schema

Five tables, of which four carry data: `catalogue`, `inventory`, `users`,
`chat_messages`. (`sqlite_sequence` is SQLite's internal AUTOINCREMENT
bookkeeping, not application data.)

```
users ──< chat_messages
catalogue ──< inventory
```

### `catalogue` — 102 rows, one per product

| Field | Type | Why it matters |
|---|---|---|
| `product_id` | TEXT, PK | Slug like `basic-hoodie-big-yale`; the join key to `inventory` and the stem of the image filename, so it ties all three data sources together. |
| `name` | TEXT, NOT NULL | The human-readable title the shop and chatbot show to a shopper. |
| `garment_type` | TEXT, NOT NULL | The vendor's raw product-type label. Too inconsistent to filter on directly — kept as source data, superseded by `category`. |
| `description` | TEXT, NOT NULL | Full-sentence prose covering color, fit and graphic; the richest text for the chatbot to answer "what does it look like?" and the best field to embed for semantic search. |
| `colors` | TEXT, NOT NULL | A **JSON array string** (e.g. `["navy", "white"]`), not a plain column — must be parsed before you can answer "do you have it in pink?". |
| `search_tags` | TEXT, NOT NULL | JSON array string of keywords (`"Yale hoodie"`, `"The Game"`); purpose-built for keyword retrieval, catching intent the title misses. |
| `image_file_path` | TEXT, NOT NULL | Relative path (`products/<slug>.jpg`) — the chatbot needs this to show the product, and it must be resolved against `data/` to load. |
| `price` | REAL, NOT NULL | Drives price questions and budget filters. Range $32–$98, mean $58.48. |
| `category` | TEXT | **Derived, added by us** (`scripts/add_category.py`) — the clean 7-value field the shop and chatbot actually filter on. See below. |

### `inventory` — 612 rows, one per product × size

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, PK | Surrogate row key; no business meaning. |
| `product_id` | TEXT, NOT NULL, FK → `catalogue` | Links a stock line back to the product being sold. |
| `size` | TEXT, NOT NULL | One of exactly six values — `XS, S, M, L, XL, XXL` — each appearing 102 times, so every product carries a full size run. Clean enough to filter on directly. |
| `quantity` | INTEGER, NOT NULL | Units on hand, 0–25. **145 of 612 rows are 0**, so the chatbot must check stock per size rather than assume availability — "do you have it in XL?" is a real question with a real no. |

### `users` — 3 rows

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, PK | Identifies the shopper; the key `chat_messages` hangs off, so it's what scopes a conversation to one person. |
| `name` | TEXT, NOT NULL | Full display name. Currently always equals `first_name + ' ' + last_name` — redundant, and a field that can drift out of sync. |
| `email` | TEXT, NOT NULL, UNIQUE | Login identity and the natural account key. |
| `password_hash` | TEXT, NOT NULL | PBKDF2-SHA256 with a per-user salt — correctly hashed, not plaintext. **Must never reach the chatbot's context or any API call.** |
| `created_at` | TEXT, NOT NULL | Signup timestamp, defaulted to `datetime('now')`; useful for cohorting new vs returning shoppers. |
| `first_name` / `last_name` | TEXT, nullable | Lets the chatbot greet someone by first name. Nullable, so greeting code needs a fallback. |

### `chat_messages` — 22 rows (11 user / 11 assistant)

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, PK | Ordering key for replaying a conversation in sequence. |
| `user_id` | INTEGER, NOT NULL, FK → `users` | Scopes history to one shopper — the filter that stops one user seeing another's chat. |
| `role` | TEXT, NOT NULL | `user` or `assistant`; maps directly onto the message roles an LLM API expects when replaying history. |
| `content` | TEXT, NOT NULL | The message text. Assistant turns contain Markdown (`**$68**`, bullet lists), so the UI has to render Markdown, not plain text. |
| `products_json` | TEXT, nullable | Set on assistant turns only (11 of 11). A JSON snapshot of the products that reply recommended, including `inventory` and `total_stock` — it preserves what was shown at the time, so history renders product cards without re-querying. |
| `created_at` | TEXT, NOT NULL | Message timestamp, defaults to `datetime('now')`; separates sessions and orders the transcript. |

### Notes carried forward

- **Two fields are JSON-in-TEXT**: `catalogue.colors` and `catalogue.search_tags`
  (plus `chat_messages.products_json`). SQL `LIKE` on them works but is fragile;
  parse with `json.loads`, or use SQLite's JSON functions.
- **Referential integrity is clean** — no orphan inventory rows, no catalogue
  product missing stock, every user `name` consistent with first/last.
- **No indexes beyond the primary keys.** Fine at 612 rows; worth revisiting only
  if the dataset grows.
- **There is no orders/cart table.** The database supports browsing, search and
  chat — not checkout.

---

## Problem 2a — Normalizing `garment_type` into `category`

### The problem

The vendor's `garment_type` field spreads 102 products across **22 distinct
labels** that overlap in meaning and disagree on casing: `short-sleeve t-shirt`
(16) vs `short-sleeve T-shirt` (6) vs `t-shirt` (1) vs `heavyweight short-sleeve
t-shirt` (1); `pullover hoodie` (18) vs `hoodie` (5) vs `hooded sweatshirt` (1).
A shopper asking for hoodies and a naive `WHERE garment_type = 'hoodie'` would
see 5 products instead of 25.

### What we checked first

Before remapping anything we tested whether the labels were *wrong* or merely
*inconsistent*, by reading each product's `description` against its label. **Every
label agrees with its description.** Where a conflict exists it's the product
*name* that misleads — "School Of Architecture Crewneck" is labelled
`quarter-zip pullover sweatshirt`, and its description confirms "quarter-zip
pullover with a stand collar." Likewise the "Fleece Sweater" products really are
full-zip fleece jackets.

This matters: it makes normalization a safe, deterministic mapping job rather
than a re-classification problem needing an LLM or manual review of 102 items.

### The fix

`scripts/add_category.py` adds a `category` column and populates it from an
explicit 22-entry dictionary. Design choices:

- **Additive.** `garment_type` is never modified, so the vendor's original data
  stays auditable and the mapping can be revised later.
- **Explicit, not fuzzy.** Every raw label is listed by hand. No substring or
  similarity matching that could silently misfile a product.
- **Fails loudly.** The script aborts if the data contains a label the map
  doesn't cover, if any product ends up `NULL`, or if the resulting counts don't
  match the expected totals — so a future data refresh can't quietly degrade.
- **Idempotent.** Re-running repopulates in place rather than duplicating.

### The 7 categories

| Category | Count | Raw labels rolled up |
|---|---:|---|
| `crewneck` | 28 | crewneck sweatshirt · crewneck · raglan crewneck sweatshirt |
| `hoodie` | 25 | pullover hoodie · hoodie · hooded sweatshirt · hooded pullover sweatshirt |
| `t-shirt` | 25 | short-sleeve t-shirt · short-sleeve T-shirt · t-shirt · heavyweight short-sleeve t-shirt · short-sleeve crew-neck t-shirt |
| `quarter-zip` | 11 | quarter-zip pullover sweatshirt · quarter-zip pullover |
| `jacket` | 8 | full-zip fleece jacket · fleece jacket · jacket · bomber jacket |
| `sweatshirt` | 3 | mockneck sweatshirt · full-zip hooded sweatshirt |
| `long-sleeve-shirt` | 2 | long-sleeve performance shirt · men's long-sleeve performance shirt |

Totals to 102. `sweatshirt` is deliberately a catch-all for sweatshirts that are
neither a plain crewneck nor a pullover hoodie — the mockneck and the two
full-zip hooded styles — keeping `crewneck` and `hoodie` meaning exactly what a
shopper expects when they ask for them.

### Verification

Two independent checks agree with the mapping:

1. Keyword presence across name + description + `search_tags` across all 102
   products: 27 mention "hood", 29 "crewneck", 11 "quarter-zip", 8 "jacket",
   25 "t-shirt" — consistent with the category counts once the 3 `sweatshirt`
   products (which mention both "hood" and "crewneck" vocabulary) are accounted
   for.
2. The script's own assertions: no unmapped labels, no `NULL` categories, and
   counts matching expected totals exactly.

### Still true after this fix

`category` is a **filter, not a search engine.** It answers "show me hoodies" but
not "something for my mom" or "Harvard-Yale game gear" — those need
`search_tags` and `description`. Keep both paths.

---

## Problem 3 — The Campus Customs Website

### Brand research (yalebulldogblue.com)

The real store informs both the design and the agent prompt later:

- **Who they are.** Campus Customs has sold Yale gear at 57 Broadway in New
  Haven since 1973 — family-run, now by co-owners Joel and Jeremy Cobden,
  carrying on their father's business. They do large-scale screen printing,
  embroidery and graphic design in house rather than reselling.
- **Palette.** Navy dominant (Yale Blue `#00356b`), white ground, gold accents.
  Serif headings against sans body copy; generous whitespace; grid of product
  cards.
- **Voice.** Enthusiastic but plain-spoken, feature-forward. Real examples:
  *"Casual comfort, classic Bulldog pride"*, *"Add a touch of Bulldog pride"*.
- **Navigation shape.** Organized by constituency, not just garment —
  Residential Colleges, Sports, Relatives, Graduate & Professional Schools. That
  structure is a strong hint for how shoppers actually think, and it matches the
  `search_tags` in our data.

**Copy note:** our Home and About Us text is originally written, informed by that
tone but not lifted from the site. Voice brief chosen for this build: *warm and
personal*, emphasizing **craft/quality** and **belonging**.

### Architecture

```
React + Vite + TS  (localhost:5173)
        |
        |  /api/*  and  /images/*  proxied by Vite
        v
FastAPI backend    (localhost:8000)
        |
        v
data/campus_customs.db  +  data/products/*.jpg
```

The Vite proxy means the browser sees one origin in development, so CORS never
comes up. CORS middleware is configured on the backend anyway for when the two
are served separately.

### API surface (`backend/main.py`)

| Endpoint | Returns |
|---|---|
| `GET /api/health` | Status + product count; useful as a readiness check |
| `GET /api/categories` | The 7 derived categories with counts |
| `GET /api/products` | Grid data; optional `?category=` and `?search=` |
| `GET /api/products/{id}` | Full detail incl. per-size stock, 404 if unknown |
| `GET /images/{file}.jpg` | Static product photography |
| `POST /api/chat` | **Stub** — fixed reply, same response shape as the real agent |

Three decisions worth recording:

1. **JSON-in-TEXT is parsed at the boundary.** `colors` and `search_tags` are
   `json.loads`-ed in the API, so the frontend never sees raw JSON strings.
2. **Sizes are returned in wearing order**, not alphabetical. SQL `ORDER BY size`
   gives `L, M, S, XL, XS, XXL`; the API imposes `XS → XXL` instead.
3. **The chat stub returns the agent's eventual shape** — `{reply, products[]}` —
   so swapping in the real agent in Problem 5 requires no frontend change.

### Frontend pages

| Route | Page |
|---|---|
| `/` | Home — hero, category tiles, featured in-stock products, three craft/belonging pitches |
| `/products` | Grid of all 102, with category chips and debounced search |
| `/products/:productId` | Single item — large image left, details right, per-size stock |
| `/about` | About Us |
| `/login`, `/signup` | Auth forms (render and validate; submit to nothing yet) |

The floating chat panel is mounted globally in `App.tsx`, so it is available on
every page — collapsed to a launcher button in the bottom right, expanding to a
370×520 panel.

### Verified working

- `npm run build` passes `tsc -b` with no type errors.
- Backend returns 102 products; categories match Problem 2 counts exactly.
- Vite proxy resolves `/api/health`, `/images/*.jpg` and `POST /api/chat`.
- `?search=mom` returns exactly *Yale Mom Crewneck* and *Yale Mom Hoodie*;
  `?category=hoodie` returns 25.
- Unknown product id returns 404 rather than a server error.

### Version control

The repository root is **`Homework 4/`**, not the `AI Foundations` folder — that
keeps other coursework and a 95 MB `my-app/node_modules` out of history.

Status: **local only, by choice.** Commits exist on this machine; nothing has
been pushed to a remote. To connect it later, create an empty repo on GitHub and
run:

```bash
git remote add origin <url>
git push -u origin main
```

What's tracked (37 files) and what isn't:

| Excluded | Why |
|---|---|
| `node_modules/` (95 MB) | Reinstallable from `package-lock.json` |
| `.venv/` (37 MB) | Reinstallable from `backend/requirements.txt` |
| `data/` (4 MB) | Fully reproducible: `unzip data.zip` + `scripts/add_category.py`. Committing the binary `.db` would churn history every time the category script runs. |
| `dist/` | Build output |
| `.env` | Pre-emptive — the Problem 5 agent will need an API key, and it must never be committed |

`data.zip` **is** committed as the source of truth, so a fresh clone can rebuild
the database from scratch. Note it contains the three seeded user rows with
PBKDF2 password hashes — fixture data from the assignment, not real credentials,
but worth remembering before making the repo public.

---

## Problem 3a — Design Pass and Image Repair

### The product photos: tried whitening, reverted

**73 of the 102 supplied JPGs are composited on pure black**, while the other 29
ship on white or cream. The mixed backgrounds are a property of the source data,
not of our CSS, so no stylesheet change makes them consistent.

We built `scripts/whiten_product_images.py` to flood-fill the black background
to white, then **reverted it on review** — the whitened images looked worse than
the originals in context. The backend serves `data/products/` directly again and
the script has been removed. It is recoverable from git history at commit
`187ef34` if we ever want to revisit.

**Worth keeping from the attempt**, in case this comes up again:

- A first pass using a flood-fill tolerance of 60 **destroyed the garments**. The
  fill leaked through the shadowed folds of a navy hoodie and dissolved the whole
  product into white.
- Measuring the pixels explained it:

  | Region | RGB |
  |---|---|
  | Background | exactly `(0, 0, 0)` |
  | Navy garment, darkest folds | sum of roughly 40 to 180 across channels |

- A tolerance of **6** separates them cleanly: tight enough never to reach the
  garment, loose enough to take the antialiased edge. That version worked
  technically; it was rejected on aesthetics, not correctness.

**Open question for later:** the catalogue mixes black-background and
white-background photography, so the product grid will look uneven whatever
frame we use. Options if it starts to bother us: a uniform dark image tile, a
per-image background sampled from the photo's own corner, or sourcing
replacement photography.

### Design direction: casual but sophisticated

Moved away from the first pass, which was heavy and institutional (navy slabs,
Georgia serif, hard shadows).

| | Before | After |
|---|---|---|
| Hero | Full-bleed navy gradient block | Warm cream, navy serif headline |
| Palette | `#00356b` navy, `#bd9b60` gold | Softer `#1b3a5f` navy, `#b08d57` brass, cream and sand neutrals |
| Nav | Solid navy bar, white links | Translucent white, blurred, hairline border |
| Type | Georgia, weight 700 | Iowan Old Style / Palatino, weight 400 to 500, tighter tracking |
| Corners | 6px | 10px, 16px on larger surfaces |
| Chat launcher | Circular emoji button | Pill reading "Ask us anything" |

Navy is now an accent rather than the ground. The effect is quieter and more
expensive-looking while staying unmistakably Yale.

### Layout symmetry

Both home-page grids previously used `auto-fit`/`auto-fill`, which left ragged
final rows.

- **"Find your corner of campus"** now uses a fixed 4-column grid. There are 7
  categories, which would leave a gap, so the page adds an eighth **"Shop all"**
  tile. 8 tiles fill 2 complete rows. Tiles are flex columns with a 132px
  minimum height, so every one occupies identical space regardless of label
  length. Collapses to 2 columns under 900px, still even.
- **"Picked for this week"** is pinned to `repeat(4, 1fr)` and the section only
  renders when exactly 4 in-stock products are available, so it can never show a
  partial row. Falls back to 2 columns under 980px and 1 under 540px, both
  symmetric.

### Copy: removing AI tells

Em dashes were stripped from every user-facing string across the frontend,
`index.html` metadata, and the backend chat stub. Replaced with commas, periods,
or parentheses depending on what the sentence needed. Verified by grep: zero
remaining in `frontend/src`, `frontend/index.html` and `backend/main.py`.

The internal documents (this harness, `README.md`, `AI_prompts.md`) still use
them, on the grounds that they are working notes rather than site copy.

### Carried into Problem 5

- The chat stub needs replacing with a real agent; the response contract is
  already fixed.
- The brand facts above (1973, 57 Broadway, in-house printing, family-run) are
  the raw material for the agent's system prompt.
- Auth is still unbuilt — `users.password_hash` is PBKDF2-SHA256 and must never
  enter the agent's context.
