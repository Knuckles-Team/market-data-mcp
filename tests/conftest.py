"""Shared test fixtures. No live network: every HTTP call is mocked."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Read one recorded or synthetic fixture JSON file by name."""
    return json.loads((FIXTURES / name).read_text())


def mock_client(
    base_url: str, handler: Callable[[httpx.Request], httpx.Response]
) -> httpx.AsyncClient:
    """An ``httpx.AsyncClient`` whose transport is a synchronous fixture handler."""
    return httpx.AsyncClient(base_url=base_url, transport=httpx.MockTransport(handler))


def json_response(payload: dict) -> httpx.Response:
    """A 200 JSON response carrying ``payload``."""
    return httpx.Response(200, json=payload)


@pytest.fixture
def fixture() -> Callable[[str], dict]:
    return load_fixture
