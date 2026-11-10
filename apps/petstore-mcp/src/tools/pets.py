from typing import Any, Literal

from mcp.types import ToolAnnotations

from core.petstore import request, summarize
from core.server import mcp


@mcp.tool(annotations=ToolAnnotations(title="Find pets by status", readOnlyHint=True))
def find_pets_by_status(status: Literal["available", "pending", "sold"] = "available") -> list[dict[str, Any]]:
    """List pets in the store with the given status. Use this first when a customer wants to browse or find a pet.

    Args:
        status: One of available, pending, sold. Defaults to available.

    Returns:
        Pets with id, name, category, status, tags and demo_unit_price. Prices are a deterministic
        demo value derived from category and id (the Petstore API itself has no prices).
    """
    return [summarize(p) for p in request("GET", "/pet/findByStatus", params={"status": status})]


@mcp.tool(annotations=ToolAnnotations(title="Get pet", readOnlyHint=True))
def get_pet(pet_id: int) -> dict[str, Any]:
    """Get full details of one pet by its numeric id (from find_pets_by_status).

    Args:
        pet_id: Numeric pet id.

    Returns:
        The pet's details including demo_unit_price (deterministic demo price; the Petstore has no prices).
    """
    return summarize(request("GET", f"/pet/{pet_id}"))
