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


class ProductDescription(BaseModel):
    """Return type for the description lookup tool.

    Carries the fields a shopper asks about when they want to know what a
    product *is*: its name, what kind of garment it is, the full description,
    and the colors it comes in. Price and stock are deliberately separate tools,
    so the model asks for exactly what it needs.
    """

    product_id: str
    name: str
    category: str
    description: str
    colors: list[str]


class ProductPrice(BaseModel):
    """Return type for the price lookup tool.

    Just the product and its price. Narrow on purpose: a price question should
    not depend on, or drag along, description or stock data, and the single
    authoritative number comes straight from the database.
    """

    product_id: str
    name: str
    price: float


class SizeStock(BaseModel):
    """Stock for one size."""

    size: str
    quantity: int
    in_stock: bool


class StockReport(BaseModel):
    """Return type for the stock lookup tool.

    `sizes` is the per-size breakdown the shopper asked about (one size if they
    named one, otherwise the full run). `available_sizes` always lists every
    size currently buyable, so the agent can offer an alternative when the
    requested size is out. `requested_size` is set when the shopper named a
    size, so the agent knows to answer that size specifically and say clearly if
    it is out of stock.
    """

    product_id: str
    name: str
    sizes: list[SizeStock]
    available_sizes: list[str]
    total_stock: int
    in_stock: bool
    requested_size: str | None = None


class ProductFull(BaseModel):
    """Combined lookup: description, price, and per-size stock in one call.

    Added in Problem 9 so a broad question about one product ("tell me about the
    Mom hoodie, how much, what sizes") is answered with a single tool call
    instead of three, cutting model round-trips.
    """

    product_id: str
    name: str
    category: str
    description: str
    colors: list[str]
    price: float
    sizes: list[SizeStock]
    available_sizes: list[str]
    total_stock: int
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
