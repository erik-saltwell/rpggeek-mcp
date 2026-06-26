# PRD: RPGGeek MCP Server

Status: needs-triage

## Overview

Build an MCP (Model Context Protocol) server that exposes two tools for querying the RPGGeek XML API. The server allows AI assistants and other MCP clients to look up RPG products by search signals and retrieve structured product details.

## Goals

- Provide a reliable way to find RPG products on RPGGeek given partial identifying information (name, ISBN)
- Provide structured product detail retrieval by RPGGeek ID
- Integrate cleanly with Claude Desktop and other stdio MCP clients

## Non-goals

- Writing to RPGGeek (no user authentication, no reviews/ratings/collections)
- Exposing more than two tools in v1
- Building a web-accessible HTTP endpoint

---

## Transport & Framework

- **Library:** FastMCP
- **Transport:** stdio (client manages the process lifecycle)
- **Entry point:** `rpggeek-mcp serve` — a Typer subcommand added to the existing CLI scaffold that calls `mcp.run(transport="stdio")`

---

## Tools

### `find_candidates`

Finds potential RPGGeek product matches given one or more search signals.

**Inputs** (all optional, but at least one must be provided — raises if both are `None`):

| Field | Type | Notes |
|-------|------|-------|
| `name` | `str \| None` | Product name |
| `isbn` | `str \| None` | ISBN (any format) |

**Search strategy:**
1. If `isbn` is provided, query the RPGGeek search API using the ISBN string first
2. If the ISBN search returns no results (or no ISBN was provided), fall back to a name search
3. Return up to **5 candidates** from whichever search path yielded results

**Output:** list of up to 5 candidate objects. Empty list = nothing found.

Each candidate:

| Field | Type |
|-------|------|
| `rpggeek_id` | `int` |
| `name` | `str` |
| `year_published` | `int \| None` |

**Errors:** raises on API failure or if both inputs are `None`.

---

### `get_product_details`

Returns full structured product data for a known RPGGeek ID.

**Input:**

| Field | Type |
|-------|------|
| `rpggeek_id` | `int` |

**Output:**

| Field | Type | Source |
|-------|------|--------|
| `rpggeek_id` | `int` | |
| `name` | `str` | primary name |
| `year_published` | `int \| None` | |
| `description` | `str \| None` | |
| `systems` | `list[str]` | `rpgfamily` links prefixed `RPG System:` |
| `categories` | `list[str]` | `rpgcategory` links (e.g. Core Rulebook, Adventure/Scenario, Supplement) |
| `designers` | `list[str]` | `rpgdesigner` links |
| `publishers` | `list[str]` | `rpgpublisher` links |
| `thumbnail_url` | `str \| None` | |
| `rating` | `float \| None` | average rating from statistics |

**Errors:** raises on API failure or unknown ID.

---

## HTTP Layer

- **Client:** `httpx.AsyncClient` (async throughout)
- **Rate limiting:** `asyncio.sleep(1)` between every API call to comply with RPGGeek's ~1 req/sec guideline
- **Base URL:** `https://rpggeek.com/xmlapi2/`
- **Authentication:** none required for public read-only endpoints
- **XML parsing:** stdlib `xml.etree.ElementTree`
- **Relevant endpoints:**
  - `GET /search?query=<text>&type=rpgitem` — search
  - `GET /thing?id=<id>&type=rpgitem&stats=1` — product detail

---

## Logging & Observability

- **File logger only** — stdout is reserved for the MCP wire protocol; no Rich/console output
- **Tracer** — used for structured logging of API calls and command durations (existing scaffold)
- Log and trace files written to the standard paths defined in `common_paths`

---

## Error Handling

- All failures raise exceptions
- FastMCP converts raised exceptions to MCP error responses automatically
- No structured error payloads in tool return types — return types are always the happy-path shape

---

## Testing

- **Library:** `respx` (httpx-native mock transport)
- Hand-written XML response fixtures matching real RPGGeek API2 response shapes
- Tests run fully offline — no real network calls
- Test paths: `tests/unit/`

---

## Module Structure (proposed)

```
src/rpggeek_mcp/
├── mcp/
│   ├── __init__.py
│   ├── server.py          # FastMCP app instance + @mcp.tool() definitions
│   ├── rpggeek_client.py  # httpx client, rate limiting, XML parsing
│   └── models.py          # Pydantic models for tool inputs/outputs
├── console/
│   └── main.py            # existing Typer CLI — add `serve` subcommand here
└── ... (existing scaffold unchanged)
```

---

## Open Questions

- None — all design decisions resolved in grilling session.
