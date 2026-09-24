"""Credential references for the two keyed sources (CoinMarketCap, FRED).

Every value is resolved through ``agent_connector_sdk.credentials`` at call
time — never read directly from ``os.environ``, never logged, never cached to
disk, never embedded in a fixture, and never accepted as an MCP tool argument.
"""

from __future__ import annotations

from agent_connector_sdk.credentials.references import parse_secret_reference
from agent_connector_sdk.credentials.resolver import (
    CompositeCredentialResolver,
    CredentialResolver,
    CredentialUnavailableError,
    EnvironmentCredentialResolver,
)

__all__ = [
    "CredentialUnavailableError",
    "CMC_API_KEY_REFERENCE",
    "FRED_API_KEY_REFERENCE",
    "default_resolver",
    "resolve_cmc_api_key",
    "resolve_fred_api_key",
]

#: ``env://`` is the default; a deployment may repoint either to
#: ``openbao://apps/market-data-mcp#<field>`` via the same-named environment
#: variable holding an ``openbao://`` reference instead.
CMC_API_KEY_REFERENCE = "env://MARKET_DATA_CMC_API_KEY"
FRED_API_KEY_REFERENCE = "env://MARKET_DATA_FRED_API_KEY"


def default_resolver() -> CredentialResolver:
    """The environment resolver; OpenBao is added by the deployment composition root."""
    return CompositeCredentialResolver({"env": EnvironmentCredentialResolver()})


def _resolve(reference: str, resolver: CredentialResolver | None) -> str:
    return (resolver or default_resolver()).resolve(parse_secret_reference(reference))


def resolve_cmc_api_key(resolver: CredentialResolver | None = None) -> str:
    """Return the CoinMarketCap Pro API key.

    Raises:
        CredentialUnavailableError: the reference is not resolvable.
    """
    return _resolve(CMC_API_KEY_REFERENCE, resolver)


def resolve_fred_api_key(resolver: CredentialResolver | None = None) -> str:
    """Return the FRED/ALFRED API key.

    Raises:
        CredentialUnavailableError: the reference is not resolvable.
    """
    return _resolve(FRED_API_KEY_REFERENCE, resolver)
