# rpggeek-mcp

An MCP (Model Context Protocol) server for querying [RPGGeek](https://rpggeek.com) — the RPG section of the BoardGameGeek network. Connect it to Claude Desktop (or any MCP client) to let an AI assistant look up RPG products by name or ISBN and retrieve detailed product information.

> Unofficial community project. Not affiliated with or endorsed by RPGGeek.

## Tools

### `find_candidates`

Searches RPGGeek for products matching a name and/or ISBN. Returns up to 5 candidates.

**Parameters** (at least one required):

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `string` | Product name to search for |
| `isbn` | `string` | ISBN (any format) |

**Strategy:** if an ISBN is provided it is tried first; the name is used as a fallback if the ISBN search returns no results.

**Returns:** a list of up to 5 candidates, each with:
- `rpggeek_id` — RPGGeek's numeric item ID
- `name` — primary product name
- `year_published` — publication year, or `null`

An empty list means nothing was found. Pass `rpggeek_id` from a candidate to `get_product_details` to retrieve full data.

---

### `get_product_details`

Returns full structured data for a known RPGGeek item.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `rpggeek_id` | `integer` | RPGGeek's numeric item ID |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `rpggeek_id` | `integer` | |
| `name` | `string` | Primary product name |
| `year_published` | `integer \| null` | |
| `description` | `string \| null` | Full product description |
| `systems` | `string[]` | RPG systems (e.g. `"Dungeons & Dragons 5E"`) |
| `categories` | `string[]` | Product categories (e.g. `"Core Rulebook"`, `"Adventure/Scenario"`) |
| `designers` | `string[]` | Designer names |
| `publishers` | `string[]` | Publisher names |
| `thumbnail_url` | `string \| null` | Cover thumbnail URL |
| `rating` | `number \| null` | Average community rating |

---

## Requirements

- [uv](https://docs.astral.sh/uv/) must be installed. Python is managed automatically by uv.
- A free [RPGGeek account](https://rpggeek.com/login) — the XML API requires authentication.

## Installation

**1. Create a `.env` file** in the directory where you'll run the server (or set the variables in your shell / Claude Desktop config):

```bash
cp .env.example .env
# then edit .env and fill in your RPGGeek username and password
```

**2. Run the server** — no cloning or venv management required with `uvx`:

```bash
uvx rpggeek-mcp serve
```

To install permanently as a tool:

```bash
uv tool install rpggeek-mcp
rpggeek-mcp serve
```

## Connecting to Claude Desktop

Add the server to your Claude Desktop configuration file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rpggeek": {
      "command": "uvx",
      "args": ["rpggeek-mcp", "serve"],
      "env": {
        "RPGGEEK_USERNAME": "your_rpggeek_username",
        "RPGGEEK_PASSWORD": "your_rpggeek_password"
      }
    }
  }
}
```

Restart Claude Desktop after saving. The RPGGeek tools will appear in the tool picker.

## Usage example

Once connected, you can ask Claude things like:

> "Find the RPGGeek entry for Dungeon Crawl Classics"

Claude will call `find_candidates` to get a list of matches, then `get_product_details` on the best one to pull full metadata.

## Running the server manually

```bash
uv run rpggeek-mcp serve
```

The server speaks the MCP protocol over stdio and is designed to be launched by an MCP client rather than run interactively. Logs are written to `logs/rpggeek_mcp.log`.

## Development

**Run tests:**

```bash
uv run pytest
```

**Type-check:**

```bash
uv run pyright
```

**Lint and format:**

```bash
uv run ruff check .
uv run ruff format .
```

## Notes

- Uses the [RPGGeek XML API 2](https://rpggeek.com/wiki/page/XML_API2). A free RPGGeek account is required; credentials are read from `RPGGEEK_USERNAME` and `RPGGEEK_PASSWORD`.
- Requests are rate-limited to 1 per second to respect the API's usage guidelines.
