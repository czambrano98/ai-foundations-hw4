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
from functools import lru_cache
from pathlib import Path

from openai import AsyncOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from models import AgentReply
from tools import (
    get_price,
    get_product_description,
    get_stock,
    list_categories,
    search_catalogue,
)

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

    return Agent(
        model,
        output_type=AgentReply,
        system_prompt=load_prompt(),
        tools=[
            search_catalogue,
            get_product_description,
            get_price,
            get_stock,
            list_categories,
        ],
        # Allow a couple of retries so a malformed tool call or output (e.g. a
        # mistyped field name) is corrected rather than surfaced as an error.
        retries=2,
    )


async def run_chat(message: str) -> AgentReply:
    """Run one shopper message through the agent and return its structured reply."""
    agent = get_agent()
    result = await agent.run(message)
    return result.output
