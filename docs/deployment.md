# Deployment

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`market-data-mcp` supports local stdio, a loopback-only development listener,
a least-privilege stdio container, and a remote authenticated HTTPS boundary.
Credential and trust material are supplied at runtime through the environment
(`agent_connector_sdk.credentials`); none is stored in this repository.

### Installed stdio process

```json
{
  "mcpServers": {
    "market-data-mcp": {
      "command": "market-data-mcp",
      "args": [],
      "env": {"MCP_TOOL_MODE": "condensed"}
    }
  }
}
```

### Loopback development listener

```bash
market-data-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Do not expose this listener beyond loopback. Network deployments require
direct TLS or an explicitly trusted TLS-terminating ingress and configured
authentication.

### Least-privilege local container

```bash
docker run -i --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --pids-limit=256 \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m \
  -e TRANSPORT=stdio \
  -e MARKET_DATA_CMC_API_KEY=your_coinmarketcap_key \
  -e MARKET_DATA_FRED_API_KEY=your_fred_key \
  registry.example.invalid/market-data-mcp@sha256:<digest> market-data-mcp
```

### Remote authenticated HTTPS endpoint

```json
{
  "mcpServers": {
    "market-data-mcp": {"url": "https://service.example.invalid/mcp"}
  }
}
```
<!-- END GENERATED: deployment-options -->

This page covers running `market-data-mcp` as a long-lived server: the
transports, a Docker Compose stack, putting it behind a Caddy reverse proxy,
and giving it a DNS name with Technitium. `market-data-mcp` ships **one**
server — an MCP server (console script `market-data-mcp`); there is no
separate agent process (see [Overview](overview.md)).

## Run the MCP server

The transport is selected with `--transport` (or the `TRANSPORT` env var):

=== "stdio (default)"

    ```bash
    market-data-mcp
    ```
    For IDE / desktop MCP clients that launch the server as a subprocess.

=== "streamable-http"

    ```bash
    market-data-mcp --transport streamable-http --host 0.0.0.0 --port 8000
    ```
    A network server with a `/health` endpoint and `/mcp` route.

=== "sse"

    ```bash
    market-data-mcp --transport sse --host 0.0.0.0 --port 8000
    ```

Health check (HTTP transports):

```bash
curl -s http://localhost:8000/health        # {"status":"OK"}
```

## Configuration (environment)

`market-data-mcp` is configured entirely from the environment:

| Var | Default | Meaning |
|---|---|---|
| `MARKET_DATA_CMC_API_KEY` | _(unset)_ | CoinMarketCap Pro API key reference (`env://` or `openbao://`) — required for `cmc_*` tools |
| `MARKET_DATA_FRED_API_KEY` | _(unset)_ | FRED/ALFRED API key reference — required for `fred_*` tools |
| `MARKET_DATA_CONTACT_EMAIL` | `connectors@knuckles.team` | Contact identity advertised in the `User-Agent` header |
| `MARKET_DATA_CMC_BASE_URL` | `https://pro-api.coinmarketcap.com` | CoinMarketCap API base URL override |
| `MARKET_DATA_CMC_MIN_INTERVAL` | `2.0` | Minimum seconds between CoinMarketCap requests |
| `MARKET_DATA_CMC_PAGE_SIZE` | `100` | Default CoinMarketCap listings page size |
| `MARKET_DATA_FRED_BASE_URL` | `https://api.stlouisfed.org/fred` | FRED API base URL override |
| `MARKET_DATA_FRED_MIN_INTERVAL` | `0.5` | Minimum seconds between FRED requests |
| `MARKET_DATA_FRED_PAGE_SIZE` | `1000` | Default FRED observations page size |
| `MARKET_DATA_FOMC_SOURCE_URL` | `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` | FOMC calendar's documented source page |
| `MCP_TOOL_MODE` | `condensed` | `condensed` / `verbose` / `both` tool registration |
| `TRANSPORT` / `HOST` / `PORT` | `stdio` / `127.0.0.1` / `8000` | Transport selection for HTTP modes |

`fomc_calendar_list` needs neither credential and performs no network `I/O`.
Copy [`.env.example`](https://github.com/Knuckles-Team/market-data-mcp/blob/main/.env.example)
to `.env` and populate only what the operator use.

## Docker Compose

The repo ships [`docker/mcp.compose.yml`](https://github.com/Knuckles-Team/market-data-mcp/blob/main/docker/mcp.compose.yml).
It reads a sibling `.env` and publishes the HTTP server on `:8000`:

```bash
cp .env.example .env          # then edit MARKET_DATA_* values
docker compose -f docker/mcp.compose.yml up -d
docker compose -f docker/mcp.compose.yml logs -f
```

## Behind a Caddy reverse proxy

```caddy
# Internal (self-signed) — homelab .example.invalid zone
market-data-mcp.example.invalid {
    tls internal
    reverse_proxy market-data-mcp-mcp:8000
}
```

```caddy
# Public — automatic Let's Encrypt
market-data-mcp.example.com {
    reverse_proxy market-data-mcp-mcp:8000
}
```

Reload Caddy:

```bash
docker compose -f services/caddy/compose.yml exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## DNS with Technitium

```bash
curl -s "http://technitium.example.invalid:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=market-data-mcp.example.invalid" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=192.0.2.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** in the Technitium web console. The ecosystem
[`technitium-dns-mcp`](https://knuckles-team.github.io/technitium-dns-mcp/) automates
this as a tool.

## Register with an MCP client

Add to the operator's client's `mcp_config.json`:

```json
{
  "mcpServers": {
    "market-data-mcp": {
      "command": "uv",
      "args": ["run", "market-data-mcp"],
      "env": {
        "MARKET_DATA_CMC_API_KEY": "your_coinmarketcap_key",
        "MARKET_DATA_FRED_API_KEY": "your_fred_key"
      }
    }
  }
}
```

For a remote HTTP server, point the client at
`http://market-data-mcp.example.invalid/mcp` instead.
