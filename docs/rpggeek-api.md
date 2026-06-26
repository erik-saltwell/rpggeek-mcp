# RPGGeek XML API — Research Notes

RPGGeek shares its API infrastructure with BoardGameGeek (BGG) and VideoGameGeek. The same XML API 2 endpoints work on all three domains; the base URL is the only difference.

---

## Base URL

```
https://rpggeek.com/xmlapi2
```

Do **not** use the `www.` subdomain — it can interfere with authentication cookies.

---

## Authentication

### Current situation: bearer tokens required

BGG announced in late 2024 that all XML API usage now requires registration and a bearer token. The rollout was enforced through 2025. Requests without a valid token return `Access denied`.

**How to register:**
1. Log in to your BGG/RPGGeek account.
2. Go to `https://boardgamegeek.com/applications/create` and submit an application describing your use case.
3. Once approved, a token is issued via your account page.

**How to include the token in requests:**

```http
Authorization: Bearer <your-token>
```

Add this header to every XML API request.

### Exceptions (no token needed)
- Downloading **your own** collection while logged in via session cookies.
- The CSV bulk data dump of all games (while logged in).

### Legacy cookie-based auth (now secondary)

Before the bearer token rollout, the pattern was:

```
POST https://rpggeek.com/login/api/v1
Content-Type: application/json

{"credentials": {"username": "...", "password": "..."}}
```

A successful response sets session cookies (`bggusername`, `bggpassword`) that the HTTP client then sends on subsequent requests. This is what the current `RpgGeekClient._ensure_authenticated()` does. It still works for session-scoped private data (own collection) but is **not sufficient** for public API calls that now require the bearer token.

### What this means for this project

The client currently uses only cookie auth. For public searches and thing lookups the token header needs to be added. The `.env` should hold the token and the client should attach it as a header on every request.

---

## Endpoints

### `GET /xmlapi2/search`

Search for items by name.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search string |
| `type` | string | Comma-delimited item types (see below) |
| `exact` | 0/1 | Match exact title only |

**RPG item types:**
- `rpgitem` — a published RPG product (book, boxed set, PDF)
- `rpgissue` — a magazine issue
- `rpgperiodical` — a periodical series

**Example:**
```
GET /xmlapi2/search?query=Masks+of+Nyarlathotep&type=rpgitem
```

**Response:** XML `<items total="N">` containing `<item id="..." type="rpgitem">` elements, each with `<name value="..."/>` and `<yearpublished value="..."/>`.

---

### `GET /xmlapi2/thing`

Fetch full details for one or more items by numeric ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | int (comma-list) | RPGGeek numeric ID(s), max 20 per call |
| `type` | string | Optional type filter |
| `stats` | 0/1 | Include ratings/statistics |
| `versions` | 0/1 | Include edition/version records |
| `videos` | 0/1 | Include linked videos |
| `comments` | 0/1 | Include user comments |
| `page` | int | Page for paginated results |
| `pagesize` | int | Items per page |

**Example:**
```
GET /xmlapi2/thing?id=41752&type=rpgitem&stats=1
```

**Response:** XML `<items>` with one `<item>` per ID. Key child elements:

| Element | Notes |
|---------|-------|
| `<name type="primary" value="..."/>` | Primary title |
| `<yearpublished value="..."/>` | Publication year |
| `<description>` | Full text description (HTML entities encoded) |
| `<thumbnail>` | URL of cover thumbnail |
| `<link type="rpgfamily" value="RPG System: ..."/>` | Game system |
| `<link type="rpgcategory" value="..."/>` | Categories |
| `<link type="rpgdesigner" value="..."/>` | Designers |
| `<link type="rpgpublisher" value="..."/>` | Publishers |
| `<statistics><ratings><average value="..."/>` | Average user rating |

---

### `GET /xmlapi2/collection`

Fetch a user's collection. Requires either session cookies (own collection) or a bearer token.

| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | string | BGG/RPGGeek username |
| `subtype` | string | e.g. `rpgitem` |
| `own` | 0/1 | Filter to owned items |
| `stats` | 0/1 | Include ratings |
| `brief` | 0/1 | Abbreviated response |

**Note:** The server may return HTTP **202** (queued) rather than 200. The caller must retry after a delay until it gets 200.

---

### Other endpoints (less relevant to this project)

| Endpoint | Purpose |
|----------|---------|
| `/xmlapi2/hot` | Currently trending items (`type=rpgitem`) |
| `/xmlapi2/user` | User profile, buddies, top lists |
| `/xmlapi2/plays` | Play log for a user |
| `/xmlapi2/forumlist` | Forums attached to an item |
| `/xmlapi2/forum` | Threads in a forum |
| `/xmlapi2/thread` | Posts in a thread |
| `/xmlapi2/guild` | Guild membership |
| `/xmlapi2/family` | Item families/series |

---

## Rate Limiting

- The API has no published rate limit number.
- The docs recommend a **5-second delay** between requests to avoid 500/503 errors.
- The current client uses a 1-second delay (`rate_limit_delay = 1.0`). This is likely fine for interactive use but may need tuning for bulk work.
- Batches of 250–500 IDs on the `/thing` endpoint work well in practice; hard limit is 20 IDs per call per the docs.

---

## Numeric ID space

IDs are shared across BGG, RPGGeek, and VideoGameGeek. An ID from a BGG search is the same ID you pass to `/xmlapi2/thing` on rpggeek.com. There is no separate RPGGeek ID namespace.

---

## Sources

- [BGG XML API2 Wiki (RPGGeek mirror)](https://rpggeek.com/wiki/page/bgg_xml_api2)
- [BGG XML API2 Wiki (BoardGameGeek)](https://boardgamegeek.com/wiki/page/BGG_XML_API2)
- [Using the XML API (BGG)](https://boardgamegeek.com/using_the_xml_api)
- [Registration and Authorization announcement](https://boardgamegeek.com/thread/3492262/registration-and-authorization-coming-to-the-xml-a)
- [Registration now open thread](https://boardgamegeek.com/thread/3525319/registration-to-use-the-xml-api-and-obtain-soon-to)
- [Bearer token enforcement announcement](https://boardgamegeek.com/thread/3600185/heads-up-bgg-now-requiring-authorization-tokens-fo)
- [XML API Terms of Use](https://rpggeek.com/wiki/page/XML_API_Terms_of_Use)
