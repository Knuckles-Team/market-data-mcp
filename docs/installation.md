# Installation

`market-data-mcp` is a standard Python package and a prebuilt container image.

## Requirements

- **Python 3.12 – 3.14**.
- A **CoinMarketCap Pro API key** and a **FRED/ALFRED API key** for the keyed
  tools. `fomc_calendar_list` needs neither — it reads a packaged, curated
  dataset.

## From PyPI (recommended)

```bash
pip install market-data-mcp
```

The install already includes the MCP-server runtime (`agent-connector-sdk` +
`httpx`), so the `market-data-mcp` console script is ready immediately — there
is no separate "agent" extra to install (this package ships no A2A agent; see
[Overview](overview.md)).

### Optional extras

| Extra | Install | Pulls in |
|---|---|---|
| _(base)_ | `pip install market-data-mcp` | `agent-connector-sdk`, `httpx` |
| `test` | `pip install "market-data-mcp[test]"` | `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist` |

## From source

```bash
git clone https://github.com/Knuckles-Team/market-data-mcp.git
cd market-data-mcp
pip install -e ".[test]"
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[test]"
uv run market-data-mcp
```

## Prebuilt Docker image

A single-target runtime image is published on every release (entrypoint
`market-data-mcp`):

```bash
docker pull example/market-data-mcp@sha256:<digest>

docker run --rm -i \
  -e MARKET_DATA_CMC_API_KEY=your_coinmarketcap_key \
  -e MARKET_DATA_FRED_API_KEY=your_fred_key \
  example/market-data-mcp@sha256:<digest>        # stdio transport (default)
```

For an HTTP server with a published port, see [Deployment](deployment.md).

## Verify the install

```bash
market-data-mcp --help
```

## Next steps

- **[Deployment](deployment.md)** — run it as a long-lived MCP server behind Caddy + DNS.
- **[Usage](usage.md)** — call the eight tools and read the source-adapter presets.
- **[Configuration](configuration.md)** — the operator contract and every environment variable.
