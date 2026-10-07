# Campus Customs — Usability Improvements (Problem 9)

Five improvements: three on the front end, two on the agent/backend. (The
assignment asked for two each; we chose to do an extra front-end one.) For each:
what we added, and why it helps a Campus Customs shopper or the business.

---

## Front end

### 1. Markdown rendering in chat replies

**What we added.** The chat bubble now renders the assistant's Markdown
(`react-markdown`): bold, bullet lists, and links display properly. Before, a
reply like "all priced at **$68**" showed the literal asterisks, and bulleted
product lists ran together as one line.

**Why it helps.** The agent (and the seed replies) naturally write in Markdown,
so this was a visible defect on nearly every answer. Clean formatting makes
prices and lists scannable and makes the shop look professional rather than
broken, which matters for trust on a store that is asking people to buy.

### 2. Shopping filters: in-stock toggle and price sort

**What we added.** The Products page has an "In stock only" checkbox and a sort
control (Featured, Price: Low to High, Price: High to Low), applied to the
current grid.

**Why it helps.** These are the two filters shoppers reach for most. "In stock
only" stops someone falling for an item they cannot actually buy in their size
run, which avoids dead-end frustration; price sorting lets budget shoppers and
gift buyers find something in range fast. For the business, it moves people
toward purchasable, in-budget items with less friction.

### 3. Loading skeletons

**What we added.** While the product grid or a product page loads, the page now
shows shimmer placeholders shaped like the real cards and detail layout, instead
of a "Loading..." text line.

**Why it helps.** Skeletons make the wait feel shorter and keep the layout from
jumping when content arrives, which reads as faster and more polished. A store
that feels snappy keeps shoppers browsing instead of bouncing.

---

## Agent / backend

### 4. Price and in-stock filters on `search_catalogue`

**What we added.** The search tool now takes `max_price` and `in_stock_only` and
filters in SQL. The system prompt tells the agent to pass these for budget
queries ("hoodies under $50") and availability queries ("what's in stock"),
rather than reasoning over prices itself.

**Why it helps.** It is faster and cheaper, and more correct. Before, a budget
query made the model fetch a broad list and reason about prices, which earlier
testing showed it doing poorly (several wasted tool calls for "hoodies under
$70"). Filtering in the database gives the right answer in one call, so the
shopper gets an accurate budget list and the business pays for fewer, shorter
model round-trips.

### 5. Combined `get_product` tool

**What we added.** A single tool that returns a product's description, price,
colors, and per-size stock together. The prompt directs the agent to use it when
a shopper asks broadly about one product, and to keep the narrow single-fact
tools (`get_price`, `get_stock`, `get_product_description`) for one-off questions.

**Why it helps.** A natural question like "tell me about the Mom hoodie, how much
and what sizes?" previously took two or three separate tool calls, each its own
model round-trip. Collapsing that into one call makes the reply arrive faster and
costs less per conversation, while the shopper gets a complete answer in one go.

---

## How each was verified

- **Markdown:** the seed history (which contains `**$68**` and bullet lists) and
  live agent replies now render formatted in the bubble; `npm run build` passes.
- **Filters / skeletons:** build passes; the in-stock/sort logic runs on the
  fetched set; skeletons replace the loading text on both pages.
- **Search filters:** live, "what can I get for under $40?" returned six cards
  all priced at $40 or below.
- **Combined tool:** live, "tell me all about the Basic Hoodie Big Yale, price
  and sizes" was answered with description, price, and sizes from one
  `get_product` call.
