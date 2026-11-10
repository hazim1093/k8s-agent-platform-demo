import time
from typing import Any

import httpx
from mcp.types import ToolAnnotations

from core.petstore import new_quote, order_payload, quotes, request
from core.server import mcp


@mcp.tool(annotations=ToolAnnotations(title="Prepare order quote", readOnlyHint=True))
def prepare_order(pet_id: int, quantity: int = 1) -> dict[str, Any]:
    """Create a price quote for ordering a pet. This does NOT place an order and has no side effects on the store.

    Always call this before confirm_order, show the customer the pet details, unit price and total, and
    ask for explicit confirmation. The Petstore has no prices, so unit_price is a deterministic demo price
    derived from the pet's category and id. The quote expires after 10 minutes.

    Args:
        pet_id: Numeric id of an available pet.
        quantity: Number of units, 1 to 10.

    Returns:
        A quote with quote_id, pet details, unit_price, total, currency and expires_in_seconds.
    """
    if not 1 <= quantity <= 10:
        raise ValueError("quantity must be between 1 and 10")
    pet = request("GET", f"/pet/{pet_id}")
    if pet.get("status") != "available":
        raise ValueError(f"pet {pet_id} is not available (status: {pet.get('status')})")
    quote = new_quote(pet, quantity)
    return {**quote, "expires_in_seconds": int(quote["expires_at"] - time.time())}


@mcp.tool(annotations=ToolAnnotations(title="Confirm order", readOnlyHint=False, destructiveHint=True, idempotentHint=True))
def confirm_order(quote_id: str) -> dict[str, Any]:
    """Place the real order for a quote from prepare_order. This has a side effect and spends money.

    Only call this after the customer has explicitly confirmed the quote's pet, quantity and total in
    the conversation. Calling it again with the same quote_id returns the existing order.

    Args:
        quote_id: The quote_id returned by prepare_order.

    Returns:
        The placed order (order id, pet id, quantity, status) and the quoted total.
    """
    quote = quotes.get(quote_id)
    if quote is None or quote["expires_at"] < time.time():
        raise ValueError("unknown or expired quote_id; call prepare_order again")
    if quote["order_id"] is None:
        try:
            order = request("POST", "/store/order", json=order_payload(quote))
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Petstore rejected the order: {e.response.status_code}") from e
        quote["order_id"] = order["id"]
        quote["order"] = order
    return {"order": quote["order"], "total": quote["total"], "currency": quote["currency"]}
