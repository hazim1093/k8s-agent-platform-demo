from typing import Any

from mcp.types import ToolAnnotations

from core.petstore import request
from core.server import mcp


@mcp.tool(annotations=ToolAnnotations(title="Get inventory", readOnlyHint=True))
def get_inventory() -> dict[str, Any]:
    """Get store inventory: a count of pets per status (available, pending, sold). Read-only; use for stock questions.

    Returns:
        Mapping of status to number of pets.
    """
    return request("GET", "/store/inventory")
