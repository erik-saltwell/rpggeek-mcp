from __future__ import annotations

from pydantic import BaseModel


class Candidate(BaseModel):
    rpggeek_id: int
    name: str
    year_published: int | None = None


class ProductDetails(BaseModel):
    rpggeek_id: int
    name: str
    year_published: int | None = None
    description: str | None = None
    systems: list[str] = []
    categories: list[str] = []
    designers: list[str] = []
    publishers: list[str] = []
    thumbnail_url: str | None = None
    rating: float | None = None
