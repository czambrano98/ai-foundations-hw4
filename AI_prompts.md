# Homework 4 — AI Prompt Log

Carine Zambrano · AI Foundations · Fall 2026

A record of the prompts I gave Claude Code while working through Homework 4. Each
section covers one problem and lists my initial prompt, the follow-up prompt I
needed, and what the first answer was missing.

---

## Problem 1 — Vibe Coder Prompts

**Initial prompt**

> hello! today, we'll be working off the Homework 4 folder within AI Foundations.
> let's create AI_prompts.md, and this will be the log of what I type into here.
> we need one section for each problem, and each section must include: 1. the
> problem number and title 2. at least one prompt I typed 3. one follow-up prompt
> and one sentence on what was lacking after the first

**Follow-up prompt**

> BTW, that was Problem 1: Vibe coder prompts. could you pls amend the
> AI_prompts.md file?

**What was lacking after the first prompt**

My first prompt described the format of the log but never said which problem we
were on, so Claude could only produce an empty template section — it had no
problem number or title to write down, and the Homework 4 folder contained just
`data.zip` with no assignment document to infer them from.

---

## Problem 2 — Analyze the Database

**Initial prompt**

> this is Problem 2: Analyze the database
> we'll look into the database data/campus_customs.db and understand the fields
> of each table. at minimum, we should understand catalogue, inventory, and users
> then we'll start the file output/hardness.md, in which we'll write down each
> table and its fields, and one short line on why each field matters for the shop
> or the chatbot. we'll keep growing this harness file in later problems

**Follow-up prompts**

> How should we address the garment_type situation?

> Yes, let's move ahead with adding a derived category column, but instead of
> rolling mockneck sweatshirt and full-zip hooded sweatshirt into crewneck and
> hoodie, respectively, let's create a new sweatshirt category

**What was lacking after the first prompt**

The first pass documented the schema and surfaced that `garment_type` uses 22
inconsistent labels for 102 products, but it only flagged the problem — it
didn't propose or implement a fix, so the harness described a broken filter
without resolving it.

---

## Problem 3 — Build the Campus Customs Website

**Initial prompt**

> Now, this is Problem 3: Build the Campus Customs website
> first, let's research yalebulldogblue.com for the style of Campus Customs page
> and information for our agent prompt
> we'll scaffold a react + vite + typescript front end for Campus Customs. we'll
> put a navigation bat at the top that anchors to Home, Products, About Us, Log
> in, and Create account
> let's pull the Campus Customs-style wording from yalebulldogblue.com for Home
> and About Us, but we should twist it so it reflects my voice (let me know what
> you need to tailor that)
> on the Products page, we'll display the product images from the catalogue
> (using the image paths in the database) with basic product info (name, price,
> and short description)
> we'll also need to make each product open a single-item page (large image on
> one side, full product text on the other with a description, price, sizes/stock
> when you have them. when someone clicks on a card on Product, it should take
> the shopper to that page
> we'll then add the chat interface in the bottom right of the side (a floating
> chat panel). the chat doesn't need to talk to an agent yet (a stub that will
> call our backend later should be enough for this problem)
> we'll also need an API to read the database. we can start with backend/main.py
> for the products and images, which we can then grow in Problem 5

**Follow-up prompts**

> (answering Claude's question on voice) Tone: warm & personal — first-person,
> conversational, leaning on the family-business story. Emphasis: craft & quality
> and belonging.

> Instead of putting the website locally, can we connect it to my Github? but,
> let's not push it live just yet, let's leave it in draft mode

> (answering Claude's question on what "draft mode" meant) Local commits only,
> no push. When ready, I'll create the repo on GitHub and hand over the URL.

**What was lacking after the first prompt**

The first prompt specified the whole build but left "my voice" undefined, so
Claude had everything it needed except the one input required to write the Home
and About Us copy — it had to stop and ask for a tone before that part could be
written.

> OK, the white background also looks wack. Can we revert to the original pls?

> Oooh, let's sample each photo's own corner color, and use it as that card's
> background

> This is the URL: https://github.com/czambrano98/ai-foundations-hw4
> While you're wiring, let's also make some website edits:
> For design, let's make it casual, but sophisticated
> Let's remove AI-recognizable copy (like the em dashes)
> For the cards on "Find your corner of campus," let's make sure they're
> symmetrical and occupy the same space across the rows
> For the pictures on "Picked for this week," let's put the pictures on a white
> background bc the black looks unprofessional, and let's also make sure that it
> only displays one row for symmetry

**Note on the second follow-up**

"Draft mode" was ambiguous between *private repo* and *nothing pushed at all*, and
the two differ in whether code leaves the machine — so Claude set up the local
repository and committed, then asked before doing anything outward-facing.

**Note on the third follow-up**

The first build looked AI-generated in three specific ways that only became
obvious on screen: em dashes throughout the copy, ragged final rows from CSS
`auto-fit` grids, and product photos sitting on black. The last turned out not to
be a styling problem at all — 73 of the 102 source JPGs have black baked into the
pixels, so it needed an image-processing pass rather than a CSS change.

**Note on the design iterations**

I am particular about the design of the website, so Problem 3 took several
rounds rather than one. The product images alone went through three states:
original black backgrounds, then flood-filled to white (which I rejected), then
reverted to the originals with each card tile painted the color sampled from its
own photo. That last version is the one I wanted, and it was not something
either of us specified up front — it came out of looking at the result and
reacting to it.

The general pattern across this problem: the first output was structurally
correct but visually generic, and getting to something I actually liked took
me describing what looked wrong in plain terms and iterating on it. Worth
recording because the prompts that moved the design forward were short reactions
("the white background also looks wack") rather than detailed specifications.

---

## Problem 4 — Create Account and Login

**Initial prompt**

> this is now Problem 4: Create account and login
> build a create-account/login flow
> for create account, it should be first name, last name, email, password (and
> confirm password pls)
> log in it's email and password
> new accounts go into the users table, and let's make sure that it can store
> passwords securely so hackers (either human or AI) cannot access them
> the seed database already has a test user that we can use while building
> (test@campuscustoms.yale.edu;password). let's confirm we can log in as that
> user, and that a brand-new account we create also works
> let's update output/harness.md with how auth words (what we store for a user
> and how passwords are protected)

**Follow-up prompt**

> (none needed — the initial prompt specified the fields, the storage
> requirement, the exact test credential to verify against, and the harness
> update, so there was enough to build and verify the whole flow in one pass.)

**What was lacking after the first prompt**

Nothing substantive was missing from the instructions. The only unknown that had
to be discovered rather than specified was the seed hash's parameters: the stored
format omits the iteration count, so the exact PBKDF2 settings had to be
recovered by reproducing the provided test credential before existing users
could be verified with the same code that creates new ones.

---

## Problem 5 — PydanticAI Agent Backend

**Initial prompt**

> now, we're on Problem 5: PydanticAI agent backend
> let's build the shop chatbot as a PydanticAI agent behind FastPI, plugged into
> our front-end chat widget. let's put the API app in backend/main.py, which is
> the file that we run with Uvicorn. we'll keep the agent as these four files next
> to it (same idea as HW3):
> 1. backend/prompts/prompt.md (system prompt, which we'll grow in later probs)
> 2. backend/agent.py (agent entry and wiring)
> 3. backend/tools.py (tools that the agent can call)
> 4. backend/models.py (Pydantic and PydanticAI structured types)
> In main.py, we'll expose a chat route so a message from the website retuns a
> reply from the agent (and whatever else we need for products/auth). we'll need
> our AI model API key for the agent (the portkey api key is an env file on the
> AI foundations folder)
> then, we'll put Campus Customs voice and safety basics into prompts/prompts.md
> (in which we'll expand tools and safety later). we'll start or update types in
> models.py for chat replies and/or product cards as needed
> In output/harness.md, we'll note how the front end talks to FastAPI and how the
> agent is loaded (prompt file + model)
> Let's make sure that the backend runs from the backend/ folder like: uvicorn
> main:app --reload --port 8000

**Follow-up prompt**

> Let's rerun, since the model flagged a message

(This came after a safety classifier stopped a mid-task message during the
password-calibration step; re-running continued the build without changing the
plan.)

**What was lacking after the first prompt**

The instructions were complete, but the first working build had three issues that
only surfaced when the agent was actually run: the catalogue search matched the
query as one literal phrase (so "hoodies under $70" found nothing until retried
as "hoodie"), the model sometimes emitted the output field as `product_id`
instead of `product_ids` (silently dropping the cards until the schema was made
strict), and the Portkey/Azure content filter returned a 400 on a jailbreak test
that had to be caught and turned into a safe refusal rather than a server error.

---

## Problem 6 — Tools: Product Info and Stock

**Initial prompt**

> now, we're Problem 6: Tools: product info and stock
> let's give the agent tools that look up real information from
> campus_customs.db: 1. product description 2. price, and 3. how many are in
> stock (by size when the customer asks). the agent must use the database, it
> cannot invent prices or quantities. if a size is out of stock, then we need to
> say so clearly
> then we'll expand prompts/prompt.md so the agent knows to call these tools for
> price and stock questions. we'll add or update return types in models.py
> In output/harness.md, we'll list each tool and explain which model fields we
> chose for lookup results and why

**Follow-up prompt**

> (none needed — the three lookup types, the grounding requirement, the
> out-of-stock clarity, the prompt expansion, the typed returns, and the harness
> note were all specified, so it built and verified in one pass.)

**What was lacking after the first prompt**

Nothing was missing from the instructions. The one design judgment left open was
how finely to split the tools: Problem 5 already had a single rich
`get_product_details`, and the choice to break it into three narrow typed tools
(description, price, stock) was made to match the three items the prompt listed
and to keep price and stock as single authoritative sources the model cannot
blur together.

---

## Problem 7 — Chat Search That Updates the Page

**Initial prompt**

> now, we're on Problem 7: Chat search that updates the page
> now, we'll add a feature to the site so that when a customer asks about a type
> of item (e.g., "what hoodies do you have?"), the agent should search the
> catalogue and the website should dynamically show these matching items as
> product cards (image, name, price, short info). this is an API contract: the
> agent returns structured product matches and then the front end renders them on
> the website
> after the dynamic product cards are loaded by this new feature, we'll make sure
> that the same single-item behavior we built on problem 3 still works (that is,
> each product card, inc the ones the chat just put on the page, should still open
> that detail view (large image + full info) when clicked)
> we should also update prompts/prompt.md and output/harness.md so it's clear how
> search results reach the page

**Follow-up prompt**

> (none needed — the feature, the API-contract framing, the single-item
> requirement, and the two doc updates were all specified.)

**What was lacking after the first prompt**

The structured API contract the prompt asks for already existed from Problem 5:
`/api/chat` already returned product matches with image, name, price, and short
info. So the real gap was only on the front end, where those matches were being
shown as small text links inside the chat bubble instead of as product cards on
the page. The main design judgment left open was where on the site the cards
should appear; the Products page was chosen because the floating chat panel is too
narrow for real cards and the page already has the grid and card component.

---

## Problem 8 — Customer Memory

**Initial prompt**

> We're all set! Now, we're on Problem 8: Customer memory
> when a shopper is logged in, we should save their chat history in the database
> in an appropriate table and reload it when they return. the chatbot should know
> who is chatting (name and email), put that in agent deps (or an equivalent clear
> pattern) and/or tools the agent can call.
> also, we should pass enough page context so that if someone is in a product page
> and asks something like, "do you have this in yellow?" the agent knows which
> item they mean (this should be code into the agent context)
> guests can still chat, but history only needs to exist for logged in users
> we should document in output/harness.md, how user chat history is stored, what
> customer fields the agent sees, and how page context is passed

**Follow-up prompt**

> I tested the chat, and when I asked if the hoodie was available in white,
> instead of showing the results for that, it just showed me the product that I
> was viewing

**What was lacking after the first prompt**

The page-context feature worked, but it interacted badly with the Problem 7
"show results on the page" behavior: asking about the product you are already
viewing made the agent return that product as a match, which navigated you to the
Products page to show the single item you were already looking at. The fix was to
tell the agent not to echo the currently-viewed product back as a card (answer in
the message instead), plus a frontend guard that only updates the page with
products the shopper is not already viewing. (Also note: the right table,
`chat_messages`, already existed in the seed schema, and the chosen patterns were
PydanticAI `instructions` for fresh per-run context and replayed `message_history`
for memory, exposing only name and email to the agent, never the password hash.)

---

## Problem 9 — Usability Improvements

**Initial prompt**

> now, we'll need to choose and implement two front-end usability improvements
> and two agent/backend usability improvements (which can be new agent tools or
> things that make the agent run faster and cheaper
> can you help me brainstorm options?
> once we decide, we'll write output/usability.md, specifying for each
> improvement, 1. what we added, and 2. why it helps a campus customs shopper or
> the business

**Follow-up prompt**

> (via the brainstorm selection) Front end: Markdown in chat replies, shopping
> filters (stock + price sort), and loading skeletons. Backend: price + in-stock
> search filters, and a combined get_product tool.

**What was lacking after the first prompt**

The first prompt asked for a brainstorm rather than an immediate build, so what
was "lacking" was the decision itself: the options had to be laid out with
trade-offs (which front-end rough edges were real defects, which backend changes
actually reduce model round-trips) before picking. The shopper chose three
front-end items instead of two, so we over-delivered there.

---

## Problem 10 — Style the Website

**Initial prompt**

> now, we're on Problem 10: Style the website
> we should add creative designs so the site feels like a real Campus Customs
> storefront (fonts, color, hierarchy, motion, product presentation, chat feel,
> etc). we'll get points for being creative, so keep that in mind
> we'll then write output/design.md, describing what we changed and why it should
> help customers stick around and buy. it should be concrete and short

**Follow-up prompt**

> (none needed — the brief named the areas to work on, flagged that creativity is
> graded, and specified the design.md deliverable, so one creative pass covered it.)

**What was lacking after the first prompt**

Nothing was missing, but the key judgment was restraint: a brand palette was
already locked in from the earlier request to match yalebulldogblue.com, so the
creative work had to add character through type, motion, and detail without
reintroducing off-brand colors, and had to keep motion accessible (disabled under
prefers-reduced-motion) rather than decorative for its own sake.

---

## Problem 11 — Site Testing (App Check)

**Initial prompt**

> now, we're on Problem 11: Site testing (app check)
> let's test the live site and document in output/app_check.html (which we can
> double-click open). we'll need to include clear screenshots and short captions
> for: 1. chat checking the inventory level of an item (honest stock/price from
> the DB) 2. the dynamic search-results cards appearing after a category question
> 3. one of the usability features that we added in Problem 9
> we'll need to make the HTML easy to grade: heading for each check, screenshot,
> one or two sentences on what the screenshot proves. the screesnshot images
> should go in output/app_check_images and we should link them from app_check/html
> with relative paths (like, app_check_images/inventory.png)

**Follow-up prompt**

> (none needed — the three checks, the HTML structure, the images folder, and the
> relative-path linking were all specified.)

**What was lacking after the first prompt**

The instructions were complete; the only real work beyond them was producing
genuine screenshots of the running site (no browser is available to Claude
directly), which was solved by installing Playwright and driving headless
Chromium against the live localhost app, so the captured stock number (5 in M at
$58) and the dynamic cards are real, not mocked.

---

## Problem 12 — Audit Trail, Safety, and Finish Harness

**Initial prompt**

> now we're on Problem 12: Audit trail, safety, and finish harness
> keep an append-only output/audit_trail.json of agent-loop activity (time, tool
> name, short args/result, stop reason) that should't be wiped between runs
> also, we should think of some safety rules to give to the agent and put them
> into prompts/prompt.md
> then, we should finish output/harness.md so it's clear how the system works. the
> file should include: model fields in models.py and why we chose them, tools and
> abilities, safety rules, and specs (loop limits, result caps, models, how to run
> front + back)

**Follow-up prompt**

> (none needed — the audit fields, the persistence requirement, the safety-rules
> task, and the exact harness contents were all specified.)

**What was lacking after the first prompt**

The spec was complete; the notable outcome was that building the audit trail
immediately paid off by exposing a real bug. Its first entries showed the agent
searching three times and failing to find the "Yale Mom Crewneck" (a generic
token plus an alphabetical limit buried the relevant match), which prompted a
search-relevance fix. A second gap surfaced while testing safety: a harsher
jailbreak tripped the provider content filter in a wrapped exception that the
old handler missed and returned as a 502, so the handler was broadened to detect
content-filter blocks by message and deflect them safely.

---

<!-- Template for the next problem — copy, fill in, delete this comment.

## Problem N — [Title]

**Initial prompt**

> (what I typed first)

**Follow-up prompt**

> (what I typed next)

**What was lacking after the first prompt**

(one sentence)

-->

