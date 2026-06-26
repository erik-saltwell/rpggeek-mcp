from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

# Resolve .env relative to this file so it's found regardless of CWD
load_dotenv(Path(__file__).parents[3] / ".env")

from .models import Candidate, ProductDetails  # noqa: E402
from .rpggeek_client import RpgGeekClient  # noqa: E402

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
