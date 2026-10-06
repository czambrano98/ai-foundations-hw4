"""Pydantic and PydanticAI structured types for the Campus Customs agent.

Grows alongside the agent in later problems. Right now it covers the chat
reply contract and the product-card shape the storefront renders.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProductCard(BaseModel):
    """A product as shown in the chat widget.

    A subset of the storefront product shape, carrying exactly what a card
    needs to render and link through to the product page. The API fills these
    in from the database so prices and stock are always canonical, never
    whatever the model might have paraphrased.
    """

    product_id: str
    name: str
    price: float
    image_url: str
    image_bg: str = "#ffffff"
    short_description: str
    category: str
    in_stock: bool


class AgentReply(BaseModel):
    """Structured output the agent returns.

    The agent decides what to say and which products to surface; it names them
    by id only. The API turns those ids into full ProductCards, so the model
    cannot invent a price, an image, or a stock level.
    """

    # Forbid extra keys so a near-miss like "product_id" (singular) fails
    # validation and PydanticAI retries, rather than silently dropping the ids.
    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        description="The reply to show the shopper, in the Campus Customs voice."
    )
    product_ids: list[str] = Field(
        default_factory=list,
        description=(
            "The field name is product_ids (plural). A list of product_id "
            "values to display as cards beneath the reply, in the order they "
            "should appear. Only ids returned by a tool call. Empty when no "
            "specific product is being recommended."
        ),
    )


class ChatResponse(BaseModel):
    """The body returned by POST /api/chat.

    Shape is unchanged from the Problem 3 stub (`reply` + `products`) so the
    frontend chat widget did not have to change when the real agent replaced
    the stub.
    """

    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    stub: bool = False
