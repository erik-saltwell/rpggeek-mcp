from __future__ import annotations

from fastmcp import FastMCP

from .models import Candidate, ProductDetails
from .rpggeek_client import RpgGeekClient

mcp: FastMCP = FastMCP("rpggeek")

_client = RpgGeekClient()


@mcp.tool()
async def find_candidates(name: str | None = None, isbn: str | None = None) -> list[Candidate]:
    """Find RPGGeek products matching the given name and/or ISBN. Returns up to 5 candidates."""
    return await _client.find_candidates(name=name, isbn=isbn)


@mcp.tool()
async def get_product_details(rpggeek_id: int) -> ProductDetails:
    """Return full product details for an RPGGeek item by its numeric ID."""
    return await _client.get_product_details(rpggeek_id)
