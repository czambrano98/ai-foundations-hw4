"""Campus Customs shop agent: entry point and wiring.

Loads the system prompt from prompts/prompt.md, builds a PydanticAI agent backed
by the Portkey gateway (same approach as HW3), gives it the catalogue tools, and
exposes run_chat() for the FastAPI chat route to call.

The agent is built lazily on first use, so importing this module (and therefore
starting the API) does not require the API key or a network call. The app can
serve products and auth even if the agent is misconfigured.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from models import AgentReply
from tools import (
    get_price,
    get_product,
    get_product_description,
    get_stock,
    list_categories,
    search_catalogue,
)


@dataclass
class ChatDeps:
    """Per-request context the agent sees (Problem 8).

    Carries who is chatting and what they are looking at. Guests leave the
    customer fields None. `current_product_*` is set when the shopper is on a
    product page, so "do you have this in yellow?" resolves to that product.
    """

    customer_name: str | None = None
    customer_email: str | None = None
    current_product_id: str | None = None
    current_product_name: str | None = None


def _customer_instructions(ctx: RunContext[ChatDeps]) -> str:
    """Tell the agent who it is talking to."""
    deps = ctx.deps
    if deps.customer_name:
        return (
            f"You are chatting with {deps.customer_name} "
            f"({deps.customer_email}), a signed-in customer. You may greet them "
            f"by their first name. Never reveal account details beyond their own "
            f"name and email, and never mention other customers."
        )
    return "The shopper is browsing as a guest and is not signed in."


def _page_instructions(ctx: RunContext[ChatDeps]) -> str:
    """Tell the agent what the shopper is currently looking at."""
    deps = ctx.deps
    if deps.current_product_id:
        return (
            f"The shopper is currently viewing this product: "
            f"{deps.current_product_name} (product_id: "
            f"{deps.current_product_id}). If they say 'this', 'it', 'this one', "
            f"or ask about a color or size without naming a product, they mean "
            f"this product. Use this product_id with your tools. Name the product "
            f"({deps.current_product_name}) at least once in your reply, so the "
            f"conversation stays clear if they ask a follow-up later."
        )
    return ""

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent  # Homework 4/
PROMPT_PATH = BACKEND_DIR / "prompts" / "prompt.md"

# gpt-4o is the model HW3 used through Portkey; it supports tool calling and
# structured output, which this agent needs.
MODEL_NAME = "gpt-4o"


def _load_env() -> None:
    """Load KEY=VALUE pairs from the first env file found, without overriding
    anything already set in the real environment.

    Checked in order: a local backend/.env, then the Homework 4 env.txt, then
    the AI Foundations env.txt one level up (where the Portkey key lives).
    """
    candidates = [
        BACKEND_DIR / ".env",
        PROJECT_ROOT / ".env",  # project-root .env (copied from .env.example)
        PROJECT_ROOT / "env.txt",
        PROJECT_ROOT.parent / "env.txt",  # AI Foundations folder
    ]
    for path in candidates:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_env()


def load_prompt() -> str:
    """Read the system prompt from the prompt file.

    Kept as a function (not read once at import) so editing prompt.md and
    restarting is all it takes to change the agent's behaviour.
    """
    return PROMPT_PATH.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def get_agent() -> Agent[None, AgentReply]:
    """Build the agent once and reuse it.

    Routes OpenAI-compatible calls through the Portkey gateway using the
    x-portkey-api-key header, exactly as HW3 did.
    """
    portkey_key = os.getenv("PORTKEY_API_KEY")
    if not portkey_key:
        raise RuntimeError(
            "PORTKEY_API_KEY is not set. Put it in the AI Foundations env.txt, "
            "the Homework 4 env.txt, or backend/.env."
        )

    client = AsyncOpenAI(
        api_key="portkey",  # ignored by the gateway; the real key is the header
        base_url="https://api.portkey.ai/v1",
        default_headers={"x-portkey-api-key": portkey_key},
    )
    model = OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))

    agent = Agent(
        model,
        deps_type=ChatDeps,
        output_type=AgentReply,
        # `instructions` (not `system_prompt`) so the base prompt and the
        # deps-based context below are re-applied fresh on every run, including
        # runs that replay prior history. They are not stored in the history.
        instructions=load_prompt(),
        tools=[
            search_catalogue,
            get_product,
            get_product_description,
            get_price,
            get_stock,
            list_categories,
        ],
        # Allow a couple of retries so a malformed tool call or output (e.g. a
        # mistyped field name) is corrected rather than surfaced as an error.
        retries=2,
    )
    # Dynamic instructions that read per-request deps (customer, current page).
    agent.instructions(_customer_instructions)
    agent.instructions(_page_instructions)
    return agent


async def run_chat(
    message: str,
    deps: ChatDeps | None = None,
    message_history: list[ModelMessage] | None = None,
):
    """Run one shopper message through the agent and return the full run result.

    `deps` carries who is chatting and the current page; `message_history` is the
    shopper's earlier turns, so the agent has conversational memory. The caller
    reads `.output` for the reply and `.new_messages()` for the audit trail.
    """
    agent = get_agent()
    return await agent.run(
        message,
        deps=deps or ChatDeps(),
        message_history=message_history,
    )
