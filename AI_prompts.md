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

**Note on the second follow-up**

"Draft mode" was ambiguous between *private repo* and *nothing pushed at all*, and
the two differ in whether code leaves the machine — so Claude set up the local
repository and committed, then asked before doing anything outward-facing.

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

