from __future__ import annotations

import httpx
import pytest
import respx

from rpggeek_mcp.mcp.rpggeek_client import RpgGeekClient

THING_XML_FULL = """<?xml version="1.0" encoding="utf-8"?>
<items termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
  <item type="rpgitem" id="226905">
    <thumbnail>https://cf.geekdo-images.com/thumb.jpg</thumbnail>
    <image>https://cf.geekdo-images.com/full.jpg</image>
    <name type="primary" sortindex="1" value="Dungeon Crawl Classics"/>
    <name type="alternate" sortindex="1" value="DCC RPG"/>
    <description>A grim and perilous RPG.</description>
    <yearpublished value="2012"/>
    <link type="rpgcategory" id="1085" value="Core Rulebook"/>
    <link type="rpgfamily" id="8374" value="RPG System: Dungeon Crawl Classics"/>
    <link type="rpgfamily" id="1234" value="Setting: Some Setting"/>
    <link type="rpgdesigner" id="1" value="Joseph Goodman"/>
    <link type="rpgpublisher" id="1" value="Goodman Games"/>
    <statistics page="1">
      <ratings>
        <average value="8.5"/>
      </ratings>
    </statistics>
  </item>
</items>"""


@respx.mock
async def test_get_product_details_returns_id_and_name() -> None:
    respx.get("https://rpggeek.com/xmlapi2/thing").mock(return_value=httpx.Response(200, text=THING_XML_FULL))
    client = RpgGeekClient(rate_limit_delay=0)
    result = await client.get_product_details(226905)

    assert result.rpggeek_id == 226905
    assert result.name == "Dungeon Crawl Classics"


THING_XML_SPARSE = """<?xml version="1.0" encoding="utf-8"?>
<items termsofuse="https://boardgamegeek.com/xmlapi/termsofuse">
  <item type="rpgitem" id="999">
    <name type="primary" sortindex="1" value="Sparse RPG"/>
  </item>
</items>"""


@respx.mock
async def test_get_product_details_parses_all_fields() -> None:
    respx.get("https://rpggeek.com/xmlapi2/thing").mock(return_value=httpx.Response(200, text=THING_XML_FULL))
    client = RpgGeekClient(rate_limit_delay=0)
    result = await client.get_product_details(226905)

    assert result.year_published == 2012
    assert result.description == "A grim and perilous RPG."
    assert result.thumbnail_url == "https://cf.geekdo-images.com/thumb.jpg"
    assert result.rating == pytest.approx(8.5)
    assert result.systems == ["Dungeon Crawl Classics"]
    assert result.categories == ["Core Rulebook"]
    assert result.designers == ["Joseph Goodman"]
    assert result.publishers == ["Goodman Games"]


@respx.mock
async def test_get_product_details_optional_fields_absent() -> None:
    respx.get("https://rpggeek.com/xmlapi2/thing").mock(return_value=httpx.Response(200, text=THING_XML_SPARSE))
    client = RpgGeekClient(rate_limit_delay=0)
    result = await client.get_product_details(999)

    assert result.rpggeek_id == 999
    assert result.name == "Sparse RPG"
    assert result.year_published is None
    assert result.description is None
    assert result.thumbnail_url is None
    assert result.rating is None
    assert result.systems == []
    assert result.categories == []
    assert result.designers == []
    assert result.publishers == []


@respx.mock
async def test_get_product_details_raises_on_http_error() -> None:
    respx.get("https://rpggeek.com/xmlapi2/thing").mock(return_value=httpx.Response(500))
    client = RpgGeekClient(rate_limit_delay=0)

    with pytest.raises(httpx.HTTPStatusError):
        await client.get_product_details(226905)
