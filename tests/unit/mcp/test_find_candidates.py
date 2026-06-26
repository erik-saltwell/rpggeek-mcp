from __future__ import annotations

import httpx
import pytest
import respx

from rpggeek_mcp.mcp.rpggeek_client import RpgGeekClient

SEARCH_XML_TWO_RESULTS = """<?xml version="1.0" encoding="utf-8"?>
<items total="2" termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
  <item type="rpgitem" id="226905">
    <name type="primary" value="Dungeon Crawl Classics"/>
    <yearpublished value="2012"/>
  </item>
  <item type="rpgitem" id="226906">
    <name type="primary" value="Dungeon Crawl Classics: Quick Start"/>
    <yearpublished value="2013"/>
  </item>
</items>"""

SEARCH_XML_ONE_NO_YEAR = """<?xml version="1.0" encoding="utf-8"?>
<items total="1" termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
  <item type="rpgitem" id="1">
    <name type="primary" value="No Year RPG"/>
  </item>
</items>"""

SEARCH_XML_EMPTY = """<?xml version="1.0" encoding="utf-8"?>
<items total="0" termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
</items>"""


@respx.mock
async def test_find_candidates_by_name_returns_id_and_name() -> None:
    respx.get("https://rpggeek.com/xmlapi2/search").mock(return_value=httpx.Response(200, text=SEARCH_XML_TWO_RESULTS))
    client = RpgGeekClient(rate_limit_delay=0)
    results = await client.find_candidates(name="Dungeon Crawl Classics", isbn=None)

    assert len(results) == 2
    assert results[0].rpggeek_id == 226905
    assert results[0].name == "Dungeon Crawl Classics"


@respx.mock
async def test_find_candidates_parses_year_published() -> None:
    respx.get("https://rpggeek.com/xmlapi2/search").mock(return_value=httpx.Response(200, text=SEARCH_XML_TWO_RESULTS))
    client = RpgGeekClient(rate_limit_delay=0)
    results = await client.find_candidates(name="Dungeon Crawl Classics", isbn=None)

    assert results[0].year_published == 2012
    assert results[1].year_published == 2013


@respx.mock
async def test_find_candidates_year_published_none_when_absent() -> None:
    respx.get("https://rpggeek.com/xmlapi2/search").mock(return_value=httpx.Response(200, text=SEARCH_XML_ONE_NO_YEAR))
    client = RpgGeekClient(rate_limit_delay=0)
    results = await client.find_candidates(name="No Year RPG", isbn=None)

    assert results[0].year_published is None


@respx.mock
async def test_find_candidates_isbn_path_uses_isbn_as_query() -> None:
    route = respx.get("https://rpggeek.com/xmlapi2/search").mock(
        return_value=httpx.Response(200, text=SEARCH_XML_TWO_RESULTS)
    )
    client = RpgGeekClient(rate_limit_delay=0)
    await client.find_candidates(name=None, isbn="978-0-9818565-2-7")

    assert route.called
    assert route.calls[0].request.url.params["query"] == "978-0-9818565-2-7"


@respx.mock
async def test_find_candidates_isbn_empty_falls_back_to_name() -> None:
    route = respx.get("https://rpggeek.com/xmlapi2/search").mock(
        side_effect=[
            httpx.Response(200, text=SEARCH_XML_EMPTY),
            httpx.Response(200, text=SEARCH_XML_TWO_RESULTS),
        ]
    )
    client = RpgGeekClient(rate_limit_delay=0)
    results = await client.find_candidates(name="Dungeon Crawl Classics", isbn="000-0-0000000-0-0")

    assert len(results) == 2
    assert route.call_count == 2
    assert route.calls[0].request.url.params["query"] == "000-0-0000000-0-0"
    assert route.calls[1].request.url.params["query"] == "Dungeon Crawl Classics"


SEARCH_XML_SEVEN_RESULTS = """<?xml version="1.0" encoding="utf-8"?>
<items total="7" termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
  <item type="rpgitem" id="1"><name type="primary" value="A"/></item>
  <item type="rpgitem" id="2"><name type="primary" value="B"/></item>
  <item type="rpgitem" id="3"><name type="primary" value="C"/></item>
  <item type="rpgitem" id="4"><name type="primary" value="D"/></item>
  <item type="rpgitem" id="5"><name type="primary" value="E"/></item>
  <item type="rpgitem" id="6"><name type="primary" value="F"/></item>
  <item type="rpgitem" id="7"><name type="primary" value="G"/></item>
</items>"""


@respx.mock
async def test_find_candidates_capped_at_five() -> None:
    respx.get("https://rpggeek.com/xmlapi2/search").mock(
        return_value=httpx.Response(200, text=SEARCH_XML_SEVEN_RESULTS)
    )
    client = RpgGeekClient(rate_limit_delay=0)
    results = await client.find_candidates(name="something", isbn=None)

    assert len(results) == 5


@respx.mock
async def test_find_candidates_returns_empty_list_when_nothing_found() -> None:
    respx.get("https://rpggeek.com/xmlapi2/search").mock(return_value=httpx.Response(200, text=SEARCH_XML_EMPTY))
    client = RpgGeekClient(rate_limit_delay=0)
    results = await client.find_candidates(name="xyzzy no match", isbn=None)

    assert results == []


async def test_find_candidates_raises_when_both_none() -> None:
    client = RpgGeekClient(rate_limit_delay=0)
    with pytest.raises(ValueError):
        await client.find_candidates(name=None, isbn=None)
