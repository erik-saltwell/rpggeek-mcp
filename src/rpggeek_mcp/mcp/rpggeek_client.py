from __future__ import annotations

import asyncio
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

import httpx
import structlog

from ..utils import load_dotenv_from
from .models import Candidate, ProductDetails

load_dotenv_from(__file__)

_log = structlog.get_logger(__name__)

_BASE_URL = "https://rpggeek.com/xmlapi2"


@dataclass
class RpgGeekClient:
    rate_limit_delay: float = field(default=1.0)
    _http: httpx.AsyncClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        token = os.environ.get("RPGGEEK_BEARER_TOKEN", "")
        if not token:
            _log.warning("rpggeek_bearer_token_missing", reason="RPGGEEK_BEARER_TOKEN not set")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        self._http = httpx.AsyncClient(headers=headers)

    async def _search(self, query: str) -> list[Candidate]:
        await asyncio.sleep(self.rate_limit_delay)
        response = await self._http.get(
            f"{_BASE_URL}/search",
            params={"query": query, "type": "rpgitem"},
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)
        candidates = []
        for item in root.findall("item"):
            name_el = item.find("name")
            year_el = item.find("yearpublished")
            candidates.append(
                Candidate(
                    rpggeek_id=int(item.get("id", "0")),
                    name=name_el.get("value", "") if name_el is not None else "",
                    year_published=int(year_el.get("value", "0")) if year_el is not None else None,
                )
            )
        return candidates

    async def find_candidates(self, name: str | None, isbn: str | None) -> list[Candidate]:
        if name is None and isbn is None:
            raise ValueError("At least one of name or isbn must be provided")

        if isbn is not None:
            results = await self._search(isbn)
            if results:
                return results[:5]

        if name is not None:
            return (await self._search(name))[:5]

        return []

    async def get_product_details(self, rpggeek_id: int) -> ProductDetails:
        await asyncio.sleep(self.rate_limit_delay)
        response = await self._http.get(
            f"{_BASE_URL}/thing",
            params={"id": rpggeek_id, "type": "rpgitem", "stats": 1},
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)
        item = root.find("item")
        if item is None:
            raise ValueError(f"No RPGGeek item found for id {rpggeek_id}")

        name_el = item.find("name[@type='primary']")
        name = name_el.get("value", "") if name_el is not None else ""

        year_el = item.find("yearpublished")
        year_published = int(year_el.get("value", "0")) if year_el is not None else None

        desc_el = item.find("description")
        description = desc_el.text if desc_el is not None else None

        thumb_el = item.find("thumbnail")
        thumbnail_url = thumb_el.text if thumb_el is not None else None

        systems = [
            el.get("value", "").removeprefix("RPG System: ")
            for el in item.findall("link[@type='rpgfamily']")
            if el.get("value", "").startswith("RPG System:")
        ]
        categories = [el.get("value", "") for el in item.findall("link[@type='rpgcategory']")]
        designers = [el.get("value", "") for el in item.findall("link[@type='rpgdesigner']")]
        publishers = [el.get("value", "") for el in item.findall("link[@type='rpgpublisher']")]

        rating_el = item.find("statistics/ratings/average")
        rating = float(rating_el.get("value", "0")) if rating_el is not None else None

        return ProductDetails(
            rpggeek_id=int(item.get("id", "0")),
            name=name,
            year_published=year_published,
            description=description,
            thumbnail_url=thumbnail_url,
            systems=systems,
            categories=categories,
            designers=designers,
            publishers=publishers,
            rating=rating,
        )
